#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run backend tests inside Docker.
#>

docker compose exec backend pytest tests/ -v --tb=short
