@echo off
echo Starting Myra Voice Assistant...

cd /d "D:\Pys"

REM Activate the virtual environment
call "D:\Pys\Myra\Myra\Scripts\activate.bat"

REM Start Myra with startup greeting
python "D:\Pys\myra_startup.py"

REM If script exits, pause to show any error messages
pause
