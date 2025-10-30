# Crypto Universe — Windows Setup Guide

This guide explains how to install and run Crypto Universe on Windows step by step. It is written for non‑technical users.

## Prerequisites
- Git
  - Download from https://git-scm.com/download/win and install (keep defaults).
- Node.js (LTS)
  - Download from https://nodejs.org and install (LTS, keep defaults).
- Python 3.10.11
  - Download from https://www.python.org/downloads/release/python-31011/ and install.
  - During install, check “Add Python to PATH”.

## Quick Setup (Recommended)
If you already have Git, Node.js, and Python 3.10.11 installed, run this single command in PowerShell to perform the initial install:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "iwr -UseBasicParsing https://raw.githubusercontent.com/starling114/crypto-universe/refs/heads/main/bin/setup_windows.ps1 | iex"
```

And then start application via `CU` shortcut on desktop.

What this does (one-time):
- Clones or updates the project at `C:\Users\YourName\Desktop\crypto-universe`.
- Installs Node and Python project dependencies.

### Machine ID
To get your Machine ID, run this single command in PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "iwr -UseBasicParsing https://raw.githubusercontent.com/starling114/crypto-universe/refs/heads/main/bin/machine_id_windows.ps1 | iex"
```

### After initial setup
- To start the app click `CU` shortcut on desktop
- To update the app click `update.sh` file in `C:\Users\YourName\Desktop\crypto-universe\bin`

## Troubleshooting
- Node/Python not found: install them from the links in Prerequisites and restart PowerShell.
- Python version too old: install Python 3.10+.
- ExecutionPolicy errors: start PowerShell as Administrator or use the one‑liner (it bypasses policy for the current process only).

## Uninstall / Clean up
- Stop the app (Ctrl+C in the terminal running `npm start`).
- Delete the folder `C:\Users\YourName\Desktop\crypto-universe`.
