@echo off
title BTC Dashboard — Setup ^& Launch
color 0A

echo.
echo  =============================================
echo   BTC Live Dashboard  ^|  Setup ^& Launch
echo  =============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found. Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo  [1/3] Installing dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to install dependencies. Try: pip install -r requirements.txt
    pause
    exit /b 1
)

echo  [2/3] Dependencies installed.
echo.
echo  [3/3] Launching dashboard at http://localhost:8501
echo.
echo  -----------------------------------------------
echo   Press Ctrl+C to stop the dashboard
echo  -----------------------------------------------
echo.

streamlit run btc_dashboard.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

pause
