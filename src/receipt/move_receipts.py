import shutil
from pathlib import Path


def move_file(src_path, dest_dir):
    src_path = Path(src_path)
    dest_dir = Path(dest_dir)

    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / src_path.name
    shutil.move(str(src_path), str(dest_path))

    return dest_path
