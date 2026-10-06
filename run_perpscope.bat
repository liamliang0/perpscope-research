@echo off
setlocal

rem Always run from the folder containing this script.
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found.
    echo Please install Python 3.10 or newer, then double-click setup_perpscope.bat.
    echo.
    pause
    exit /b 1
)

python -c "import requests, dotenv" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: PerpScope dependencies are missing.
    echo Please double-click setup_perpscope.bat once, then try again.
    echo.
    pause
    exit /b 1
)

echo Running PerpScope...
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: PerpScope did not finish successfully. Review the error above.
    echo.
    pause
    exit /b 1
)

if not exist "output\daily_report.md" (
    echo.
    echo ERROR: PerpScope finished, but output\daily_report.md was not found.
    echo.
    pause
    exit /b 1
)

echo.
echo PerpScope finished successfully. Opening the report...
start "" notepad.exe "%CD%\output\daily_report.md"
exit /b 0
