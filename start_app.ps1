Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting Advanced OCR with Layout Understanding" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$root = $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }

# 1. Check & start backend
$backendRunning = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($backendRunning) {
    Write-Host "[OK] Backend is already running on port 8000." -ForegroundColor Green
} else {
    Write-Host "[1/2] Starting Backend on port 8000..." -ForegroundColor Yellow
    Start-Process -FilePath "$root\backend\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000" -WorkingDirectory "$root\backend" -WindowStyle Hidden
}

# 2. Check & start frontend
$frontendRunning = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($frontendRunning) {
    Write-Host "[OK] Frontend is already running on port 3000." -ForegroundColor Green
} else {
    Write-Host "[2/2] Starting Frontend on port 3000..." -ForegroundColor Yellow
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run dev" -WorkingDirectory "$root\frontend" -WindowStyle Hidden
}

Write-Host ""
Write-Host "Waiting for services to become ready..." -ForegroundColor Gray

# 3. Wait until http://localhost:3000 answers HTTP 200
$ready = $false
for ($i = 0; $i -lt 45; $i++) {
    Start-Sleep -Seconds 1
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 1
        if ($resp.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        # continue waiting
    }
}

if ($ready) {
    Write-Host "[OK] Ready! Opening http://localhost:3000 in your browser..." -ForegroundColor Green
} else {
    Write-Host "Opening http://localhost:3000..." -ForegroundColor Yellow
}

Start-Process "http://localhost:3000"
Start-Sleep -Seconds 2
