@echo off
echo ===========================================================
echo GTK/WeasyPrint Dependency Installer for Windows
echo ===========================================================
echo.
echo This script will install GTK3 for WeasyPrint PDF export functionality
echo.

echo Checking for Python...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python not found in PATH.
    echo Please ensure Python is installed and in your PATH.
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
python install_gtk_windows.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Installation via script failed. Opening GTK download page...
    start https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
    echo Please download and run the latest gtk3-runtime installer manually.
    echo After installation, restart your computer and try running the application again.
    pause
    exit /b 1
)

echo.
echo Installation completed. Please restart your application.
pause
