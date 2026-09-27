"""
Export service for preparing cluster data for export.
Handles data transformation for CSV and Excel exports.
"""
from typing import List, Dict
from src.services.cluster import cluster_service


class ExportService:
    """Service for preparing cluster data for export."""

    @staticmethod
    def prepare_cluster_data() -> List[Dict]:
        """
        Prepare all cluster data for export.
        
        Returns:
            List of dictionaries ready for export (CSV/Excel)
        """
        # Get combined sites data (includes both Segments Manager and manual clusters)
        sites_data = cluster_service.get_combined_sites()
        
        # Flatten sites into a single list of clusters
        all_clusters = []
        for site_response in sites_data:
            for cluster in site_response.clusters:
                # Convert Pydantic model to dict
                cluster_dict = cluster.model_dump()
                all_clusters.append(cluster_dict)
        
        # Flatten cluster data for export
        export_data = []
        for cluster in all_clusters:
            # Handle loadBalancerIP as list or single value
            load_balancer_ip = cluster.get("loadBalancerIP")
            if load_balancer_ip:
                if isinstance(load_balancer_ip, list):
                    load_balancer_ip_str = ", ".join(load_balancer_ip)
                else:
                    load_balancer_ip_str = str(load_balancer_ip)
            else:
                load_balancer_ip_str = ""
            
            export_data.append({
                "Cluster Name": cluster.get("clusterName", ""),
                "Site": cluster.get("site", ""),
                "Domain": cluster.get("domainName", ""),
                "Segments": ", ".join(cluster.get("segments", [])),
                "Segment Count": len(cluster.get("segments", [])),
                "LoadBalancer IP(s)": load_balancer_ip_str,
                "LoadBalancer IP Count": len(load_balancer_ip) if isinstance(load_balancer_ip, list) else (1 if load_balancer_ip else 0),
                "Console URL": cluster.get("consoleUrl", ""),
                "Source": cluster.get("source", "manual"),
                "Created At": cluster.get("createdAt", ""),
                "ID": cluster.get("id", "")
            })
        
        return export_data


# Global service instance
export_service = ExportService()

