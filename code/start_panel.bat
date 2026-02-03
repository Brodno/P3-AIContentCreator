@echo off
echo Starting AI Content Factory v0.2 Panel...
echo Trying ports: 8502, 8503, 8504...
echo.
cd /d "%~dp0"

REM Try different ports until one works
python -m streamlit run app_v02.py --server.port 8503 2>nul
if errorlevel 1 (
    python -m streamlit run app_v02.py --server.port 8504
)

pause
