[CmdletBinding()]
param(
    [ValidateSet("sast", "dast", "all")]
    [string]$Mode = "all",
    [switch]$KeepApplication
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$reports = Join-Path $repoRoot "security-reports"
$dastProject = "ai-real-estate-dast"
$applicationStarted = $false

docker info --format '{{.ServerVersion}}' 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Docker daemon is unavailable. Start Docker Desktop, switch to Linux containers, and retry."
}

New-Item -ItemType Directory -Force -Path $reports | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $reports ".zap-home") | Out-Null

Push-Location $repoRoot
try {
    if ($Mode -in @("sast", "all")) {
        Write-Host "Running Semgrep SAST..."
        $env:SEMGREP_FORMAT = "json"
        $env:SEMGREP_REPORT = "semgrep.json"
        docker compose -p ai-real-estate-sast -f compose.security.yml run --rm semgrep
        if ($LASTEXITCODE -ne 0) {
            throw "Semgrep failed with exit code $LASTEXITCODE"
        }
    }

    if ($Mode -in @("dast", "all")) {
        if (-not (Test-Path ".env")) {
            throw "Missing .env. Copy .env.example to .env and set the local values before DAST."
        }

        Write-Host "Starting the application for OWASP ZAP..."
        $env:AUTO_SEED_CATALOG = "false"
        docker compose -p $dastProject -f docker-compose.yml -f compose.dast.yml up -d --build frontend
        if ($LASTEXITCODE -ne 0) {
            throw "The application stack failed to start."
        }
        $applicationStarted = $true

        $ready = $false
        for ($attempt = 1; $attempt -le 60; $attempt++) {
            try {
                Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/ready" -TimeoutSec 3 | Out-Null
                Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/openapi.json" -TimeoutSec 3 | Out-Null
                Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:3000" -TimeoutSec 3 | Out-Null
                $ready = $true
                break
            }
            catch {
                Start-Sleep -Seconds 5
            }
        }
        if (-not $ready) {
            docker compose -p $dastProject logs --no-color
            throw "The application did not become ready within 5 minutes."
        }

        Write-Host "Running ZAP baseline scan against the frontend..."
        $env:ZAP_TARGET = "http://frontend:3000"
        $env:ZAP_REPORT = "zap-frontend.json"
        docker compose -p $dastProject -f docker-compose.yml -f compose.dast.yml -f compose.security.yml run --rm --no-deps zap-baseline
        if ($LASTEXITCODE -ne 0) {
            throw "ZAP frontend scan failed with exit code $LASTEXITCODE"
        }

        Write-Host "Running ZAP baseline scan against the backend Swagger UI..."
        $env:ZAP_API_TARGET = "http://backend:8000/docs"
        $env:ZAP_API_REPORT = "zap-backend.json"
        docker compose -p $dastProject -f docker-compose.yml -f compose.dast.yml -f compose.security.yml run --rm --no-deps zap-api
        if ($LASTEXITCODE -ne 0) {
            $zapExit = $LASTEXITCODE
            Write-Warning "ZAP backend baseline scan could not complete. Backend and database logs follow:"
            docker compose -p $dastProject -f docker-compose.yml -f compose.dast.yml logs --no-color backend database
            throw "ZAP backend scan failed with exit code $zapExit"
        }
    }
}
finally {
    if ($applicationStarted -and -not $KeepApplication) {
        docker compose -p $dastProject down --remove-orphans --volumes
    }
    Remove-Item Env:SEMGREP_FORMAT, Env:SEMGREP_REPORT, Env:AUTO_SEED_CATALOG,
        Env:ZAP_TARGET, Env:ZAP_REPORT, Env:ZAP_API_TARGET, Env:ZAP_API_REPORT `
        -ErrorAction SilentlyContinue
    Pop-Location
}

Write-Host "Aggregating available scanner outputs..."
$aggregateInputs = @()
if ($Mode -in @("sast", "all")) {
    $aggregateInputs += Join-Path $reports "semgrep.json"
}
if ($Mode -in @("dast", "all")) {
    $aggregateInputs += Join-Path $reports "zap-frontend.json"
    $aggregateInputs += Join-Path $reports "zap-backend.json"
}
$aggregateInputs = @($aggregateInputs | Where-Object { Test-Path $_ })
if ($aggregateInputs.Count -gt 0) {
    python scripts/security/aggregate_security_reports.py @aggregateInputs `
        --output-dir security-data-lake
    if ($LASTEXITCODE -ne 0) {
        throw "Security report aggregation failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Security reports are available in $reports"
Write-Host "Unified data lake is available in $(Join-Path $repoRoot 'security-data-lake')"
