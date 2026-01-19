@echo off
cd /d %~dp0

echo ======================================
echo   BUILDING PORTABLE MATRIX SERVER
echo ======================================
echo.

echo Cleaning old builds...
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul
del launcher.spec 2>nul

echo.
echo Running PyInstaller...
echo.

python -m PyInstaller launcher.py ^
  --name "Finley_Private_Server" ^
  --icon matrix.ico ^
  --add-data "python;python" ^
  --add-data "app.py;." ^
  --add-data "matrix.py;." ^
  --add-data "hack;hack" ^
  --add-data "web;web"

echo.
echo ======================================
echo   BUILD COMPLETE
echo ======================================
echo.

pause
endlocal