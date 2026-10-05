#!/usr/bin/env bash
# =============================================================================
# Grocery POS – Development startup script (Linux/macOS)
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"

echo -e "\e[36m🛒 Grocery POS – Development Startup\e[0m"
echo -e "\e[36m====================================\e[0m"

# Check .env
if [ ! -f "$ROOT_DIR/.env" ]; then
    echo -e "\e[33m⚠  .env not found. Copying from .env.example...\e[0m"
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    echo -e "\e[32m✅ .env created. Edit credentials before continuing.\e[0m"
    exit 0
fi

# Check backend .env
if [ ! -f "$ROOT_DIR/backend/.env" ]; then
    echo -e "\e[33m⚠  backend/.env not found. Copying...\e[0m"
    cp "$ROOT_DIR/backend/.env.example" "$ROOT_DIR/backend/.env"
    echo -e "\e[32m✅ backend/.env created. Edit credentials!\e[0m"
fi

echo -e "\n\e[36m🐳 Starting Docker services...\e[0m"
cd "$ROOT_DIR"
docker compose up --build -d

echo -e "\n\e[32m✅ All services started!\e[0m"
echo -e "  📦 Backend API : http://localhost:8000"
echo -e "  📖 API Docs    : http://localhost:8000/docs"
echo -e "  ❤  Health      : http://localhost:8000/health"
