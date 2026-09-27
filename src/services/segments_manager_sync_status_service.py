"""
Segments Manager sync status service for formatting sync status information.
"""
import os
from datetime import datetime
from typing import Dict
from src.services import segments_manager_sync_service
from src.config import config


class SegmentsManagerSyncStatusService:
    """Service for Segments Manager sync status information."""

    @staticmethod
    def get_sync_status() -> Dict:
        """
        Get the current status of the Segments Manager sync service.

        Returns:
            Dictionary with sync status information
        """
        cache_exists = segments_manager_sync_service.cache_file.exists()
        cache_age = None
        last_updated = None

        if cache_exists:
            cache_mtime = os.path.getmtime(segments_manager_sync_service.cache_file)
            cache_age = (datetime.now().timestamp() - cache_mtime) / 60  # in minutes
            last_updated = datetime.fromtimestamp(cache_mtime).isoformat()

        return {
            "service_running": segments_manager_sync_service.is_running,
            "sync_interval_seconds": config.sync_interval,
            "cache_exists": cache_exists,
            "cache_age_minutes": round(cache_age, 2) if cache_age else None,
            "last_updated": last_updated,
            "segments_manager_url": config.segments_manager_url
        }

    @staticmethod
    def get_sites() -> Dict:
        """
        Get the list of available sites from Segments Manager.

        Returns:
            Dictionary with sites list and count
        """
        cached_data = segments_manager_sync_service.load_from_cache()

        if cached_data:
            # Extract unique site names from the sites list
            sites = cached_data.get("sites", [])
            site_names = sorted(list(set(sites)))
            return {
                "sites": site_names,
                "count": len(site_names)
            }
        else:
            return {
                "sites": [],
                "count": 0
            }


# Global service instance
segments_manager_sync_status_service = SegmentsManagerSyncStatusService()
