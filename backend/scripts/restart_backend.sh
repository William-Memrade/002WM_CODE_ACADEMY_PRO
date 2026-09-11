#!/bin/bash
# Kill old uvicorn and clear pycache, then restart fresh

echo "Killing uvicorn..."
pkill -f "uvicorn main:app" 2>/dev/null || true
sleep 2

echo "Clearing __pycache__..."
find /mnt/c/Users/guill/Documents/Personal_Projects/Academy_Test/backend -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
echo "Cache cleared."

echo "Starting uvicorn..."
cd /mnt/c/Users/guill/Documents/Personal_Projects/Academy_Test/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/uvicorn.log 2>&1 &
echo "PID: $!"
sleep 6

echo "Testing health..."
curl -s http://localhost:8000/health
echo ""
echo "Done!"
