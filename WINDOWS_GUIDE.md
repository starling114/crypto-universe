# Crypto Universe — Windows Setup Guide (Non‑Technical)

This guide shows how to install and run Crypto Universe on Windows step by step. No coding knowledge required.

### 1) Prerequisites (install these once)
- Install Git: download from `https://git-scm.com/download/win` → run installer → keep defaults.
- Install Node.js LTS: download from `https://nodejs.org` (LTS) → run installer → keep defaults.
- Install Python 3.10+ for Windows: download from `https://www.python.org/downloads/windows/` → during install, check “Add Python to PATH”.
- Optional (only if you plan to use ADS profiles): install AdsPower from `https://adspower.com` and keep it running.

### 2) Download the project
1. Open Start → type "Command Prompt" → open it.
2. Choose a folder where you want the project (e.g., `C:\Users\YourName\Projects`).
3. Run:
```bash
cd C:\Users\YourName\Projects
git clone https://github.com/starling114/crypto-universe.git
cd crypto-universe
```

### 3) Install app dependencies (Node.js)
From the project folder (you should be in `...\crypto-universe`):
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
3. Activate the environment (Windows):
```bash
myenv\Scripts\activate
```
4. Install required Python packages:
```bash
pip install -r requirements.txt
```

### 5) Start the application
From the project root (`...\crypto-universe`) start the app:
```bash
npm start
```
What happens:
- A local server starts on `http://localhost:3000`.
- Your browser will not open automatically; open it yourself and go to `http://localhost:3000`.

Windows firewall: If Windows asks to allow access, click “Allow access”.

### 6) Using the app
- Navigate through the UI to select modules (e.g., Bridge, Swap, Transfer, etc.).
- When you click Start in the UI, the app runs the Python module in the background and streams live logs to the page.

### 7) Updating the app later
From the project root (`...\crypto-universe`):
```bash
git pull
```
Then start the app:
```bash
npm start
```

### 8) Uninstall / clean up
- Stop the app (press Ctrl+C in the terminal running `npm start`).
- Delete the `crypto-universe` folder.
- Optionally remove Node.js/Python if you installed them only for this.

You’re all set! Open `http://localhost:3000` to use Crypto Universe on Windows.
