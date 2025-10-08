# Crypto Universe — macOS Setup Guide

This guide explains how to install and run Crypto Universe on macOS step by step. It is written for non‑technical users.

## Prerequisites
- Git
  - Open Terminal and run: `xcode-select --install` and follow prompts. (Alternative via Homebrew: `brew install git`)
- Node.js (LTS)
  - Download from https://nodejs.org and install (LTS). (Alternative via Homebrew: `brew install node`)
- Python 3.10+
  - Download from https://www.python.org/downloads/macos/ and install. (Alternative via Homebrew: `brew install python@3.11`)

Tip: If you don’t have Homebrew, get it from https://brew.sh (optional).

## Quick Setup (Recommended)
If you already have Git, Node.js, and Python 3.10+ installed, run this single command in Terminal to perform the initial install:

```bash
curl -fsSL https://raw.githubusercontent.com/starling114/crypto-universe/refs/heads/main/bin/setup.sh | bash
```
What this does (one-time):
- Clones or updates the project at `~/Desktop/crypto-universe`.
- Installs Node and Python project dependencies.

### After initial setup
- Start the app:
  - Double-click `Desktop/crypto-universe/bin/start.sh`
  - Or from Terminal in the project folder: `./bin/start.sh` or `npm start`
- Update the app:
  - Double-click `Desktop/crypto-universe/bin/setup.sh`
  - Or run from Terminal in the project folder: `./bin/setup.sh`

Tip: If double-click doesn’t run in Terminal, right‑click the file and choose “Open With” → Terminal.

## Troubleshooting
- Node/Python not found: install them from the links in Prerequisites and close/reopen Terminal.
- Python version too old: install Python 3.10+.
- Permission errors creating folders: ensure your user can write to `~/Desktop`.

## Uninstall / Clean up
- Stop the app (Ctrl+C in the terminal running `npm start`).
- Delete the folder `~/Desktop/crypto-universe`.
