# OpenShift Cluster Navigator Helm Chart

A Helm chart for deploying the OpenShift Cluster Navigator application on OpenShift clusters.

## Overview

OpenShift Cluster Navigator is a web application that helps you navigate and manage your OpenShift clusters organized by site. It integrates with Segments Manager to automatically sync cluster and network segment information.

## Features

- 🔄 Automatic sync with Segments Manager API
- 📊 Cluster organization by site
- 🎨 Red Bull Racing × OpenShift branding
- 🔒 Secure authentication
- 📱 Responsive design with dark mode
- 💾 Persistent cache storage
- 🚀 Horizontal Pod Autoscaling support
- 📈 Prometheus monitoring support

## Prerequisites

- Kubernetes 1.19+ or OpenShift 4.x+
- Helm 3.0+
- PersistentVolume provisioner support (if persistence is enabled)

## Installing the Chart

### Quick Start

```bash
# Add the Helm repository (if published)
helm repo add cluster-navigator https://your-repo-url
helm repo update

# Install with default values
helm install cluster-navigator cluster-navigator/openshift-cluster-navigator
```

### Local Installation

```bash
# From the helm directory
cd helm

# Install the chart
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --create-namespace
```

### Custom Installation

```bash
# Install with custom values
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --create-namespace \
  --set app.title="Red Bull Racing Clusters" \
  --set app.segmentsManagerUrl="http://segments-manager.segments-manager.svc:8000" \
  --set auth.password="YourSecurePassword123" \
  --set route.host="clusters.apps.ocp.example.com"
```

### Using a Custom Values File

```bash
# Create your custom values file
cat > my-values.yaml <<EOF
app:
  title: "Production Cluster Navigator"
  segmentsManagerUrl: "http://segments-manager.production.svc:8000"

auth:
  existingSecret: "cluster-navigator-credentials"

route:
  host: "clusters.apps.prod.example.com"

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
EOF

# Install with custom values
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --create-namespace \
  --values my-values.yaml
```

## Configuration

The following table lists the configurable parameters of the chart and their default values.

### Application Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `app.title` | Application title displayed in UI | `"OpenShift Cluster Navigator"` |
| `app.segmentsManagerUrl` | Segments Manager API URL | `"http://segments-manager:8000"` |
| `app.syncInterval` | Sync interval in seconds | `300` |

### Authentication

| Parameter | Description | Default |
|-----------|-------------|---------|
| `auth.username` | Admin username | `"admin"` |
| `auth.password` | Admin password (change in production!) | `"Password1"` |
| `auth.existingSecret` | Use existing secret for credentials | `""` |

### Image Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Image repository | `quay.io/your-org/openshift-cluster-navigator` |
| `image.tag` | Image tag | `"latest"` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `imagePullSecrets` | Image pull secrets | `[]` |

### Deployment

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `2` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |

### Persistence

| Parameter | Description | Default |
|-----------|-------------|---------|
| `persistence.enabled` | Enable persistent storage | `true` |
| `persistence.size` | PVC size | `1Gi` |
| `persistence.storageClass` | Storage class | `""` (default) |
| `persistence.existingClaim` | Use existing PVC | `""` |

### OpenShift Route

| Parameter | Description | Default |
|-----------|-------------|---------|
| `route.enabled` | Enable OpenShift Route | `true` |
| `route.host` | Route hostname | `""` (auto-generated) |
| `route.tls.enabled` | Enable TLS | `true` |
| `route.tls.termination` | TLS termination type | `edge` |

### Autoscaling

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable HPA | `false` |
| `autoscaling.minReplicas` | Minimum replicas | `2` |
| `autoscaling.maxReplicas` | Maximum replicas | `10` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU % | `80` |

### Network Policy

| Parameter | Description | Default |
|-----------|-------------|---------|
| `networkPolicy.enabled` | Enable Network Policy | `false` |

### Monitoring

| Parameter | Description | Default |
|-----------|-------------|---------|
| `monitoring.serviceMonitor.enabled` | Enable ServiceMonitor | `false` |

## Examples

### Production Deployment with HA

```yaml
# production-values.yaml
replicaCount: 3

app:
  title: "Production Cluster Navigator"
  segmentsManagerUrl: "http://segments-manager.production.svc.cluster.local:8000"
  syncInterval: 180

auth:
  existingSecret: "cluster-navigator-prod-credentials"

image:
  repository: quay.io/rbr-infrastructure/cluster-navigator
  tag: "v1.0.0"
  pullPolicy: Always

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 256Mi

persistence:
  enabled: true
  size: 5Gi
  storageClass: "gp3-csi"

route:
  enabled: true
  host: "clusters.prod.rbr.io"
  annotations:
    haproxy.router.openshift.io/timeout: "5m"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 15
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

podDisruptionBudget:
  enabled: true
  minAvailable: 2

networkPolicy:
  enabled: true

monitoring:
  serviceMonitor:
    enabled: true
    labels:
      prometheus: kube-prometheus
```

Deploy:
```bash
helm upgrade --install cluster-navigator ./openshift-cluster-navigator \
  --namespace production \
  --create-namespace \
  --values production-values.yaml
```

### Development Deployment

```yaml
# dev-values.yaml
replicaCount: 1

app:
  title: "Dev Cluster Navigator"
  segmentsManagerUrl: "http://segments-manager.dev.svc:8000"

auth:
  username: "admin"
  password: "DevPassword123"

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 50m
    memory: 64Mi

persistence:
  enabled: false

route:
  host: "clusters.dev.example.com"

autoscaling:
  enabled: false
```

### Using External Segments Manager

```yaml
# external-segments-manager.yaml
app:
  segmentsManagerUrl: "https://segments-manager.external.example.com"
  syncInterval: 600  # 10 minutes

networkPolicy:
  enabled: true
  egress:
    # Allow Segments Manager
    - to:
      - namespaceSelector: {}
      ports:
      - protocol: TCP
        port: 443
```

## Upgrading

```bash
# Upgrade to new version
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --values my-values.yaml

# Upgrade with new image
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --set image.tag=v1.1.0
```

## Uninstalling

```bash
# Uninstall the release
helm uninstall cluster-navigator --namespace cluster-navigator

# Delete the namespace
kubectl delete namespace cluster-navigator
```

## Security Considerations

### 1. Credentials

**Never commit default passwords to production!** Always use secure passwords or existing secrets:

```bash
# Create secret with secure credentials
kubectl create secret generic cluster-navigator-credentials \
  --from-literal=username=admin \
  --from-literal=password="$(openssl rand -base64 32)" \
  --namespace cluster-navigator

# Use in values
auth:
  existingSecret: "cluster-navigator-credentials"
```

### 2. TLS/SSL

For production, always enable TLS:

```yaml
route:
  tls:
    enabled: true
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
```

### 3. Network Policies

Enable network policies to restrict traffic:

```yaml
networkPolicy:
  enabled: true
```

### 4. Security Context

The chart uses restrictive security contexts by default:
- Non-root user (UID 1000)
- Read-only root filesystem (where possible)
- Dropped capabilities

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n cluster-navigator
kubectl describe pod <pod-name> -n cluster-navigator
kubectl logs -f deployment/cluster-navigator -n cluster-navigator
```

### Check Route

```bash
oc get route cluster-navigator -n cluster-navigator
curl -k https://$(oc get route cluster-navigator -o jsonpath='{.spec.host}')/health
```

### Sync Issues

Check Segments Manager connectivity:
```bash
kubectl exec -it deployment/cluster-navigator -n cluster-navigator -- \
  curl http://segments-manager:8000/api/segments
```

### View Cache

```bash
kubectl exec -it deployment/cluster-navigator -n cluster-navigator -- \
  cat /app/data/segments_manager_cache.json
```

### Reset Cache

```bash
# Delete the pod to force resync
kubectl delete pod -l app.kubernetes.io/name=openshift-cluster-navigator -n cluster-navigator
```

## Development

### Testing the Chart

```bash
# Lint the chart
helm lint ./openshift-cluster-navigator

# Template the chart (dry-run)
helm template cluster-navigator ./openshift-cluster-navigator \
  --values values.yaml \
  --debug

# Install in dry-run mode
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace test \
  --dry-run --debug
```

### Package the Chart

```bash
# Package for distribution
helm package ./openshift-cluster-navigator

# Update repository index
helm repo index .
```

## Support

For issues and feature requests, please visit:
https://github.com/yourusername/openshift-cluster-navigator/issues

## License

Copyright © 2024 Red Bull Racing Infrastructure Team
