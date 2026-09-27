# OpenShift Cluster Navigator - Deployment Guide

Complete guide for deploying the OpenShift Cluster Navigator on OpenShift clusters using Helm.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Steps](#pre-deployment-steps)
3. [Building the Container Image](#building-the-container-image)
4. [Deployment Methods](#deployment-methods)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- OpenShift CLI (`oc`) version 4.x+
- Helm 3.0+
- Docker or Podman
- kubectl (optional, oc provides similar functionality)

```bash
# Verify installations
oc version
helm version
podman --version
```

### Cluster Requirements

- OpenShift 4.x cluster with admin access
- Available storage class for PersistentVolumeClaims
- Segments Manager API accessible from the cluster
- Minimum cluster resources:
  - 2 CPU cores available
  - 2GB RAM available
  - 5GB storage for cache

## Pre-Deployment Steps

### 1. Login to OpenShift Cluster

```bash
# Login to your OpenShift cluster
oc login https://api.your-cluster.example.com:6443 --token=YOUR_TOKEN

# Or with username/password
oc login https://api.your-cluster.example.com:6443 -u admin -p password
```

### 2. Create Namespace

```bash
# Create dedicated namespace
oc new-project cluster-navigator

# Or use existing namespace
oc project cluster-navigator
```

### 3. Create Secrets

#### Option A: Create Secret with Random Password

```bash
# Generate secure password
ADMIN_PASSWORD=$(openssl rand -base64 32)

# Create secret
oc create secret generic cluster-navigator-credentials \
  --from-literal=username=admin \
  --from-literal=password="$ADMIN_PASSWORD" \
  --namespace cluster-navigator

# Save password securely
echo "Admin password: $ADMIN_PASSWORD" | tee cluster-navigator-password.txt
chmod 600 cluster-navigator-password.txt
```

#### Option B: Create Secret with Specific Password

```bash
oc create secret generic cluster-navigator-credentials \
  --from-literal=username=admin \
  --from-literal=password="YourSecurePassword123!" \
  --namespace cluster-navigator
```

### 4. Configure Segments Manager Access

Ensure Segments Manager is accessible from the cluster:

```bash
# Test connectivity from a pod
oc run test-curl --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl -v http://segments-manager.segments-manager.svc:8000/api/segments
```

## Building the Container Image

### 1. Build with Podman/Docker

```bash
# Navigate to project directory
cd /home/roi/Documents/scripts/ClickCluster-Navigator

# Build the image
podman build -t openshift-cluster-navigator:v1.0.0 .

# Tag for registry
podman tag openshift-cluster-navigator:v1.0.0 \
  quay.io/your-org/openshift-cluster-navigator:v1.0.0
```

### 2. Push to Container Registry

#### Quay.io

```bash
# Login to Quay.io
podman login quay.io

# Push image
podman push quay.io/your-org/openshift-cluster-navigator:v1.0.0
```

#### OpenShift Internal Registry

```bash
# Get registry route
REGISTRY=$(oc get route default-route -n openshift-image-registry -o jsonpath='{.spec.host}')

# Login to OpenShift registry
podman login -u $(oc whoami) -p $(oc whoami -t) $REGISTRY

# Tag and push
podman tag openshift-cluster-navigator:v1.0.0 \
  $REGISTRY/cluster-navigator/openshift-cluster-navigator:v1.0.0

podman push $REGISTRY/cluster-navigator/openshift-cluster-navigator:v1.0.0
```

### 3. Configure Image Pull Secrets (if using private registry)

```bash
# Create pull secret for private registry
oc create secret docker-registry quay-pull-secret \
  --docker-server=quay.io \
  --docker-username=your-username \
  --docker-password=your-password \
  --docker-email=your-email@example.com \
  --namespace cluster-navigator
```

## Deployment Methods

### Method 1: Quick Deployment (Development)

```bash
cd helm

# Deploy with development values
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --values ./openshift-cluster-navigator/values-development.yaml
```

### Method 2: Production Deployment

```bash
cd helm

# Create custom production values
cat > production-custom.yaml <<EOF
app:
  title: "Production Cluster Navigator"
  segmentsManagerUrl: "http://segments-manager.production.svc:8000"

auth:
  existingSecret: "cluster-navigator-credentials"

image:
  repository: quay.io/your-org/openshift-cluster-navigator
  tag: "v1.0.0"

route:
  host: "clusters.prod.rbr.io"

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

# Deploy
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --values ./openshift-cluster-navigator/values-production.yaml \
  --values production-custom.yaml
```

### Method 3: Deployment with Custom Configuration

```bash
# Deploy with inline overrides
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --set app.title="Red Bull Racing Clusters" \
  --set app.segmentsManagerUrl="http://segments-manager:8000" \
  --set auth.existingSecret="cluster-navigator-credentials" \
  --set image.repository="quay.io/rbr/cluster-navigator" \
  --set image.tag="v1.0.0" \
  --set route.host="clusters.rbr.example.com" \
  --set persistence.size="10Gi"
```

### Method 4: GitOps Deployment (ArgoCD)

Create ArgoCD Application:

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cluster-navigator
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/openshift-cluster-navigator
    targetRevision: main
    path: helm/openshift-cluster-navigator
    helm:
      valueFiles:
        - values-production.yaml
      values: |
        app:
          title: "Production Cluster Navigator"
          segmentsManagerUrl: "http://segments-manager.segments-manager.svc:8000"
        auth:
          existingSecret: "cluster-navigator-credentials"
        image:
          repository: quay.io/your-org/openshift-cluster-navigator
          tag: "v1.0.0"
        route:
          host: "clusters.prod.example.com"
  destination:
    server: https://kubernetes.default.svc
    namespace: cluster-navigator
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

Apply:
```bash
oc apply -f argocd-application.yaml
```

## Post-Deployment Verification

### 1. Check Deployment Status

```bash
# Check pods
oc get pods -n cluster-navigator

# Check deployment
oc get deployment -n cluster-navigator

# Check services
oc get svc -n cluster-navigator

# Check route
oc get route -n cluster-navigator
```

### 2. View Logs

```bash
# View deployment logs
oc logs -f deployment/cluster-navigator -n cluster-navigator

# View all pods logs
oc logs -l app.kubernetes.io/name=openshift-cluster-navigator -n cluster-navigator --tail=100
```

### 3. Test Health Endpoint

```bash
# Get route URL
ROUTE_URL=$(oc get route cluster-navigator -n cluster-navigator -o jsonpath='{.spec.host}')

# Test health endpoint
curl -k https://$ROUTE_URL/health

# Expected output:
# {"status":"healthy","service":"openshift-cluster-navigator"}
```

### 4. Access the Application

```bash
# Get the URL
echo "Application URL: https://$(oc get route cluster-navigator -n cluster-navigator -o jsonpath='{.spec.host}')"

# Open in browser
xdg-open "https://$(oc get route cluster-navigator -n cluster-navigator -o jsonpath='{.spec.host}')"
```

### 5. Test Segments Manager Sync

```bash
# Trigger manual sync
ROUTE_URL=$(oc get route cluster-navigator -n cluster-navigator -o jsonpath='{.spec.host}')

# Get admin password
ADMIN_PASSWORD=$(oc get secret cluster-navigator-credentials -n cluster-navigator -o jsonpath='{.data.password}' | base64 -d)

# Trigger sync (requires admin credentials)
curl -k -X POST https://$ROUTE_URL/api/segments-sync/sync \
  -u admin:$ADMIN_PASSWORD

# Check cache
oc exec deployment/cluster-navigator -n cluster-navigator -- cat /app/data/segments_manager_cache.json
```

## Configuration

### Update Configuration After Deployment

```bash
# Update Segments Manager URL
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --reuse-values \
  --set app.segmentsManagerUrl="http://new-segments-manager:8000"

# Update sync interval
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --reuse-values \
  --set app.syncInterval=600

# Update application title
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --reuse-values \
  --set app.title="Updated Title"
```

### Scale Replicas

```bash
# Scale manually
oc scale deployment cluster-navigator --replicas=5 -n cluster-navigator

# Or via Helm
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --reuse-values \
  --set replicaCount=5
```

### Enable Autoscaling

```bash
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --reuse-values \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=3 \
  --set autoscaling.maxReplicas=10
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
oc describe pod -l app.kubernetes.io/name=openshift-cluster-navigator -n cluster-navigator

# Check deployment events
oc describe deployment cluster-navigator -n cluster-navigator

# Common issues:
# - Image pull errors: Check imagePullSecrets
# - Resource limits: Check node resources
# - PVC issues: Check storage class availability
```

### Segments Manager Connection Issues

```bash
# Test from pod
oc exec deployment/cluster-navigator -n cluster-navigator -- \
  curl -v http://segments-manager:8000/api/segments

# Check network policy
oc get networkpolicy -n cluster-navigator

# Disable network policy temporarily
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --reuse-values \
  --set networkPolicy.enabled=false
```

### Route Not Accessible

```bash
# Check route status
oc get route cluster-navigator -n cluster-navigator -o yaml

# Check router pods
oc get pods -n openshift-ingress

# Test from within cluster
oc run test-curl --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl -v http://cluster-navigator:8000/health
```

### SCC (Security Context Constraint) Issues

The Helm chart is configured to work with OpenShift's default `restricted-v2` SCC without requiring `anyuid`. 

**If you see SCC errors:**

```bash
# Check current SCC assignment
oc describe sa cluster-navigator -n cluster-navigator

# The chart uses fsGroup and dynamic UID assignment
# No special SCC permissions should be required
```

**If initContainer fails with permission errors:**

```bash
# Option 1: Disable initContainer (fsGroup should handle permissions)
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --reuse-values \
  --set initContainer.enabled=false

# Option 2: Grant specific SCC if needed (not recommended)
# oc adm policy add-scc-to-user anyuid system:serviceaccount:cluster-navigator:cluster-navigator
```

**Key changes for SCC compliance:**
- Removed `runAsUser: 1000` (allows OpenShift to assign random UID)
- Added `fsGroup: 1000` (ensures volume access by group)
- Added optional initContainer to fix permissions
- Dockerfile ensures `/app/data` is group-writable

### Permission Denied on /app/data

**Symptoms:** Application cannot write to `/app/data` directory

**Solutions:**

```bash
# Check pod security context
oc get pod -n cluster-navigator -o yaml | grep -A 10 securityContext

# Check volume permissions
oc exec deployment/cluster-navigator -n cluster-navigator -- ls -lah /app/data

# Verify fsGroup is set
oc get pod -n cluster-navigator -o jsonpath='{.spec.securityContext.fsGroup}'

# If permissions are wrong, enable initContainer
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --reuse-values \
  --set initContainer.enabled=true

# Or manually fix permissions (if you have access)
oc exec deployment/cluster-navigator -n cluster-navigator -- \
  sh -c "chmod -R 775 /app/data"
```

**For disconnected environments:**
- The chart works with default `restricted-v2` SCC
- No `anyuid` SCC required
- `fsGroup` handles volume permissions automatically
- InitContainer is optional and can be disabled if it causes issues

### Cache Issues

```bash
# Check PVC
oc get pvc -n cluster-navigator

# Check cache file
oc exec deployment/cluster-navigator -n cluster-navigator -- ls -lah /app/data/

# Clear cache (delete pod to force resync)
oc delete pod -l app.kubernetes.io/name=openshift-cluster-navigator -n cluster-navigator
```

### High Memory Usage

```bash
# Check resource usage
oc adm top pod -n cluster-navigator

# Increase memory limits
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --reuse-values \
  --set resources.limits.memory=2Gi
```

## Upgrading

### Upgrade to New Version

```bash
# Pull latest chart
cd helm

# Review changes
helm diff upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --values production-custom.yaml

# Upgrade
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  --namespace cluster-navigator \
  --values production-custom.yaml

# Monitor rollout
oc rollout status deployment/cluster-navigator -n cluster-navigator
```

### Rollback

```bash
# View release history
helm history cluster-navigator -n cluster-navigator

# Rollback to previous version
helm rollback cluster-navigator -n cluster-navigator

# Rollback to specific revision
helm rollback cluster-navigator 2 -n cluster-navigator
```

## Uninstalling

```bash
# Uninstall Helm release
helm uninstall cluster-navigator --namespace cluster-navigator

# Delete namespace
oc delete project cluster-navigator

# Clean up secrets (if needed)
oc delete secret cluster-navigator-credentials
```

## Production Checklist

Before deploying to production, ensure:

- [ ] Container image built and pushed to registry
- [ ] Secure password generated and stored safely
- [ ] Segments Manager connectivity tested
- [ ] Resource limits appropriate for workload
- [ ] Persistent storage configured
- [ ] TLS/SSL enabled on route
- [ ] Autoscaling configured
- [ ] Network policies enabled
- [ ] Monitoring/alerting configured
- [ ] Backup strategy for cache data
- [ ] Documentation updated with custom configurations
- [ ] Team trained on accessing and using the application

## Support

For issues and questions:
- Check logs: `oc logs -f deployment/cluster-navigator -n cluster-navigator`
- Review events: `oc get events -n cluster-navigator --sort-by='.lastTimestamp'`
- Open issue: https://github.com/your-org/openshift-cluster-navigator/issues
