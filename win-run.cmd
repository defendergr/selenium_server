@echo off
cd %~dp0
venv\Scripts\activate.bat && python run.py
pause
