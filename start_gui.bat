@echo off
echo ================================================
echo   BLOCKCHAIN VOTING SYSTEM - DESKTOP GUI
echo ================================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Installing required packages...
pip install -q hypothesis pytest

echo.
echo Starting Blockchain Voting System...
echo.
python run_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start the application
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo Application closed successfully
pause