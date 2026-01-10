#!/bin/bash

# Script para build y push de imágenes Docker a DockerHub
# Uso: ./docker-push.sh [auth|user|all]

set -e

DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:-tu-usuario}"

echo "=========================================="
echo "UCE Backend - Docker Build & Push"
echo "=========================================="

build_and_push() {
    local service=$1
    local context=$2
    local image_name=$3
    
    echo ""
    echo "Building $service..."
    docker build -t $DOCKERHUB_USERNAME/$image_name:latest $context
    
    echo ""
    echo "Pushing $service to DockerHub..."
    docker push $DOCKERHUB_USERNAME/$image_name:latest
    
    echo "✅ $service pushed successfully!"
}

case "${1:-all}" in
    auth)
        build_and_push "Auth Service" "./apps/Micro1_Auth_Service" "uce-auth-service"
        ;;
    user)
        build_and_push "User Service" "./apps/Micro2_User_Service" "uce-user-service"
        ;;
    all)
        build_and_push "Auth Service" "./apps/Micro1_Auth_Service" "uce-auth-service"
        build_and_push "User Service" "./apps/Micro2_User_Service" "uce-user-service"
        ;;
    *)
        echo "Usage: $0 [auth|user|all]"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "All images pushed successfully!"
echo "=========================================="
echo ""
echo "Verify at: https://hub.docker.com/u/$DOCKERHUB_USERNAME"
