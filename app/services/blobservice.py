import os
import shutil
import asyncio
from typing import List, Optional
from azure.storage.blob.aio import BlobServiceClient
from fastapi import UploadFile
from config import Config
from app.log_config import logger

connection_string = Config.BLOB_CONNECTION_STRING
container_name = Config.BLOB_CONTAINER_NAME

async def get_blob_service_client() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(connection_string)

async def upload_blob(files: Optional[List[UploadFile]]):
    blob_service_client = await get_blob_service_client()
    try:
        container_client = blob_service_client.get_container_client(container_name)
        file_contents = []
        uploaded_files = []
        # create container if not exists
        try:
            await container_client.create_container()
            print(f"Created container: {container_name}")
        except Exception as create_error:
            print(f"Container {container_name} may already exist: {create_error}")
            pass
        for file in files:
            blob_client = container_client.get_blob_client(blob=file.filename)
            content = await file.read()
            file_contents.append({"filename": file.filename, "content_type": file.content_type})
            print(f"Read file: {file.filename}, content_type: {file.content_type}")
            await blob_client.upload_blob(data=content, metadata={"content_type": file.content_type}, overwrite=True)
            uploaded_files.append({
                "filename": file.filename,
                "blob_url": blob_client.url
            })
            try:
                await file.close()
            except Exception as close_error:
                print(f"Error closing file {file.filename}: {close_error}")
                pass
            print(f"Uploaded blob: {file.filename} to container: {container_name}, blob url: {blob_client.url}")
        return {"uploaded_files": uploaded_files, "message": "Files uploaded successfully"}
    except Exception as e:
        print(f"Error uploading blob: {e}")
        raise
    finally:
        await blob_service_client.close()
        logger.info("Closing BlobServiceClient")


async def upload_png_to_blob(png_directory: str, file_name: str):
    blob_service_client = await get_blob_service_client()
    container_client = blob_service_client.get_container_client(container_name)
    logger.info(f"uploading pngs from directory: {png_directory} - under file: {file_name}")
    uploaded_pngs = []
    try:
        try:
            await container_client.create_container()
            logger.info(f"Created container: {container_name}")
        except Exception as create_error:
            logger.info(f"Container {container_name} may already exist: {create_error}")
            pass

        for index, png_file in enumerate(os.listdir(png_directory)):
            if png_file.endswith(".png"):
                png_path = os.path.join(png_directory, png_file)
                blob_path = f"{file_name}/{index}_{png_file}"
                blob_client = container_client.get_blob_client(blob=blob_path)
                with open(png_path, "rb") as data:
                    await blob_client.upload_blob(data, overwrite=True)
                logger.info(f"Uploaded PNG blob: {blob_path} to container: {container_name}, blob url: {blob_client.url}")
                uploaded_pngs.append({
                    "filename": png_file,
                    "blob_url": blob_client.url
                })
        return uploaded_pngs
    except Exception as e:
        logger.error(f"Error uploading PNGs to blob: {e}")
        raise
    finally:
        try:
            await blob_service_client.close()
        except Exception as close_err:
            logger.warning(f"Error closing BlobServiceClient: {close_err}")

        # remove directory (may contain files). Use a thread to avoid blocking the event loop.
        if os.path.isdir(png_directory):
            try:
                await asyncio.to_thread(shutil.rmtree, png_directory)
                logger.info(f"Removed temporary PNG directory: {png_directory}")
            except Exception as rm_err:
                logger.error(f"Failed to remove temporary PNG directory {png_directory}: {rm_err}")
        else:
            logger.debug(f"PNG directory not found or already removed: {png_directory}")
        logger.info("Closing BlobServiceClient and cleaned up temporary PNG directory")


async def download_blob_to_local(blob_url: str, local_path: str):
    blob_service_client = await get_blob_service_client()
    logger.info(f"Downloading blob from {blob_url}")
    try:
        # Extract blob name from URL if full URL is passed
        if blob_url.startswith("http"):
            blob_name = blob_url.split("/")[-1]
        else:
            blob_name = blob_url
        
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(local_path, "wb") as download_file:
            download_stream = await blob_client.download_blob()
            data = await download_stream.readall()
            download_file.write(data)
        logger.info(f"Downloaded blob from {blob_url} to local path {local_path}")
    except Exception as e:
        logger.error(f"Error downloading blob: {e}")
        raise
    finally:
        await blob_service_client.close()
        logger.info("Closing BlobServiceClient")