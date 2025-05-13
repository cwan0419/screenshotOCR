@echo off
REM 가상환경 활성화
call venv\Scripts\activate.bat

REM python 프로그램 실행
python main.py

REM 가상환경 비활성화
call venv\Scripts\deactivate.bat

pause