# OpenShift Cluster Navigator - Docker Images

This directory contains pre-built Docker images for the OpenShift Cluster Navigator application.

## Available Images

### openshift-cluster-navigator-v1.0.0.tar
- **Version**: 1.0.0
- **Size**: ~373 MB
- **Base Image**: python:3.11-slim
- **Architecture**: x86_64/amd64

## Loading the Image

### Using Podman

```bash
# Load the image from tarball
podman load -i docker-images/openshift-cluster-navigator-v1.0.0.tar

# Verify the image is loaded
podman images | grep openshift-cluster-navigator

# Run the container
podman run -d \
  --name cluster-navigator \
  -p 8000:8000 \
  -e APP_TITLE="My Cluster Navigator" \
  -e ADMIN_USERNAME="admin" \
  -e ADMIN_PASSWORD="SecurePassword123" \
  localhost/openshift-cluster-navigator:v1.0.0
```

### Using Docker

```bash
# Load the image from tarball
docker load -i docker-images/openshift-cluster-navigator-v1.0.0.tar

# Verify the image is loaded
docker images | grep openshift-cluster-navigator

# Run the container
docker run -d \
  --name cluster-navigator \
  -p 8000:8000 \
  -e APP_TITLE="My Cluster Navigator" \
  -e ADMIN_USERNAME="admin" \
  -e ADMIN_PASSWORD="SecurePassword123" \
  localhost/openshift-cluster-navigator:v1.0.0
```

## Pushing to a Container Registry

### Quay.io

```bash
# Load the image
podman load -i docker-images/openshift-cluster-navigator-v1.0.0.tar

# Login to Quay.io
podman login quay.io

# Tag for your registry
podman tag localhost/openshift-cluster-navigator:v1.0.0 \
  quay.io/your-org/openshift-cluster-navigator:v1.0.0

podman tag localhost/openshift-cluster-navigator:v1.0.0 \
  quay.io/your-org/openshift-cluster-navigator:latest

# Push to registry
podman push quay.io/your-org/openshift-cluster-navigator:v1.0.0
podman push quay.io/your-org/openshift-cluster-navigator:latest
```

### Docker Hub

```bash
# Load the image
podman load -i docker-images/openshift-cluster-navigator-v1.0.0.tar

# Login to Docker Hub
podman login docker.io

# Tag for Docker Hub
podman tag localhost/openshift-cluster-navigator:v1.0.0 \
  docker.io/your-username/openshift-cluster-navigator:v1.0.0

podman tag localhost/openshift-cluster-navigator:v1.0.0 \
  docker.io/your-username/openshift-cluster-navigator:latest

# Push to Docker Hub
podman push docker.io/your-username/openshift-cluster-navigator:v1.0.0
podman push docker.io/your-username/openshift-cluster-navigator:latest
```

### OpenShift Internal Registry

```bash
# Load the image
podman load -i docker-images/openshift-cluster-navigator-v1.0.0.tar

# Get OpenShift registry route
REGISTRY=$(oc get route default-route -n openshift-image-registry -o jsonpath='{.spec.host}')

# Login to OpenShift registry
podman login -u $(oc whoami) -p $(oc whoami -t) $REGISTRY --tls-verify=false

# Create project/namespace if needed
oc new-project cluster-navigator

# Tag for OpenShift registry
podman tag localhost/openshift-cluster-navigator:v1.0.0 \
  $REGISTRY/cluster-navigator/openshift-cluster-navigator:v1.0.0

podman tag localhost/openshift-cluster-navigator:v1.0.0 \
  $REGISTRY/cluster-navigator/openshift-cluster-navigator:latest

# Push to OpenShift registry
podman push $REGISTRY/cluster-navigator/openshift-cluster-navigator:v1.0.0 --tls-verify=false
podman push $REGISTRY/cluster-navigator/openshift-cluster-navigator:latest --tls-verify=false
```

### Harbor Registry

```bash
# Load the image
podman load -i docker-images/openshift-cluster-navigator-v1.0.0.tar

# Login to Harbor
podman login harbor.example.com

# Tag for Harbor
podman tag localhost/openshift-cluster-navigator:v1.0.0 \
  harbor.example.com/your-project/openshift-cluster-navigator:v1.0.0

podman tag localhost/openshift-cluster-navigator:v1.0.0 \
  harbor.example.com/your-project/openshift-cluster-navigator:latest

# Push to Harbor
podman push harbor.example.com/your-project/openshift-cluster-navigator:v1.0.0
podman push harbor.example.com/your-project/openshift-cluster-navigator:latest
```

## Using the Image with Helm

After pushing to a registry, update your Helm values:

```yaml
# values.yaml
image:
  repository: quay.io/your-org/openshift-cluster-navigator
  tag: "v1.0.0"
  pullPolicy: IfNotPresent

# If using a private registry
imagePullSecrets:
  - name: registry-credentials
```

Then deploy with Helm:

```bash
helm install cluster-navigator ./helm/openshift-cluster-navigator \
  --namespace cluster-navigator \
  --create-namespace \
  --set image.repository="quay.io/your-org/openshift-cluster-navigator" \
  --set image.tag="v1.0.0"
```

## Image Details

### Included Components
- Python 3.11
- FastAPI application
- All required Python dependencies
- Configuration files
- Static assets (HTML, CSS, JavaScript)
- Red Bull x OpenShift logo

### Environment Variables
- `APP_TITLE` - Application title (default: "OpenShift Cluster Navigator")
- `ADMIN_USERNAME` - Admin username (default: "admin")
- `ADMIN_PASSWORD` - Admin password (default: "Password1")
- `PYTHONUNBUFFERED` - Python unbuffered output (default: "1")

### Exposed Ports
- `8000` - HTTP port for the application

### Volumes
- `/app/data` - Cache directory for Segments Manager sync data

### User
- Runs as non-root user `appuser` (UID 1000)

## Testing the Image Locally

```bash
# Load the image
podman load -i docker-images/openshift-cluster-navigator-v1.0.0.tar

# Run with port forwarding
podman run -d \
  --name cluster-navigator-test \
  -p 8000:8000 \
  -e APP_TITLE="Test Navigator" \
  -e ADMIN_USERNAME="admin" \
  -e ADMIN_PASSWORD="test123" \
  localhost/openshift-cluster-navigator:v1.0.0

# Check if it's running
curl http://localhost:8000/health

# View logs
podman logs -f cluster-navigator-test

# Access the application
xdg-open http://localhost:8000

# Clean up
podman stop cluster-navigator-test
podman rm cluster-navigator-test
```

## Building a New Image

If you need to rebuild the image:

```bash
# From the project root
podman build -t openshift-cluster-navigator:v1.0.0 .

# Save as tarball
podman save -o docker-images/openshift-cluster-navigator-v1.0.0.tar \
  localhost/openshift-cluster-navigator:v1.0.0
```

## Troubleshooting

### Image Won't Load
```bash
# Check tarball integrity
tar -tzf docker-images/openshift-cluster-navigator-v1.0.0.tar > /dev/null
echo $?  # Should be 0
```

### Container Won't Start
```bash
# Check logs
podman logs cluster-navigator

# Run interactively for debugging
podman run -it --rm \
  -p 8000:8000 \
  localhost/openshift-cluster-navigator:v1.0.0 \
  /bin/bash
```

### Permission Issues
```bash
# The image runs as user 1000
# Ensure volumes have correct permissions
mkdir -p /path/to/data
chown 1000:1000 /path/to/data

podman run -d \
  -p 8000:8000 \
  -v /path/to/data:/app/data:Z \
  localhost/openshift-cluster-navigator:v1.0.0
```

## Security Considerations

1. **Change Default Passwords**: Always use secure passwords in production
2. **Use TLS**: Enable TLS termination at load balancer or reverse proxy
3. **Registry Security**: Use private registries for production images
4. **Image Scanning**: Scan images for vulnerabilities before deployment
5. **Access Control**: Limit who can pull/push images

## Support

For issues with the image:
1. Check logs: `podman logs container-name`
2. Verify environment variables are set correctly
3. Ensure Segments Manager is accessible
4. Review the application logs inside the container

For more information, see:
- [Main README](../README.md)
- [Deployment Guide](../helm/DEPLOYMENT_GUIDE.md)
- [Helm Chart Documentation](../helm/openshift-cluster-navigator/README.md)
