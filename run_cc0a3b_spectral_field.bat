@echo off
setlocal
cd /d "%~dp0"
where python3.13 >nul 2>nul
if %errorlevel%==0 (
  python3.13 experiments\cc0a3b_local_spectral_field_fixednorm_gui.py
) else (
  python experiments\cc0a3b_local_spectral_field_fixednorm_gui.py
)
if errorlevel 1 pause
endlocal
