@echo off
REM Installation script for Windows

echo Installing Screen Translation Application...
echo.

REM Check py
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: py is not installed or not in PATH
    echo Please install py 3.8 or higher from https://www.py.org/
    pause
    exit /b 1
)

echo py found!
echo.

REM Create virtual environment (optional but recommended)
echo Creating virtual environment...
py -m venv venv
call venv\Scripts\activate.bat

REM Install requirements
echo Installing py packages...
pip install -r requirements.txt

echo.
echo ============================================
echo Installation complete!
echo ============================================
echo.
echo IMPORTANT: You also need to install Tesseract OCR:
echo 1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo 2. Install it and add to PATH
echo.
echo OPTIONAL: For offline translation, install Ollama:
echo 1. Download from: https://ollama.ai
echo 2. Run: ollama pull gemma
echo.
echo To run the application:
echo   py main.py
echo.
pause
