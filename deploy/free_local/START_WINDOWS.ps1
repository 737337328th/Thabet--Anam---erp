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
