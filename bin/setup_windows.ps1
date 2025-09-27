$ErrorActionPreference = "Stop"

$DesktopDir = [Environment]::GetFolderPath("Desktop")
$TargetDir = Join-Path $DesktopDir "crypto-universe"

Write-Output "🐳 Preparing Crypto Universe setup..."

if (-not (Test-Path -Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir | Out-Null
}
Set-Location $TargetDir

Write-Output "📁 Using Desktop at: $DesktopDir"
Write-Output "📂 Working directory: $TargetDir"

$ScriptUrl = "https://raw.githubusercontent.com/starling114/crypto-universe/migration_to_docker/bin/docker_run.ps1"
$ScriptFile = "docker_run.ps1"

Write-Output "⬇️  Downloading docker_run.ps1..."

Invoke-WebRequest -Uri $ScriptUrl -OutFile $ScriptFile -UseBasicParsing

Write-Output "🚀 Running docker_run.ps1..."
& ".\$ScriptFile"