@echo off
echo ========================================
echo Personal Financial Management System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 18 or higher
    pause
    exit /b 1
)

echo Starting Personal Financial Management System...
echo.

REM Start backend in a new window
echo Starting Backend Server...
start "Financial Backend" cmd /k "cd /d %~dp0backend && if not exist venv (echo Creating virtual environment... && python -m venv venv) && venv\Scripts\activate && pip install -r requirements.txt && echo Backend server starting on http://localhost:8100 && python main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
echo Starting Frontend Server...
start "Financial Frontend" cmd /k "cd /d %~dp0frontend && if not exist node_modules (echo Installing dependencies... && npm install) && echo Frontend server starting on http://localhost:3100 && npm run dev"

echo.
echo ========================================
echo System is starting up...
echo.
echo Backend:  http://localhost:8100
echo Frontend: http://localhost:3100
echo API Docs: http://localhost:8100/api/docs
echo.
echo Press any key to open the application in your browser...
echo ========================================
pause >nul

REM Open browser
start http://localhost:3100

echo.
echo System is running!
echo Close this window to keep the system running.
echo To stop the system, close the Backend and Frontend windows.
echo.
pause