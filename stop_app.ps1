Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Stopping AORL Services" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$ports = @(8000, 3000)
foreach ($p in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue
    if ($conns) {
        $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $pids) {
            if ($procId -gt 0) {
                Write-Host "Stopping process $procId on port $p..." -ForegroundColor Yellow
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

Write-Host ""
Write-Host "[OK] All AORL services have been stopped." -ForegroundColor Green
Start-Sleep -Seconds 2
