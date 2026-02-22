#!/bin/bash
# Post-Deployment Smoke Test for Project149

set -e

API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost}"

echo "🧪 Running Post-Deployment Checks..."
echo "API URL: $API_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Check 1: API Root
echo "1️⃣  Checking API root..."
curl -f -s "$API_URL/" > /dev/null && echo "✅ API root accessible" || (echo "❌ API root failed" && exit 1)

# Check 2: API Docs
echo "2️⃣  Checking API docs..."
curl -f -s "$API_URL/docs" > /dev/null && echo "✅ API docs accessible" || echo "⚠️  API docs not accessible"

# Check 3: Health endpoint
echo "3️⃣  Checking health endpoint..."
HEALTH=$(curl -s "$API_URL/health")
echo "$HEALTH" | grep -q "healthy" && echo "✅ Health check passed" || (echo "❌ Health check failed" && exit 1)

# Check 4: Products endpoint
echo "4️⃣  Checking products endpoint..."
curl -f -s "$API_URL/products/?limit=1" > /dev/null && echo "✅ Products endpoint working" || (echo "❌ Products endpoint failed" && exit 1)

# Check 5: Recommendation health
echo "5️⃣  Checking recommendation service..."
curl -s "$API_URL/recommend/health" > /dev/null && echo "✅ Recommendations service accessible" || echo "⚠️  Recommendations service not available"

# Check 6: Frontend
echo "6️⃣  Checking frontend..."
curl -f -s "$FRONTEND_URL/" > /dev/null && echo "✅ Frontend accessible" || (echo "❌ Frontend failed" && exit 1)

# Check 7: Static images
echo "7️⃣  Checking static images..."
curl -f -s "$API_URL/images/" > /dev/null 2>&1 && echo "✅ Images endpoint accessible" || echo "⚠️  Images endpoint check skipped"

echo ""
echo "🎉 All critical checks passed!"
echo ""
echo "Next steps:"
echo "  - Test user signup/login"
echo "  - Verify cart functionality"
echo "  - Check recommendations panel"
echo "  - Run: node frontend/tests/smoke_auth.js"
