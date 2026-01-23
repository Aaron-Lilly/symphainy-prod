#!/bin/bash
set -e

echo "🔍 Checking firewall rules..."
gcloud compute firewall-rules list --filter="name~'allow-http' OR name~'default-allow-http'" 2>&1 || echo "Note: gcloud may require authentication"

echo ""
echo "🔧 Creating firewall rule for port 80..."
gcloud compute firewall-rules create allow-http-traefik \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow HTTP traffic to Traefik on port 80" \
  --target-tags http-server \
  2>&1 | grep -v "already exists" || echo "Rule already exists or creation failed"

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
  2>&1 || echo "Tag may already exist or command failed"

echo ""
echo "✅ Done! Test with: curl -I http://35.215.64.103/"
echo ""
echo "If the commands above failed, you may need to:"
echo "1. Authenticate: gcloud auth login"
echo "2. Set project: gcloud config set project YOUR_PROJECT_ID"
echo "3. Or use GCP Console to create the firewall rule manually"
