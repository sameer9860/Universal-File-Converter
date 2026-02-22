from PIL import Image
import subprocess
from pathlib import Path

# Basic image formats handled by Pillow
PILLOW_SUPPORTED = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff", ".ico"]

def convert(input_path: Path, output_path: Path) -> None:
    """Converts images using Pillow or ImageMagick (convert)."""
    in_ext = input_path.suffix.lower()
    out_ext = output_path.suffix.lower()
    
    # SVG requires ImageMagick, Pillow cannot read it
    if in_ext == ".svg" or out_ext == ".svg":
        _convert_imagemagick(input_path, output_path)
        return
        
    # Pillow conversion
    try:
        with Image.open(input_path) as img:
            # Drop alpha channel if converting to JPEG
            if out_ext in [".jpg", ".jpeg"] and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Special case for ICO which needs size arrays sometimes, but Pillow defaults are ok
            img.save(output_path)
    except Exception as e:
        # Fallback to imagemagick if Pillow fails
        _convert_imagemagick(input_path, output_path)

def _convert_imagemagick(input_path: Path, output_path: Path):
    try:
        subprocess.run(
            ["convert", str(input_path), str(output_path)],
            check=True,
            timeout=60,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ImageMagick conversion failed: {e}")
