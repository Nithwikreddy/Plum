@echo off
REM Quick start script for local development (Windows)

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo OPD Claim Adjudication MVP - Quick Start
echo ==========================================
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker found
    
    REM Check if docker-compose is available
    docker-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Docker Compose found
        echo.
        echo Starting services with Docker Compose...
        echo.
        
        REM Build images
        echo Building Docker images...
        call docker-compose build
        
        REM Start services
        echo.
        echo Starting services...
        call docker-compose up -d
        
        echo.
        echo Waiting for services to start...
        timeout /t 10 /nobreak
        
        REM Check health
        echo.
        echo Checking service health...
        
        REM Check API
        powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 3 -ErrorAction Stop; Write-Host '[OK] API (http://localhost:8000) is running' } catch { Write-Host '[...] API starting...' }"
        
        echo.
        echo ==========================================
        echo Services Ready!
        echo ==========================================
        echo.
        echo Frontend: http://localhost:3000
        echo API: http://localhost:8000
        echo API Health: http://localhost:8000/health
        echo Database: localhost:5432 ^(opd_user/opd_password^)
        echo.
        echo Next steps:
        echo   1. Open http://localhost:3000 in your browser
        echo   2. Run tests: docker-compose exec api pytest tests/ -v
        echo   3. View logs: docker-compose logs -f
        echo   4. Stop services: docker-compose down
        echo.
        
        REM Open browser
        echo Opening http://localhost:3000 in browser...
        start http://localhost:3000
        
        goto :eof
    ) else (
        echo [ERROR] Docker Compose not found. Please install it.
        exit /b 1
    )
) else (
    echo [ERROR] Docker not found. Please install Docker Desktop.
    echo.
    echo For local development, install:
    echo   - Python 3.11+ from https://python.org
    echo   - Node.js 18+ from https://nodejs.org
    echo   - PostgreSQL 15 from https://postgresql.org
    echo.
    exit /b 1
)
