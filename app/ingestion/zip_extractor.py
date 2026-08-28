"""
Safe ZIP extraction module for Obsidian vaults.
Includes protection against ZipSlip vulnerabilities, symlink exploitation,
and resource exhaustion.
"""

import os
import shutil
import zipfile
from pathlib import Path
from typing import Tuple, List
from app.config import settings


class ZipExtractionError(Exception):
    """Custom exception raised when ZIP extraction fails or is unsafe."""
    pass


def is_safe_path(base_dir: Path, target_path: Path) -> bool:
    """
    Verify that target_path is strictly inside base_dir to prevent ZipSlip attacks.
    """
    try:
        base_dir_resolved = base_dir.resolve()
        target_resolved = target_path.resolve()
        # commonpath will raise ValueError if paths are on different drives (Windows)
        # or returns the common parent directory.
        common = os.path.commonpath([str(base_dir_resolved), str(target_resolved)])
        return common == str(base_dir_resolved)
    except (ValueError, Exception):
        return False


def extract_zip_safely(
    zip_path: Path,
    target_dir: Path,
    max_size_mb: int = settings.MAX_FILE_SIZE_MB,
    clear_target: bool = True
) -> Tuple[Path, List[str]]:
    """
    Safely extract a ZIP archive into target_dir.

    Args:
        zip_path: Path to the uploaded ZIP file.
        target_dir: Directory where files should be extracted.
        max_size_mb: Maximum allowed total uncompressed size in megabytes.
        clear_target: If True, deletes existing files in target_dir before extraction.

    Returns:
        Tuple of (target_dir, list_of_extracted_rel_paths)

    Raises:
        ZipExtractionError: If file is invalid, corrupt, unsafe, or exceeds size limits.
    """
    if not zip_path.exists():
        raise ZipExtractionError(f"ZIP file does not exist: {zip_path}")

    # Check zip file size
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    if zip_size_mb > max_size_mb:
        raise ZipExtractionError(
            f"Uploaded ZIP size ({zip_size_mb:.1f} MB) exceeds maximum allowed limit ({max_size_mb} MB)."
        )

    if clear_target and target_dir.exists():
        try:
            shutil.rmtree(target_dir)
        except Exception as e:
            raise ZipExtractionError(f"Failed to clean target directory: {e}")

    target_dir.mkdir(parents=True, exist_ok=True)
    extracted_files: List[str] = []
    total_uncompressed_bytes = 0
    max_bytes = max_size_mb * 1024 * 1024

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            # First pass: check for malicious file names, path traversal, symlinks, total size
            for member in zf.infolist():
                # Check for ZipBomb / size exhaustion
                total_uncompressed_bytes += member.file_size
                if total_uncompressed_bytes > max_bytes:
                    raise ZipExtractionError(
                        f"Uncompressed vault size exceeds safety limit of {max_size_mb} MB."
                    )

                # Check for path traversal (ZipSlip)
                member_path = target_dir / member.filename
                if not is_safe_path(target_dir, member_path):
                    raise ZipExtractionError(
                        f"Malicious path traversal detected in ZIP entry: {member.filename}"
                    )

                # Check for symlinks
                # Mode 0o120000 indicates a symbolic link in POSIX zip header
                if (member.external_attr >> 16) & 0o120000 == 0o120000:
                    raise ZipExtractionError(
                        f"Symbolic link detected in ZIP entry (rejected for security): {member.filename}"
                    )

            # Second pass: extract files safely
            for member in zf.infolist():
                # Skip macOS resource forks and metadata
                clean_name = member.filename.replace("\\", "/")
                if clean_name.startswith("__MACOSX/") or "/__MACOSX/" in clean_name or Path(clean_name).name.startswith("._"):
                    continue

                dest_path = target_dir / member.filename

                # If entry is a directory
                if member.is_dir() or member.filename.endswith("/"):
                    dest_path.mkdir(parents=True, exist_ok=True)
                    continue

                # Ensure parent directory exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                with zf.open(member) as source, open(dest_path, "wb") as target:
                    shutil.copyfileobj(source, target)

                rel_path = str(dest_path.relative_to(target_dir))
                extracted_files.append(rel_path)

    except zipfile.BadZipFile:
        raise ZipExtractionError("The uploaded file is not a valid or readable ZIP archive.")
    except ZipExtractionError:
        raise
    except Exception as e:
        raise ZipExtractionError(f"Unexpected error during ZIP extraction: {str(e)}")

    return target_dir, extracted_files
