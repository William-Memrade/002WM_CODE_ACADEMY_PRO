#!/bin/bash
# CodeAcademy Pro — Frontend Dev Server Launch Script
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
cd /mnt/c/Users/guill/Documents/Personal_Projects/Academy_Test/frontend
echo "Starting Next.js on http://localhost:3000"
echo "Press Ctrl+C to stop"
exec npx next dev -p 3000
