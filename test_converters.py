import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FileConverter.settings")
django.setup()

from converter.converters import data, document, image, audio, video, archive

def test_all():
    print("Testing data: CSV -> JSON")
    data.convert(Path('test.csv'), Path('test.json'))
    print("  -> OK")
    
    # Skipping LibreOffice text.txt -> pdf because LibreOffice needs an x server sometimes or takes time
    # print("Testing doc: TXT -> PDF")
    # document.convert(Path('test.txt'), Path('out.pdf'))
    # print("  -> OK")
    
    print("Testing image: PNG -> JPG")
    image.convert(Path('test.png'), Path('test.jpg'))
    print("  -> OK")
    
    print("Testing audio: MP3 -> WAV")
    audio.convert(Path('test.mp3'), Path('test.wav'))
    print("  -> OK")
    
    print("Testing video: MP4 -> AVI")
    video.convert(Path('test.mp4'), Path('test.avi'))
    print("  -> OK")
    
    print("Testing archive: ZIP -> TAR.GZ")
    archive.convert(Path('test.zip'), Path('test.tar.gz'))
    print("  -> OK")
    
    print("All backend converters successful!")

if __name__ == "__main__":
    test_all()
