@echo off
chcp 65001 >nul
title AURA-EJUST — Restore Golden Master v2.0
echo ======================================================================
echo   AURA-EJUST HUMANOID ROBOT — GOLDEN MASTER RESTORATION UTILITY
echo ======================================================================
echo.
echo This script will restore the pristine Golden Master v2.0 files:
echo   - Dual Ultrasonic Sonar (Front & Rear)
echo   - 3-Channel IR Line Following & Station Checkpoints
echo   - Non-blocking Wi-Fi Firmware for ESP32
echo   - AI Screen & Floating Command Bar with Quick-Action Pills
echo   - Vertex AI Gemini 2.5 Flash & High-Definition Neural Voice Bridge
echo.
echo Press ANY KEY to restore now, or close this window to cancel...
pause >nul

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0RESTORE_GOLDEN_MASTER.ps1"

echo.
echo ======================================================================
echo   RESTORATION COMPLETE! All files have been reset to Golden Master v2.0
echo ======================================================================
echo.
pause
