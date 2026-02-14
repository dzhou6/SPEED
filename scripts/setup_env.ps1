$ErrorActionPreference = "Stop"

if (Test-Path ".env") {
  Write-Host ".env already exists. Nothing to do."
  exit 0
}

Copy-Item ".env.example" ".env"
Write-Host "Created .env from .env.example"
Write-Host "Next: edit .env and set MONGO_URI to your MongoDB Atlas URI (or local Mongo)."
