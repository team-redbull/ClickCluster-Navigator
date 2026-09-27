"""
Centralized API routes - all endpoints defined here.
"""
import logging
from typing import List, Dict
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import Response
import pandas as pd
import io
from datetime import datetime

from src.models import ClusterResponse, ClusterCreate, SiteResponse
from src.services.cluster import cluster_service, IPResolverService, availability_service
from src.services.export_service import export_service
from src.services.statistics_service import statistics_service
from src.services import segments_manager_sync_service
from src.services.segments_manager_sync_status_service import segments_manager_sync_status_service
from src.database import cluster_store
from src.utils import SiteUtils
from src.auth import get_current_admin
from src.exceptions import (
    ClusterNotFoundError,
    ClusterAlreadyExistsError,
    SegmentsManagerClusterProtectedError
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["api"])

# ============================================================================
# Cluster Routes
# ============================================================================

@router.get("/clusters", response_model=List[ClusterResponse], summary="Get all clusters")
async def get_all_clusters() -> List[ClusterResponse]:
    """Get all manual clusters. Note: Primary data source is Segments Manager. Use /api/sites-combined for complete data."""
    clusters = cluster_service.get_all_manual_clusters()
    return [ClusterResponse(**cluster) for cluster in clusters]


@router.get("/clusters/availability", summary="Check availability of all clusters")
async def get_clusters_availability() -> Dict:
    """Check each cluster's console URL via HTTP HEAD. Returns {cluster_id: bool}."""
    sites = cluster_service.get_combined_sites()
    clusters = [
        {"id": c.id, "consoleUrl": c.consoleUrl}
        for site in sites
        for c in site.clusters
    ]
    return await availability_service.check_all(clusters)


@router.get("/clusters/{cluster_id}", response_model=ClusterResponse, summary="Get a specific cluster by ID")
async def get_cluster(cluster_id: str) -> ClusterResponse:
    """Get details of a specific cluster by its ID."""
    try:
        cluster = cluster_service.get_cluster_by_id(cluster_id)
        if not cluster:
            raise ClusterNotFoundError(cluster_id)
        return ClusterResponse(**cluster)
    except ClusterNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/clusters", response_model=ClusterResponse, status_code=status.HTTP_201_CREATED, summary="Create a new cluster (Admin only)", dependencies=[Depends(get_current_admin)])
async def create_cluster(cluster_data: ClusterCreate) -> ClusterResponse:
    """Create a new manual cluster entry. Requires admin authentication."""
    logger.info(f"Creating cluster: {cluster_data.clusterName} at site: {cluster_data.site}")
    logger.debug(f"Cluster data: {cluster_data.dict()}")

    try:
        if cluster_service.cluster_exists(cluster_data.clusterName, cluster_data.site):
            logger.warning(f"Cluster already exists: {cluster_data.clusterName} at {cluster_data.site}")
            raise ClusterAlreadyExistsError(cluster_data.clusterName, cluster_data.site)

        cluster_dict = {
            "clusterName": cluster_data.clusterName,
            "site": cluster_data.site,
            "segments": cluster_data.segments,
            "domainName": cluster_data.domainName or "example.com",
            "loadBalancerIP": cluster_data.loadBalancerIP
        }

        cluster = cluster_service.create_manual_cluster(cluster_dict)
        logger.info(f"Successfully created cluster: {cluster_data.clusterName} with ID: {cluster['id']}")
        return ClusterResponse(**cluster)

    except ClusterAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.post("/clusters/bulk", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Create multiple clusters (Admin only)", dependencies=[Depends(get_current_admin)])
async def create_clusters_bulk(clusters_data: List[ClusterCreate]):
    """Create multiple clusters in a single request (bulk operation). Requires admin authentication."""
    logger.info(f"Bulk creating {len(clusters_data)} clusters")

    results = {
        "success": [],
        "failed": [],
        "total": len(clusters_data),
        "created_count": 0,
        "failed_count": 0
    }

    for cluster_data in clusters_data:
        logger.debug(f"Processing cluster: {cluster_data.clusterName} at {cluster_data.site}")
        try:
            if cluster_service.cluster_exists(cluster_data.clusterName, cluster_data.site):
                results["failed"].append({
                    "clusterName": cluster_data.clusterName,
                    "site": cluster_data.site,
                    "error": "Cluster already exists"
                })
                results["failed_count"] += 1
                continue

            cluster_dict = {
                "clusterName": cluster_data.clusterName,
                "site": cluster_data.site,
                "segments": cluster_data.segments,
                "domainName": cluster_data.domainName or "example.com",
                "loadBalancerIP": cluster_data.loadBalancerIP
            }

            cluster = cluster_service.create_manual_cluster(cluster_dict)
            results["success"].append({
                "id": cluster["id"],
                "clusterName": cluster["clusterName"],
                "site": cluster["site"],
                "loadBalancerIP": cluster.get("loadBalancerIP")
            })
            results["created_count"] += 1

        except Exception as e:
            results["failed"].append({
                "clusterName": cluster_data.clusterName,
                "site": cluster_data.site,
                "error": str(e)
            })
            results["failed_count"] += 1

    return results


@router.delete("/clusters/{cluster_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a cluster (Admin only)", dependencies=[Depends(get_current_admin)])
async def delete_cluster(cluster_id: str):
    """Delete a manual cluster entry. Requires admin authentication. Only manual clusters can be deleted."""
    try:
        cluster = cluster_service.get_cluster_by_id(cluster_id)
        if not cluster:
            raise ClusterNotFoundError(cluster_id)

        if cluster.get("source") == "segments-manager":
            raise SegmentsManagerClusterProtectedError(cluster_id)

        success = cluster_service.delete_manual_cluster(cluster_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete cluster")

        return None

    except ClusterNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SegmentsManagerClusterProtectedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)

# ============================================================================
# Site Routes
# ============================================================================

@router.get("/sites", response_model=List[SiteResponse], summary="Get all sites with clusters")
async def get_all_sites() -> List[SiteResponse]:
    """Retrieve all sites organized with their clusters."""
    sites_data = cluster_store.get_all_sites()
    return SiteUtils.create_sites_response_list(sites_data)


@router.get("/sites/{site_name}", response_model=SiteResponse, summary="Get specific site with clusters")
async def get_site(site_name: str) -> SiteResponse:
    """Retrieve a specific site with all its clusters."""
    clusters = cluster_store.get_clusters_by_site(site_name)
    return SiteUtils.create_site_response(site_name, clusters)

# ============================================================================
# Combined Routes
# ============================================================================

@router.get("/sites-combined", response_model=List[SiteResponse], summary="Get all sites with combined data from Segments Manager and manual entries")
async def get_combined_sites() -> List[SiteResponse]:
    """Get sites with clusters from both Segments Manager (synced) and manual entries. Segments Manager data takes precedence."""
    return cluster_service.get_combined_sites()

# ============================================================================
# Segments Manager Sync Routes
# ============================================================================

@router.get("/segments-sync/data", summary="Get synced Segments Manager data")
async def get_synced_data() -> Dict:
    """Get the latest synced data from Segments Manager. Returns clusters, sites, and statistics. Falls back to cached data if API is unavailable."""
    cached_data = segments_manager_sync_service.load_from_cache()
    if cached_data:
        return cached_data
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Segments Manager data not available and no cache exists"
        )


@router.post("/segments-sync/sync", summary="Trigger manual sync")
async def trigger_sync() -> Dict:
    """Manually trigger a sync with Segments Manager API. Useful for immediate updates without waiting for the scheduled sync."""
    try:
        data = await segments_manager_sync_service.sync_data()
        return {
            "status": "success",
            "message": "Sync completed successfully",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Sync failed: {str(e)}")


@router.get("/auth/verify", summary="Verify admin credentials")
async def verify_auth(admin: str = Depends(get_current_admin)) -> Dict:
    return {"authenticated": True, "username": admin}


@router.get("/segments-sync/status", summary="Get sync service status")
async def get_sync_status() -> Dict:
    """Get the current status of the Segments Manager sync service."""
    return segments_manager_sync_status_service.get_sync_status()


@router.get("/segments-sync/sites", summary="Get available sites from Segments Manager")
async def get_segments_sync_sites() -> Dict:
    """Get the list of available sites from Segments Manager. Returns a list of unique site names."""
    return segments_manager_sync_status_service.get_sites()

# ============================================================================
# Statistics Routes
# ============================================================================

@router.get("/statistics", summary="Get cluster statistics")
async def get_statistics() -> Dict:
    """Get comprehensive statistics about clusters, sites, and segments."""
    return statistics_service.get_statistics()

# ============================================================================
# Export Routes
# ============================================================================

@router.get("/export/csv", summary="Export clusters as CSV")
async def export_csv():
    """Export all clusters as CSV file."""
    try:
        data = export_service.prepare_cluster_data()
        df = pd.DataFrame(data)
        
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        filename = f"clusters-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Export failed: {str(e)}")


@router.get("/export/excel", summary="Export clusters as Excel")
async def export_excel():
    """Export all clusters as Excel file (.xlsx)."""
    try:
        data = export_service.prepare_cluster_data()
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Clusters')
            
            worksheet = writer.sheets['Clusters']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col))
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        output.seek(0)
        filename = f"clusters-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}.xlsx"
        
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Export failed: {str(e)}")

# ============================================================================
# DNS Routes
# ============================================================================

@router.get("/dns/stats", summary="Get DNS resolution statistics")
async def get_dns_stats():
    """Get DNS resolution statistics. Returns statistics about DNS resolution requests including total request count, success/failure counts, and total/average resolution time."""
    return IPResolverService.get_dns_stats()


@router.post("/dns/stats/reset", summary="Reset DNS resolution statistics")
async def reset_dns_stats():
    """Reset DNS resolution statistics."""
    IPResolverService.reset_dns_stats()
    return {"status": "success", "message": "DNS statistics reset"}
