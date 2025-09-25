@echo off

echo 🐳 Starting Crypto Universe with Docker Hub...

if not exist "scripts" mkdir scripts
if not exist "backend" mkdir backend

docker ps -aq -f name=crypto-universe >nul 2>&1
if %errorlevel% equ 0 (
    echo 🛑 Stopping existing container...
    docker stop crypto-universe
    docker rm crypto-universe
)

echo 🚀 Starting new container with configuration persistence...
docker run -d -p 3000:3000 -v ./scripts:/app/scripts -v ./backend:/app/backend --name crypto-universe starling114/crypto-universe:latest

echo ✅ Crypto Universe is starting up!
echo 🌐 Open your browser and go to: http://localhost:3000
echo.
echo 📁 Your configurations will be saved in: ./scripts/ and ./backend/
echo 🔄 To update: run this script again
echo 📋 To view logs: docker logs crypto-universe

pause
