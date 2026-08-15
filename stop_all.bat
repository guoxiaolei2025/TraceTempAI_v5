@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo TraceTempAI Stop Services Script
echo ========================================
echo.

echo [INFO] Stopping backend service (FastAPI)...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im uvicorn.exe >nul 2>&1

echo [INFO] Stopping frontend service (Vue)...
taskkill /f /im node.exe >nul 2>&1

echo.
echo [INFO] All services stopped!
echo.
echo Press any key to exit...
pause >nul 2>&1
