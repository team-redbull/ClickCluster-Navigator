"""
Segments Manager integration services.

This package provides services for integrating with Segments Manager API.
"""
from pathlib import Path
from src.services.segments_manager.sync_orchestrator import SegmentsManagerSyncOrchestrator

CACHE_FILE = Path(__file__).parent.parent.parent.parent / "data" / "segments_manager_cache.json"

segments_manager_sync_service = SegmentsManagerSyncOrchestrator(CACHE_FILE)

__all__ = [
    "segments_manager_sync_service",
    "SegmentsManagerSyncOrchestrator",
]
