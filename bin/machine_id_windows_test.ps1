#!/usr/bin/env pwsh

function Write-Info {
    Write-Host "[INFO] $($args -join ' ')" -ForegroundColor Cyan
}

function Write-Warning {
    Write-Host "[WARN] $($args -join ' ')" -ForegroundColor Yellow
}

function Write-ErrorAndExit {
    Write-Host "[ERROR] $($args -join ' ')" -ForegroundColor Red
    exit 1
}

function Get-PythonPath {
    $python = $null

    try {
        $python3 = Get-Command python3 -ErrorAction SilentlyContinue
        if ($python3) {
            $version = & python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
            if ($version -ge 3.10) {
                return "python3"
            }
        }
    } catch {}

    try {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if ($python) {
            $version = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
            if ($version -ge 3.10) {
                return "python"
            }
        }
    } catch {}

    Write-ErrorAndExit "Python 3.10 or higher is required. Please install it from https://www.python.org/downloads/"
}

try {
    $python = Get-PythonPath
    $pythonScript = @'
import uuid, platform, subprocess, hashlib

def machine_id():
    commands = [
        ("UUID", "wmic csproduct get uuid"),
        ("CPU", "wmic cpu get processorid"),
        ("MB Serial", "wmic baseboard get serialnumber"),
    ]

    for name, cmd in commands:
        result = subprocess.check_output(cmd, shell=True).decode()
        print(f"\n{name}:\n{result}")

    return "success finished"

print(f"Machine ID: {machine_id()}")
'@

    $pythonScript | & $python -
} catch {
    Write-ErrorAndExit "Failed to generate machine ID: $_"
}
