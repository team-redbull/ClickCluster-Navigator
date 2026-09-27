"""
Cluster-related services.
"""
from src.services.cluster.ip_resolver_service import IPResolverService
from src.services.cluster.url_generator_service import URLGeneratorService
from src.services.cluster.crud_service import ClusterCRUDService
from src.services.cluster.merge_service import ClusterMergeService
from src.services.cluster.processor_service import ClusterProcessorService
from src.services.cluster.availability_service import availability_service


class ClusterService:
    """
    Unified service layer for cluster business logic.
    Combines CRUD operations, data merging, and cluster processing.
    """

    def __init__(self):
        self.crud = ClusterCRUDService()
        self.merge = ClusterMergeService()
        self.processor = ClusterProcessorService()

    # CRUD operations - delegate to CRUD service
    def get_all_manual_clusters(self):
        """Get all manual clusters."""
        return self.crud.get_all_manual_clusters()

    def get_cluster_by_id(self, cluster_id: str):
        """Get a specific cluster by ID."""
        return self.crud.get_cluster_by_id(cluster_id)

    def create_manual_cluster(self, cluster_data: dict):
        """Create a new manual cluster."""
        return self.crud.create_manual_cluster(cluster_data)

    def delete_manual_cluster(self, cluster_id: str) -> bool:
        """Delete a manual cluster."""
        return self.crud.delete_manual_cluster(cluster_id)

    def cluster_exists(self, cluster_name: str, site: str) -> bool:
        """Check if a cluster exists."""
        return self.crud.cluster_exists(cluster_name, site)

    # Merging operations - delegate to merge service
    def get_combined_sites(self):
        """Get all sites with clusters from both Segments Manager and manual entries."""
        return self.merge.get_combined_sites()


# Global service instance
cluster_service = ClusterService()

__all__ = [
    "IPResolverService",
    "URLGeneratorService",
    "ClusterCRUDService",
    "ClusterMergeService",
    "ClusterProcessorService",
    "ClusterService",
    "cluster_service",
    "availability_service",
]
