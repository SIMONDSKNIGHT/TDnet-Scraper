@echo off
REM Get the directory of the currently running script
set CURRENT_DIR=%~dp0

REM Change to the script's directory
cd /d "%CURRENT_DIR%"

REM (Optional) Activate the virtual environment, if any
REM call "%CURRENT_DIR%\venv\Scripts\activate.bat"

REM Run the Python script
python "%CURRENT_DIR%\main.py"