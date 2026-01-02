@echo off
echo ================================================
echo   BLOCKCHAIN VOTING SYSTEM - SETUP
echo ================================================
echo.
echo This will create a virtual environment and install dependencies
echo.
pause

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete! Virtual environment is now active.
echo.
echo Available commands:
echo   python run_gui.py     - Start the voting application
echo   python run_tests.py   - Run system tests
echo   deactivate           - Exit virtual environment
echo.
echo To reactivate later, run: venv\Scripts\activate.bat
echo.