# OpenShift Cluster Navigator - Quick Reference

Essential commands and configurations for deploying and managing the application.

## Installation Commands

### Development
```bash
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace dev --create-namespace \
  --values ./openshift-cluster-navigator/values-development.yaml
```

### Production
```bash
# 1. Create secret
oc create secret generic cluster-navigator-credentials \
  --from-literal=username=admin \
  --from-literal=password="$(openssl rand -base64 32)" \
  -n production

# 2. Install
helm install cluster-navigator ./openshift-cluster-navigator \
  --namespace production --create-namespace \
  --values ./openshift-cluster-navigator/values-production.yaml \
  --set route.host="clusters.prod.example.com" \
  --set image.tag="v1.0.0"
```

## Common Operations

### Get Application URL
```bash
oc get route cluster-navigator -n cluster-navigator -o jsonpath='{.spec.host}'
```

### View Logs
```bash
oc logs -f deployment/cluster-navigator -n cluster-navigator
```

### Check Status
```bash
# Pods
oc get pods -n cluster-navigator

# Deployment
oc get deployment cluster-navigator -n cluster-navigator

# Route
oc get route cluster-navigator -n cluster-navigator

# Health check
curl -k https://$(oc get route cluster-navigator -n cluster-navigator -o jsonpath='{.spec.host}')/health
```

### Trigger Manual Sync
```bash
ROUTE_HOST=$(oc get route cluster-navigator -n cluster-navigator -o jsonpath='{.spec.host}')
ADMIN_PASS=$(oc get secret cluster-navigator-credentials -n cluster-navigator -o jsonpath='{.data.password}' | base64 -d)

curl -k -X POST https://$ROUTE_HOST/api/segments-sync/sync -u admin:$ADMIN_PASS
```

### Scale Replicas
```bash
oc scale deployment cluster-navigator --replicas=5 -n cluster-navigator
```

### View Cache
```bash
oc exec deployment/cluster-navigator -n cluster-navigator -- cat /app/data/segments_manager_cache.json | jq .
```

## Configuration Updates

### Update Segments Manager URL
```bash
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  -n cluster-navigator --reuse-values \
  --set app.segmentsManagerUrl="http://new-segments-manager:8000"
```

### Update Title
```bash
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  -n cluster-navigator --reuse-values \
  --set app.title="New Title"
```

### Enable Autoscaling
```bash
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  -n cluster-navigator --reuse-values \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=3 \
  --set autoscaling.maxReplicas=10
```

### Update Resources
```bash
helm upgrade cluster-navigator ./openshift-cluster-navigator \
  -n cluster-navigator --reuse-values \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=1Gi
```

## Troubleshooting

### Restart Pods
```bash
oc rollout restart deployment/cluster-navigator -n cluster-navigator
```

### Check Events
```bash
oc get events -n cluster-navigator --sort-by='.lastTimestamp'
```

### Debug Pod
```bash
oc debug deployment/cluster-navigator -n cluster-navigator
```

### Test Segments Manager Connection
```bash
oc exec deployment/cluster-navigator -n cluster-navigator -- \
  curl -v http://segments-manager:8000/api/segments
```

### View Secrets
```bash
# Username
oc get secret cluster-navigator-credentials -n cluster-navigator -o jsonpath='{.data.username}' | base64 -d

# Password
oc get secret cluster-navigator-credentials -n cluster-navigator -o jsonpath='{.data.password}' | base64 -d
```

## Helm Operations

### List Releases
```bash
helm list -n cluster-navigator
```

### Get Values
```bash
helm get values cluster-navigator -n cluster-navigator
```

### View Manifests
```bash
helm get manifest cluster-navigator -n cluster-navigator
```

### History
```bash
helm history cluster-navigator -n cluster-navigator
```

### Rollback
```bash
helm rollback cluster-navigator -n cluster-navigator
```

### Uninstall
```bash
helm uninstall cluster-navigator -n cluster-navigator
```

## Monitoring

### Resource Usage
```bash
oc adm top pod -n cluster-navigator
```

### HPA Status (if enabled)
```bash
oc get hpa -n cluster-navigator
```

### PVC Usage
```bash
oc get pvc -n cluster-navigator
oc exec deployment/cluster-navigator -n cluster-navigator -- df -h /app/data
```

## Validation

### Lint Chart
```bash
helm lint ./openshift-cluster-navigator
```

### Dry Run
```bash
helm install test ./openshift-cluster-navigator --dry-run --debug
```

### Template Validation
```bash
helm template test ./openshift-cluster-navigator > test-manifests.yaml
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_TITLE` | Application title | `"OpenShift Cluster Navigator"` |
| `ADMIN_USERNAME` | Admin username | `"admin"` |
| `ADMIN_PASSWORD` | Admin password | From secret |

## Important Files

| File | Purpose |
|------|---------|
| `/app/config.json` | Application configuration |
| `/app/data/segments_manager_cache.json` | Segments Manager cache |
| `/app/src/static/images/logo.png` | Application logo |

## URLs

- **Application**: `https://$(oc get route cluster-navigator -o jsonpath='{.spec.host}')`
- **Health Check**: `https://.../health`
- **API Docs**: `https://.../api/docs`
- **Sync Endpoint**: `POST https://.../api/segments-sync/sync`
- **Sites (Combined)**: `https://.../api/sites-combined`

## Support

- **Logs**: `oc logs -f deployment/cluster-navigator -n cluster-navigator`
- **Events**: `oc get events -n cluster-navigator --sort-by='.lastTimestamp'`
- **Documentation**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) and [README.md](openshift-cluster-navigator/README.md)
