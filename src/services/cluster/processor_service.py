"""
Cluster processing and transformation logic.
Handles processing of Segments Manager clusters and manual clusters.
"""
from typing import List, Dict
from datetime import datetime
from src.config import config
from src.utils import ClusterUtils
import logging

logger = logging.getLogger(__name__)


class ClusterProcessorService:
    """Service for processing and transforming cluster data."""

    def process_segments_manager_clusters(self, segments_manager_clusters: List[Dict]) -> List[Dict]:
        """
        Transform Segments Manager clusters to API response format.

        Args:
            segments_manager_clusters: Raw clusters from Segments Manager cache

        Returns:
            List of processed cluster dictionaries
        """
        processed = []

        for cluster in segments_manager_clusters:
            domain_name = cluster.get("domainName", config.default_domain)

            # LoadBalancer IP was already resolved during the periodic sync
            # (src/services/segments_manager/sync_orchestrator.py) and is
            # stored on the cached cluster. Re-resolving it here would mean
            # every request to /api/sites-combined pays a synchronous DNS
            # lookup per cluster, blocking the event loop on every reload.
            load_balancer_ip = cluster.get("loadBalancerIP")

            cluster_entry = {
                "id": f"segments-{cluster['clusterName']}@{cluster['site']}",
                "clusterName": cluster["clusterName"],
                "site": cluster["site"],
                "segments": cluster["segments"],
                "domainName": domain_name,
                "consoleUrl": ClusterUtils.generate_console_url(
                    cluster['clusterName'],
                    domain_name
                ),
                "createdAt": datetime.utcnow().isoformat(),
                "source": "segments-manager",
                "loadBalancerIP": load_balancer_ip,  # Already a list or None
                "metadata": cluster.get("metadata", {})
            }

            processed.append(cluster_entry)

        return processed

    def process_manual_clusters(
        self,
        manual_clusters: List[Dict],
        segments_manager_cluster_keys: set
    ) -> List[Dict]:
        """
        Process manual clusters, filtering out duplicates from Segments Manager.

        Args:
            manual_clusters: Manual clusters from cluster store
            segments_manager_cluster_keys: Set of (clusterName, site) tuples from Segments Manager

        Returns:
            List of manual clusters not in Segments Manager
        """
        processed = []

        for cluster in manual_clusters:
            # Skip if this cluster already exists from Segments Manager
            cluster_key = (cluster["clusterName"], cluster["site"])
            if cluster_key in segments_manager_cluster_keys:
                logger.debug(
                    f"Skipping manual cluster {cluster['clusterName']}@{cluster['site']} "
                    f"(exists in Segments Manager)"
                )
                continue

            # Ensure source field is set
            if "source" not in cluster:
                cluster["source"] = "manual"

            # Normalize LoadBalancer IP to list format (handle backward compatibility)
            if "loadBalancerIP" in cluster and cluster["loadBalancerIP"] is not None:
                # Normalize: convert string to list, keep list as-is
                if isinstance(cluster["loadBalancerIP"], str):
                    cluster["loadBalancerIP"] = [cluster["loadBalancerIP"]]
                elif not isinstance(cluster["loadBalancerIP"], list):
                    # Invalid type, reset to None so it gets resolved
                    cluster["loadBalancerIP"] = None
            else:
                # Resolve LoadBalancer IP if not already present
                cluster["loadBalancerIP"] = ClusterUtils.resolve_loadbalancer_ip(
                    cluster["clusterName"],
                    cluster.get("domainName")
                )

            processed.append(cluster)

        return processed
