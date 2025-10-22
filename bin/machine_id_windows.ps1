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

    identifiers.append(platform.system())
    identifiers.append(platform.machine())

    try:
        if platform.system() == "Windows":
            result = subprocess.check_output(
                "wmic csproduct get uuid", shell=True, stderr=subprocess.DEVNULL
            ).decode()
            uuid_line = result.split("\n")[1].strip()
            if uuid_line and uuid_line.lower() not in ['', 'ffffffff-ffff-ffff-ffff-ffffffffffff']:
                identifiers.append(uuid_line)

            try:
                cpu_result = subprocess.check_output(
                    "wmic cpu get processorid", shell=True, stderr=subprocess.DEVNULL
                ).decode()
                cpu_id = cpu_result.split("\n")[1].strip()
                if cpu_id:
                    identifiers.append(cpu_id)
            except:
                pass

            try:
                mb_result = subprocess.check_output(
                    "wmic baseboard get serialnumber", shell=True, stderr=subprocess.DEVNULL
                ).decode()
                mb_serial = mb_result.split("\n")[1].strip()
                if mb_serial and mb_serial.lower() not in ['', 'to be filled by o.e.m.']:
                    identifiers.append(mb_serial)
            except:
                pass

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

    if len(identifiers) <= 2:
        mac = uuid.getnode()
        identifiers.append(str(mac))

    combined = "|".join(identifiers)
    machine_id = hashlib.sha256(combined.encode()).hexdigest()
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
