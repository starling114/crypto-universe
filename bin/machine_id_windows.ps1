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
    identifiers = []

    mac = uuid.getnode()
    identifiers.append(str(mac))

    identifiers.append(platform.system())
    identifiers.append(platform.machine())

    try:
        if platform.system() == "Windows":
            result = subprocess.check_output(
                "wmic csproduct get uuid", shell=True, stderr=subprocess.DEVNULL
            ).decode()
            uuid_line = result.split("\n")[1].strip()
            if uuid_line:
                identifiers.append(uuid_line)

        elif platform.system() == "Linux":
            try:
                with open("/etc/machine-id", "r") as f:
                    identifiers.append(f.read().strip())
            except:
                try:
                    with open("/sys/class/dmi/id/product_uuid", "r") as f:
                        identifiers.append(f.read().strip())
                except:
                    pass

        elif platform.system() == "Darwin":
            result = subprocess.check_output(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], stderr=subprocess.DEVNULL
            ).decode()
            for line in result.split("\n"):
                if "IOPlatformUUID" in line:
                    uuid_val = line.split('"')[3]
                    identifiers.append(uuid_val)
                    break
    except Exception:
        pass

    combined = "|".join(identifiers)
    machine_id = hashlib.sha256(combined.encode()).hexdigest()
    # Take first 32 characters for readability
    short_id = machine_id[:32].upper()
    group_size = 4
    groups = [short_id[i : i + group_size] for i in range(0, len(short_id), group_size)]
    return "-".join(groups)

print(f"Machine ID: {machine_id()}")
'@

    $pythonScript | & $python -
} catch {
    Write-ErrorAndExit "Failed to generate machine ID: $_"
}
