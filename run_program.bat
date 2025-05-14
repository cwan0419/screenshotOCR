@echo off
cd /d %~dp0
call venv\Scripts\activate
python src/main.py
call venv\Scripts\deactivate
pause REM