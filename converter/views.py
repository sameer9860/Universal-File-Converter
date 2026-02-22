import os
import uuid
import subprocess
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

UPLOAD_DIR = settings.MEDIA_ROOT / "uploads"
OUTPUT_DIR = settings.MEDIA_ROOT / "converted"

ALLOWED_TYPES = {
    ".odt": "docx",
    ".ods": "xlsx",
    ".odp": "pptx",
}

def upload_file(request):
    if request.method == "POST" and request.FILES.get("file"):

        file = request.FILES["file"]

        # ✅ File size validation
        if file.size > settings.MAX_UPLOAD_SIZE:
            return HttpResponse("File too large (Max 10MB)")

        ext = os.path.splitext(file.name)[1].lower()

        # ✅ Extension validation
        if ext not in ALLOWED_TYPES:
            return HttpResponse("Unsupported file format")

        # ✅ Unique filename (security)
        unique_name = f"{uuid.uuid4()}{ext}"

        fs = FileSystemStorage(location=UPLOAD_DIR)
        filename = fs.save(unique_name, file)
        filepath = UPLOAD_DIR / filename

        target_format = ALLOWED_TYPES[ext]

        try:
            subprocess.run([
                "libreoffice",
                "--headless",
                "--convert-to", target_format,
                str(filepath),
                "--outdir", str(OUTPUT_DIR)
            ], check=True)

            output_filename = f"{filename.replace(ext, '.' + target_format)}"
            output_file_path = OUTPUT_DIR / output_filename

            response = FileResponse(
                open(output_file_path, "rb"),
                as_attachment=True,
                filename=output_filename
            )

            # # ✅ Cleanup after response
            # os.remove(filepath)
            # os.remove(output_file_path)

            return response

        except subprocess.CalledProcessError:
            return HttpResponse("Conversion failed")

    return render(request, "upload.html")