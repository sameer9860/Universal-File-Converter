import os
import uuid
import subprocess
from pathlib import Path
from django.shortcuts import render
from django.http import HttpResponse, FileResponse, JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.http import require_GET

from .converters import document, image, audio, video, data, archive

UPLOAD_DIR = settings.MEDIA_ROOT / "uploads"
OUTPUT_DIR = settings.MEDIA_ROOT / "converted"

# Ensure dirs exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Map from incoming extension -> allowed outgoing extensions -> (category, handler_module)
# We use lowercase with dot
CONVERSION_MAP = {
    # Documents (LibreOffice + Pandoc)
    ".docx": {"pdf": document, "odt": document, "txt": document, "html": document, "rtf": document, "md": document},
    ".odt":  {"docx": document, "pdf": document, "txt": document, "html": document, "rtf": document},
    ".pdf":  {"docx": document, "txt": document, "html": document}, # via pandoc/libreoffice (best effort)
    ".rtf":  {"docx": document, "pdf": document, "odt": document, "txt": document},
    ".txt":  {"docx": document, "pdf": document, "html": document, "md": document},
    ".md":   {"html": document, "pdf": document, "docx": document},
    ".html": {"pdf": document, "docx": document, "md": document, "txt": document},
    ".pptx": {"pdf": document, "html": document, "odp": document},
    ".odp":  {"pptx": document, "pdf": document},
    
    # Images (Pillow + ImageMagick)
    ".png":  {"jpg": image, "webp": image, "bmp": image, "gif": image, "svg": image, "ico": image, "tiff": image},
    ".jpg":  {"png": image, "webp": image, "bmp": image, "gif": image, "tiff": image, "ico": image},
    ".jpeg": {"png": image, "webp": image, "bmp": image, "gif": image, "tiff": image, "ico": image},
    ".svg":  {"png": image, "jpg": image, "pdf": image},
    ".webp": {"png": image, "jpg": image, "gif": image},
    ".heic": {"jpg": image, "png": image},
    ".bmp":  {"png": image, "jpg": image, "webp": image},
    ".tiff": {"png": image, "jpg": image, "pdf": image},
    
    # Audio (FFmpeg)
    ".mp3":  {"wav": audio, "ogg": audio, "flac": audio, "aac": audio, "m4a": audio},
    ".wav":  {"mp3": audio, "ogg": audio, "flac": audio, "aac": audio},
    ".flac": {"mp3": audio, "wav": audio, "ogg": audio, "aac": audio},
    ".ogg":  {"mp3": audio, "wav": audio, "flac": audio},
    ".aac":  {"mp3": audio, "wav": audio, "ogg": audio},
    ".m4a":  {"mp3": audio, "wav": audio, "ogg": audio},

    # Video (FFmpeg)
    ".mp4":  {"avi": video, "mkv": video, "mov": video, "webm": video, "gif": video, "mp3": video, "wav": video},
    ".avi":  {"mp4": video, "mkv": video, "mov": video, "webm": video},
    ".mkv":  {"mp4": video, "avi": video, "mov": video},
    ".mov":  {"mp4": video, "avi": video, "mkv": video},
    ".webm": {"mp4": video, "gif": video},

    # Data/Spreadsheets (pandas)
    ".xlsx": {"csv": data, "ods": document, "pdf": document, "json": data, "html": data},
    ".ods":  {"xlsx": document, "csv": document, "pdf": document},
    ".csv":  {"xlsx": data, "json": data, "xml": data, "yaml": data, "ods": document, "pdf": document},
    ".json": {"csv": data, "xml": data, "yaml": data, "xlsx": data},
    ".xml":  {"json": data, "csv": data, "yaml": data},
    ".yaml": {"json": data, "xml": data, "csv": data},
    ".yml":  {"json": data, "xml": data, "csv": data},

    # Archives (zipfile, tarfile, py7zr)
    ".zip":    {"tar": archive, "tar.gz": archive, "7z": archive},
    ".rar":    {"zip": archive, "tar.gz": archive, "7z": archive}, # Requires unrar potentially, will let py7zr try or fail cleanly
    ".7z":     {"zip": archive, "tar.gz": archive},
    ".tar.gz": {"zip": archive, "7z": archive},
    ".tgz":    {"zip": archive, "7z": archive},
    ".tar":    {"zip": archive, "7z": archive, "tar.gz": archive},
}


def dashboard(request):
    """Main dashboard view."""
    return render(request, "dashboard.html")


def convert_file(request):
    """AJAX endpoint: receives file and requested output format, converts, returns JSON."""
    if request.method != "POST" or not request.FILES.get("file"):
        return JsonResponse({"error": "No file provided."}, status=400)

    target_format = request.POST.get("target_format", "").lower().strip(".")
    if not target_format:
        return JsonResponse({"error": "No target format specified."}, status=400)

    file = request.FILES["file"]

    if file.size > settings.MAX_UPLOAD_SIZE:
        return JsonResponse({"error": "File too large. Max size is 10 MB."}, status=400)

    # Use Path for robust extension extraction (handles .tar.gz)
    # But for simplicity on upload, we can look at ends
    orig_name = file.name.lower()
    in_ext = ""
    for candidate_ext in sorted(CONVERSION_MAP.keys(), key=len, reverse=True):
        if orig_name.endswith(candidate_ext):
            in_ext = candidate_ext
            break
            
    if not in_ext:
        # Fallback to simple split
        in_ext = os.path.splitext(orig_name)[1]

    if in_ext not in CONVERSION_MAP:
        return JsonResponse(
            {"error": f"Unsupported input format '{in_ext}'."},
            status=400,
        )

    allowed_targets = CONVERSION_MAP[in_ext]
    if target_format not in allowed_targets:
        return JsonResponse(
            {"error": f"Cannot convert {in_ext} to .{target_format}. Allowed: {', '.join(allowed_targets.keys())}"},
            status=400,
        )

    # Hand off to the specific module
    handler_module = allowed_targets[target_format]

    # Save incoming
    unique_id = str(uuid.uuid4())
    fs = FileSystemStorage(location=UPLOAD_DIR)
    filename = fs.save(unique_id + in_ext, file)
    filepath = UPLOAD_DIR / filename

    output_filename = unique_id + "." + target_format
    output_file_path = OUTPUT_DIR / output_filename

    try:
        handler_module.convert(filepath, output_file_path)
    except Exception as e:
        return JsonResponse({"error": f"Conversion failed: {str(e)}"}, status=500)

    if not output_file_path.exists() or output_file_path.stat().st_size == 0:
        return JsonResponse({"error": "Conversion generated an empty or missing file."}, status=500)

    # Determine original base name
    orig_base = orig_name
    if orig_base.endswith(in_ext):
        orig_base = orig_base[:-len(in_ext)]
    new_friendly_name = orig_base + "." + target_format

    return JsonResponse(
        {
            "success": True,
            "token": output_filename,
            "original_name": new_friendly_name,
            "label": f"{in_ext[1:].upper()} → {target_format.upper()}",
            "format_name": f"{target_format.upper()} File",
            "size_kb": round(output_file_path.stat().st_size / 1024, 1),
        }
    )


@require_GET
def download_file(request, token):
    """Serves the converted file for download by token."""
    if "/" in token or "\\" in token or ".." in token:
        return HttpResponse("Invalid token.", status=400)

    output_file_path = OUTPUT_DIR / token
    if not output_file_path.exists():
        return HttpResponse("File not found or expired.", status=404)

    ext = ""
    # Look for compound extensions first
    for candidate_ext in [".tar.gz"]:
        if token.endswith(candidate_ext):
            ext = candidate_ext
            break
    if not ext:
        ext = os.path.splitext(token)[1]
        
    friendly_name = f"converted{ext}"

    response = FileResponse(
        open(output_file_path, "rb"),
        as_attachment=True,
        filename=friendly_name,
    )
    return response