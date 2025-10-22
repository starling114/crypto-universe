#!/usr/bin/env bash

set -euo pipefail

info() { echo "[INFO] $*" ; }
warn() { echo "[WARN] $*" ; }
err()  { echo "[ERROR] $*" 1>&2 ; exit 1 ; }

ensure_python() {
  if command -v python3 >/dev/null 2>&1; then
    PY=python3
  elif command -v python >/dev/null 2>&1; then
    PY=python
  else
    err "Python 3 is not installed. Please install Python 3.10 or higher from https://www.python.org/downloads/ and try again."
  fi

  if "$PY" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    PY_VER=$("$PY" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
  else
    CUR_VER=$("$PY" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null || echo "unknown")
    err "Your Python version ($CUR_VER) is too old. Please install Python 3.10 or higher from https://www.python.org/downloads/ and try again."
  fi
}

ensure_python

"$PY" - <<'EOF'
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
EOF
