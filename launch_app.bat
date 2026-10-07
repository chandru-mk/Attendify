@echo off
title Attendify - Student Attendance Analysis
echo ===================================================
echo   Attendify - Student Attendance Analysis Desktop
echo ===================================================
echo Starting application server...

:: Check if port 8501 is already active
netstat -ano | findstr :8501 | findstr LISTENING >nul
if %ERRORLEVEL% equ 0 (
    echo Server is already active on port 8501.
) else (
    echo Starting Streamlit background engine...
    start /b python -m streamlit run app.py --server.headless true --server.port 8501
    echo Waiting for server initialization...
    timeout /t 3 /nobreak >nul
)

:: Launch in native window mode (without browser toolbars or URL bar)
echo Launching native desktop window...
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app=http://localhost:8501 --window-size=1280,820
) else if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://localhost:8501 --window-size=1280,820
) else (
    start http://localhost:8501
)

echo Done! Attendify is running.
