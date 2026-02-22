import os
import uuid
import subprocess
from django.shortcuts import render
from django.http import HttpResponse, FileResponse, JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.http import require_GET

UPLOAD_DIR = settings.MEDIA_ROOT / "uploads"
OUTPUT_DIR = settings.MEDIA_ROOT / "converted"

ALLOWED_TYPES = {
    ".odt": "docx",
    ".ods": "xlsx",
    ".odp": "pptx",
}

FORMAT_LABELS = {
    ".odt": ("ODT → DOCX", "Word Document"),
    ".ods": ("ODS → XLSX", "Excel Spreadsheet"),
    ".odp": ("ODP → PPTX", "PowerPoint Presentation"),
}

# Ensure dirs exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def dashboard(request):
    """Main dashboard view."""
    return render(request, "dashboard.html")


def convert_file(request):
    """AJAX endpoint: receives file, converts, returns JSON with download token."""
    if request.method != "POST" or not request.FILES.get("file"):
        return JsonResponse({"error": "No file provided."}, status=400)

    file = request.FILES["file"]

    # File size validation
    if file.size > settings.MAX_UPLOAD_SIZE:
        return JsonResponse({"error": "File too large. Max size is 10 MB."}, status=400)

    ext = os.path.splitext(file.name)[1].lower()

    # Extension validation
    if ext not in ALLOWED_TYPES:
        return JsonResponse(
            {"error": f"Unsupported format '{ext}'. Only ODT, ODS, ODP are accepted."},
            status=400,
        )

    # Unique filename (security)
    unique_name = f"{uuid.uuid4()}{ext}"

    fs = FileSystemStorage(location=UPLOAD_DIR)
    filename = fs.save(unique_name, file)
    filepath = UPLOAD_DIR / filename

    target_format = ALLOWED_TYPES[ext]
    output_filename = filename.replace(ext, "." + target_format)
    output_file_path = OUTPUT_DIR / output_filename

    try:
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to", target_format,
                str(filepath),
                "--outdir", str(OUTPUT_DIR),
            ],
            check=True,
            timeout=60,
        )
    except subprocess.CalledProcessError:
        return JsonResponse({"error": "Conversion failed. Please try again."}, status=500)
    except subprocess.TimeoutExpired:
        return JsonResponse({"error": "Conversion timed out."}, status=500)

    label, format_name = FORMAT_LABELS[ext]
    original_name = os.path.splitext(file.name)[0] + "." + target_format

    return JsonResponse(
        {
            "success": True,
            "token": output_filename,
            "original_name": original_name,
            "label": label,
            "format_name": format_name,
            "size_kb": round(output_file_path.stat().st_size / 1024, 1),
        }
    )


@require_GET
def download_file(request, token):
    """Serves the converted file for download by token."""
    # Security: token must be a plain filename (no path traversal)
    if "/" in token or "\\" in token or ".." in token:
        return HttpResponse("Invalid token.", status=400)

    output_file_path = OUTPUT_DIR / token
    if not output_file_path.exists():
        return HttpResponse("File not found or expired.", status=404)

    # Derive a friendly download name from the token
    ext = os.path.splitext(token)[1]
    friendly_name = f"converted{ext}"

    response = FileResponse(
        open(output_file_path, "rb"),
        as_attachment=True,
        filename=friendly_name,
    )
    return response