@echo off
setlocal enabledelayedexpansion
title FinGenius Toolkit

:: Color codes for better display
set "BLUE=[94m"
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "RESET=[0m"

:: Set paths
set "SCRIPT_DIR=%~dp0"
set "APP_DIR=%SCRIPT_DIR%FING"
set "PYTHON_SCRIPT=%SCRIPT_DIR%fingenius_toolkit.py"

:: Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %RED%Error: Python not found in PATH.%RESET%
    echo Please ensure Python is installed and in your PATH.
    pause
    exit /b 1
)

:: Check if the toolkit script exists
if not exist "%PYTHON_SCRIPT%" (
    echo %RED%Error: Cannot find fingenius_toolkit.py%RESET%
    echo It should be in the same directory as this batch file.
    pause
    exit /b 1
)

:menu
cls
echo %BLUE%===============================================================%RESET%
echo %BLUE%                      FinGenius Toolkit                        %RESET%
echo %BLUE%===============================================================%RESET%
echo.
echo  [1] %GREEN%Run Application%RESET%
echo  [2] %GREEN%Install/Update Application%RESET%
echo  [3] %GREEN%Fix Database Issues%RESET%
echo  [4] %GREEN%Install OpenAI for DeepSeek Integration%RESET%
echo  [5] %GREEN%Install Anthropic for Claude Integration%RESET%
echo  [6] %GREEN%Install GTK for PDF Export%RESET%
echo  [7] %GREEN%Test DeepSeek Integration%RESET%
echo  [8] %GREEN%Test Claude Integration%RESET%
echo  [9] %GREEN%Test Environment Variables%RESET%
echo  [C] %YELLOW%Clean Installation%RESET%
echo  [Q] %RED%Quit%RESET%
echo.
echo %BLUE%===============================================================%RESET%
echo.

set /p choice="Enter your choice: "

if "%choice%"=="1" goto run_app
if "%choice%"=="2" goto install_app
if "%choice%"=="3" goto fix_db
if "%choice%"=="4" goto install_openai
if "%choice%"=="5" goto install_anthropic
if "%choice%"=="6" goto install_gtk
if "%choice%"=="7" goto test_deepseek
if "%choice%"=="8" goto test_claude
if "%choice%"=="9" goto test_env
if /i "%choice%"=="c" goto clean_app
if /i "%choice%"=="q" goto end
goto menu

:run_app
cls
echo %BLUE%===============================================================%RESET%
echo %BLUE%                     Running FinGenius                         %RESET%
echo %BLUE%===============================================================%RESET%
echo.
python "%PYTHON_SCRIPT%" run
pause
goto menu

:install_app
cls
echo %BLUE%===============================================================%RESET%
echo %BLUE%               Installing/Updating FinGenius                   %RESET%
echo %BLUE%===============================================================%RESET%
echo.
python "%PYTHON_SCRIPT%" install
pause
goto menu

:fix_db
cls
echo %BLUE%===============================================================%RESET%
echo %BLUE%                 Fixing Database Issues                        %RESET%
echo %BLUE%===============================================================%RESET%
echo.
python "%PYTHON_SCRIPT%" fix_db
pause
goto menu

:install_openai
cls
echo %BLUE%===============================================================%RESET%
echo %BLUE%           Install OpenAI SDK for DeepSeek                     %RESET%
echo %BLUE%===============================================================%RESET%
echo.
python "%PYTHON_SCRIPT%" install_openai
pause
goto menu

:install_anthropic
cls
echo %BLUE%===============================================================%RESET%
echo %BLUE%          Install Anthropic SDK for Claude 3                   %RESET%
echo %BLUE%===============================================================%RESET%
echo.
python "%PYTHON_SCRIPT%" install_anthropic
pause
goto menu

:install_gtk
cls
echo %BLUE%===============================================================%RESET%
echo %BLUE%             Install GTK for PDF Export                        %RESET%
echo %BLUE%===============================================================%RESET%
echo.
python "%PYTHON_SCRIPT%" install_gtk
pause
goto menu

:test_deepseek
cls
echo %BLUE%===============================================================%RESET%
echo %BLUE%               Test DeepSeek Integration                       %RESET%
echo %BLUE%===============================================================%RESET%
echo.
python "%PYTHON_SCRIPT%" test_deepseek
pause
goto menu

:test_claude
cls
echo %BLUE%===============================================================%RESET%
echo %BLUE%                Test Claude Integration                        %RESET%
echo %BLUE%===============================================================%RESET%
echo.
python "%PYTHON_SCRIPT%" test_claude
pause
goto menu

:test_env
cls
echo %BLUE%===============================================================%RESET%
echo %BLUE%            Test Environment Variables                         %RESET%
echo %BLUE%===============================================================%RESET%
echo.
python "%PYTHON_SCRIPT%" test_env
pause
goto menu

:clean_app
cls
echo %BLUE%===============================================================%RESET%
echo %BLUE%                 Clean Installation                            %RESET%
echo %BLUE%===============================================================%RESET%
echo.
python "%PYTHON_SCRIPT%" clean
pause
goto menu

:end
echo.
echo %BLUE%Thank you for using FinGenius Toolkit%RESET%
echo.
exit /b 0
