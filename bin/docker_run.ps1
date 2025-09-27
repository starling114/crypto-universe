Write-Output "🐳 Starting Crypto Universe with Docker Hub..."

if (-not (Test-Path -Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
}

$container = docker ps -aq -f name=crypto-universe

if ($container) {
    Write-Output "🛑 Stopping existing container..."
    docker stop crypto-universe | Out-Null
    docker rm crypto-universe | Out-Null
}

Write-Output "🚀 Starting new container with configuration persistence..."
docker run -d -p 3000:3000 -v ./data:/data --name crypto-universe starling114/crypto-universe:latest | Out-Null

Write-Output "✅ Crypto Universe is starting up!"
Write-Output "🌐 Open your browser and go to: http://localhost:3000"
Write-Output ""
Write-Output "📁 Your data and configs will be saved in: ./data/"
Write-Output "🔄 To update: run this script again"
Write-Output "📋 To view logs: docker logs crypto-universe"

Pause
