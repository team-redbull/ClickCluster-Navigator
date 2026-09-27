# OpenShift Cluster Navigator

A modern web application for managing and navigating OpenShift clusters with Segments Manager integration, automatic DNS resolution, and comprehensive cluster management features.

## 🎯 Key Features

- **Segments Manager Integration**: Automatic synchronization with Segments Manager API (HC/MCE segment types)
- **DNS Resolution API**: Query and validate DNS records for clusters
- **Manual Cluster Management**: Add, edit, and delete clusters manually
- **LoadBalancer IP Resolution**: Automatic DNS-based IP resolution with configurable path
- **Statistics Dashboard**: Visual analytics with charts and metrics
- **Export Capabilities**: Export to CSV and Excel formats
- **Comprehensive Logging**: Structured logging with environment-based log levels
- **Performance Optimized**: Minimal overhead, efficient data processing
- **Site Organization**: Clusters organized by deployment site
- **Network Segments**: Track and copy network segments (CIDR)
- **Quick Navigation**: One-click access to OpenShift console
- **Dark Mode**: Built-in dark mode support
- **Multi-Replica Safe**: File locking for concurrent deployments

## 🚀 Quick Start

### Local Development
```bash
./run.sh
```

Access the application at: http://localhost:8000

### Container Deployment
```bash
podman build -t openshift-cluster-navigator:v2.0.0 .
podman run -d --name cluster-navigator -p 8000:8000 \
  -v $(pwd)/data:/app/data:Z \
  openshift-cluster-navigator:v2.0.0
```

### Kubernetes/OpenShift Deployment
```bash
cd helm/
helm install cluster-navigator ./openshift-cluster-navigator -f values-production.yaml
```

## 📋 Requirements

- Python 3.11+
- Podman or Docker (for containerized deployment)
- DNS server for LoadBalancer IP resolution

## 🔧 Configuration

### Config File (`config.json`)
```json
{
  "segments_manager": {
    "url": "http://segments-manager:8000",
    "sync_interval_seconds": 300,
    "insecure_tls_verify": false,
    "segment_types": ["HC", "MCE"]
  },
  "application": {
    "host": "0.0.0.0",
    "port": 8000,
    "default_domain": "example.com"
  },
  "dns": {
    "server": "8.8.8.8",
    "timeout_seconds": 3,
    "resolution_path": "ingress.{cluster_name}.{domain_name}"
  },
  "auth": {
    "admin_username": "admin",
    "admin_password": "Password1"
  }
}
```

### Environment Variables

- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR) - default: INFO
- `SEGMENTS_MANAGER_URL` - Segments Manager API URL
- `SEGMENT_TYPES` - Comma-separated segment types to sync (default: HC,MCE)
- `DEFAULT_DOMAIN` - Default domain for clusters
- `DNS_SERVER` - DNS server for IP resolution
- `DNS_TIMEOUT` - DNS query timeout in seconds
- `DNS_RESOLUTION_PATH` - DNS resolution path template
- `ADMIN_USERNAME` - Admin username
- `ADMIN_PASSWORD` - Admin password
- `APP_TITLE` - Application title

**Example:**

```bash
export LOG_LEVEL=DEBUG
export SEGMENTS_MANAGER_URL=http://segments-manager:8000
export DNS_SERVER=8.8.8.8
```

## 📖 API Documentation

### Main Endpoints

#### Combined Data
- `GET /api/sites-combined` - Get all sites with clusters from Segments Manager + manual

#### Cluster Management
- `POST /api/clusters` - Create a manual cluster (Admin)
- `POST /api/clusters/bulk` - Create multiple clusters (Admin)
- `GET /api/clusters` - Get all manual clusters
- `GET /api/clusters/{id}` - Get cluster by ID
- `DELETE /api/clusters/{id}` - Delete manual cluster (Admin)

#### Statistics & Export
- `GET /api/statistics` - Get cluster statistics
- `GET /api/export/csv` - Export clusters as CSV
- `GET /api/export/excel` - Export clusters as Excel

#### Segments Manager Sync

- `GET /api/segments-sync/status` - Get sync status
- `POST /api/segments-sync/sync` - Trigger manual sync (Admin)

#### DNS Resolution

- `POST /api/dns/resolve` - Resolve cluster LoadBalancer IP via DNS
- `POST /api/dns/resolve/batch` - Batch resolve multiple clusters

### Interactive API Docs
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 🎨 Features

### Segments Manager Integration
- Automatic synchronization every 5 minutes
- Read-only access (GET requests only)
- Only syncs configured segment types (default: HC, MCE)
- Caches data locally for offline access
- Manual sync trigger available

### LoadBalancer IP Resolution
- Configurable DNS server
- Configurable resolution path template
- Automatic resolution for all clusters
- Manual IP entry supported

### Statistics Dashboard
- Total clusters, sites, segments
- Clusters per site (bar chart)
- Source distribution (doughnut chart)
- Domain distribution (pie chart)
- Segments per site (bar chart)

### Export Features
- CSV export with all cluster data
- Excel export with formatting
- Timestamped file names
- Complete field coverage

### UI Features
- Responsive grid/list view toggle
- Dark mode support
- Click-to-copy for names, IPs, segments
- Quick filter by site
- Real-time search
- Console URL quick access
- Last sync time display

## 🏗️ Architecture

The application follows **SOLID principles** with clean layered architecture:

```
API Layer (FastAPI)
    ↓
Service Layer (Business Logic)
    ↓
Data Layer (Storage)
    ↓
Utils Layer (Reusable Utilities)
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

### File Structure
```
src/
├── api/              # API endpoints (HTTP layer)
├── services/         # Business logic layer
├── database/         # Data persistence layer
├── models/           # Pydantic models & validation
├── utils/            # Reusable utilities
├── static/           # Frontend assets (CSS, JS)
├── templates/        # HTML templates
├── config.py         # Configuration management
├── auth.py           # Authentication
├── exceptions.py     # Custom exceptions
└── main.py           # Application entry point
```

## 🔐 Security

- HTTP Basic Authentication for admin endpoints
- Input validation using Pydantic
- CIDR and IPv4 validation
- Cluster name pattern validation (`ocp4-*`)
- Segments Manager clusters protected from deletion
- Non-root user in container
- Read-only Segments Manager access

## 📚 Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture and SOLID principles
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md) - Configuration guide
- [docs/CODE_REVIEW.md](docs/CODE_REVIEW.md) - Code structure and improvements
- [docs/TROUBLESHOOTING_GUIDE.md](docs/TROUBLESHOOTING_GUIDE.md) - Common issues and solutions
- [helm/DEPLOYMENT_GUIDE.md](helm/DEPLOYMENT_GUIDE.md) - Kubernetes deployment guide

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Check health
curl http://localhost:8000/health
```

## 🐳 Docker Image

Available on Docker Hub:
```bash
podman pull docker.io/roi12345/openshift-cluster-navigator:v2
```

## 📝 Data Model

### Cluster
```json
{
  "clusterName": "ocp4-roi",
  "site": "site1",
  "segments": ["192.178.1.0/24", "192.178.2.0/24"],
  "domainName": "example.com",
  "loadBalancerIP": "192.168.100.10",
  "source": "manual"
}
```

**Validation Rules:**
- `clusterName`: Must start with `ocp4-`, lowercase alphanumeric with hyphens
- `site`: Required, 1-50 characters
- `segments`: Array of valid CIDR notation
- `domainName`: Optional, defaults to configured domain
- `loadBalancerIP`: Optional IPv4 address (auto-resolved if not provided)

## 🚢 Deployment

### Production Deployment with Helm
```bash
cd helm/
helm install cluster-navigator ./openshift-cluster-navigator \
  -f values-production.yaml \
  --set app.segmentsManagerUrl=http://your-segments-manager:8000 \
  --set config.dns.server=your-dns-server
```

### Environment-Specific Configuration
```bash
# Development
export DEFAULT_DOMAIN="dev.example.com"

# Production
export DEFAULT_DOMAIN="prod.example.com"
export DNS_SERVER="10.0.0.1"
export DNS_RESOLUTION_PATH="api.{cluster_name}.{domain_name}"
```

## 🔄 Version History

### v2.1.0 (Latest)

- ✅ Comprehensive logging system with environment-based log levels
- ✅ Performance optimizations (removed excessive console logging, improved data cloning)
- ✅ Frontend structured logger with color-coded output
- ✅ HTTP request/response logging middleware
- ✅ DNS resolution API endpoints
- ✅ Enhanced debug logging throughout backend
- ✅ Log rotation and file management
- ✅ Chart.js bundled for air-gapped environments

### v2.0.0

- ✅ Added configurable DNS resolution path
- ✅ LoadBalancer IP badge color matching
- ✅ Bulk cluster creation endpoint
- ✅ Improved list view organization

### v1.0.0

- ✅ VLAN Manager integration
- ✅ Manual cluster management
- ✅ Statistics dashboard
- ✅ CSV/Excel export
- ✅ Dark mode support
- ✅ Multi-replica safety

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows SOLID principles
- Pydantic models include validation
- API endpoints have proper error handling
- Frontend is responsive and accessible
- Tests are included for new features

## 📄 License

MIT License

## 🙏 Acknowledgments

Built with:
- FastAPI - Modern web framework
- Pydantic - Data validation
- Chart.js - Data visualization
- dnspython - DNS resolution
- pandas - Data export

---

## Credits

![Credits](credits.jpeg)
