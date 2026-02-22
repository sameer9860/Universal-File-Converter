import subprocess
import os
from pathlib import Path

# Formats LibreOffice can handle
LIBREOFFICE_FORMATS = {
    ".odt": ["docx", "pdf", "txt", "html", "rtf"],
    ".ods": ["xlsx", "csv", "pdf"],
    ".odp": ["pptx", "pdf"],
    ".docx": ["pdf", "odt", "txt", "html", "rtf"],
    ".xlsx": ["csv", "ods", "pdf", "html"],
    ".pptx": ["pdf", "html", "odp"],
    ".csv": ["xlsx", "ods", "pdf"],
}

# Formats Pandoc can handle (that LibreOffice doesn't do as well or at all)
PANDOC_FORMATS = {
    ".md": ["html", "pdf", "docx"],
    ".html": ["pdf", "docx", "md", "txt"],
    ".txt": ["docx", "pdf", "html", "md"],
    ".rtf": ["docx", "pdf", "odt", "txt"],
}

def convert(input_path: Path, output_path: Path) -> None:
    """Converts documents using LibreOffice or Pandoc based on extension."""
    in_ext = input_path.suffix.lower()
    out_ext = output_path.suffix.lower().lstrip(".")

    # Try LibreOffice first for primary office formats
    if in_ext in LIBREOFFICE_FORMATS and out_ext in LIBREOFFICE_FORMATS.get(in_ext, []):
        _convert_libreoffice(input_path, output_path, out_ext)
    else:
        # Fallback to Pandoc for text/markdown/html
        _convert_pandoc(input_path, output_path)

def _convert_libreoffice(input_path: Path, output_path: Path, out_ext: str):
    # Libreoffice outputs to a directory and auto-names the file.
    # We output to the target directory and rename if necessary.
    outdir = output_path.parent
    try:
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to", out_ext,
                str(input_path),
                "--outdir", str(outdir)
            ],
            check=True,
            timeout=120,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Libreoffice creates the file using the original name + new extension
        expected_output = outdir / (input_path.stem + "." + out_ext)
        if expected_output.exists() and expected_output != output_path:
            expected_output.rename(output_path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"LibreOffice conversion failed: {e}")

def _convert_pandoc(input_path: Path, output_path: Path):
    try:
        # For PDF via Pandoc on ubuntu, typically requires pdflatex or wkhtmltopdf. 
        # But we can also use pandoc's native pdf or docx engine. 
        cmd = ["pandoc", str(input_path), "-o", str(output_path)]
        subprocess.run(
            cmd,
            check=True,
            timeout=120,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Pandoc conversion failed: {e}")
