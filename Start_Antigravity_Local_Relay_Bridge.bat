@echo off
title Antigravity Local Relay Bridge (Galaxy A24 Gateway)
color 0A
cls
echo ========================================================================
echo        ANTIGRAVITY LOCAL RELAY BRIDGE -- GALAXY A24 GATEWAY
echo ========================================================================
echo.
echo  Starting local proxy gateway on port 8080...
echo  Active Google Session: ali.mohamed.220906@gmail.com
echo  Project ID: kemetpro-503518
echo.
echo  Connect your Samsung Galaxy A24 to the same Wi-Fi / Hotspot
echo  and open Chrome to:
echo.
echo         http://192.168.1.19:8080
echo.
echo ========================================================================
echo.
cd /d C:\VIP_Humanoid_Robot
python Antigravity_Local_Relay_Bridge.py
pause
