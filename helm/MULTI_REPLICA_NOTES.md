# Multi-Replica Deployment Configuration

This application now supports running with **multiple replicas** (e.g., 3 replicas for high availability) sharing the same PersistentVolumeClaim (PVC).

## Requirements

### 1. **ReadWriteMany (RWX) Access Mode**

The PVC must support `ReadWriteMany` access mode to allow multiple pods to mount it simultaneously.

**Compatible Storage Classes:**
- NFS
- CephFS
- GlusterFS
- Azure Files
- AWS EFS

**Note:** `ReadWriteOnce` (RWO) storage classes like AWS EBS or local volumes will NOT work with multiple replicas.

### 2. **File Locking Implementation**

The code has been updated with:
- ✅ **File locking** using `fcntl` for safe concurrent writes
- ✅ **Atomic writes** using temporary files and rename operations
- ✅ **Retry logic** with exponential backoff
- ✅ **Shared locks** for reads (multiple readers allowed)
- ✅ **Exclusive locks** for writes (only one writer at a time)

## Updated Files

Two cache files are used:
1. `/app/data/segments_manager_cache.json` - Segments Manager sync data
2. `/app/data/manual_clusters.json` - Manually created clusters

Both files now use file locking to prevent race conditions across replicas.

## Helm Configuration

Update your `values.yaml`:

```yaml
# Number of replicas
replicaCount: 3

# Persistence configuration
persistence:
  enabled: true
  accessMode: ReadWriteMany  # IMPORTANT: Must be RWX for multiple replicas
  size: 1Gi
  storageClass: "nfs-client"  # Use your RWX storage class
  # storageClass: "azurefile"  # For Azure
  # storageClass: "efs-sc"     # For AWS EFS

# Pod Disruption Budget (optional but recommended for HA)
podDisruptionBudget:
  enabled: true
  minAvailable: 1

# Horizontal Pod Autoscaler (optional)
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

## Testing Multi-Replica Setup

1. **Deploy with 3 replicas:**
   ```bash
   helm upgrade --install cluster-navigator ./helm/cluster-navigator \
     --set replicaCount=3 \
     --set persistence.accessMode=ReadWriteMany \
     --set persistence.storageClass=nfs-client
   ```

2. **Verify all pods are running:**
   ```bash
   kubectl get pods -l app=cluster-navigator
   ```

3. **Test cluster creation:**
   - Create a manual cluster through the UI
   - Check that it appears on all replicas
   - Delete the cluster
   - Verify it's removed from all replicas

4. **Check logs for file locking:**
   ```bash
   kubectl logs -l app=cluster-navigator --tail=100 | grep -i "cache\|lock"
   ```

5. **Simulate pod restart:**
   ```bash
   kubectl delete pod <pod-name>
   # New pod should load manual clusters from cache
   ```

## How It Works

### Write Operations (Create/Update/Delete Cluster)

```
Pod 1: Request to create cluster
  ↓
1. Acquire EXCLUSIVE lock on manual_clusters.tmp
2. Write data to temporary file
3. Flush and fsync to disk
4. Release lock
5. Atomically rename .tmp to .json
  ↓
Pod 2 & 3: Will wait if trying to write simultaneously
```

### Read Operations (Load Clusters)

```
Pod 1, 2, 3: Load clusters on startup
  ↓
1. Each pod acquires SHARED lock on manual_clusters.json
2. Multiple pods can read simultaneously
3. Read cluster data
4. Release lock
  ↓
All pods have consistent data
```

### Segments Manager Sync

Only **one pod** should actively sync from Segments Manager (typically the leader). However, all pods can safely read the cache:

```
Pod 1 (Leader): Syncs every 5 minutes
  ↓
1. Fetch data from Segments Manager API
2. Acquire EXCLUSIVE lock
3. Write to segments_manager_cache.tmp
4. Atomic rename
  ↓
Pod 2 & 3: Read from cache when serving requests
```

## Troubleshooting

### Issue: Pods stuck in Pending state

**Cause:** PVC with RWO (ReadWriteOnce) mode

**Solution:** Change to RWX storage class:
```bash
kubectl patch pvc cluster-navigator-data -p '{"spec":{"accessModes":["ReadWriteMany"]}}'
```

### Issue: "Resource temporarily unavailable" errors

**Cause:** File locking contention

**Solution:** This is normal and handled by retry logic. If persistent, increase retry delay in code.

### Issue: Stale data on some pods

**Cause:** Cache not being read after updates

**Solution:** Pods load cache on startup. Force refresh:
```bash
kubectl rollout restart deployment/cluster-navigator
```

## Performance Considerations

- **Writes:** Serialized with file locking (only one pod writes at a time)
- **Reads:** Parallel (all pods can read simultaneously)
- **Cache Size:** Small JSON files (<1MB) - very fast
- **Lock Contention:** Minimal due to infrequent writes

## Recommended Configuration

For production with HA:

```yaml
replicaCount: 3
persistence:
  enabled: true
  accessMode: ReadWriteMany
  size: 2Gi
  storageClass: "nfs-client"

podDisruptionBudget:
  enabled: true
  minAvailable: 2

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 5
  targetCPUUtilizationPercentage: 75

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

This ensures:
- ✅ Always at least 2 pods running (minAvailable)
- ✅ Can handle pod failures gracefully
- ✅ Scales based on load
- ✅ Shared persistent storage across all replicas
