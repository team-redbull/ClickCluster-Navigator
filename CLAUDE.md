# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Local development (creates venv, installs deps, runs on :8000)
./run.sh

# Build only (no run)
./run.sh build

# Container (podman)
./run.sh podman          # build + run
./run.sh podman-build    # build only

# Tests
pytest tests/

# API docs (when running)
# Swagger: http://localhost:8000/api/docs
# Health:  http://localhost:8000/health
```

## Architecture

FastAPI app that synchronizes OpenShift cluster data from Segments Manager (read-only) and manages manual cluster entries. No SQL database — uses file-based storage with in-memory caching.

**Layers (top → bottom):**
1. **API** (`src/api/routes.py`) — all endpoints, no business logic
2. **Services** (`src/services/`) — business logic, orchestration
3. **Data** (`src/database/store.py`) — file + in-memory storage with file locking
4. **Models** (`src/models/cluster.py`) — Pydantic validation
5. **Utils** (`src/utils/`) — validators, file I/O, logging; no upstream deps

**Key service areas:**
- `src/services/cluster/` — CRUD, DNS resolution, URL generation, merging, availability checks (concurrent HTTP HEAD probes against console URLs, backing `GET /api/clusters/availability`)
- `src/services/segments_manager/` — Segments Manager API client, sync orchestrator, cache, transformer
- `src/services/export_service.py` — CSV/Excel export (pandas + openpyxl)
- `src/services/statistics_service.py` — analytics for dashboard

## Data Flow

```
Segments Manager API → SegmentsManagerApiClient → SegmentsManagerDataTransformer → SegmentsManagerCacheService → segments_manager_cache.json
                                                                                                                    ↓
Manual clusters ─────────────────────────────────────────────────────────────────────────────────────────  manual_clusters.json
                                                                                                                    ↓
                                                                                            ClusterService.get_combined_sites()
                                                                                            (Segments Manager takes precedence; manual
                                                                                            fills gaps and merges its segments into a
                                                                                            matching cluster when name+site match)
```

Segments Manager only exposes segments carrying a `type` when `status: Allocated` (`MCE | INVENTORY_REDFISH | INVENTORY_IPMI | HC | PXE`). `SegmentsManagerDataTransformer` filters to `config.segment_types` (default `["HC", "MCE"]`) — inventory/PXE networks are not cluster-facing and are dropped.

Segments Manager sync runs as a background task every 300s (configurable) via the FastAPI lifespan context manager in `src/main.py`.

## Configuration

Priority (highest to lowest): env vars → `config.json` → code defaults.

Key env vars: `LOG_LEVEL`, `SEGMENTS_MANAGER_URL`, `SEGMENT_TYPES` (comma-separated, e.g. `HC,MCE`), `DNS_SERVER`, `DNS_TIMEOUT`, `DNS_RESOLUTION_PATH`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `APP_TITLE`, `DEFAULT_DOMAIN`.

`segments_manager_insecure_tls_verify` is config.json-only — no env var override.

Config is loaded once as a singleton in `src/config.py`.

## Key Patterns

**Source tagging** — every cluster has `"source": "segments-manager"` or `"source": "manual"`. Only manual clusters can be deleted via API.

**Singleton instances** — `Config`, `ClusterStore`, and `SegmentsManagerSyncOrchestrator` are module-level singletons imported across the app.

**Thread-safe file I/O** — `src/utils/file_operations.py` uses `fcntl` locks + atomic temp-file rename; supports multi-replica pods sharing a PVC.

**Backward-compat wrappers** — `src/services/cluster_service.py`, `src/services/segments_manager_sync.py`, and `src/utils/cluster_utils.py` re-export from refactored modules. Prefer the canonical submodule paths for new code.

**Lazy imports** — some utils use deferred `from src.services...` imports inside functions to break circular dependencies.

**Route ordering** — static routes under `/clusters/*` (e.g. `/clusters/availability`) must be declared in `src/api/routes.py` *before* `/clusters/{cluster_id}`, or FastAPI matches the static segment as a `cluster_id`. Keep new static routes above the dynamic one.

**DNS resolution** — hostname template from config (default `ingress.{cluster_name}.{domain_name}`) is resolved via dnspython; supports multiple A records for round-robin.

## Authentication

HTTP Basic Auth on admin endpoints (`POST /api/clusters`, `DELETE /api/clusters/{id}`, `POST /api/segments-sync/sync`). Credentials from env vars or `config.json`. See `src/auth.py`.

`GET /api/auth/verify` validates credentials without side effects — used by the frontend's admin-login form.

## Storage Files

- `data/manual_clusters.json` — user-created clusters
- `data/segments_manager_cache.json` — Segments Manager sync cache
- `logs/app.log` — rotating log (10 MB × 5)

## Frontend

Vanilla JS + Jinja2 template (`src/templates/index.html`). Chart.js is vendored locally under `src/static/js/vendor/` for offline/air-gapped use.
