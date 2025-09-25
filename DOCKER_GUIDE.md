# Crypto Universe — Docker Setup Guide

This guide shows how to install and run Crypto Universe using Docker.

## Prerequisites

### Install Docker Desktop
1. Download Docker Desktop for Windows from: https://www.docker.com/products/docker-desktop/
2. Run the installer and follow the setup wizard
3. Restart your computer when prompted
4. Launch Docker Desktop and wait for it to start (you'll see the Docker icon in your system tray)

## Quick Start

### Method 1: Using Helper Script (Easiest)
1. Download the helper script:
   - **Windows**: Download `bin/docker-run.bat` and double-click it
   - **Mac/Linux**: Download `bin/docker-run.sh` and run: `chmod +x docker-run.sh && ./docker-run.sh`

### Method 2: Manual Command
1. Open Command Prompt or PowerShell
2. Create a directory for your configurations:
```bash
mkdir crypto-universe
cd crypto-universe
```
1. Run this command (includes volume mounting for persistence):
```bash
docker run -d -p 3000:3000 \
  -v ./scripts:/app/scripts \
  -v ./backend:/app/backend \
  --name crypto-universe \
  starling114/crypto-universe:latest
```
1. Open your browser and go to: http://localhost:3000

## AdsPower Configuration

Make sure:

1. **AdsPower is running** on your host machine
2. **AdsPower API is enabled** (usually on port 50325)
3. **The container is pre-configured** to connect to AdsPower automatically

### Docker Desktop Not Starting
- Make sure Windows Hyper-V is enabled
- Check that virtualization is enabled in BIOS
- Try running Docker Desktop as Administrator

### Container Won't Start
Check the logs for errors:
```bash
docker logs crypto-universe
```

### Permission Issues
If you encounter permission issues, try running Command Prompt as Administrator.
