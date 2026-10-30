@echo off
title AURA-EJUST Robot Complete Launcher
color 0B
cls
echo ========================================================================
echo        AURA-EJUST ROBOT -- 1-CLICK LAUNCHER (BRIDGE + TUNNEL)
echo ========================================================================
echo.
echo  Starting Antigravity Local Relay Bridge on Port 8080...
echo.

cd /d C:\VIP_Humanoid_Robot

start "AURA Relay Bridge (Port 8080)" cmd /k "color 0A && python Antigravity_Local_Relay_Bridge.py"

timeout /t 3 /nobreak >nul

echo  Starting Cloudflare Secure HTTPS Tunnel...
echo.
start "AURA Cloudflare HTTPS Tunnel" cmd /k "color 0E && cloudflared.exe tunnel --url http://127.0.0.1:8080"

echo ========================================================================
echo  Both services launched!
echo.
echo  Look at the "AURA Cloudflare HTTPS Tunnel" window for the URL:
echo  https://xxxx-xxxx-xxxx.trycloudflare.com
echo.
echo  Open that URL on your phone's Chrome browser!
echo ========================================================================
pause
