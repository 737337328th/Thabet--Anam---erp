$ErrorActionPreference = "Stop"

Write-Host "Thabet Anam ERP V4 - Free Local Launcher" -ForegroundColor Cyan

if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "WSL is not installed." -ForegroundColor Yellow
    Write-Host "Open PowerShell as Administrator and run:" -ForegroundColor Yellow
    Write-Host "  wsl --install -d Ubuntu"
    Write-Host "Restart Windows if requested, then run this file again."
    exit 2
}

& wsl.exe --status *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "WSL is present but not ready." -ForegroundColor Yellow
    Write-Host "Open PowerShell as Administrator and run:"
    Write-Host "  wsl --install -d Ubuntu"
    exit 3
}

$repoPath = (Get-Location).Path
$wslPath = (& wsl.exe wslpath -a "$repoPath").Trim()
if (-not $wslPath) {
    throw "Could not translate the repository path to WSL."
}

$escapedPath = $wslPath.Replace("'", "'\\''")
$dockerCheck = & wsl.exe bash -lc "command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1"
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Docker Engine/Compose is not ready inside WSL." -ForegroundColor Yellow
    Write-Host "Run this command once in Ubuntu/WSL:"
    Write-Host "  cd '$wslPath' && bash deploy/free_local/prepare_ubuntu.sh"
    Write-Host "Then close/reopen WSL and run this launcher again."
    exit 4
}

$command = "cd '$escapedPath' && bash deploy/free_local/docker_zero_cost.sh"

Write-Host ""
Write-Host "Starting free local ERP deployment through WSL..." -ForegroundColor Green
& wsl.exe bash -lc $command
if ($LASTEXITCODE -ne 0) {
    throw "Deployment failed. Review the error shown above."
}

Write-Host ""
Write-Host "ERP URL: http://localhost:8080" -ForegroundColor Green
Write-Host "No financial vouchers or opening balances were posted automatically."
