#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the Grocery POS development environment.
.DESCRIPTION
    Copies .env.example to .env if .env doesn't exist, then starts Docker Compose.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot

Write-Host "🛒 Grocery POS – Development Startup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Check for .env file
$envFile = Join-Path $root ".env"
$envExample = Join-Path $root ".env.example"

if (-not (Test-Path $envFile)) {
    Write-Host "⚠  .env not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item $envExample $envFile
    Write-Host "✅ .env created. Please edit it with real credentials before continuing." -ForegroundColor Green
    Write-Host "   Edit: $envFile" -ForegroundColor White
    exit 0
}

# Check backend .env
$backendEnv = Join-Path $root "backend" ".env"
$backendEnvExample = Join-Path $root "backend" ".env.example"
if (-not (Test-Path $backendEnv)) {
    Write-Host "⚠  backend/.env not found. Copying from backend/.env.example..." -ForegroundColor Yellow
    Copy-Item $backendEnvExample $backendEnv
    Write-Host "✅ backend/.env created. Edit credentials!" -ForegroundColor Green
}

Write-Host ""
Write-Host "🐳 Starting Docker services..." -ForegroundColor Cyan

Set-Location $root
docker compose up --build -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All services started!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  📦 Backend API : http://localhost:8000" -ForegroundColor White
    Write-Host "  📖 API Docs    : http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  ❤  Health      : http://localhost:8000/health" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Docker Compose failed. Check logs with: docker compose logs" -ForegroundColor Red
    exit 1
}
