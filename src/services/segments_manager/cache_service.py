"""
Segments Manager cache service.
Handles caching of Segments Manager data to local storage.
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging
from src.utils.file_operations import FileOperations

logger = logging.getLogger(__name__)


class SegmentsManagerCacheService:
    """Service for managing Segments Manager data cache."""

    def __init__(self, cache_file: Path):
        """
        Initialize cache service.

        Args:
            cache_file: Path to cache file
        """
        self.cache_file = cache_file
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def save(self, data: Dict) -> bool:
        """
        Save data to local cache file with file locking for multi-replica support.

        Args:
            data: Data to cache

        Returns:
            True if successful, False otherwise
        """
        cache_data = {
            "last_updated": datetime.utcnow().isoformat(),
            "data": data
        }

        success = FileOperations.write_json_with_lock(self.cache_file, cache_data)

        if success:
            logger.info(f"Cache updated successfully at {cache_data['last_updated']}")
        else:
            logger.error("Failed to save cache")

        return success

    def load(self) -> Optional[Dict]:
        """
        Load data from local cache file with file locking for multi-replica support.

        Returns:
            Cached data or None if not available
        """
        cache_data = FileOperations.read_json_with_lock(self.cache_file)

        if cache_data:
            logger.info(f"Loaded cache from {cache_data.get('last_updated', 'unknown time')}")
            return cache_data.get("data")

        return None

    def get_last_updated(self) -> Optional[str]:
        """
        Get last update timestamp from cache.

        Returns:
            ISO format timestamp or None
        """
        cache_data = FileOperations.read_json_with_lock(self.cache_file)
        if cache_data:
            return cache_data.get("last_updated")
        return None
