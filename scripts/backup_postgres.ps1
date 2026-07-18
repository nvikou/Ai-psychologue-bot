# Backup PostgreSQL from Docker (Windows PowerShell).
param(
    [string]$OutDir = "./backups"
)

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$file = Join-Path $OutDir "psychologue_$stamp.sql"

docker compose exec -T postgres pg_dump -U psychologue psychologue | Set-Content -Path $file -Encoding utf8
Write-Host "Backup written to $file"
