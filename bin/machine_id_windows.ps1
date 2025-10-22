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

    def is_valid_uuid(uuid_str: str) -> bool:
        if not uuid_str:
            return False

        uuid_str = uuid_str.lower().strip()
        invalid_patterns = [
            "ffffffff-ffff-ffff-ffff-ffffffffffff",
            "00000000-0000-0000-0000-000000000000",
            "to be filled",
            "unknown",
        ]
        return not any(pattern in uuid_str for pattern in invalid_patterns)

    try:
        if platform.system() == "Windows":
            try:
                result = (
                    subprocess.check_output(
                        "wmic csproduct get uuid", shell=True, stderr=subprocess.DEVNULL, timeout=5
                    )
                    .decode()
                    .strip()
                )

                lines = [l.strip() for l in result.split("\n") if l.strip()]
                if len(lines) > 1 and is_valid_uuid(lines[1]):
                    identifiers.append(lines[1])
            except Exception:
                try:
                    ps_cmd = 'powershell -Command "(Get-CimInstance -ClassName Win32_ComputerSystemProduct).UUID"'
                    result = (
                        subprocess.check_output(ps_cmd, shell=True, stderr=subprocess.DEVNULL, timeout=5)
                        .decode()
                        .strip()
                    )

                    if result and is_valid_uuid(result):
                        identifiers.append(result)
                except Exception:
                    pass

            try:
                cpu_result = (
                    subprocess.check_output(
                        "wmic cpu get processorid", shell=True, stderr=subprocess.DEVNULL, timeout=5
                    )
                    .decode()
                    .strip()
                )

                lines = [l.strip() for l in cpu_result.split("\n") if l.strip()]
                if len(lines) > 1 and lines[1]:
                    identifiers.append(lines[1])
            except Exception:
                try:
                    ps_cmd = 'powershell -Command "(Get-CimInstance -ClassName Win32_Processor).ProcessorId"'
                    result = (
                        subprocess.check_output(ps_cmd, shell=True, stderr=subprocess.DEVNULL, timeout=5)
                        .decode()
                        .strip()
                    )

                    if result:
                        identifiers.append(result)
                except Exception:
                    pass

            try:
                mb_result = (
                    subprocess.check_output(
                        "wmic baseboard get serialnumber", shell=True, stderr=subprocess.DEVNULL, timeout=5
                    )
                    .decode()
                    .strip()
                )

                lines = [l.strip() for l in mb_result.split("\n") if l.strip()]
                if len(lines) > 1 and is_valid_uuid(lines[1]):
                    identifiers.append(lines[1])
            except Exception:
                try:
                    ps_cmd = 'powershell -Command "(Get-CimInstance -ClassName Win32_BaseBoard).SerialNumber"'
                    result = (
                        subprocess.check_output(ps_cmd, shell=True, stderr=subprocess.DEVNULL, timeout=5)
                        .decode()
                        .strip()
                    )

                    if result and is_valid_uuid(result):
                        identifiers.append(result)
                except Exception:
                    pass

        elif platform.system() == "Linux":
            try:
                with open("/etc/machine-id", "r") as f:
                    identifiers.append(f.read().strip())
            except Exception:
                try:
                    with open("/sys/class/dmi/id/product_uuid", "r") as f:
                        identifiers.append(f.read().strip())
                except Exception:
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
