@echo off
title Body Metrics
cd /d "%~dp0"
python app.py
if errorlevel 1 pause
