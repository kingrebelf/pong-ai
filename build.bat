@echo off
echo Building Pong Executable...
echo.
echo Installing dependencies...
py -m pip install -r requirements.txt
echo.
echo Building .exe...
py -m PyInstaller --onefile --windowed --name "PONG_PlayerVsAI" pong.py
echo.
echo Build complete! Check the 'dist' folder.
pause
