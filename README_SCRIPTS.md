# Quick Script Reference

All scripts should be run from the **project root** (`/home/founders/demoversion/symphainy_source_code/`).

## Main Scripts (Project Root)

### Rebuild Everything
```bash
./rebuild.sh
```
- Stops all containers
- Builds all containers
- Starts all services
- Shows status

### Cleanup Docker
```bash
./cleanup.sh
```
- Interactive cleanup
- Stops containers (optional)
- Cleans unused images/containers
- Cleans volumes
- Cleans build cache

### Start Services
```bash
./startup.sh
```
- Starts all services in correct order
- Waits for health checks
- Shows service status

## Advanced Scripts (scripts/ directory)

### Full Rebuild with Health Checks
```bash
./scripts/rebuild_all_containers.sh
```

### Test Services
```bash
./scripts/test_services.sh
```

### Cleanup (non-interactive)
```bash
./scripts/cleanup_docker.sh
```

## Making Scripts Executable

If you get "permission denied" errors:

```bash
chmod +x rebuild.sh startup.sh cleanup.sh
chmod +x scripts/*.sh
```

## Troubleshooting

**"docker-compose.yml not found"**
- Make sure you're in the project root
- Run: `cd /home/founders/demoversion/symphainy_source_code`

**"Permission denied"**
- Make scripts executable: `chmod +x script_name.sh`

**"No such file or directory"**
- Check you're in the right directory: `pwd`
- Should show: `/home/founders/demoversion/symphainy_source_code`
