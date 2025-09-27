# Crypto Universe — Docker Setup Guide

This guide shows how to install and run Crypto Universe using Docker.

## Prerequisites

### Install Docker Desktop
1. Download Docker Desktop for Windows from: https://www.docker.com/products/docker-desktop/
2. Run the installer and follow the setup wizard
3. Restart your computer when prompted
4. Launch Docker Desktop and wait for it to start (you'll see the Docker icon in your system tray)

## Quick Start
These helper scripts will automatically create a `crypto-universe` folder on your Desktop, go into it, and then download and start the app for you.

### Windows
1. Open the Start Menu, search for `PowerShell`, and open it.
2. Copy and paste this line, then press `Enter`:
  ```powershell
  iwr https://raw.githubusercontent.com/starling114/crypto-universe/migration_to_docker/bin/setup_windows.ps1 | Invoke-Expression
  ```

#### Running the app again (after first setup)
Once you’ve already installed it, you don’t need to run the setup again. Just choose **one of these** methods:

- From folder:
  Open the `crypto-universe` folder on your Desktop and double-click the file `docker_run.ps1`.  
  (If Windows asks how to open it, choose `PowerShell`.)
- PowerShell:
  Open `crypto-universe` folder and run:
  ```powershell
  .\docker_run.ps1
  ```
- Docker Desktop application (might not properly get new updates):
  1. Open `Docker Desktop`  
  2. Go to `Containers`  
  3. Find `crypto-universe` in the list  
  4. Use the buttons to `Start`, `Stop`, or `Restart` the app

### MaOS
1. Open the `Terminal` app.
2. Copy and paste this line, then press `Enter`:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/starling114/crypto-universe/migration_to_docker/bin/setup_macos.sh | bash
   ```

#### Running the app again (after first setup)
Once you’ve already installed it, you don’t need to run the setup again. Just:

- Docker Desktop application:
  1. Open `Docker Desktop`  
  2. Go to `Containers`  
  3. Find `crypto-universe` in the list  
  4. Use the buttons to `Start`, `Stop`, or `Restart` the app
- Terminal app:
  Open `crypto-universe` folder and run:
  ```bash
  ./docker_run.sh
  ```

## AdsPower Setup

Ensure the following:

1. AdsPower is running on the host machine.
2. AdsPower API is enabled (default port `50325`).

Defaults and overrides:
- Default inside image: `ADSPOWER_PORT=50325` (works on Docker Desktop for Mac/Windows)
- You can override at runtime via Compose (`.env`) or with `-e ADSPOWER_PORT=...` in `docker run`.

