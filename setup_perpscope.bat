@echo off
setlocal

rem Always run from the folder containing this script.
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found.
    echo Please install Python 3.10 or newer and make sure "Add Python to PATH" is enabled.
    echo.
    pause
    exit /b 1
)

echo Installing PerpScope dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Dependency installation failed. Review the error above.
    echo.
    pause
    exit /b 1
)

echo.
echo Setup complete. You can now double-click run_perpscope.bat each day.
echo.
pause
exit /b 0
