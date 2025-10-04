@echo off
REM MetaWipe - Windows Setup Script
REM This script helps you install all dependencies on Windows

echo ============================================================
echo    METAWIPE - Windows Setup and Installation Helper
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Install Python dependencies
echo [1/3] Installing Python packages...
echo.
pip install pillow pypdf python-docx mutagen openpyxl
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Some packages failed to install
    echo Try running this script as Administrator
    echo.
)
echo.

REM Check for exiftool
echo [2/3] Checking for exiftool...
exiftool -ver >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] exiftool not found
    echo.
    echo To install exiftool on Windows:
    echo 1. Download from: https://exiftool.org/
    echo 2. Extract the ZIP file
    echo 3. Rename 'exiftool(-k).exe' to 'exiftool.exe'
    echo 4. Either:
    echo    - Place exiftool.exe in the same folder as clean_metadata.py
    echo    - Or add its location to your PATH environment variable
    echo.
    echo Press any key to open the download page...
    pause >nul
    start https://exiftool.org/
) else (
    echo [OK] exiftool is installed
    exiftool -ver
)
echo.

REM Check for ffmpeg
echo [3/3] Checking for ffmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] ffmpeg not found
    echo.
    echo To install ffmpeg on Windows:
    echo 1. Download from: https://ffmpeg.org/download.html
    echo    Recommended: https://www.gyan.dev/ffmpeg/builds/
    echo 2. Extract the ZIP file
    echo 3. Add the 'bin' folder to your PATH environment variable
    echo.
    echo Press any key to open the download page...
    pause >nul
    start https://www.gyan.dev/ffmpeg/builds/
) else (
    echo [OK] ffmpeg is installed
    ffmpeg -version | findstr "ffmpeg version"
)
echo.

echo ============================================================
echo                   SETUP COMPLETE
echo ============================================================
echo.
echo You can now run MetaWipe with:
echo   python clean_metadata.py --help
echo.
echo For maximum privacy, use:
echo   python clean_metadata.py --backup --reencode-videos --normalize-time
echo.
echo Quick examples:
echo   python clean_metadata.py --dry-run          (preview only)
echo   python clean_metadata.py --backup           (with backups)
echo   python clean_metadata.py --path "C:\Photos" (specific folder)
echo.
pause