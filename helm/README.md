# OpenShift Cluster Navigator - Helm Charts

This directory contains Helm charts for deploying the OpenShift Cluster Navigator application to OpenShift clusters.

## Quick Start

```bash
# Lint the chart
helm lint ./openshift-cluster-navigator

# Install with default values
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --create-namespace

# Get the application URL
export ROUTE_HOST=$(oc get route cluster-navigator -n cluster-navigator -o jsonpath='{.spec.host}')
echo "Application URL: https://$ROUTE_HOST"
```

## Directory Structure

```
helm/
├── openshift-cluster-navigator/     # Main Helm chart
│   ├── Chart.yaml                    # Chart metadata
│   ├── values.yaml                   # Default values
│   ├── values-production.yaml        # Production configuration
│   ├── values-development.yaml       # Development configuration
│   ├── README.md                     # Chart documentation
│   ├── .helmignore                   # Helm ignore patterns
│   └── templates/                    # Kubernetes manifests templates
│       ├── _helpers.tpl              # Template helpers
│       ├── deployment.yaml           # Deployment manifest
│       ├── service.yaml              # Service manifest
│       ├── route.yaml                # OpenShift Route
│       ├── ingress.yaml              # Kubernetes Ingress (alternative)
│       ├── configmap.yaml            # Configuration
│       ├── secret.yaml               # Credentials
│       ├── serviceaccount.yaml       # Service account
│       ├── pvc.yaml                  # Persistent volume claim
│       ├── hpa.yaml                  # Horizontal Pod Autoscaler
│       ├── pdb.yaml                  # Pod Disruption Budget
│       ├── networkpolicy.yaml        # Network Policy
│       ├── servicemonitor.yaml       # Prometheus ServiceMonitor
│       └── NOTES.txt                 # Post-install notes
├── DEPLOYMENT_GUIDE.md               # Complete deployment guide
├── validate-chart.sh                 # Chart validation script
└── README.md                         # This file
```

## Files

### Chart Files

- **[openshift-cluster-navigator/Chart.yaml](openshift-cluster-navigator/Chart.yaml)** - Chart metadata and version information
- **[openshift-cluster-navigator/values.yaml](openshift-cluster-navigator/values.yaml)** - Default configuration values
- **[openshift-cluster-navigator/values-production.yaml](openshift-cluster-navigator/values-production.yaml)** - Production-ready configuration
- **[openshift-cluster-navigator/values-development.yaml](openshift-cluster-navigator/values-development.yaml)** - Development configuration

### Documentation

- **[openshift-cluster-navigator/README.md](openshift-cluster-navigator/README.md)** - Detailed chart documentation with examples
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Step-by-step deployment instructions

### Tools

- **[validate-chart.sh](validate-chart.sh)** - Validation script to test chart before deployment

## Quick Deployment Examples

### Development Environment

```bash
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace dev \
  --create-namespace \
  --values ./openshift-cluster-navigator/values-development.yaml
```

### Production Environment

```bash
# Create credentials secret first
oc create secret generic cluster-navigator-credentials \
  --from-literal=username=admin \
  --from-literal=password="$(openssl rand -base64 32)" \
  --namespace production

# Deploy
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace production \
  --create-namespace \
  --values ./openshift-cluster-navigator/values-production.yaml \
  --set route.host="clusters.prod.example.com"
```

### Custom Configuration

```bash
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --create-namespace \
  --set app.title="Custom Title" \
  --set app.segmentsManagerUrl="http://custom-segments-manager:8000" \
  --set image.repository="quay.io/your-org/cluster-navigator" \
  --set image.tag="v1.0.0"
```

## Validation

Before deploying, validate the chart:

```bash
# Run validation script
./validate-chart.sh

# Or manually:
helm lint ./openshift-cluster-navigator
helm template test ./openshift-cluster-navigator --debug
helm install test ./openshift-cluster-navigator --dry-run --debug
```

## Configuration

Key configuration parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `app.title` | Application title | `"OpenShift Cluster Navigator"` |
| `app.segmentsManagerUrl` | Segments Manager API URL | `"http://segments-manager:8000"` |
| `app.syncInterval` | Sync interval (seconds) | `300` |
| `auth.username` | Admin username | `"admin"` |
| `auth.password` | Admin password | `"Password1"` |
| `replicaCount` | Number of replicas | `2` |
| `persistence.enabled` | Enable persistent storage | `true` |
| `route.enabled` | Enable OpenShift Route | `true` |
| `autoscaling.enabled` | Enable HPA | `false` |

See [values.yaml](openshift-cluster-navigator/values.yaml) for all available options.

## Upgrading

```bash
# Upgrade to new version
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --values my-custom-values.yaml

# Rollback if needed
helm rollback cluster-navigator --namespace cluster-navigator
```

## Uninstalling

```bash
# Remove the release
helm uninstall cluster-navigator --namespace cluster-navigator

# Delete namespace
oc delete project cluster-navigator
```

## Documentation

- **Chart README**: [openshift-cluster-navigator/README.md](openshift-cluster-navigator/README.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Main Project**: [../README.md](../README.md)

## Support

For detailed deployment instructions, troubleshooting, and configuration examples, see:
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- [Chart README](openshift-cluster-navigator/README.md)

For issues and questions:
- GitHub Issues: https://github.com/your-org/openshift-cluster-navigator/issues
- Documentation: https://github.com/your-org/openshift-cluster-navigator/docs
