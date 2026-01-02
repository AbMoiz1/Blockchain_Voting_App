@echo off
echo ================================================
echo   BLOCKCHAIN VOTING SYSTEM - TEST RUNNER
echo ================================================
echo.
echo Installing test dependencies...
pip install -q hypothesis pytest

echo.
echo Running comprehensive test suite...
echo.
python run_tests.py

if errorlevel 1 (
    echo.
    echo Some tests failed. Please check the output above.
) else (
    echo.
    echo All tests passed successfully!
)

echo.
pause