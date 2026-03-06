"""
Simple File-Based Cache for OCR Results

Provides temporary caching of Tesseract OCR results between the two phases
of the hybrid OCR workflow:
1. Phase 1: Run Tesseract, cache results, return instructions for Claude
2. Phase 2: Load cached results, merge with Claude's text extraction

The cache uses JSON files in a temp directory, keyed by image path hash.
Cache entries expire after a configurable timeout (default 5 minutes).
"""

import json
import hashlib
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger("tactile.cache")

# Default cache timeout in seconds (5 minutes)
DEFAULT_CACHE_TIMEOUT = 300

# Cache directory within system temp
CACHE_DIR_NAME = "tactile_core_ocr_cache"


def _get_cache_dir() -> Path:
    """Get or create the cache directory."""
    cache_dir = Path(tempfile.gettempdir()) / CACHE_DIR_NAME
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


def _get_cache_key(image_path: str) -> str:
    """
    Generate a cache key from the image path.

    Uses MD5 hash of the absolute path for consistent, safe filenames.
    """
    abs_path = str(Path(image_path).absolute())
    return hashlib.md5(abs_path.encode()).hexdigest()


def _get_cache_file(image_path: str) -> Path:
    """Get the cache file path for an image."""
    cache_key = _get_cache_key(image_path)
    return _get_cache_dir() / f"{cache_key}.json"


def cache_tesseract_results(
    image_path: str,
    results: List[Any],
    image_size: tuple = None,
    grid_info: dict = None
) -> bool:
    """
    Cache Tesseract OCR results for later retrieval.

    Args:
        image_path: Path to the source image
        results: List of DetectedText objects (will be serialized)
        image_size: Optional tuple of (width, height) to cache
        grid_info: Optional dict with grid overlay info (rows, cols, path)

    Returns:
        True if caching succeeded, False otherwise
    """
    try:
        cache_file = _get_cache_file(image_path)

        # Serialize DetectedText objects to dicts
        serialized = []
        for r in results:
            serialized.append({
                'text': r.text,
                'x': r.x,
                'y': r.y,
                'width': r.width,
                'height': r.height,
                'confidence': r.confidence,
                'is_dimension': r.is_dimension,
                'rotation_degrees': getattr(r, 'rotation_degrees', 0.0),
                'page_number': getattr(r, 'page_number', 1)
            })

        cache_data = {
            'image_path': str(Path(image_path).absolute()),
            'timestamp': time.time(),
            'results': serialized,
            'count': len(serialized)
        }

        if image_size:
            cache_data['image_size'] = list(image_size)

        if grid_info:
            cache_data['grid_info'] = grid_info

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)

        logger.debug(f"Cached {len(results)} Tesseract results for {image_path}")
        return True

    except Exception as e:
        logger.warning(f"Failed to cache Tesseract results: {e}")
        return False


def load_cached_tesseract(
    image_path: str,
    timeout: int = DEFAULT_CACHE_TIMEOUT
) -> Optional[Dict[str, Any]]:
    """
    Load cached Tesseract results if available and not expired.

    Args:
        image_path: Path to the source image
        timeout: Cache timeout in seconds (default 5 minutes)

    Returns:
        Dict with 'results' (list of dicts) and 'image_size' if found,
        None if cache miss or expired
    """
    try:
        cache_file = _get_cache_file(image_path)

        if not cache_file.exists():
            logger.debug(f"Cache miss for {image_path}")
            return None

        with open(cache_file, 'r') as f:
            cache_data = json.load(f)

        # Check if expired
        age = time.time() - cache_data.get('timestamp', 0)
        if age > timeout:
            logger.debug(f"Cache expired for {image_path} (age: {age:.0f}s)")
            cache_file.unlink()  # Clean up expired cache
            return None

        logger.debug(
            f"Cache hit for {image_path}: "
            f"{cache_data.get('count', 0)} results, age {age:.0f}s"
        )

        result = {
            'results': cache_data.get('results', []),
            'image_size': tuple(cache_data.get('image_size', [0, 0]))
        }

        # Include grid_info if present
        if 'grid_info' in cache_data:
            result['grid_info'] = cache_data['grid_info']

        return result

    except Exception as e:
        logger.warning(f"Failed to load cached results: {e}")
        return None


def clear_cache(image_path: str = None) -> int:
    """
    Clear cache entries.

    Args:
        image_path: If provided, clear only this image's cache.
                    If None, clear all expired entries.

    Returns:
        Number of cache entries cleared
    """
    cache_dir = _get_cache_dir()
    cleared = 0

    try:
        if image_path:
            # Clear specific cache
            cache_file = _get_cache_file(image_path)
            if cache_file.exists():
                cache_file.unlink()
                cleared = 1
        else:
            # Clear all expired entries
            for cache_file in cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    age = time.time() - data.get('timestamp', 0)
                    if age > DEFAULT_CACHE_TIMEOUT:
                        cache_file.unlink()
                        cleared += 1
                except Exception:
                    # If we can't read it, delete it
                    cache_file.unlink()
                    cleared += 1

        logger.debug(f"Cleared {cleared} cache entries")
        return cleared

    except Exception as e:
        logger.warning(f"Failed to clear cache: {e}")
        return cleared


def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the cache.

    Returns:
        Dict with cache statistics
    """
    cache_dir = _get_cache_dir()
    total = 0
    expired = 0
    total_size = 0

    for cache_file in cache_dir.glob("*.json"):
        total += 1
        total_size += cache_file.stat().st_size
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            age = time.time() - data.get('timestamp', 0)
            if age > DEFAULT_CACHE_TIMEOUT:
                expired += 1
        except Exception:
            expired += 1

    return {
        'cache_dir': str(cache_dir),
        'total_entries': total,
        'expired_entries': expired,
        'active_entries': total - expired,
        'total_size_bytes': total_size
    }
