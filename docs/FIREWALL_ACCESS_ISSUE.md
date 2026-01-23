# Firewall Access Issue - Port 80 Blocked

**Date:** January 23, 2026  
**Issue:** `ERR_CONNECTION_REFUSED` when accessing `http://35.215.64.103/`  
**Status:** Firewall blocking external access to port 80

---

## Diagnosis

✅ **Services Running:**
- Traefik: Running on port 80 (listening on 0.0.0.0:80)
- Frontend: Running and healthy
- Backend: Running and healthy

✅ **Local Access Works:**
- `curl http://localhost:80/` → Returns 200 OK
- Frontend HTML is being served correctly

❌ **External Access Blocked:**
- `http://35.215.64.103/` → Connection refused
- **Root Cause:** GCP firewall blocking port 80

---

## Solution: Create/Update Firewall Rule

### Option 1: Using gcloud CLI (Recommended)

```bash
# Check existing firewall rules
gcloud compute firewall-rules list --filter="name~'allow-http' OR name~'default-allow-http'"

# Create firewall rule to allow HTTP traffic (port 80)
gcloud compute firewall-rules create allow-http-traefik \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow HTTP traffic to Traefik on port 80" \
  --target-tags http-server

# Apply tag to your VM instance (if needed)
# First, get your instance name and zone
INSTANCE_NAME=$(hostname)
ZONE=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/zone -H "Metadata-Flavor: Google" | cut -d/ -f4)

# Add the http-server tag to your instance
gcloud compute instances add-tags $INSTANCE_NAME \
  --zone=$ZONE \
  --tags=http-server
```

### Option 2: Using GCP Console

1. Go to **VPC Network** → **Firewall** in GCP Console
2. Click **Create Firewall Rule**
3. Configure:
   - **Name:** `allow-http-traefik`
   - **Direction:** Ingress
   - **Action:** Allow
   - **Targets:** Specified target tags
   - **Target tags:** `http-server`
   - **Source IP ranges:** `0.0.0.0/0` (or specific IPs for security)
   - **Protocols and ports:** TCP port `80`
4. Click **Create**
5. Apply the `http-server` tag to your VM instance:
   - Go to **Compute Engine** → **VM instances**
   - Click on your instance
   - Click **Edit**
   - Under **Network tags**, add `http-server`
   - Click **Save**

---

## Security Considerations

### For Production (Recommended)

**Restrict Source IPs:**
```bash
# Only allow specific IP ranges
gcloud compute firewall-rules create allow-http-traefik \
  --allow tcp:80 \
  --source-ranges YOUR_IP/32,ANOTHER_IP/32 \
  --description "Allow HTTP traffic from specific IPs" \
  --target-tags http-server
```

**Or use IAP (Identity-Aware Proxy):**
- More secure for production
- Requires authentication before access
- Better for internal tools

### For Development/Demo

**Allow from anywhere (current setup):**
```bash
gcloud compute firewall-rules create allow-http-traefik \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow HTTP traffic to Traefik" \
  --target-tags http-server
```

---

## Verify Firewall Rule

After creating the rule:

```bash
# Test external access
curl -I http://35.215.64.103/

# Should return:
# HTTP/1.1 200 OK
```

---

## Alternative: Check Existing Rules

If you had this working before, check if there's an existing rule:

```bash
# List all firewall rules
gcloud compute firewall-rules list

# Check if default-allow-http exists
gcloud compute firewall-rules describe default-allow-http

# If it exists but doesn't allow port 80, update it:
gcloud compute firewall-rules update default-allow-http \
  --allow tcp:80,8080
```

---

## Quick Fix Script

Save this as `fix-firewall.sh`:

```bash
#!/bin/bash
set -e

echo "🔍 Checking firewall rules..."
gcloud compute firewall-rules list --filter="name~'allow-http' OR name~'default-allow-http'"

echo ""
echo "🔧 Creating firewall rule for port 80..."
gcloud compute firewall-rules create allow-http-traefik \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow HTTP traffic to Traefik on port 80" \
  --target-tags http-server \
  2>&1 | grep -v "already exists" || echo "Rule already exists"

echo ""
echo "🏷️  Getting instance info..."
INSTANCE_NAME=$(hostname)
ZONE=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/zone -H "Metadata-Flavor: Google" 2>/dev/null | cut -d/ -f4 || echo "us-central1-a")

echo "Instance: $INSTANCE_NAME"
echo "Zone: $ZONE"

echo ""
echo "🏷️  Adding http-server tag to instance..."
gcloud compute instances add-tags $INSTANCE_NAME \
  --zone=$ZONE \
  --tags=http-server \
  2>&1 || echo "Tag may already exist"

echo ""
echo "✅ Done! Test with: curl -I http://35.215.64.103/"
```

Run: `chmod +x fix-firewall.sh && ./fix-firewall.sh`

---

**Last Updated:** January 23, 2026
