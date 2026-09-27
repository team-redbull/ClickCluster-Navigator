"""
Unit tests for SegmentsManagerDataTransformer.
"""
from src.services.segments_manager.data_transformer import SegmentsManagerDataTransformer


def _segment(**overrides):
    base = {
        "cluster_name": "ocp4-roi",
        "site": "site1",
        "segment": "192.10.10.0/24",
        "type": "HC",
        "status": "Allocated",
        "vlan_id": 1010,
        "epg_name": "EPG_site1_MCE_10",
    }
    base.update(overrides)
    return base


class TestTransformSegmentsToClusters:
    """Tests for SegmentsManagerDataTransformer.transform_segments_to_clusters."""

    def test_keeps_configured_segment_types(self):
        """HC and MCE segments (the default configured types) become a cluster."""
        clusters = SegmentsManagerDataTransformer.transform_segments_to_clusters([_segment()])
        assert len(clusters) == 1
        assert clusters[0]["clusterName"] == "ocp4-roi"
        assert clusters[0]["segments"] == ["192.10.10.0/24"]
        assert clusters[0]["source"] == "segments-manager"

    def test_drops_unconfigured_segment_types(self):
        """Inventory/PXE segment types are not cluster-facing and must be dropped."""
        segments = [
            _segment(type="INVENTORY_REDFISH", segment="192.10.11.0/24"),
            _segment(type="PXE", segment="192.10.12.0/24"),
        ]
        clusters = SegmentsManagerDataTransformer.transform_segments_to_clusters(segments)
        assert clusters == []

    def test_drops_non_allocated_segments_even_with_valid_type(self):
        """Defense in depth: a segment must be Allocated regardless of the server-side filter."""
        segments = [_segment(status="Available")]
        clusters = SegmentsManagerDataTransformer.transform_segments_to_clusters(segments)
        assert clusters == []

    def test_drops_cluster_names_without_ocp4_prefix(self):
        """Only cluster names starting with 'ocp4-' are tracked."""
        segments = [_segment(cluster_name="not-a-cluster")]
        clusters = SegmentsManagerDataTransformer.transform_segments_to_clusters(segments)
        assert clusters == []

    def test_groups_multiple_segments_by_cluster_and_site(self):
        """Multiple segments for the same (cluster_name, site) merge into one cluster."""
        segments = [
            _segment(segment="192.10.10.0/24", type="HC"),
            _segment(segment="192.10.11.0/24", type="MCE", vlan_id=1011, epg_name="EPG_site1_MCE_11"),
        ]
        clusters = SegmentsManagerDataTransformer.transform_segments_to_clusters(segments)
        assert len(clusters) == 1
        assert sorted(clusters[0]["segments"]) == ["192.10.10.0/24", "192.10.11.0/24"]
        assert sorted(clusters[0]["metadata"]["types"]) == ["HC", "MCE"]

    def test_same_cluster_name_different_sites_stay_separate(self):
        """(cluster_name, site) is the composite key, so a name can repeat across sites."""
        segments = [
            _segment(site="site1"),
            _segment(site="site2"),
        ]
        clusters = SegmentsManagerDataTransformer.transform_segments_to_clusters(segments)
        assert len(clusters) == 2
        assert {c["site"] for c in clusters} == {"site1", "site2"}
