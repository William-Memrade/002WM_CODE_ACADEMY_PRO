#!/bin/bash
set -e
BASE="http://localhost:8000/api/v1"

echo "=== Login ==="
TOKEN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@codeacademypro.com","password":"Admin123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token: ${TOKEN:0:30}..."

echo ""
echo "=== GET /courses/admin/all ==="
curl -s "$BASE/courses/admin/all" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -25

echo ""
echo "=== GET /users/admin/metrics ==="
curl -s "$BASE/users/admin/metrics" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== GET /courses/categories (with full fields) ==="
curl -s "$BASE/courses/categories" | python3 -m json.tool | head -30

echo ""
echo "=== GET /payments/admin/list ==="
curl -s "$BASE/payments/admin/list?status=pending" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "=== GET /users/admin/users?role=student ==="
curl -s "$BASE/users/admin/users?role=student" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
