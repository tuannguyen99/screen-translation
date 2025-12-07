@echo off
echo ========================================
echo Building Screen Translator EXE
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install PyInstaller if not installed
pip install pyinstaller

REM Build the exe
echo.
echo Building executable...
pyinstaller build.spec --clean

echo.
echo ========================================
echo Build complete!
echo.
echo The executable is located at:
echo   dist\ScreenTranslator.exe
echo.
echo NOTE: The user needs to have the Windows
echo Japanese OCR language pack installed:
echo   Add-WindowsCapability -Online -Name "Language.OCR~~~ja-JP~0.0.1.0"
echo ========================================
pause
