"""
Data merging logic for combining Segments Manager and manual clusters.
Handles merging clusters from different sources with precedence rules.
"""
from typing import List, Dict
from src.services import segments_manager_sync_service
from src.services.cluster.processor_service import ClusterProcessorService
from src.services.cluster.ip_resolver_service import IPResolverService
from src.utils import SiteUtils
import logging

logger = logging.getLogger(__name__)


class ClusterMergeService:
    """Service for merging cluster data from multiple sources."""

    def __init__(self):
        self.segments_manager_service = segments_manager_sync_service
        self.processor = ClusterProcessorService()

    def get_combined_sites(self):
        """
        Get all sites with clusters from both Segments Manager and manual entries.

        Business logic:
        - Segments Manager data takes precedence for duplicate clusters
        - Manual clusters are added only if they don't exist in Segments Manager
        - Clusters are grouped by site

        Returns:
            List of SiteResponse objects with clusters
        """
        # Reset DNS stats at the start of processing
        IPResolverService.reset_dns_stats()
        logger.info("Starting cluster processing and DNS resolution...")

        # Get Segments Manager synced data
        segments_manager_data = self.segments_manager_service.load_from_cache()
        logger.debug(f"Loaded Segments Manager data: {len(segments_manager_data.get('clusters', [])) if segments_manager_data else 0} clusters")

        # Get manual clusters from in-memory store
        from src.database import cluster_store
        manual_clusters = cluster_store.get_all_clusters()
        logger.debug(f"Loaded manual clusters: {len(manual_clusters)} clusters")

        # Prepare combined data structure
        sites_dict = {}

        # Add Segments Manager clusters first (they take precedence)
        if segments_manager_data:
            segments_manager_clusters = self.processor.process_segments_manager_clusters(segments_manager_data.get("clusters", []))
            logger.debug(f"Processed {len(segments_manager_clusters)} Segments Manager clusters")
            for cluster in segments_manager_clusters:
                site_name = cluster["site"]

                if site_name not in sites_dict:
                    sites_dict[site_name] = {
                        "site": site_name,
                        "clusters": [],
                        "clusterCount": 0
                    }
                    logger.debug(f"Created new site entry: {site_name}")

                sites_dict[site_name]["clusters"].append(cluster)
                sites_dict[site_name]["clusterCount"] += 1
                logger.debug(f"Added Segments Manager cluster '{cluster['clusterName']}' to site '{site_name}'")

        # Build a lookup map of processed Segments Manager clusters so supplements can mutate their segments
        segments_manager_cluster_map = {}
        for site_data in sites_dict.values():
            for cluster in site_data["clusters"]:
                key = (cluster["clusterName"], cluster["site"])
                segments_manager_cluster_map[key] = cluster

        segments_manager_cluster_keys = self._get_segments_manager_cluster_keys(segments_manager_data)
        logger.debug(f"Segments Manager cluster keys for deduplication: {segments_manager_cluster_keys}")

        # Separate manual clusters: those that supplement a Segments Manager cluster vs standalone
        supplement_manuals = []
        standalone_manuals = []
        for mc in manual_clusters:
            key = (mc["clusterName"], mc["site"])
            if key in segments_manager_cluster_keys:
                supplement_manuals.append(mc)
            else:
                standalone_manuals.append(mc)

        # Merge segments from supplement entries into their matching Segments Manager cluster
        for mc in supplement_manuals:
            key = (mc["clusterName"], mc["site"])
            target = segments_manager_cluster_map.get(key)
            if target and mc.get("segments"):
                existing = set(target["segments"])
                new_segs = [s for s in mc["segments"] if s not in existing]
                if new_segs:
                    target["segments"] = target["segments"] + new_segs
                    logger.debug(
                        f"Supplemented Segments Manager cluster {key} with segments: {new_segs}"
                    )

        manual_clusters_processed = self.processor.process_manual_clusters(
            standalone_manuals,
            segments_manager_cluster_keys
        )
        logger.debug(f"Processed {len(manual_clusters_processed)} manual clusters (after deduplication)")

        for cluster in manual_clusters_processed:
            site_name = cluster["site"]

            if site_name not in sites_dict:
                sites_dict[site_name] = {
                    "site": site_name,
                    "clusters": [],
                    "clusterCount": 0
                }
                logger.debug(f"Created new site entry for manual cluster: {site_name}")

            sites_dict[site_name]["clusters"].append(cluster)
            sites_dict[site_name]["clusterCount"] += 1
            logger.debug(f"Added manual cluster '{cluster['clusterName']}' to site '{site_name}'")

        # Log DNS resolution statistics at INFO level after all processing
        dns_stats = IPResolverService.get_dns_stats()
        avg_time_msg = f", average time: {dns_stats['average_time_seconds']}s per request" if dns_stats['request_count'] > 0 else ""
        logger.info(
            f"Cluster processing completed - DNS resolution stats: "
            f"{dns_stats['request_count']} DNS requests, "
            f"{dns_stats['success_count']} successful, {dns_stats['failure_count']} failed, "
            f"total time: {dns_stats['total_time_seconds']}s{avg_time_msg}"
        )

        # Convert to SiteResponse objects
        sites_response = [
            SiteUtils.create_site_response(site_data["site"], site_data["clusters"])
            for site_data in sites_dict.values()
        ]
        sites_response.sort(key=lambda x: x.site)

        return sites_response

    def _get_segments_manager_cluster_keys(self, segments_manager_data: Dict) -> set:
        """
        Extract unique cluster keys from Segments Manager data.

        Args:
            segments_manager_data: Segments Manager cache data

        Returns:
            Set of (clusterName, site) tuples
        """
        if not segments_manager_data:
            return set()

        clusters = segments_manager_data.get("clusters", [])
        return {(c["clusterName"], c["site"]) for c in clusters}
