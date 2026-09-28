@echo off
title NeuroLearn AI Launcher
echo ========================================================
echo               NeuroLearn AI One-Click Launcher
echo ========================================================
echo.
echo Starting Flask Backend Server (Port 5000)...
start "NeuroLearn Backend Server" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe app.py"

echo Waiting for Backend to initialize...
timeout /t 3 /nobreak >nul

echo Starting Frontend Web Dashboard (Port 3000)...
start "NeuroLearn Frontend Server" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Waiting for Frontend to initialize...
timeout /t 3 /nobreak >nul

echo Opening NeuroLearn AI in your default web browser...
start http://localhost:3000

echo.
echo ========================================================
echo [SUCCESS] NeuroLearn AI is now running!
echo - Frontend: http://localhost:3000
echo - Backend:  http://localhost:5000
echo.
echo Simply keep the two server command windows open while using the app.
echo ========================================================
pause
