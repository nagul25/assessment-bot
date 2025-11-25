import platform
import subprocess
import os

from app.log_config import logger

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def convert_ppt_to_png(local_file_path: str, file_name: str) -> str:
    try:
        logger.info(f"Local ppt file path: {local_file_path} - {file_name}")
        output_dir = os.path.join(PROJECT_ROOT, "tempfiles", file_name, "slides")
        logger.info(f"Output directory for PNGs: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

        libreoffice_path = get_libreoffice_path()

        # Important: run conversion from the directory that contains the PPTX
        working_dir = os.path.dirname(local_file_path)

        command = [
            libreoffice_path,
            "--headless",
            "--invisible",
            "--nologo",
            "--nodefault",
            "--nofirststartwizard",
            "--convert-to",
            "png",
            "--outdir",
            output_dir,
            local_file_path
        ]

        logger.info(f"Running command: {' '.join(command)}")

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=working_dir,
            check=True,
        )

        if result.returncode != 0:
            logger.error(result.stderr)
            raise RuntimeError("LibreOffice conversion failed")

        return output_dir
    except subprocess.CalledProcessError as e:
        logger.error(f"Conversion failed: {e}")
        raise



def get_libreoffice_path():
    system = platform.system()

    if system == "Darwin":  # macOS
        return "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    elif system == "Linux":  # Ubuntu servers
        return "libreoffice"
    elif system == "Windows":
        return r"C:\Program Files\LibreOffice\program\soffice.exe"
    else:
        raise RuntimeError("Unsupported OS for LibreOffice conversion")