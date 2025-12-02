import platform
import subprocess
import os
import shutil
import glob

from app.log_config import logger

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def convert_ppt_to_png(local_file_path: str, file_name: str) -> str:
    try:
        logger.info(f"Local ppt file path: {local_file_path} - {file_name}")
        output_dir = os.path.join(PROJECT_ROOT, "tempfiles", file_name, "slides")
        logger.info(f"Output directory for PNGs: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

        libreoffice_path = get_libreoffice_path()

        # Convert PPT/PPTX -> PDF first (more reliable for multi-slide export)
        logger.info("Converting presentation to PDF using LibreOffice...")
        cmd_pdf = [
            libreoffice_path,
            "--headless",
            "--invisible",
            "--nologo",
            "--nodefault",
            "--nofirststartwizard",
            "--convert-to",
            "pdf",
            "--outdir",
            output_dir,
            local_file_path,
        ]
        logger.debug(f"Running command: {' '.join(cmd_pdf)}")
        subprocess.run(cmd_pdf, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Find produced PDF (LibreOffice names it same as input but with .pdf)
        base_name = os.path.splitext(os.path.basename(local_file_path))[0]
        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        if not os.path.exists(pdf_path):
            # try to find any pdf in output_dir produced recently
            pdfs = glob.glob(os.path.join(output_dir, "*.pdf"))
            if pdfs:
                pdf_path = sorted(pdfs, key=os.path.getmtime)[-1]
                logger.debug(f"Using discovered PDF: {pdf_path}")
            else:
                raise RuntimeError("PDF not produced by LibreOffice conversion")

        # Convert PDF -> PNG pages
        # Prefer pdftoppm (poppler) which produces one PNG per page: prefix-1.png, prefix-2.png, ...
        pdftoppm_path = shutil.which("pdftoppm")
        if pdftoppm_path:
            logger.info("Converting PDF to PNG using pdftoppm...")
            prefix = os.path.join(output_dir, "slide")
            cmd_pdftoppm = [pdftoppm_path, "-png", pdf_path, prefix]
            logger.debug(f"Running command: {' '.join(cmd_pdftoppm)}")
            subprocess.run(cmd_pdftoppm, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        else:
            # Fallback to ImageMagick (magick) if available
            magick_path = shutil.which("magick") or shutil.which("convert")
            if magick_path:
                logger.info("Converting PDF to PNG using ImageMagick...")
                # magick will write multiple files: slide-0.png, slide-1.png etc.
                out_pattern = os.path.join(output_dir, "slide.png")
                cmd_magick = [magick_path, "-density", "150", pdf_path, out_pattern]
                logger.debug(f"Running command: {' '.join(cmd_magick)}")
                subprocess.run(cmd_magick, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            else:
                # As last resort try direct LibreOffice PNG conversion (may only produce first slide)
                logger.warning("pdftoppm and ImageMagick not found; falling back to direct LibreOffice PNG conversion (may produce only first slide).")
                cmd_direct = [
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
                    local_file_path,
                ]
                logger.debug(f"Running command: {' '.join(cmd_direct)}")
                subprocess.run(cmd_direct, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Verify that at least one PNG was created
        pngs = sorted(glob.glob(os.path.join(output_dir, "*.png")))
        if not pngs:
            raise RuntimeError("No PNGs were created during conversion")

        logger.info(f"Created {len(pngs)} PNG files in {output_dir}")
        return output_dir

    except subprocess.CalledProcessError as e:
        logger.error(f"Conversion failed: returncode={getattr(e, 'returncode', None)} stderr={getattr(e, 'stderr', None)}")
        raise
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        raise


def get_libreoffice_path():
    # ...existing code...
    system = platform.system()

    if system == "Darwin":  # macOS
        return "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    elif system == "Linux":  # Ubuntu servers
        return "libreoffice"
    elif system == "Windows":
        return r"C:\Program Files\LibreOffice\program\soffice.exe"
    else:
        raise RuntimeError("Unsupported OS for LibreOffice conversion")
