<#
.SYNOPSIS
    Builds the Android APK for YoutubeDownloader.

.EXAMPLE
    .\build_apk.ps1
    .\build_apk.ps1 -Arch arm64-v8a
    .\build_apk.ps1 -Clean          # wipe the flet build cache first
#>
param(
    [string]$Arch = "armeabi-v7a",
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# Prefer the project venv's flet, fall back to whatever is on PATH.
$flet = Join-Path $PSScriptRoot ".venv\Scripts\flet.exe"
if (-not (Test-Path $flet)) { $flet = "flet" }

# Force UTF-8 so the flet CLI doesn't crash on non-ASCII output.
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$fletArgs = @(
    "build", "apk",
    "--arch", $Arch,
    "--exclude", ".venv", ".git", ".github", ".dart_tool", "__pycache__", "build", ".claude", "dist",
    "--compile-app", "--compile-packages",
    "--cleanup-app", "--cleanup-packages",
    "--deep-linking-scheme", "https",
    "--deep-linking-host", "music.youtube.com"
)
if ($Clean) { $fletArgs += "--clear-cache" }

Write-Host "Building APK for $Arch ..." -ForegroundColor Cyan
& $flet @fletArgs
if ($LASTEXITCODE -ne 0) { throw "flet build failed (exit $LASTEXITCODE)" }

$src = Join-Path $PSScriptRoot "build\apk\app-release.apk"
$dst = Join-Path $PSScriptRoot "build\apk\YoutubeDownloader-$Arch.apk"
Copy-Item $src $dst -Force

$sizeMB = [math]::Round((Get-Item $dst).Length / 1MB, 1)
Write-Host ""
Write-Host "APK ready: $dst" -ForegroundColor Green
Write-Host "Size: $sizeMB MB" -ForegroundColor Green
