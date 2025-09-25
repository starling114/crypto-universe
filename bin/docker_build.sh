#!/bin/bash
set -e

DOCKER_USERNAME="starling114"
IMAGE_NAME="crypto-universe"
VERSION=${1:-"latest"}

echo "🐳 Building Docker image for Crypto Universe..."
echo "Image: $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"

docker build -t $DOCKER_USERNAME/$IMAGE_NAME:$VERSION .

echo "✅ Build completed successfully!"

if [ "$VERSION" != "latest" ]; then
    echo "🏷️  Tagging as latest..."
    docker tag $DOCKER_USERNAME/$IMAGE_NAME:$VERSION $DOCKER_USERNAME/$IMAGE_NAME:latest
fi

# echo ""
# echo "📤 Do you want to publish this image to Docker Hub? (y/N)"
# read -r response

# if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
#     echo "📤 Pushing to Docker Hub..."
#     docker push $DOCKER_USERNAME/$IMAGE_NAME:$VERSION
    
#     if [ "$VERSION" != "latest" ]; then
#         docker push $DOCKER_USERNAME/$IMAGE_NAME:latest
#     fi
    
#     echo "🎉 Successfully published $DOCKER_USERNAME/$IMAGE_NAME:$VERSION to Docker Hub!"
#     echo ""
#     echo "You can now run:"
#     echo "docker run --rm -p 3000:3000 -v ./scripts:/app/scripts --name crypto-universe $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
# else
  echo "🏠 Image built locally!"
  echo ""
  echo "You can now run:"
  echo "docker run --rm -p 3000:3000 -v ./scripts:/app/scripts --name crypto-universe $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
# fi
