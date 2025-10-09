#!/usr/bin/env pwsh

$ErrorActionPreference = 'Stop'

$RepoUrl   = 'https://github.com/starling114/crypto-universe.git'
$Desktop   = [Environment]::GetFolderPath('Desktop')
$TargetDir = Join-Path $Desktop 'crypto-universe'

function Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Warn($msg) { Write-Host "[WARNING] $msg" -ForegroundColor Yellow }
function Err ($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }

function Need-Cmd($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    Err "$name is not installed or not in PATH. Please install it and try again."
  }
}

function Ensure-Node {
  Need-Cmd node
  Need-Cmd npm
  $nodeVer = (node -v) 2>$null
  $npmVer  = (npm -v) 2>$null
  Info "Node.js $nodeVer and npm $npmVer detected"
}

function Ensure-Python {
  $global:PY = $null
  if (Get-Command python -ErrorAction SilentlyContinue) {
    $global:PY = 'python'
  }
  if (-not $global:PY) { Err 'Python is not installed. Please install Python 3.10+ from https://www.python.org/downloads/ and try again.' }

  & $global:PY -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) {
    $cur = & $global:PY -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
    Err "Your Python version ($cur) is too old. Please install Python 3.10+ from https://www.python.org/downloads/."
  }
  $pyVer = & $global:PY -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
  Info "Python $pyVer detected (>= 3.10)"
}

Need-Cmd git
Ensure-Node
Ensure-Python

if (Test-Path (Join-Path $TargetDir '.git')) {
  Info "Found existing project at $TargetDir. Updating..."
  try {
    Push-Location $TargetDir
    $stdout = [System.IO.Path]::GetTempFileName()
    $stderr = [System.IO.Path]::GetTempFileName()
    
    Info 'Resetting to main branch...'
    
    $fetch = Start-Process -FilePath 'git' -ArgumentList 'fetch','--all' -WorkingDirectory $TargetDir -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if ($fetch.ExitCode -ne 0) {
      $errMsg = try { Get-Content -Raw -ErrorAction SilentlyContinue $stderr } catch { 'Unknown error' }
      Err "Failed to fetch from remote: $errMsg"
    }
    
    $stash = Start-Process -FilePath 'git' -ArgumentList 'stash','--include-untracked' -WorkingDirectory $TargetDir -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if ($stash.ExitCode -eq 0) {
      $stashed = $true
      Info 'Stashed local changes before reset.'
    }
    
    $checkout = Start-Process -FilePath 'git' -ArgumentList 'checkout','--force','main' -WorkingDirectory $TargetDir -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if ($checkout.ExitCode -ne 0) {
      $errMsg = try { Get-Content -Raw -ErrorAction SilentlyContinue $stderr } catch { 'Unknown error' }
      Err "Failed to checkout main branch: $errMsg"
    }
    
    $reset = Start-Process -FilePath 'git' -ArgumentList 'reset','--hard','origin/main' -WorkingDirectory $TargetDir -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if ($reset.ExitCode -ne 0) {
      $errMsg = try { Get-Content -Raw -ErrorAction SilentlyContinue $stderr } catch { 'Unknown error' }
      Err "Failed to reset to origin/main: $errMsg"
    }
    
    $clean = Start-Process -FilePath 'git' -ArgumentList 'clean','-fd' -WorkingDirectory $TargetDir -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if ($clean.ExitCode -ne 0) {
      $errMsg = try { Get-Content -Raw -ErrorAction SilentlyContinue $stderr } catch { 'Unknown error' }
      Warn "Warning: Failed to clean untracked files: $errMsg"
    }
  } finally { Pop-Location }
}
else {
  Info "Cloning repository to $TargetDir ..."
  New-Item -ItemType Directory -Force -Path (Split-Path $TargetDir) | Out-Null
  git clone $RepoUrl $TargetDir | Out-Null
}

Info 'Installing Node.js dependencies (npm install) ...'
try {
  Push-Location $TargetDir
  npm install
} catch {
  Err 'Failed to install Node.js dependencies. Please check your internet connection or Node.js installation.'
} finally { Pop-Location }

$ScriptsDir = Join-Path $TargetDir 'scripts'
$VenvDir    = Join-Path $ScriptsDir 'myenv'
${PipPath}  = Join-Path (Join-Path $VenvDir 'Scripts') 'pip.exe'

Info 'Setting up Python virtual environment in scripts\myenv ...'
if (-not (Test-Path $VenvDir)) {
  try {
    Push-Location $ScriptsDir
    & $global:PY -m venv 'myenv'
  } catch {
    Err 'Failed to create Python virtual environment.'
  } finally { Pop-Location }
}

$Activate = Join-Path (Join-Path $VenvDir 'Scripts') 'Activate.ps1'
if (Test-Path $Activate) {
  try {
    . $Activate
    Info 'Virtual environment activated.'
  } catch {
    Warn 'Failed to activate virtual environment. Falling back to direct pip path.'
  }
} else {
  Warn 'Activate.ps1 not found. Falling back to direct pip path.'
}

if (Get-Command pip -ErrorAction SilentlyContinue) {
  Info 'Upgrading pip and installing Python requirements (activated environment) ...'
  pip install --upgrade pip
  pip install -r (Join-Path $ScriptsDir 'requirements.txt')
}
elseif (Test-Path $PipPath) {
  Info 'Upgrading pip and installing Python requirements (direct path) ...'
  & $PipPath install --upgrade pip
  & $PipPath install -r (Join-Path $ScriptsDir 'requirements.txt')
}
else {
  Err "pip not found in virtual environment at $PipPath"
}

try {
    $ShortcutPath = Join-Path $Desktop 'CU.lnk'
    $StartSh = Join-Path $TargetDir 'bin\start.sh'
    $IconPath = Join-Path $TargetDir 'frontend\public\logo.ico'
    $GitBashCands = @(
        'C:\Program Files\Git\bin\bash.exe',
        'C:\Program Files\Git\usr\bin\bash.exe',
        (Get-Command 'bash.exe' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
    )

    if (-not (Test-Path $StartSh)) {
        throw "start.sh not found at $StartSh"
    }
    $gitBash = $GitBashCands | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
    if (-not $gitBash) {
        throw "Git Bash not found. Ensure Git is installed."
    }

    if (Test-Path $ShortcutPath) {
        try {
            Remove-Item -Path $ShortcutPath -Force
        }
        catch {
            Write-Warning "Failed to delete existing shortcut: $ShortcutPath. Error: $_"
        }
    }

    $wsh = New-Object -ComObject WScript.Shell
    $sc = $wsh.CreateShortcut($ShortcutPath)
    $sc.TargetPath = $gitBash
    $relativeShPath = $StartSh -replace ([regex]::Escape($TargetDir + '\')), '' -replace '\\', '/'
    $sc.Arguments = "-c `"./$relativeShPath`""
    $sc.WorkingDirectory = $TargetDir
    $sc.IconLocation = if (Test-Path $IconPath) { "$IconPath, 0" } else { 'C:\Windows\System32\shell32.dll, 167' }
    $sc.Save()

    Write-Information "Created Desktop shortcut for start.sh: $ShortcutPath" -InformationAction Continue
} catch {
  Warn "Failed to create Desktop shortcut: $_"
}

Info 'Setup/update complete.'
