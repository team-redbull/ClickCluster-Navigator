"""
Background service to sync data from Segments Manager API.

DEPRECATED: This module is kept for backward compatibility.
Use src.services.segments_manager.sync_orchestrator instead.
"""
from src.services.segments_manager import segments_manager_sync_service

# Re-export for backward compatibility
SegmentsManagerSyncService = type(segments_manager_sync_service)

__all__ = ["segments_manager_sync_service", "SegmentsManagerSyncService"]
