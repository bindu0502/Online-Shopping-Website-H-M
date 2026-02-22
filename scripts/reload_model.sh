#!/bin/bash
# Model Reload Script for Project149
# Safely reloads the recommendation model

set -e

API_URL="${API_URL:-http://localhost:8000}"
TOKEN="${AUTH_TOKEN}"

echo "🔄 Reloading recommendation model..."

if [ -z "$TOKEN" ]; then
    echo "⚠️  Warning: No AUTH_TOKEN provided. Attempting without authentication..."
    RESPONSE=$(curl -s -X POST "$API_URL/recommend/reload" \
        -H "Content-Type: application/json")
else
    RESPONSE=$(curl -s -X POST "$API_URL/recommend/reload" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN")
fi

echo "Response: $RESPONSE"

# Check health after reload
echo ""
echo "🏥 Checking recommendation service health..."
HEALTH=$(curl -s "$API_URL/recommend/health" || echo '{"status":"error"}')
echo "Health: $HEALTH"

if echo "$HEALTH" | grep -q "healthy\|ok"; then
    echo "✅ Model reload successful!"
    exit 0
else
    echo "❌ Model reload may have failed. Check logs."
    exit 1
fi
