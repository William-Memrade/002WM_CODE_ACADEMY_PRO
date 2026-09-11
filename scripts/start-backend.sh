#!/bin/bash
# CodeAcademy Pro — Backend Dev Server Launch Script
cd /mnt/c/Users/guill/Documents/Personal_Projects/Academy_Test/backend
source venv/bin/activate
echo "Starting FastAPI on http://localhost:8000"
echo "Docs: http://localhost:8000/api/docs"
echo "Press Ctrl+C to stop"
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
