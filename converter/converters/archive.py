import zipfile
import tarfile
import py7zr
import shutil
import os
import tempfile
from pathlib import Path

def convert(input_path: Path, output_path: Path) -> None:
    """Converts archives by extracting to a temp directory, then re-packaging."""
    in_ext = input_path.name.lower()
    out_ext = output_path.name.lower()
    
    # We use a temporary directory to extract everything
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        _extract(input_path, temp_path)
        _compress(temp_path, output_path)

def _extract(archive_path: Path, target_dir: Path):
    name = archive_path.name.lower()
    if name.endswith(".zip"):
        with zipfile.ZipFile(archive_path, 'r') as z:
            z.extractall(target_dir)
    elif name.endswith(".tar.gz") or name.endswith(".tgz"):
        with tarfile.open(archive_path, 'r:gz') as t:
            t.extractall(target_dir, filter="data")
    elif name.endswith(".tar"):
        with tarfile.open(archive_path, 'r:') as t:
            t.extractall(target_dir, filter="data")
    elif name.endswith(".7z"):
        with py7zr.SevenZipFile(archive_path, mode='r') as z:
            z.extractall(path=target_dir)
    else:
        raise ValueError("Unsupported archive format for reading.")

def _compress(source_dir: Path, output_path: Path):
    name = output_path.name.lower()
    
    # Get all files and dirs in source_dir
    items = list(source_dir.glob("*"))
    
    if name.endswith(".zip"):
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for item in items:
                _add_to_zip(z, item, source_dir)
    elif name.endswith(".tar.gz") or name.endswith(".tgz"):
        with tarfile.open(output_path, 'w:gz') as t:
            for item in items:
                t.add(item, arcname=item.relative_to(source_dir))
    elif name.endswith(".tar"):
        with tarfile.open(output_path, 'w:') as t:
            for item in items:
                t.add(item, arcname=item.relative_to(source_dir))
    elif name.endswith(".7z"):
        with py7zr.SevenZipFile(output_path, mode='w') as z:
            z.writeall(source_dir, arcname='')
    else:
        raise ValueError("Unsupported archive format for writing.")

def _add_to_zip(z: zipfile.ZipFile, path: Path, base_dir: Path):
    if path.is_file():
        z.write(path, arcname=path.relative_to(base_dir))
    elif path.is_dir():
        for sub_path in path.iterdir():
            _add_to_zip(z, sub_path, base_dir)
