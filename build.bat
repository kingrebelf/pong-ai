@echo off
echo Building Pong Executable...
pip install -r requirements.txt
pyinstaller --onefile --windowed --name "PONG_PlayerVsAI" pong.py
echo Build complete! Check the 'dist' folder.
pause
