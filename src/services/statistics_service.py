"""
Statistics service for calculating cluster and site statistics.
"""
from typing import Dict
from src.services.cluster import cluster_service


class StatisticsService:
    """Service for calculating application statistics."""

    @staticmethod
    def get_statistics() -> Dict:
        """
        Get comprehensive statistics about clusters, sites, and segments.
        
        Returns:
            Dictionary containing various statistics
        """
        # Get combined sites data
        sites_data = cluster_service.get_combined_sites()
        
        # Flatten all clusters
        all_clusters = []
        for site_response in sites_data:
            for cluster in site_response.clusters:
                cluster_dict = cluster.model_dump()
                all_clusters.append(cluster_dict)
        
        # Calculate statistics
        total_clusters = len(all_clusters)
        total_sites = len(sites_data)
        total_segments = sum(len(cluster.get("segments", [])) for cluster in all_clusters)
        
        # Clusters per site
        clusters_per_site = {}
        for cluster in all_clusters:
            site = cluster.get("site", "unknown")
            clusters_per_site[site] = clusters_per_site.get(site, 0) + 1
        
        # Segments per site
        segments_per_site = {}
        for cluster in all_clusters:
            site = cluster.get("site", "unknown")
            segment_count = len(cluster.get("segments", []))
            segments_per_site[site] = segments_per_site.get(site, 0) + segment_count
        
        # Domain distribution
        domain_distribution = {}
        for cluster in all_clusters:
            domain = cluster.get("domainName", "unknown")
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
        
        # Source distribution
        source_distribution = {
            "segments-manager": sum(1 for c in all_clusters if c.get("source") == "segments-manager"),
            "manual": sum(1 for c in all_clusters if c.get("source") == "manual" or "source" not in c)
        }
        
        # Segments distribution (count clusters by number of segments)
        segments_count_distribution = {}
        for cluster in all_clusters:
            seg_count = len(cluster.get("segments", []))
            segments_count_distribution[seg_count] = segments_count_distribution.get(seg_count, 0) + 1
        
        return {
            "overview": {
                "total_clusters": total_clusters,
                "total_sites": total_sites,
                "total_segments": total_segments,
                "average_segments_per_cluster": round(total_segments / total_clusters, 2) if total_clusters > 0 else 0
            },
            "clusters_per_site": clusters_per_site,
            "segments_per_site": segments_per_site,
            "domain_distribution": domain_distribution,
            "source_distribution": source_distribution,
            "segments_count_distribution": segments_count_distribution
        }


# Global service instance
statistics_service = StatisticsService()

