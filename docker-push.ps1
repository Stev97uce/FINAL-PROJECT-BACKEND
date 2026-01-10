# Script para build y push de imágenes Docker a DockerHub
# Uso: .\docker-push.ps1 [auth|user|all]

param(
    [Parameter(Position=0)]
    [ValidateSet("auth", "user", "all")]
    [string]$Service = "all"
)

$DOCKERHUB_USERNAME = if ($env:DOCKERHUB_USERNAME) { $env:DOCKERHUB_USERNAME } else { "tu-usuario" }

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "UCE Backend - Docker Build & Push" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

function Build-And-Push {
    param(
        [string]$ServiceName,
        [string]$Context,
        [string]$ImageName
    )
    
    Write-Host "Building $ServiceName..." -ForegroundColor Yellow
    docker build -t "$DOCKERHUB_USERNAME/${ImageName}:latest" $Context
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed for $ServiceName" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "`nPushing $ServiceName to DockerHub..." -ForegroundColor Yellow
    docker push "$DOCKERHUB_USERNAME/${ImageName}:latest"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Push failed for $ServiceName" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ $ServiceName pushed successfully!`n" -ForegroundColor Green
}

switch ($Service) {
    "auth" {
        Build-And-Push -ServiceName "Auth Service" -Context "./apps/Micro1_Auth_Service" -ImageName "uce-auth-service"
    }
    "user" {
        Build-And-Push -ServiceName "User Service" -Context "./apps/Micro2_User_Service" -ImageName "uce-user-service"
    }
    "all" {
        Build-And-Push -ServiceName "Auth Service" -Context "./apps/Micro1_Auth_Service" -ImageName "uce-auth-service"
        Build-And-Push -ServiceName "User Service" -Context "./apps/Micro2_User_Service" -ImageName "uce-user-service"
    }
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "All images pushed successfully!" -ForegroundColor Green
Write-Host "==========================================`n" -ForegroundColor Green
Write-Host "Verify at: https://hub.docker.com/u/$DOCKERHUB_USERNAME`n" -ForegroundColor Cyan
