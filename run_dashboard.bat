@echo off
cd /d "%~dp0"
python -m streamlit run dashboard.py
if errorlevel 1 py -m streamlit run dashboard.py
pause
