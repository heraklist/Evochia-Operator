@echo off
chcp 65001 >nul
echo The Mart Capture Tool
echo =====================
IF NOT EXIST .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python themart_capture.py
pause
