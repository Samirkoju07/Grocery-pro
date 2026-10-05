#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run Alembic migrations inside the backend Docker container.
.PARAMETER Message
    Migration message (used for alembic revision --autogenerate)
.PARAMETER Action
    upgrade | downgrade | revision
#>
param(
    [string]$Action = "upgrade",
    [string]$Message = "auto",
    [string]$Target = "head"
)

switch ($Action) {
    "upgrade"  { docker compose exec backend alembic upgrade $Target }
    "downgrade"{ docker compose exec backend alembic downgrade -1 }
    "revision" { docker compose exec backend alembic revision --autogenerate -m $Message }
    default    { Write-Host "Unknown action: $Action"; exit 1 }
}
