@echo off
REM RAG AI Agent - Configuration Backup Script (Windows)
REM This script creates backups of all configuration files and deployment settings

setlocal enabledelayedexpansion

REM Configuration
set "BACKUP_DIR=backups\%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_DIR=%BACKUP_DIR: =0%"
set "PROJECT_ROOT=%~dp0.."

echo 🔄 Starting configuration backup...
echo Backup directory: %BACKUP_DIR%

REM Create backup directory
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Backup Python backend configuration
echo 📦 Backing up backend configuration...
if exist "%PROJECT_ROOT%\requirements.txt" (
    copy "%PROJECT_ROOT%\requirements.txt" "%BACKUP_DIR%\" >nul 2>&1
    echo   ✅ Backed up: requirements.txt
) else (
    echo   ⚠️  requirements.txt not found
)

if exist "%PROJECT_ROOT%\Dockerfile" (
    copy "%PROJECT_ROOT%\Dockerfile" "%BACKUP_DIR%\" >nul 2>&1
    echo   ✅ Backed up: Dockerfile
) else (
    echo   ⚠️  Dockerfile not found
)

if exist "%PROJECT_ROOT%\render.yaml" (
    copy "%PROJECT_ROOT%\render.yaml" "%BACKUP_DIR%\" >nul 2>&1
    echo   ✅ Backed up: render.yaml
) else (
    echo   ⚠️  render.yaml not found
)

if exist "%PROJECT_ROOT%\.env.example" (
    copy "%PROJECT_ROOT%\.env.example" "%BACKUP_DIR%\" >nul 2>&1
    echo   ✅ Backed up: .env.example
) else (
    echo   ⚠️  .env.example not found
)

REM Backup frontend configuration
echo 📦 Backing up frontend configuration...
if exist "%PROJECT_ROOT%\agent-frontend\package.json" (
    copy "%PROJECT_ROOT%\agent-frontend\package.json" "%BACKUP_DIR%\" >nul 2>&1
    echo   ✅ Backed up: package.json
) else (
    echo   ⚠️  package.json not found
)

if exist "%PROJECT_ROOT%\agent-frontend\package-lock.json" (
    copy "%PROJECT_ROOT%\agent-frontend\package-lock.json" "%BACKUP_DIR%\" >nul 2>&1
    echo   ✅ Backed up: package-lock.json
) else (
    echo   ⚠️  package-lock.json not found
)

if exist "%PROJECT_ROOT%\agent-frontend\vite.config.js" (
    copy "%PROJECT_ROOT%\agent-frontend\vite.config.js" "%BACKUP_DIR%\" >nul 2>&1
    echo   ✅ Backed up: vite.config.js
) else (
    echo   ⚠️  vite.config.js not found
)

if exist "%PROJECT_ROOT%\agent-frontend\vercel.json" (
    copy "%PROJECT_ROOT%\agent-frontend\vercel.json" "%BACKUP_DIR%\" >nul 2>&1
    echo   ✅ Backed up: vercel.json
) else (
    echo   ⚠️  vercel.json not found
)

REM Create backup manifest
echo 📝 Creating backup manifest...
(
echo RAG AI Agent Configuration Backup
echo ================================
echo.
echo Backup created: %date% %time%
echo Backup directory: %BACKUP_DIR%
echo.
echo Files included:
dir /b "%BACKUP_DIR%"
echo.
echo System information:
echo - OS: Windows
echo - Python version: 
python --version 2>nul || echo Python not found
echo - Node.js version: 
node --version 2>nul || echo Node.js not found
echo - npm version: 
npm --version 2>nul || echo npm not found
echo.
echo Notes:
echo - This backup contains configuration files only
echo - Environment variables and secrets are NOT included
echo - Vector database data requires separate backup ^(use backup_pinecone.py^)
) > "%BACKUP_DIR%\manifest.txt"

echo.
echo ✅ Configuration backup completed successfully!
echo 📁 Backup location: %BACKUP_DIR%
echo 💾 To restore from this backup, use: scripts\restore_config.bat %BACKUP_DIR%

pause