# Crypto Universe — macOS Setup Guide (Non‑Technical)

This guide shows how to install and run Crypto Universe on macOS step by step. No coding knowledge required.

### 1) Prerequisites (install these once)
- Install Git: open Terminal and run `xcode-select --install` and follow prompts. Alternatively install Git via Homebrew.
- Install Node.js LTS: download the macOS installer from `https://nodejs.org` (LTS) and run it. Alternatively, install via Homebrew: `brew install node`.
- Install Python 3.10+ for macOS: download from `https://www.python.org/downloads/macos/` and run the installer. Alternatively, `brew install python@3.11` (or newer).
- Optional (only if you plan to use ADS profiles): install AdsPower from `https://adspower.com` and keep it running.

Tip: If you don’t have Homebrew yet, install it from `https://brew.sh` (optional).

### 2) Download the project
1. Open Terminal (Applications → Utilities → Terminal).
2. Choose a folder where you want the project (e.g., `~/Projects`).
3. Run:
```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/starling114/crypto-universe.git
cd crypto-universe
```

### 3) Install app dependencies (Node.js)
From the project folder (you should be in `.../crypto-universe`):
```bash
npm install
```
This installs the Node.js part of the application (web server and UI).

### 4) Set up Python environment (for automation modules)
1. Go to the `scripts` folder:
```bash
cd scripts
```
2. Create a virtual environment named `myenv`:
```bash
python -m venv myenv
```
3. Activate the environment (macOS):
```bash
source myenv/bin/activate
```
4. Install required Python packages:
```bash
pip install -r requirements.txt
```
Note: The app will automatically use `scripts/myenv/bin/python` when running modules.

### 5) Start the application
From the project root (`.../crypto-universe`) start the app:
```bash
cd ..
npm start
```
What happens:
- A local server starts on `http://localhost:3000`.
- Your browser will not open automatically; open it yourself and go to `http://localhost:3000`.

### 6) Using the app
- Navigate through the UI to select modules (e.g., Bridge, Swap, Transfer, etc.).
- When you click Start in the UI, the app runs the Python module in the background and streams live logs to the page.

### 7) Updating the app later
From the project root (`.../crypto-universe`):
```bash
git pull
npm install
```
Python requirements rarely change, but if they do:
```bash
cd scripts
source myenv/bin/activate
pip install -r requirements.txt
```
Then restart the app:
```bash
cd ..
npm start
```

### 8) Uninstall / clean up
- Stop the app (press Ctrl+C in the terminal running `npm start`).
- Delete the `crypto-universe` folder.

You’re all set! Open `http://localhost:3000` to use Crypto Universe on macOS.
