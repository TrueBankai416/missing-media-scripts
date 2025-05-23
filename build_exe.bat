@echo off
echo ========================================
echo Building Media Manager GUI Executable
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6+ and try again
    pause
    exit /b 1
)

echo Installing PyInstaller if not present...
pip install pyinstaller==6.13.0

echo.
echo Building executable... This may take a few minutes.
echo.

REM Clean up previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable using the spec file
pyinstaller media_manager_gui.spec

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for error details.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo The executable has been created at:
echo   dist\MediaManager.exe
echo.
echo You can now distribute this .exe file to users who don't have Python installed.
echo The executable includes all necessary dependencies.
echo.
echo Note: The first time you run the .exe, it may take a moment to start
echo as it extracts the bundled files to a temporary directory.
echo.
pause
