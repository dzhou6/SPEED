$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
  Write-Host "Missing .env. Run: .\scripts\setup_env.ps1"
  exit 1
}

docker-compose up --build
