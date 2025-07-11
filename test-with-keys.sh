#!/bin/bash

echo "🔑 Testing AI Brand Audit Tool with API Keys"
echo "============================================"

# Stop current container
docker stop brand-audit-backend 2>/dev/null || true
docker rm brand-audit-backend 2>/dev/null || true

echo "📍 Starting backend with API keys..."

# Start container with API keys (you'll need to replace these with your actual keys)
docker run -d -p 8000:8000 \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-sk-or-v1-your-key-here}" \
  -e NEWS_API_KEY="${NEWS_API_KEY:-your-news-key-here}" \
  -e BRANDFETCH_API_KEY="${BRANDFETCH_API_KEY:-your-brandfetch-key}" \
  -e OPENCORPORATES_API_KEY="${OPENCORPORATES_API_KEY:-your-opencorporates-key}" \
  -e FLASK_ENV=production \
  --name brand-audit-backend \
  brand-audit-app

sleep 3

echo "📍 Testing API with keys..."
curl -s https://207d-220-244-77-193.ngrok-free.app/api/health | jq '{service: .service, api_keys: .api_keys_configured}'

echo ""
echo "🚀 To add your real API keys, set these environment variables:"
echo "export OPENROUTER_API_KEY='sk-or-v1-your-actual-key'"
echo "export NEWS_API_KEY='your-actual-news-api-key'"
echo "export BRANDFETCH_API_KEY='your-actual-brandfetch-key'"
echo "export OPENCORPORATES_API_KEY='your-actual-opencorporates-key'"
echo ""
echo "Then run this script again to test with real data!"