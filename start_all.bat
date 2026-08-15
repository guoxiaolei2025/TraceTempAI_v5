@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo TraceTempAI FastAPI + Vue Startup Script
echo ========================================
echo.

set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%venv"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"

echo [INFO] Checking virtual environment...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [WARNING] Creating virtual environment...
    python -m venv "%VENV_DIR%"
)
call "%VENV_DIR%\Scripts\activate.bat"

echo [INFO] Upgrading pip...
pip install --upgrade pip >nul 2>&1

echo [INFO] Installing backend dependencies...
pip install -r "%PROJECT_DIR%requirements.txt" >nul 2>&1

echo [INFO] Checking .env file...
if not exist "%BACKEND_DIR%\.env" (
    echo [INFO] Creating .env file...
    copy "%BACKEND_DIR%\.env.example" "%BACKEND_DIR%\.env" >nul 2>&1
    echo [WARNING] Please edit backend/.env and add your API keys!
)

echo.
echo ========================================
echo Starting Backend Service (FastAPI)
echo ========================================
echo Backend URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.

start "TraceTempAI Backend" cmd /k "cd /d "%BACKEND_DIR%" && call "%VENV_DIR%\Scripts\activate.bat" && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul 2>&1

echo.
echo ========================================
echo Starting Frontend Service (Vue)
echo ========================================
echo Frontend URL: http://localhost:5173
echo ========================================
echo.

start "TraceTempAI Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"

echo.
echo [INFO] Services started!
echo [INFO] Frontend: http://localhost:5173
echo [INFO] Backend API: http://localhost:8000
echo.
echo Press any key to exit...
pause >nul 2>&1
