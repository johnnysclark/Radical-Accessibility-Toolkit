"""
Input validation utilities.

Provides validation functions for file paths, image formats, and processing parameters.
"""

import os
import platform
import re
from pathlib import Path
from typing import Tuple


# Supported image formats
SUPPORTED_FORMATS = {
    '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.pdf'
}


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_image_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate that the file exists and is a supported image format.

    Args:
        file_path: Path to the image file

    Returns:
        Tuple of (is_valid, message)
        - is_valid: True if valid, False otherwise
        - message: Error message if invalid, empty string if valid

    Examples:
        >>> validate_image_file("plan.jpg")
        (True, "")
        >>> validate_image_file("missing.jpg")
        (False, "File not found: missing.jpg")
    """
    path = Path(file_path)

    # Check if file exists
    if not path.exists():
        return False, f"File not found: {file_path}"

    # Check if it's a file (not directory)
    if not path.is_file():
        return False, f"Path is not a file: {file_path}"

    # Check file extension
    extension = path.suffix.lower()
    if extension not in SUPPORTED_FORMATS:
        supported_list = ', '.join(sorted(SUPPORTED_FORMATS))
        return False, f"Unsupported file format: {extension}. Supported formats: {supported_list}"

    # Check if file is readable
    if not os.access(path, os.R_OK):
        return False, f"File is not readable: {file_path}"

    return True, ""


def validate_threshold(threshold: int) -> Tuple[bool, str]:
    """
    Validate threshold value is within acceptable range.

    Args:
        threshold: Threshold value (0-255)

    Returns:
        Tuple of (is_valid, message)
        - is_valid: True if valid, False otherwise
        - message: Error message if invalid, empty string if valid

    Examples:
        >>> validate_threshold(128)
        (True, "")
        >>> validate_threshold(300)
        (False, "Threshold must be between 0 and 255, got: 300")
    """
    if not isinstance(threshold, int):
        return False, f"Threshold must be an integer, got: {type(threshold).__name__}"

    if threshold < 0 or threshold > 255:
        return False, f"Threshold must be between 0 and 255, got: {threshold}"

    return True, ""


def validate_paper_size(size: str) -> Tuple[bool, str]:
    """
    Validate paper size is supported.

    Args:
        size: Paper size name (e.g., 'letter', 'tabloid')

    Returns:
        Tuple of (is_valid, message)
        - is_valid: True if valid, False otherwise
        - message: Error message if invalid, empty string if valid
    """
    valid_sizes = {'letter', 'tabloid'}

    if size.lower() not in valid_sizes:
        return False, f"Invalid paper size: {size}. Supported sizes: {', '.join(sorted(valid_sizes))}"

    return True, ""


def validate_output_path(output_path: str) -> Tuple[bool, str]:
    """
    Validate output path is writable.

    Args:
        output_path: Path for output file

    Returns:
        Tuple of (is_valid, message)
        - is_valid: True if valid, False otherwise
        - message: Error message if invalid, empty string if valid
    """
    path = Path(output_path)

    # Check if parent directory exists
    parent = path.parent
    if not parent.exists():
        return False, f"Output directory does not exist: {parent}"

    # Check if parent directory is writable
    if not os.access(parent, os.W_OK):
        return False, f"Output directory is not writable: {parent}"

    # Check if file already exists and is writable
    if path.exists() and not os.access(path, os.W_OK):
        return False, f"Output file exists but is not writable: {output_path}"

    # Check if output has .pdf extension
    if path.suffix.lower() != '.pdf':
        return False, f"Output file must have .pdf extension, got: {path.suffix}"

    return True, ""


def validate_density(density: float) -> Tuple[bool, str]:
    """
    Validate density percentage.

    Args:
        density: Density percentage (0-100)

    Returns:
        Tuple of (is_valid, message)
        - is_valid: True if valid, False otherwise
        - message: Error message if invalid, empty string if valid
    """
    if not isinstance(density, (int, float)):
        return False, f"Density must be a number, got: {type(density).__name__}"

    if density < 0 or density > 100:
        return False, f"Density must be between 0 and 100, got: {density}"

    return True, ""


def generate_output_filename(input_path: str, suffix: str = "_piaf") -> str:
    """
    Generate output filename based on input filename.

    Args:
        input_path: Path to input file
        suffix: Suffix to add to filename (default: "_piaf")

    Returns:
        Generated output path with .pdf extension

    Examples:
        >>> generate_output_filename("plan.jpg")
        'plan_piaf.pdf'
        >>> generate_output_filename("/path/to/sketch.png", "_output")
        '/path/to/sketch_output.pdf'
    """
    path = Path(input_path)
    stem = path.stem  # Filename without extension
    parent = path.parent

    output_name = f"{stem}{suffix}.pdf"
    return str(parent / output_name)


def resolve_wsl_path(path: str) -> str:
    """
    Resolve a path that may be in WSL or Windows format to an absolute path.

    Handles:
    - /mnt/c/... WSL paths (resolve to absolute)
    - C:/... or C:\\... Windows-style paths (convert to WSL /mnt/c/...)
    - Relative paths (resolve to absolute)

    Args:
        path: Input path that may be in various formats

    Returns:
        Absolute resolved path string

    Examples:
        >>> resolve_wsl_path("C:/Users/test/file.pdf")
        '/mnt/c/Users/test/file.pdf'
        >>> resolve_wsl_path("output.pdf")
        '/current/working/dir/output.pdf'
    """
    # Check if we're in WSL (Linux with microsoft in kernel)
    is_wsl = 'microsoft' in platform.uname().release.lower()

    if is_wsl:
        # Handle Windows-style paths like C:/... or C:\...
        windows_path_match = re.match(r'^([A-Za-z]):[/\\](.*)$', path)
        if windows_path_match:
            drive = windows_path_match.group(1).lower()
            rest = windows_path_match.group(2).replace('\\', '/')
            return f'/mnt/{drive}/{rest}'

    # Resolve to absolute path
    path_obj = Path(path)
    return str(path_obj.resolve())


def verify_file_exists(file_path: str) -> Tuple[bool, str]:
    """
    Verify that a file actually exists at the given path.

    Args:
        file_path: Path to verify

    Returns:
        Tuple of (exists, absolute_path_or_error_message)
        - If exists: (True, absolute_path)
        - If not exists: (False, error_message)

    Examples:
        >>> verify_file_exists("/path/to/existing.pdf")
        (True, '/path/to/existing.pdf')
        >>> verify_file_exists("/path/to/missing.pdf")
        (False, 'File not found at: /path/to/missing.pdf')
    """
    resolved = resolve_wsl_path(file_path)
    path_obj = Path(resolved)

    if path_obj.exists() and path_obj.is_file():
        return True, str(path_obj.resolve())
    else:
        return False, f"File not found at: {resolved}"
