# Build Notes - OpenShift Cluster Navigator v1.0.0

## Build Information

**Build Date**: 2025-11-16
**Version**: v1.0.0
**Image Size**: ~373 MB
**Base Image**: python:3.11-slim
**Architecture**: linux/amd64 (x86_64)

## Build Command

```bash
podman build -t openshift-cluster-navigator:v1.0.0 -t openshift-cluster-navigator:latest .
```

## Image Layers

1. **Base Layer**: Python 3.11 slim (Debian Trixie)
2. **System Dependencies**: gcc and build tools
3. **Python Dependencies**: FastAPI, Uvicorn, Pydantic, etc.
4. **Application Code**: Source files, templates, static assets
5. **Configuration**: config.json, environment setup
6. **User Setup**: Non-root user (appuser, UID 1000)

## Installed Python Packages

### Core Framework
- fastapi==0.115.5
- uvicorn[standard]==0.32.1
- starlette==0.41.3

### Data Validation
- pydantic==2.10.3
- pydantic-core==2.27.1
- pydantic-settings==2.6.1

### Utilities
- python-multipart==0.0.17
- jinja2==3.1.4
- aiofiles==24.1.0
- httpx==0.28.1

### Security
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4
- cryptography==46.0.3
- bcrypt==5.0.0

### Testing
- pytest==8.3.4

### Full Dependency List
See [requirements.txt](../requirements.txt) for complete list.

## Security Configuration

- **Non-root User**: Runs as `appuser` (UID 1000)
- **Dropped Capabilities**: Security context restricts container privileges
- **Health Check**: Built-in health endpoint monitoring
- **No Default Secrets**: Credentials must be provided via environment variables

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONUNBUFFERED` | `1` | Python unbuffered output |
| `PYTHONDONTWRITEBYTECODE` | `1` | Prevent .pyc files |
| `PIP_NO_CACHE_DIR` | `1` | Disable pip cache |
| `APP_TITLE` | `"OpenShift Cluster Navigator"` | Application title |
| `ADMIN_USERNAME` | `"admin"` | Admin username |
| `ADMIN_PASSWORD` | `"Password1"` | Admin password (CHANGE IN PRODUCTION!) |

## Exposed Ports

- **8000**: HTTP application port

## Volumes

- `/app/data`: Cache directory for Segments Manager sync data (persistent storage recommended)

## Health Check

The image includes a health check that runs every 30 seconds:

```python
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","service":"openshift-cluster-navigator"}
```

## Image Tags

After building, the image has the following tags:
- `localhost/openshift-cluster-navigator:v1.0.0`
- `localhost/openshift-cluster-navigator:latest`

## Saved Tarball

**Location**: `docker-images/openshift-cluster-navigator-v1.0.0.tar`
**Size**: 373 MB
**Compressed**: No (uncompressed tar)

### Loading from Tarball

```bash
podman load -i docker-images/openshift-cluster-navigator-v1.0.0.tar
```

## Testing the Image

### Quick Test
```bash
podman run --rm -p 8000:8000 localhost/openshift-cluster-navigator:v1.0.0
```

### Full Test with Configuration
```bash
podman run -d \
  --name cluster-navigator-test \
  -p 8000:8000 \
  -e APP_TITLE="Test Navigator" \
  -e ADMIN_USERNAME="testadmin" \
  -e ADMIN_PASSWORD="TestPass123!" \
  -v $(pwd)/test-data:/app/data:Z \
  localhost/openshift-cluster-navigator:v1.0.0

# Test health endpoint
curl http://localhost:8000/health

# View logs
podman logs -f cluster-navigator-test

# Access application
xdg-open http://localhost:8000

# Login with credentials
# Username: testadmin
# Password: TestPass123!

# Cleanup
podman stop cluster-navigator-test
podman rm cluster-navigator-test
```

## Recommended Registry Destinations

### 1. Quay.io (Recommended for Production)
```bash
./docker-images/push-image.sh
# Select option 1
```

Benefits:
- Free for public images
- Excellent security scanning
- High availability
- Good integration with OpenShift

### 2. OpenShift Internal Registry
```bash
./docker-images/push-image.sh
# Select option 3
```

Benefits:
- No external dependencies
- Integrated with OpenShift RBAC
- Fast pulls within cluster
- Private by default

### 3. Harbor (Enterprise Option)
```bash
./docker-images/push-image.sh
# Select option 4
```

Benefits:
- Self-hosted
- Built-in vulnerability scanning
- Content trust/signing
- Replication capabilities

## Production Deployment Checklist

Before deploying to production:

- [ ] Change default admin password
- [ ] Push image to secure registry
- [ ] Configure Segments Manager URL
- [ ] Set up persistent storage for cache
- [ ] Configure TLS/SSL termination
- [ ] Enable monitoring/alerting
- [ ] Set appropriate resource limits
- [ ] Configure backup for cache data
- [ ] Test health check endpoint
- [ ] Verify Segments Manager connectivity
- [ ] Review security context constraints
- [ ] Document custom configurations

## Known Issues

1. **HEALTHCHECK Warning**: Podman shows a warning about HEALTHCHECK not being supported for OCI format. This is informational only and doesn't affect functionality. The health check works when running in Docker format or when deployed to Kubernetes/OpenShift.

2. **Debconf Warnings**: During build, you may see debconf warnings about terminal issues. These are harmless and don't affect the final image.

## Troubleshooting

### Image Won't Start

**Symptoms**: Container exits immediately after starting

**Solutions**:
- Check logs: `podman logs <container-name>`
- Verify environment variables are set correctly
- Ensure port 8000 is not already in use
- Check Segments Manager accessibility

### Permission Denied Errors

**Symptoms**: Cannot write to `/app/data`

**Solutions**:
- Ensure volume has correct permissions (UID 1000)
- Use SELinux context with `:Z` flag for volumes
- Run: `chown -R 1000:1000 /path/to/data`

### Health Check Failing

**Symptoms**: Container marked unhealthy

**Solutions**:
- Check if application is listening on port 8000
- Verify no startup errors in logs
- Test manually: `curl http://localhost:8000/health`

## Version History

### v1.0.0 (2025-11-16)
- Initial release
- FastAPI backend with Segments Manager integration
- Responsive UI with dark mode
- Red Bull x OpenShift branding
- Automatic sync with 5-minute intervals
- Support for duplicate cluster names across sites
- Support for multiple clusters sharing segments
- Configurable via environment variables
- Non-root container user
- Health check endpoint
- Comprehensive Helm chart

## Next Steps

1. **Push to Registry**: Use `./docker-images/push-image.sh`
2. **Update Helm Values**: Set `image.repository` and `image.tag`
3. **Deploy**: Follow [DEPLOYMENT_GUIDE.md](../helm/DEPLOYMENT_GUIDE.md)
4. **Test**: Verify application functionality
5. **Monitor**: Set up logging and monitoring
6. **Document**: Update team documentation with custom configs

## Support

For build-related issues:
- Check [Dockerfile](../Dockerfile)
- Review [requirements.txt](../requirements.txt)
- See [README.md](../README.md)

For deployment issues:
- See [DEPLOYMENT_GUIDE.md](../helm/DEPLOYMENT_GUIDE.md)
- Check [Helm Chart README](../helm/openshift-cluster-navigator/README.md)
