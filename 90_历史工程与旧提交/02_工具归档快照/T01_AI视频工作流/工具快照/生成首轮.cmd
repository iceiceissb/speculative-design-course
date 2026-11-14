@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -X utf8 workflow.py plan
python -X utf8 workflow.py generate
pause
