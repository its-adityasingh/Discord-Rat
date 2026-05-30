@echo off
echo Installing required modules Please Wait dont close this...

py -m pip install --upgrade pip

py -m pip install discord.py aiohttp mss psutil opencv-python pyautogui pynput

echo.
echo Done installing
echo Running Builder.py...
echo.
cls
py Builder.py

pause