@echo off
REM Build the Image Lock Tool GUI + service with PyInstaller
setlocal
cd /d %~dp0\..

echo === regenerating icons ===
python -m image_lock.gui.icon_gen || goto :err

echo === building GUI ===
pyinstaller --noconfirm --clean scripts\build_gui.spec || goto :err

echo === building service ===
pyinstaller --noconfirm --clean scripts\build_service.spec || goto :err

echo.
echo Build done.  See dist\ImageLockTool.exe and dist\ImageLockToolService.exe
exit /b 0

:err
echo Build failed.
exit /b 1
