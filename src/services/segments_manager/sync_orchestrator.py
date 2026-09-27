"""
Segments Manager sync orchestrator service.
Orchestrates the synchronization process between Segments Manager API and local cache.
"""
import asyncio
from typing import Dict
import logging
from pathlib import Path
from src.config import config
from src.services.segments_manager.api_client import SegmentsManagerApiClient
from src.services.segments_manager.data_transformer import SegmentsManagerDataTransformer
from src.services.segments_manager.cache_service import SegmentsManagerCacheService

logger = logging.getLogger(__name__)


class SegmentsManagerSyncOrchestrator:
    """
    Orchestrates Segments Manager synchronization.

    Coordinates API client, data transformer, and cache service
    to sync Segments Manager data with local storage.
    """

    def __init__(self, cache_file: Path):
        """
        Initialize sync orchestrator.

        Args:
            cache_file: Path to cache file
        """
        self.cache_file = cache_file
        self.api_client = SegmentsManagerApiClient()
        self.transformer = SegmentsManagerDataTransformer()
        self.cache_service = SegmentsManagerCacheService(cache_file)
        self.is_running = False

    async def sync_data(self) -> Dict:
        """
        Sync data from Segments Manager API.

        Returns:
            Structured data with clusters and sites
        """
        logger.info("Starting Segments Manager data sync...")

        # Fetch data from API
        segments = await self.api_client.fetch_allocated_segments()
        sites = await self.api_client.fetch_sites()

        # Fall back to cache if API fails
        if not segments:
            logger.warning("No segments fetched, attempting to load from cache...")
            cached_data = self.cache_service.load()
            if cached_data:
                logger.info("Using cached data")
                return cached_data
            else:
                logger.error("No cached data available")
                return {"clusters": [], "sites": []}

        # Transform segments to clusters
        clusters = self.transformer.transform_segments_to_clusters(segments)

        # Lazy import to avoid circular dependency
        from src.services.cluster.ip_resolver_service import IPResolverService
        from src.utils import ClusterUtils

        # Reset DNS stats before resolving IPs
        IPResolverService.reset_dns_stats()
        logger.info("Starting DNS resolution for clusters...")

        # Resolve LoadBalancer IPs for all clusters
        for cluster in clusters:
            domain_name = cluster.get("domainName", config.default_domain)
            cluster["loadBalancerIP"] = ClusterUtils.resolve_loadbalancer_ip(
                cluster["clusterName"],
                domain_name
            )

        # Log DNS resolution statistics at INFO level
        dns_stats = IPResolverService.get_dns_stats()
        avg_time_msg = f", average time: {dns_stats['average_time_seconds']}s per request" if dns_stats['request_count'] > 0 else ""
        logger.info(
            f"DNS resolution completed - {dns_stats['request_count']} DNS requests, "
            f"{dns_stats['success_count']} successful, {dns_stats['failure_count']} failed, "
            f"total time: {dns_stats['total_time_seconds']}s{avg_time_msg}"
        )

        # Calculate statistics
        stats = self.transformer.calculate_stats(clusters, sites)

        # Prepare data structure
        data = {
            "clusters": clusters,
            "sites": sites,
            "stats": stats
        }

        # Save to cache
        self.cache_service.save(data)

        logger.info(f"Sync complete: {stats['total_clusters']} clusters, "
                   f"{stats['total_sites']} sites, "
                   f"{stats['total_segments']} segments")

        return data

    async def sync_loop(self):
        """Continuous sync loop that runs every configured interval."""
        self.is_running = True
        sync_interval = config.sync_interval
        logger.info(f"Segments Manager sync service started (interval: {sync_interval}s, "
                   f"URL: {config.segments_manager_url})")

        while self.is_running:
            try:
                await self.sync_data()
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")

            # Wait for next sync
            await asyncio.sleep(sync_interval)

    async def start(self):
        """Start the background sync service."""
        if not self.is_running:
            asyncio.create_task(self.sync_loop())

    def stop(self):
        """Stop the background sync service."""
        self.is_running = False
        logger.info("Segments Manager sync service stopped")

    def load_from_cache(self) -> Dict:
        """
        Load data from cache.

        Returns:
            Cached data or empty structure
        """
        data = self.cache_service.load()
        return data if data else {"clusters": [], "sites": []}
