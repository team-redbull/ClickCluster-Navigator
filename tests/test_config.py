"""
Unit tests for environment-variable overrides in src.config.Config.
"""
from src.config import config


class TestSegmentsManagerConfig:
    """Tests for Segments Manager related config properties."""

    def test_segments_manager_url_env_override(self, monkeypatch):
        """SEGMENTS_MANAGER_URL must override config.json's value."""
        monkeypatch.setenv("SEGMENTS_MANAGER_URL", "http://override-host:8000")
        assert config.segments_manager_url == "http://override-host:8000"

    def test_segments_manager_url_falls_back_to_config_json(self, monkeypatch):
        """With no env var set, the config.json value is used."""
        monkeypatch.delenv("SEGMENTS_MANAGER_URL", raising=False)
        assert config.segments_manager_url == config._config["segments_manager"]["url"]

    def test_segment_types_default(self, monkeypatch):
        """Default segment types are HC and MCE."""
        monkeypatch.delenv("SEGMENT_TYPES", raising=False)
        assert config.segment_types == ["HC", "MCE"]

    def test_segment_types_env_override(self, monkeypatch):
        """SEGMENT_TYPES is a comma-separated override."""
        monkeypatch.setenv("SEGMENT_TYPES", "HC,MCE,PXE")
        assert config.segment_types == ["HC", "MCE", "PXE"]

    def test_segment_types_env_override_strips_whitespace(self, monkeypatch):
        """Whitespace around comma-separated entries is stripped."""
        monkeypatch.setenv("SEGMENT_TYPES", " HC , MCE ")
        assert config.segment_types == ["HC", "MCE"]
