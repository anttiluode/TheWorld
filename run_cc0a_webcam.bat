@echo off
setlocal

where python3.13 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python3.13 experiments\cc0a_webcam_gui.py %*
) else (
    python experiments\cc0a_webcam_gui.py %*
)

if errorlevel 1 pause
