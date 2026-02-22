import ffmpeg
from pathlib import Path

def convert(input_path: Path, output_path: Path) -> None:
    """Converts video files, or extracts audio, using FFmpeg via ffmpeg-python."""
    try:
        (
            ffmpeg
            .input(str(input_path))
            .output(str(output_path), loglevel="error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        stderr_txt = e.stderr.decode('utf8') if e.stderr else 'Unknown error'
        raise RuntimeError(f"FFmpeg video conversion failed: {stderr_txt}")
