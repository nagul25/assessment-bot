from datetime import datetime
import sys
from typing import List, Optional
from fastapi import UploadFile
from urllib.parse import urlparse
from app.models.models import QueryPromptRequest
from app.services.blobservice import download_blob_to_local, download_blob_to_local, upload_blob, upload_png_to_blob
from app.services.updated_conversion import convert_ppt_to_png as updated_convert_ppt_to_png
from app.services.rag_system import RAGSystem
from app.log_config import logger
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class QueryProcessorService:
    print("Initializing RAG System...")
    def __init__(self):
        try:
            self.rag_system = RAGSystem()
            print("System initialized successfully!\n")
        except Exception as e:
            print(f"Error initializing RAG system: {str(e)}")
            sys.exit(1)
    
    async def process_query(self, query: QueryPromptRequest, files: Optional[List[UploadFile]] = None):
        try:
            # Implement your query processing logic here
            print(f"Processing query with prompt: ", query)
            prompt = query.prompt

            # for file in files or []:
            if files:
                file_uploaded_response = await upload_blob(files)
            
            # pass the query to rag system to process and get response
            rag_response = self.rag_system.answer_question(prompt)
            print(f"RAG System response: ", rag_response)

            return {"message": f"Processed query: {prompt}", "upload_info": file_uploaded_response if files else None, "rag_response": rag_response}
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {"error": "Failed to process query"}
        
    async def process_assessment(self, assessment: QueryPromptRequest, files: Optional[List[UploadFile]] = None):
        try:
            # Implement your assessment processing logic here
            print(f"Processing assessment with prompt: ", assessment)
            prompt = assessment.prompt

            if files:
                # 1. upload ppt to blob storage
                file_uploaded_response = await upload_blob(files)

                # 2. iterate through each file and download it for processing
                files = file_uploaded_response.get("uploaded_files", [])
                
                for file in files:
                    blob_url = file.get("blob_url")
                    logger.info(f"Downloading and processing file from blob url: {blob_url}")
                    
                    # parse the url to get the file name
                    parsed_url = urlparse(blob_url)
                    file_name = parsed_url.path.split("/")[-1]
                    logger.info(f"Processing file: {file_name} from blob url: {blob_url}")

                    # 3. Download and write ppt slides into local path from azure
                    name, ext = os.path.splitext(file_name)
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    local_path = os.path.join(PROJECT_ROOT, "tempfiles", name, f"{name}_{timestamp}{ext}")
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    await download_blob_to_local(blob_url, local_path)
                    logger.info(f"Downloaded file to local path: {local_path}")
                    print("input file extension: ", ext)
                    
                    # 4. Convert ppt to png
                    png_output_dir = updated_convert_ppt_to_png(local_path, file_name=name)
                    logger.info(f"Converted PPT to PNGs at: {png_output_dir}")

                    # # 5. Upload converted slides to blob as png under one folder for each ppt
                    png_files = await upload_png_to_blob(png_output_dir, file_name=name)
                    logger.info(f"Uploaded PNG files to blob storage: {png_files}")

                    file["png_uploads"] = png_files
                    # 6. remove the local file after processing
                    os.remove(local_path)
                    logger.info(f"Removed local file: {local_path}")    

            # Placeholder for assessment logic
            assessment_result = f"Assessment processed for prompt: {prompt}"
            print(f"Assessment result: ", assessment_result)

            return {"message": assessment_result, "upload_info": file_uploaded_response if files else None}
        except Exception as e:
            logger.error(f"Error processing assessment: {e}")
            return {"error": "Failed to process assessment"}