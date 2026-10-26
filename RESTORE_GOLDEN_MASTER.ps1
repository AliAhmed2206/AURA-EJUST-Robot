# AURA-EJUST — Golden Master v2.0 PowerShell Restoration Engine
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$backupDir = Join-Path $root "GOLDEN_MASTER_BACKUP_v2.0"

Write-Host "Checking Golden Master archive at: $backupDir" -ForegroundColor Cyan

if (-not (Test-Path $backupDir)) {
    Write-Error "Backup directory not found at $backupDir!"
    exit 1
}

$filesToRestore = @(
    "index.html",
    "Antigravity_Local_Relay_Bridge.py",
    "vercel.json",
    "README.md",
    "Start_Antigravity_Local_Relay_Bridge.bat",
    "ejust_logo.png",
    "aura_concept1_pixar_soul.jpg",
    "aura_concept2_cyber_aperture.jpg",
    "aura_concept3_nordic_capsule.jpg",
    "aura_concept4_japan_star_mecha.jpg"
)

$dirsToRestore = @(
    "Firmware",
    "api",
    "docs",
    "WebApp_Screen"
)

foreach ($f in $filesToRestore) {
    $src = Join-Path $backupDir $f
    $dst = Join-Path $root $f
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Force
        Write-Host "  [RESTORED FILE] $f" -ForegroundColor Green
    }
}

foreach ($d in $dirsToRestore) {
    $src = Join-Path $backupDir $d
    $dst = Join-Path $root $d
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Recurse -Force
        Write-Host "  [RESTORED DIR]  $d" -ForegroundColor Green
    }
}

# Verify file hashes after restore
$h1 = (Get-FileHash (Join-Path $root "index.html")).Hash
$h2 = (Get-FileHash (Join-Path $root "docs\index.html")).Hash
$h3 = (Get-FileHash (Join-Path $root "WebApp_Screen\index.html")).Hash

if ($h1 -eq $h2 -and $h2 -eq $h3) {
    Write-Host "`nAll index.html targets verified 100% synchronized (Hash: $h1)" -ForegroundColor Cyan
} else {
    Write-Warning "Hash mismatch between index files. Resynchronizing..."
    Copy-Item (Join-Path $root "index.html") (Join-Path $root "docs\index.html") -Force
    Copy-Item (Join-Path $root "index.html") (Join-Path $root "WebApp_Screen\index.html") -Force
}

Write-Host "`nGolden Master v2.0 restoration successfully finished!`n" -ForegroundColor Yellow
