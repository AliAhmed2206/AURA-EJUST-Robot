"""
Builds the upgraded horizontal, minimalist bionic face screen for AURA-EJUST v3.0:
1. Horizontal (Landscape 16:9 / 20:9) Edge-to-Edge AMOLED pure obsidian (#000000).
2. Minimalist Face Mode: Screen is 100% just the living robot face!
   - Controls & Telemetry are hidden by default, accessible via a subtle gear toggle or gesture.
   - Clean, floating glass subtitles pill at bottom center that auto-fades.
3. Expressive, Emotive Face Engine (Feelings & Personality):
   - Organic squircle capsule eyes with dynamic specular glints.
   - Expressive cyber-eyebrows with emotional arching, furrows, and tilts.
   - Disney/Pixar squash & stretch animation with spring physics.
   - Micro-saccades & organic breathing pulse (looks conscious and alive).
   - Radiant blooming blush cheeks (#FF2A85) and morphing cyber-smile.
   - Syllable-synchronized viseme mouth movements.
4. Human Natural Neural Voice:
   - Auto-scans and prioritizes Google/Microsoft Natural Neural voices.
   - Human conversational prosody (pitch: 1.03, rate: 0.94) with sentence breathing.
"""

import os
import re

html_content = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <title>AURA-EJUST v3.0 — Bionic Humanoid Face & Speech Brain</title>
  <style>
    :root {
      --bg-black: #000000;
      --ejust-red: #C0121F;
      --ras-purple: #621B6D;
      --ras-violet: #9c27b0;
      --imperial-gold: #C8A45D;
      --neon-cyan: #00e5ff;
      --neon-magenta: #ff1744;
      --neon-green: #00e676;
      --blush-pink: #ff2a85;
      --text-white: #ffffff;
      --text-muted: #9e9ea7;
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      -webkit-user-select: none;
      -webkit-tap-highlight-color: transparent;
    }
    html, body {
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      background: var(--bg-black);
      color: var(--text-white);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* 100% Horizontal Viewport Container */
    .face-viewport {
      position: absolute;
      inset: 0;
      width: 100vw;
      height: 100vh;
      background: var(--bg-black);
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    #faceCanvas {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      display: block;
      cursor: pointer;
    }

    /* Minimalist Floating Subtitles Pill (Center Bottom) */
    .subtitles-pill {
      position: absolute;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      max-width: 82%;
      background: rgba(10, 8, 16, 0.72);
      border: 1px solid rgba(0, 229, 255, 0.22);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8), 0 0 15px rgba(0, 229, 255, 0.15);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-radius: 28px;
      padding: 8px 24px;
      display: flex;
      align-items: center;
      gap: 12px;
      z-index: 30;
      pointer-events: none;
      transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .subtitles-pill.hidden {
      opacity: 0;
      transform: translateX(-50%) translateY(16px);
    }
    .sub-speaker-tag {
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 1.5px;
      color: var(--imperial-gold);
      text-transform: uppercase;
      white-space: nowrap;
      border-right: 1px solid rgba(255, 255, 255, 0.18);
      padding-right: 10px;
    }
    .sub-text-content {
      font-size: 14px;
      font-weight: 600;
      color: #ffffff;
      line-height: 1.35;
      text-shadow: 0 1px 6px rgba(0, 0, 0, 0.8);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      max-width: 65vw;
    }

    /* Discreet Ambient HUD Overlay (Top Corners) */
    .corner-hud {
      position: absolute;
      top: 14px;
      left: 18px;
      right: 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 25;
      pointer-events: none;
      opacity: 0.35;
      transition: opacity 0.3s ease;
    }
    .corner-hud:hover, .corner-hud:active {
      opacity: 1.0;
    }
    .hud-badge-left {
      display: flex;
      align-items: center;
      gap: 8px;
      pointer-events: auto;
    }
    .hud-pill {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 20px;
      background: rgba(18, 14, 26, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.12);
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.8px;
      color: var(--text-muted);
      cursor: pointer;
      backdrop-filter: blur(8px);
    }
    .hud-pill.active {
      border-color: var(--neon-cyan);
      color: #fff;
    }
    .hud-badge-right {
      display: flex;
      align-items: center;
      gap: 6px;
      pointer-events: auto;
    }
    .dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #757575;
      display: inline-block;
    }
    .dot.green { background: #00e676; box-shadow: 0 0 8px #00e676; }
    .dot.cyan { background: #00e5ff; box-shadow: 0 0 8px #00e5ff; }
    .dot.gold { background: var(--imperial-gold); box-shadow: 0 0 8px var(--imperial-gold); }
    .btn-hud-icon {
      background: rgba(20, 16, 28, 0.75);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #fff;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      cursor: pointer;
      backdrop-filter: blur(8px);
      transition: all 0.2s;
    }
    .btn-hud-icon:hover {
      border-color: var(--neon-cyan);
      background: rgba(0, 229, 255, 0.18);
    }

    /* Tap-to-wake prompt banner (Centered Top) */
    .wake-prompt {
      position: absolute;
      top: 60px;
      left: 50%;
      transform: translateX(-50%);
      background: linear-gradient(135deg, rgba(192, 18, 31, 0.9), rgba(98, 27, 109, 0.9));
      color: #fff;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.8px;
      padding: 6px 18px;
      border-radius: 20px;
      border: 1px solid var(--imperial-gold);
      box-shadow: 0 6px 20px rgba(192, 18, 31, 0.5);
      cursor: pointer;
      z-index: 40;
      animation: pulseWake 1.8s infinite;
      white-space: nowrap;
    }
    @keyframes pulseWake {
      0%, 100% { transform: translateX(-50%) scale(1); opacity: 0.95; }
      50% { transform: translateX(-50%) scale(1.03); opacity: 1; }
    }

    /* Slide-Up Operator Control Drawer (Off-screen until ⚙️ tapped) */
    .control-drawer {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      background: rgba(12, 8, 18, 0.96);
      border-top: 1.5px solid var(--ejust-red);
      border-radius: 24px 24px 0 0;
      padding: 16px 22px;
      box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.9);
      backdrop-filter: blur(20px);
      z-index: 80;
      transform: translateY(105%);
      transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-height: 85vh;
      overflow-y: auto;
    }
    .control-drawer.open {
      transform: translateY(0);
    }
    .drawer-handle-bar {
      width: 44px;
      height: 4px;
      background: rgba(255, 255, 255, 0.25);
      border-radius: 3px;
      margin: 0 auto 4px auto;
      cursor: pointer;
    }
    .drawer-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 8px;
    }
    .drawer-title {
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 1px;
      color: var(--imperial-gold);
    }
    .chat-input-bar {
      display: flex;
      gap: 8px;
      width: 100%;
    }
    .chat-input-field {
      flex: 1;
      background: rgba(0, 0, 0, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 10px;
      padding: 8px 14px;
      color: #fff;
      font-size: 12px;
      outline: none;
    }
    .chat-input-field:focus {
      border-color: var(--neon-cyan);
    }
    .btn-chat-send {
      background: linear-gradient(135deg, var(--ejust-red), var(--ras-purple));
      border: none;
      color: #fff;
      padding: 8px 16px;
      border-radius: 10px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }
    .action-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .btn-drawer {
      flex: 1;
      min-width: 110px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 8px 12px;
      border-radius: 10px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #fff;
      transition: all 0.2s;
    }
    .btn-drawer:hover {
      background: rgba(255, 255, 255, 0.16);
    }
    .btn-drawer.primary {
      background: linear-gradient(135deg, var(--ras-purple), var(--ejust-red));
      border-color: var(--imperial-gold);
    }

    /* Settings Modal */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.88);
      backdrop-filter: blur(12px);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .modal-backdrop.open { display: flex; }
    .modal-card {
      background: #120c1a;
      border: 1.5px solid var(--ejust-red);
      border-radius: 18px;
      width: 100%;
      max-width: 520px;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 12px 45px rgba(192, 18, 31, 0.45);
      overflow: hidden;
    }
    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 20px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(98, 27, 109, 0.28);
    }
    .modal-title {
      font-size: 13px;
      font-weight: 800;
      color: var(--imperial-gold);
      letter-spacing: 1px;
    }
    .modal-close {
      background: none;
      border: none;
      color: #fff;
      font-size: 18px;
      cursor: pointer;
    }
    .modal-body {
      padding: 18px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .form-label {
      font-size: 11px;
      font-weight: 800;
      color: var(--text-muted);
      letter-spacing: 0.5px;
    }
    .form-input, .form-select {
      background: rgba(0, 0, 0, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.18);
      border-radius: 8px;
      padding: 8px 12px;
      color: #fff;
      font-size: 12px;
      outline: none;
    }
    .form-input:focus, .form-select:focus {
      border-color: var(--neon-cyan);
    }
    .ble-log-box {
      font-family: monospace;
      font-size: 10px;
      height: 70px;
      overflow-y: auto;
      background: #000;
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 6px;
      padding: 6px;
      color: #00e676;
    }

    /* Picture-in-picture camera gaze box */
    .cam-pip {
      position: absolute;
      bottom: 20px;
      right: 20px;
      width: 100px;
      height: 75px;
      border-radius: 10px;
      border: 1.5px solid rgba(0, 229, 255, 0.4);
      background: #000;
      overflow: hidden;
      z-index: 20;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s;
    }
    .cam-pip.visible {
      opacity: 0.85;
      pointer-events: auto;
    }
    #camVideo { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
    #camOverlay { position: absolute; inset: 0; width: 100%; height: 100%; }
    .cam-tag { position: absolute; bottom: 2px; left: 2px; font-size: 8px; font-weight: 700; color: var(--neon-cyan); background: rgba(0,0,0,0.7); padding: 1px 4px; border-radius: 3px; }
  </style>
</head>
<body>
  <!-- 100% Horizontal Viewport Screen (Bionic Robot Face) -->
  <div class="face-viewport" id="viewport">
    <canvas id="faceCanvas" onclick="unlockAudioAndListen()"></canvas>

    <!-- Tap-to-wake prompt -->
    <div class="wake-prompt" id="wakePrompt" onclick="unlockAudioAndListen()">
      👆 Tap anywhere to activate voice &amp; speech
    </div>

    <!-- Ambient Subtle HUD (Top Corners) -->
    <div class="corner-hud" id="cornerHud">
      <div class="hud-badge-left">
        <div class="hud-pill" id="emotionBadge">
          <span id="emotionIcon">😊</span>
          <span id="emotionText">ATTENTIVE</span>
        </div>
        <div class="hud-pill" id="gazeBadge">
          <span>👁️</span>
          <span id="gazeText">GAZE: IDLE SCAN</span>
        </div>
      </div>
      <div class="hud-badge-right">
        <div class="hud-pill" id="blePill" onclick="connectBle()" title="ESP32 BLE Link">
          <span class="dot" id="bleDot"></span>
          <span id="bleText">BLE: OFF</span>
        </div>
        <div class="hud-pill" id="aiPill" onclick="openSettings()" title="AI Model Status">
          <span class="dot green" id="geminiDot"></span>
          <span id="geminiText">AI: PRO SESSION</span>
        </div>
        <button class="btn-hud-icon" onclick="toggleDrawer()" title="Open Controls &amp; Chat">☰</button>
        <button class="btn-hud-icon" onclick="openSettings()" title="Settings">⚙️</button>
        <button class="btn-hud-icon" onclick="toggleFullScreen()" title="Fullscreen">⛶</button>
      </div>
    </div>

    <!-- Minimalist Subtitles Floating Center-Bottom -->
    <div class="subtitles-pill" id="subBox">
      <div class="sub-speaker-tag" id="subSpeaker">AURA-EJUST</div>
      <div class="sub-text-content" id="subText">Welcome to IEEE RAS E-JUST. Please tap your NFC badge on the chest reader to begin escort.</div>
    </div>

    <!-- Camera Picture-in-Picture window -->
    <div class="cam-pip" id="camPip">
      <video id="camVideo" autoplay playsinline muted></video>
      <canvas id="camOverlay"></canvas>
      <span class="cam-tag" id="camTag">GAZE: OFF</span>
    </div>
  </div>

  <!-- Slide-Up Operator Control & Chat Drawer -->
  <div class="control-drawer" id="controlDrawer">
    <div class="drawer-handle-bar" onclick="toggleDrawer()"></div>
    <div class="drawer-header">
      <div class="drawer-title">⚡ AURA-EJUST v3.0 OPERATOR DRAWER</div>
      <button class="btn-hud-icon" style="width: 24px; height: 24px; font-size: 11px;" onclick="toggleDrawer()">✕</button>
    </div>

    <!-- Typed chat bar -->
    <div class="chat-input-bar">
      <input type="text" id="userTextInput" class="chat-input-field" placeholder="Type a message to AURA (e.g. 'Thank you so much', 'Where is the hall?')..." onkeydown="if(event.key==='Enter') sendTypedText()" />
      <button class="btn-chat-send" onclick="sendTypedText()">Send</button>
    </div>

    <!-- Actions & Quick Emote Tests -->
    <div class="action-row">
      <button class="btn-drawer primary" id="micBtn" onclick="toggleMic()">
        <span id="micIcon">🎙️</span>
        <span id="micText">TAP TO SPEAK</span>
      </button>
      <button class="btn-drawer" id="bleActionBtn" onclick="connectBle()">
        <span>📶</span>
        <span id="bleActionText">PAIR ESP32 (BLE)</span>
      </button>
      <button class="btn-drawer" id="continuousBtn" onclick="toggleContinuousMode()">
        <span>🔄</span>
        <span id="continuousText">AUTO-TALK: ON</span>
      </button>
      <button class="btn-drawer" onclick="testEmotion('HAPPY', 'Thank you so much AURA, you did an amazing job!')">
        💖 Thank You!
      </button>
      <button class="btn-drawer" onclick="testEmotion('CURIOUS', 'Can you tell me about the E-JUST robotics lab?')">
        💡 Ask Question
      </button>
    </div>

    <!-- VIP Simulation row -->
    <div class="action-row">
      <button class="btn-drawer" onclick="triggerVIP('Prof. Amr Adly', 'أهلاً وسهلاً أ.د. عمرو عدلي — رئيس الجامعة المصرية اليابانية', 'Main Conference Hall', 1, 'A1:B2:C3:D4')">
        🎓 Prof. Amr (Hall)
      </button>
      <button class="btn-drawer" onclick="triggerVIP('Dr. Mariam Hassan', 'أهلاً بكِ د. مريم حسن — المتحدث الرئيسي لـ IEEE RAS', 'E-JUST Grand Theatre', 2, 'E5:F6:07:18')">
        🤖 Dr. Mariam (Theatre)
      </button>
      <button class="btn-drawer" onclick="triggerVIP('Eng. Youssef Khaled', 'مرحباً م. يوسف خالد — رئيس فرع IEEE RAS E-JUST', 'Robotics Lab &amp; Hall', 1, '12:34:56:78')">
        ⚡ Eng. Youssef
      </button>
      <button class="btn-drawer" onclick="toggleCamPip()">
        📹 Toggle Cam
      </button>
    </div>
  </div>

  <!-- Settings Modal -->
  <div class="modal-backdrop" id="settingsModal">
    <div class="modal-card">
      <div class="modal-header">
        <div class="modal-title">⚙️ AURA-EJUST v3.0 SETTINGS</div>
        <button class="modal-close" onclick="closeSettings()">✕</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">AI Conversational Brain Provider</label>
          <select id="providerSelect" class="form-select" onchange="updateProviderVisibility()">
            <option value="antigravity-relay">Antigravity Local Relay Bridge (Recommended - Free PC Pro Session)</option>
            <option value="openrouter">OpenRouter API (Free Models: Llama 3.3 70B, DeepSeek, Claude, Mistral)</option>
            <option value="gemini">Google Gemini API (Google AI Studio Key / Live WS)</option>
            <option value="offline-autonomous">Offline Autonomous Smart Dialog (Zero Quota / 100% Free)</option>
          </select>
        </div>

        <div id="antigravitySettingsGroup">
          <div class="form-group">
            <label class="form-label">Relay Bridge Address (PC Gateway)</label>
            <input type="text" id="bridgeUrlInput" class="form-input" placeholder="http://192.168.1.19:8080" />
            <span style="font-size: 9px; color: var(--neon-cyan);">Direct zero-quota connection to PC Antigravity Pro session.</span>
          </div>
        </div>

        <div id="openrouterSettingsGroup" style="display: none;">
          <div class="form-group">
            <label class="form-label">OpenRouter API Key</label>
            <input type="password" id="openRouterKeyInput" class="form-input" placeholder="sk-or-v1-..." />
            <span style="font-size: 9px; color: var(--imperial-gold);">Cached locally in browser. Free key at openrouter.ai/keys.</span>
          </div>
          <div class="form-group">
            <label class="form-label">OpenRouter Model</label>
            <select id="openRouterModelSelect" class="form-select">
              <option value="meta-llama/llama-3.3-70b-instruct:free">meta-llama/llama-3.3-70b-instruct:free (100% Free)</option>
              <option value="deepseek/deepseek-chat">deepseek/deepseek-chat (Ultra Smart &amp; Low Cost)</option>
              <option value="google/gemini-2.0-flash-001">google/gemini-2.0-flash-001 (Google Flash via OpenRouter)</option>
              <option value="mistralai/mistral-7b-instruct:free">mistralai/mistral-7b-instruct:free (Free Mistral)</option>
              <option value="qwen/qwen-2.5-72b-instruct">qwen/qwen-2.5-72b-instruct</option>
              <option value="anthropic/claude-3.5-haiku">anthropic/claude-3.5-haiku</option>
            </select>
          </div>
        </div>

        <div id="geminiSettingsGroup" style="display: none;">
          <div class="form-group">
            <label class="form-label">Gemini API Key</label>
            <input type="password" id="apiKeyInput" class="form-input" placeholder="AIzaSy..." />
          </div>
          <div class="form-group">
            <label class="form-label">Gemini Conversational Model</label>
            <select id="modelSelect" class="form-select">
              <option value="gemini-3.8-flash">gemini-3.8-flash (Recommended)</option>
              <option value="gemini-3.8-live">gemini-3.8-live (Live WebSocket)</option>
              <option value="gemini-3.5-flash">gemini-3.5-flash</option>
              <option value="offline-autonomous">Offline Smart Dialog Engine (Zero Quota Needed)</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Voice &amp; Neural Tone (Selects Highest Quality Speech)</label>
          <select id="voiceSelect" class="form-select">
            <option value="auto-neural">Auto-Select Best Natural Neural Voice (Google / Microsoft Neural)</option>
            <option value="Aoede">Aoede (Gemini Live Audio)</option>
            <option value="Puck">Puck (Gemini Live Audio)</option>
            <option value="Kore">Kore (Gemini Live Audio)</option>
            <option value="Charon">Charon (Gemini Live Audio)</option>
            <option value="native-tts">System Bilingual TTS (en-US / ar-EG)</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">ESP32 Wi-Fi AP IP (Fallback)</label>
          <input type="text" id="esp32IpInput" class="form-input" value="192.168.4.1" />
        </div>

        <div class="form-group">
          <label class="form-label">Web Bluetooth (NUS) Raw Packet Monitor</label>
          <div class="ble-log-box" id="bleLogBox">Ready to connect to Nordic UART Service...</div>
        </div>
      </div>
      <div class="modal-footer" style="padding: 12px 18px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: flex-end;">
        <button class="btn-drawer primary" style="flex: none; padding: 6px 18px;" onclick="saveSettings()">Save &amp; Apply</button>
      </div>
    </div>
  </div>

  <script>
    /* ==========================================================================
       AURA-EJUST v3.0 — Horizontal Minimalist Bionic Face, Camera Vision, BLE & AI
       ========================================================================== */

    // 1. Core Configuration & State
    const NORDIC_UART_SERVICE = '6e400001-b5a3-f393-e0a9-e50e24dcca9e';
    const NORDIC_RX_CHAR = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'; // Phone writes to ESP32
    const NORDIC_TX_CHAR = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'; // ESP32 notifies Phone

    const DEFAULT_API_KEY = 'AIzaSyDrEPiLGYrnqxzvcE9PhAP4LCx-eEAk8gk';
    let apiProvider = localStorage.getItem('AURA_API_PROVIDER') || 'antigravity-relay';
    let bridgeUrl = localStorage.getItem('AURA_BRIDGE_URL') || (window.location.origin.startsWith('http') ? window.location.origin : 'http://192.168.1.19:8080');
    let openRouterKey = localStorage.getItem('AURA_OPENROUTER_KEY') || '';
    let openRouterModel = localStorage.getItem('AURA_OPENROUTER_MODEL') || 'meta-llama/llama-3.3-70b-instruct:free';
    let apiKey = localStorage.getItem('AURA_GEMINI_KEY') || DEFAULT_API_KEY;
    let selectedModel = localStorage.getItem('AURA_GEMINI_MODEL') || 'gemini-3.8-flash';
    let selectedVoice = localStorage.getItem('AURA_VOICE') || 'auto-neural';
    let esp32Ip = localStorage.getItem('AURA_ESP32_IP') || '192.168.4.1';

    // Bluetooth Objects
    let bleDevice = null;
    let bleServer = null;
    let rxChar = null;
    let txChar = null;
    let bleConnected = false;

    // Face & Organic Emotion State
    let currentEmotion = 'ATTENTIVE'; // ATTENTIVE, HAPPY, CURIOUS, THINKING, SPEAKING, SURPRISED
    let targetEmotion = 'ATTENTIVE';
    let emotionTimer = null;
    let blushAlpha = 0.0;
    let targetGazeX = 0; // -1 (left) to +1 (right)
    let targetGazeY = 0; // -1 (up - tall) to +1 (down - short)
    let currentGazeX = 0;
    let currentGazeY = 0;

    // Saccades (living micro-movements)
    let saccadeX = 0;
    let saccadeY = 0;
    let nextSaccadeTime = performance.now() + 2000;

    // Blinking with Squash & Stretch
    let blinkProgress = 0;
    let isBlinking = false;
    let nextBlinkTime = performance.now() + 3000;
    let lipSyncOpen = 0.0;
    let speechAudioEnergy = 0.0;

    // Conversational & Live Audio State
    let isContinuousConversation = true;
    let liveWs = null;
    let isLiveWsConnected = false;
    let isLiveAudioPlaying = false;
    let audioCtx = null;
    let nextAudioStartTime = 0;

    // Camera Vision State
    let camStream = null;
    let faceDetector = null;
    let visitorNear = false;
    let visitorDetectionCount = 0;
    let lastVisitorGreetingTime = 0;

    // Escort & VIP State
    let escortTimer = null;
    let activeUid = '';
    let currentRobotState = 'IDLE';

    const ARABIC_TITLES = {
      'Prof. Amr Adly': 'أهلاً وسهلاً أ.د. عمرو عدلي — رئيس الجامعة المصرية اليابانية',
      'Dr. Mariam Hassan': 'أهلاً بكِ د. مريم حسن — المتحدث الرئيسي لـ IEEE RAS',
      'Eng. Youssef Khaled': 'مرحباً م. يوسف خالد — رئيس فرع IEEE RAS E-JUST'
    };

    /* ==========================================================================
       2. Expressive Organic Bionic Face Engine (Canvas 60 FPS Emotive Animation)
       ========================================================================== */
    const canvas = document.getElementById('faceCanvas');
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    window.addEventListener('resize', resizeCanvas);
    setTimeout(resizeCanvas, 40);

    // Natural Organic Saccades (Eyes micro-drift to look alive)
    function updateSaccades(now) {
      if (now > nextSaccadeTime) {
        if (Math.random() < 0.65) {
          saccadeX = (Math.random() - 0.5) * 0.12;
          saccadeY = (Math.random() - 0.5) * 0.08;
        } else {
          saccadeX = 0;
          saccadeY = 0;
        }
        nextSaccadeTime = now + 1800 + Math.random() * 2600;
      }
    }

    function renderFace(now) {
      const w = window.innerWidth;
      const h = window.innerHeight;

      ctx.clearRect(0, 0, w, h);

      // Living micro-saccades & breathing
      updateSaccades(now);
      const breath = Math.sin(now * 0.0022) * 0.016; // 1.6% organic breathing cycle

      // Smooth gaze interpolation with soft damping
      currentGazeX += ((targetGazeX + saccadeX) - currentGazeX) * 0.14;
      currentGazeY += ((targetGazeY + saccadeY) - currentGazeY) * 0.14;

      // Organic Blinking with Disney Squash-Stretch Physics
      if (!isBlinking && now > nextBlinkTime) {
        isBlinking = true;
        blinkProgress = 0;
      }
      if (isBlinking) {
        blinkProgress += 0.18;
        if (blinkProgress >= 1.0) {
          isBlinking = false;
          blinkProgress = 0;
          nextBlinkTime = now + 2400 + Math.random() * 3200;
        }
      }
      const blinkFactor = isBlinking ? Math.sin(blinkProgress * Math.PI) : 0;

      // Radiant Glowing Blush Cheeks (Smooth fade-in when HAPPY)
      if (currentEmotion === 'HAPPY') {
        blushAlpha = Math.min(1.0, blushAlpha + 0.06);
      } else {
        blushAlpha = Math.max(0.0, blushAlpha - 0.03);
      }

      // Horizontal Screen Geometry (Optimized for 16:9 and 20:9 Landscape)
      const eyeSpacing = Math.min(w * 0.22, 230);
      const eyeW = Math.min(w * 0.20, h * 0.46, 240) * (1.0 + breath);
      const eyeH = Math.min(h * 0.44, w * 0.18, 200) * (1.0 + breath);
      const leftEyeX = w * 0.5 - eyeSpacing;
      const rightEyeX = w * 0.5 + eyeSpacing;
      const eyeY = h * 0.43;

      // Draw Eyebrows (Dynamic Emotional Personality)
      drawEyebrow(leftEyeX, eyeY, eyeW, currentEmotion, 'left', now);
      drawEyebrow(rightEyeX, eyeY, eyeW, currentEmotion, 'right', now);

      // Draw Organic Bionic Eyes
      drawBionicEye(leftEyeX, eyeY, eyeW, eyeH, currentGazeX, currentGazeY, blinkFactor, 'left', now);
      drawBionicEye(rightEyeX, eyeY, eyeW, eyeH, currentGazeX, currentGazeY, blinkFactor, 'right', now);

      // Draw Radiant Cherry-Pink Blushing Cheeks
      if (blushAlpha > 0.01) {
        const blushR = eyeW * 0.38;
        drawCheekBlush(leftEyeX - eyeW * 0.32, eyeY + eyeH * 0.58, blushR, blushAlpha);
        drawCheekBlush(rightEyeX + eyeW * 0.32, eyeY + eyeH * 0.58, blushR, blushAlpha);
      }

      // Draw Organic Cyber Mouth with Syllable Lip-Sync
      drawCyberMouth(w * 0.5, h * 0.77, eyeW * 0.95, currentEmotion, now);

      requestAnimationFrame(renderFace);
    }
    requestAnimationFrame(renderFace);

    // Expressive Cyber-Eyebrow Rendering
    function drawEyebrow(cx, cy, eyeW, emotion, side, now) {
      ctx.save();
      ctx.translate(cx, cy);

      const sign = (side === 'left' ? -1 : 1);
      let browY = -eyeW * 0.56;
      let browTilt = 0;
      let browArch = 0;
      let browWidth = eyeW * 0.65;

      if (emotion === 'HAPPY') {
        // High arched cheerful eyebrows
        browY -= 14;
        browArch = -16;
        browTilt = sign * 4;
      } else if (emotion === 'CURIOUS') {
        // One eyebrow raised high, other cocked down
        if (side === 'left') {
          browY -= 22;
          browTilt = 10;
          browArch = -12;
        } else {
          browY += 4;
          browTilt = -6;
        }
      } else if (emotion === 'THINKING') {
        // Furrowed concentrated slant
        browY += 8;
        browTilt = sign * -14;
        browArch = 6;
      } else if (emotion === 'SURPRISED') {
        // High surprised arch
        browY -= 32;
        browArch = -22;
      } else if (emotion === 'SPEAKING') {
        // Subtle expressive cadence bounce
        const cadence = Math.sin(now * 0.008) * 4;
        browY -= 6 + cadence;
        browTilt = sign * 3;
      } else {
        // Attentive resting slight curve
        browY -= 4;
        browArch = -4;
      }

      ctx.strokeStyle = '#00e5ff';
      ctx.shadowColor = '#00e5ff';
      ctx.shadowBlur = 10;
      ctx.lineWidth = 6;
      ctx.lineCap = 'round';

      ctx.beginPath();
      ctx.moveTo(-browWidth * 0.5, browY - browTilt);
      ctx.quadraticCurveTo(0, browY + browArch, browWidth * 0.5, browY + browTilt);
      ctx.stroke();

      ctx.restore();
    }

    // Helper: Rounded squircle path
    function pathSquircle(ctx, x, y, width, height, radius) {
      ctx.beginPath();
      ctx.moveTo(x + radius, y);
      ctx.lineTo(x + width - radius, y);
      ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
      ctx.lineTo(x + width, y + height - radius);
      ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
      ctx.lineTo(x + radius, y + height);
      ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
      ctx.lineTo(x, y + radius);
      ctx.quadraticCurveTo(x, y, x + radius, y);
      ctx.closePath();
    }

    function drawBionicEye(cx, cy, w, h, gazeX, gazeY, blink, side, now) {
      ctx.save();
      ctx.translate(cx, cy);

      // Squircle Dimensions
      let squircleW = w;
      let squircleH = h;
      let cornerR = Math.min(w, h) * 0.38;

      // 1. HAPPY: Morph into joyous curved crescents (⌒)
      if (currentEmotion === 'HAPPY') {
        ctx.strokeStyle = '#00f0ff';
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 24;
        ctx.lineWidth = 14;
        ctx.lineCap = 'round';

        ctx.beginPath();
        const crescentR = w * 0.42;
        ctx.arc(0, h * 0.12, crescentR, Math.PI * 1.15, Math.PI * 1.85, false);
        ctx.stroke();

        // Sparkle stars in outer corners
        ctx.fillStyle = '#ffffff';
        ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.arc(w * 0.38, -h * 0.08, 4, 0, Math.PI * 2);
        ctx.arc(-w * 0.38, -h * 0.08, 4, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
        return;
      }

      // Eye deformation based on Emotion & Blinking
      let scaleX = 1.0;
      let scaleY = 1.0;

      if (currentEmotion === 'SURPRISED') {
        scaleX = 1.18;
        scaleY = 1.25;
      } else if (currentEmotion === 'THINKING') {
        scaleY = 0.92;
      }

      // Squash and stretch blink
      if (blink > 0) {
        scaleY *= (1.0 - blink * 0.96);
        scaleX *= (1.0 + blink * 0.08); // Slight horizontal expansion on squash
      }

      ctx.scale(scaleX, scaleY);

      const halfW = squircleW * 0.5;
      const halfH = squircleH * 0.5;

      // 1. Outer Sclera Glow
      ctx.shadowColor = currentEmotion === 'THINKING' ? '#ff1744' : '#00e5ff';
      ctx.shadowBlur = 20;

      const outerGrad = ctx.createRadialGradient(0, 0, halfW * 0.4, 0, 0, halfW);
      outerGrad.addColorStop(0, '#060a12');
      outerGrad.addColorStop(0.82, '#0c1220');
      outerGrad.addColorStop(1, currentEmotion === 'THINKING' ? 'rgba(255, 23, 68, 0.7)' : 'rgba(0, 229, 255, 0.45)');

      pathSquircle(ctx, -halfW, -halfH, squircleW, squircleH, cornerR);
      ctx.fillStyle = outerGrad;
      ctx.fill();

      // Cyber contour border
      ctx.strokeStyle = currentEmotion === 'THINKING' ? 'rgba(255, 23, 68, 0.75)' : 'rgba(0, 229, 255, 0.55)';
      ctx.lineWidth = 3;
      ctx.stroke();

      // Clip inside eye squircle for pupils and highlights
      ctx.save();
      pathSquircle(ctx, -halfW, -halfH, squircleW, squircleH, cornerR);
      ctx.clip();

      // 2. High-Tech Iris (Gaze Offsets)
      const maxGazeX = halfW * 0.42;
      const maxGazeY = halfH * 0.42;
      const px = gazeX * maxGazeX;
      const py = gazeY * maxGazeY;
      const irisR = Math.min(halfW, halfH) * 0.68;

      // Iris Multi-Stop Glow Gradient
      const irisGrad = ctx.createRadialGradient(px, py, irisR * 0.15, px, py, irisR);
      irisGrad.addColorStop(0, '#ffffff');
      irisGrad.addColorStop(0.28, '#00e5ff');
      irisGrad.addColorStop(0.65, '#0055ff');
      irisGrad.addColorStop(0.92, '#021838');
      irisGrad.addColorStop(1, 'rgba(0, 5, 20, 0.9)');

      ctx.beginPath();
      ctx.arc(px, py, irisR, 0, Math.PI * 2);
      ctx.fillStyle = irisGrad;
      ctx.shadowColor = '#00e5ff';
      ctx.shadowBlur = 18;
      ctx.fill();

      // Rotating orbital cyber ring when THINKING
      if (currentEmotion === 'THINKING') {
        ctx.save();
        ctx.translate(px, py);
        ctx.rotate((now * 0.003) * (side === 'left' ? 1 : -1));
        ctx.strokeStyle = 'rgba(255, 23, 68, 0.85)';
        ctx.lineWidth = 2.5;
        for (let a = 0; a < Math.PI * 2; a += Math.PI / 4) {
          ctx.beginPath();
          ctx.moveTo(Math.cos(a) * (irisR * 0.55), Math.sin(a) * (irisR * 0.55));
          ctx.lineTo(Math.cos(a) * irisR, Math.sin(a) * irisR);
          ctx.stroke();
        }
        ctx.restore();
      }

      // 3. Central Deep Pupil
      const pupilR = irisR * (currentEmotion === 'SURPRISED' ? 0.52 : (currentEmotion === 'CURIOUS' ? 0.42 : 0.35));
      ctx.beginPath();
      ctx.arc(px, py, pupilR, 0, Math.PI * 2);
      ctx.fillStyle = '#020306';
      ctx.fill();

      // 4. Specular Reflection Glints (Living spark)
      ctx.fillStyle = 'rgba(255, 255, 255, 0.92)';
      ctx.shadowColor = '#ffffff';
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.arc(px - irisR * 0.34, py - irisR * 0.34, pupilR * 0.44, 0, Math.PI * 2);
      ctx.fill();

      ctx.beginPath();
      ctx.arc(px + irisR * 0.28, py + irisR * 0.28, pupilR * 0.22, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore(); // remove clip
      ctx.restore();
    }

    function drawCheekBlush(cx, cy, radius, alpha) {
      ctx.save();
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
      grad.addColorStop(0, `rgba(255, 42, 133, ${alpha * 0.85})`);
      grad.addColorStop(0.55, `rgba(255, 42, 133, ${alpha * 0.4})`);
      grad.addColorStop(1, 'rgba(255, 42, 133, 0)');

      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();
      ctx.restore();
    }

    // Expressive Organic Cyber Mouth Engine
    function drawCyberMouth(cx, cy, width, emotion, now) {
      ctx.save();
      ctx.translate(cx, cy);

      ctx.strokeStyle = '#00e5ff';
      ctx.shadowColor = '#00e5ff';
      ctx.shadowBlur = 14;
      ctx.lineWidth = 5.5;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      if (emotion === 'SPEAKING') {
        // Natural harmonic waveform (Visemes vocal oscillation)
        const waveAmp = (14 + Math.sin(now * 0.024) * 11) * (lipSyncOpen + 0.35);
        ctx.fillStyle = 'rgba(0, 229, 255, 0.16)';

        ctx.beginPath();
        ctx.moveTo(-width * 0.48, 0);
        ctx.quadraticCurveTo(-width * 0.22, -waveAmp * 0.8, 0, waveAmp * 0.6);
        ctx.quadraticCurveTo(width * 0.22, waveAmp * 0.9, width * 0.48, 0);
        ctx.quadraticCurveTo(0, -waveAmp * 0.4, -width * 0.48, 0);
        ctx.stroke();
        ctx.fill();
      } else if (emotion === 'HAPPY') {
        // Broad radiant joyful smile
        ctx.strokeStyle = '#00f0ff';
        ctx.fillStyle = 'rgba(0, 240, 255, 0.22)';
        ctx.beginPath();
        ctx.moveTo(-width * 0.52, -6);
        ctx.quadraticCurveTo(0, width * 0.42, width * 0.52, -6);
        ctx.quadraticCurveTo(0, width * 0.14, -width * 0.52, -6);
        ctx.stroke();
        ctx.fill();
      } else if (emotion === 'CURIOUS') {
        // Thoughtful inquisitive quirk
        ctx.beginPath();
        ctx.moveTo(-width * 0.38, 5);
        ctx.quadraticCurveTo(-width * 0.05, 0, width * 0.42, -8);
        ctx.stroke();
      } else if (emotion === 'THINKING') {
        // Soft pulsing attentive capsule
        const pulse = Math.sin(now * 0.009) * 3;
        ctx.beginPath();
        ctx.ellipse(0, 0, width * 0.22, 6 + pulse, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 229, 255, 0.15)';
        ctx.stroke();
        ctx.fill();
      } else if (emotion === 'SURPRISED') {
        // Expressive glowing 'O'
        ctx.beginPath();
        ctx.ellipse(0, 0, width * 0.25, width * 0.32, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 229, 255, 0.2)';
        ctx.stroke();
        ctx.fill();
      } else {
        // Neutral warm attentive smile
        ctx.beginPath();
        ctx.moveTo(-width * 0.40, 0);
        ctx.quadraticCurveTo(0, width * 0.14, width * 0.40, 0);
        ctx.stroke();
      }

      ctx.restore();
    }

    function setEmotion(emotion, durationMs = 0) {
      currentEmotion = emotion;
      const badge = document.getElementById('emotionBadge');
      const icon = document.getElementById('emotionIcon');
      const txt = document.getElementById('emotionText');
      if (badge && icon && txt) {
        txt.textContent = emotion;
        if (emotion === 'HAPPY') icon.textContent = '💖';
        else if (emotion === 'CURIOUS') icon.textContent = '💡';
        else if (emotion === 'THINKING') icon.textContent = '🧠';
        else if (emotion === 'SPEAKING') icon.textContent = '🗣️';
        else if (emotion === 'SURPRISED') icon.textContent = '😲';
        else icon.textContent = '😊';
      }

      if (emotionTimer) clearTimeout(emotionTimer);
      if (durationMs > 0) {
        emotionTimer = setTimeout(() => {
          currentEmotion = 'ATTENTIVE';
          if (badge && icon && txt) {
            txt.textContent = 'ATTENTIVE';
            icon.textContent = '😊';
          }
        }, durationMs);
      }
    }

    /* ==========================================================================
       3. Human Natural Neural Voice Engine (High Quality Speech Synthesis)
       ========================================================================== */
    let cachedVoices = [];
    function loadVoices() {
      if (!('speechSynthesis' in window)) return;
      cachedVoices = window.speechSynthesis.getVoices();
    }
    if ('speechSynthesis' in window) {
      loadVoices();
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    function getBestVoice(langPrefix = 'en') {
      if (!cachedVoices || cachedVoices.length === 0) {
        cachedVoices = window.speechSynthesis.getVoices();
      }
      if (!cachedVoices || cachedVoices.length === 0) return null;

      // 1. Prioritize Google / Microsoft Online Natural / Neural Voices
      const natural = cachedVoices.find(v =>
        v.lang.toLowerCase().startsWith(langPrefix.toLowerCase()) &&
        (v.name.includes('Natural') || v.name.includes('Neural') || v.name.includes('Google') || v.name.includes('Premium') || v.name.includes('Online'))
      );
      if (natural) return natural;

      // 2. Fall back to exact language prefix
      const langMatch = cachedVoices.find(v => v.lang.toLowerCase().startsWith(langPrefix.toLowerCase()));
      if (langMatch) return langMatch;

      return cachedVoices[0];
    }

    function speakReply(text, emotionAfter) {
      if (!('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      const isArabic = /[\u0600-\u06FF]/.test(text);

      utterance.lang = isArabic ? 'ar-EG' : 'en-US';
      const bestVoice = getBestVoice(isArabic ? 'ar' : 'en');
      if (bestVoice) {
        utterance.voice = bestVoice;
      }

      // Warm Human Conversational Prosody (Not robotic!)
      utterance.rate = 0.94;  // Slightly deliberate human tempo
      utterance.pitch = 1.03; // Friendly warmth
      utterance.volume = 1.0;

      utterance.onstart = () => {
        setEmotion('SPEAKING');
        lipSyncOpen = 1.0;
        showSubtitles('AURA-EJUST', text);
      };
      utterance.onerror = (err) => {
        console.warn('Speech synthesis error:', err);
        lipSyncOpen = 0.0;
        setEmotion('ATTENTIVE');
        if (isContinuousConversation) setTimeout(startListening, 600);
      };
      utterance.onend = () => {
        lipSyncOpen = 0.0;
        setEmotion(emotionAfter || 'ATTENTIVE', 3500);
        setTimeout(fadeSubtitlesIfQuiet, 3500);
        if (isContinuousConversation) {
          setTimeout(startListening, 600);
        }
      };

      window.speechSynthesis.speak(utterance);
    }

    function speakWelcome(enText, arText) {
      if (!('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel();

      showSubtitles('AURA-EJUST', (enText ? enText : '') + (arText ? ' — ' + arText : ''));
      setEmotion('SPEAKING');
      lipSyncOpen = 1.0;

      if (enText) {
        const uEn = new SpeechSynthesisUtterance(enText);
        uEn.lang = 'en-US';
        const vEn = getBestVoice('en');
        if (vEn) uEn.voice = vEn;
        uEn.rate = 0.94;
        uEn.pitch = 1.03;

        uEn.onerror = () => {
          lipSyncOpen = 0.0;
          setEmotion('HAPPY', 5000);
          if (isContinuousConversation) setTimeout(startListening, 800);
        };
        uEn.onend = () => {
          if (arText) {
            const uAr = new SpeechSynthesisUtterance(arText);
            uAr.lang = 'ar-EG';
            const vAr = getBestVoice('ar');
            if (vAr) uAr.voice = vAr;
            uAr.rate = 0.92;
            uAr.pitch = 1.02;

            uAr.onerror = () => {
              lipSyncOpen = 0.0;
              setEmotion('HAPPY', 5000);
              if (isContinuousConversation) setTimeout(startListening, 800);
            };
            uAr.onend = () => {
              lipSyncOpen = 0.0;
              setEmotion('HAPPY', 5000);
              setTimeout(fadeSubtitlesIfQuiet, 4000);
              if (isContinuousConversation) setTimeout(startListening, 800);
            };
            window.speechSynthesis.speak(uAr);
          } else {
            lipSyncOpen = 0.0;
            setEmotion('HAPPY', 5000);
            setTimeout(fadeSubtitlesIfQuiet, 4000);
            if (isContinuousConversation) setTimeout(startListening, 800);
          }
        };
        window.speechSynthesis.speak(uEn);
      } else if (arText) {
        const uAr = new SpeechSynthesisUtterance(arText);
        uAr.lang = 'ar-EG';
        const vAr = getBestVoice('ar');
        if (vAr) uAr.voice = vAr;
        uAr.rate = 0.92;
        uAr.pitch = 1.02;
        uAr.onerror = () => {
          lipSyncOpen = 0.0;
          setEmotion('HAPPY', 5000);
          if (isContinuousConversation) setTimeout(startListening, 800);
        };
        uAr.onend = () => {
          lipSyncOpen = 0.0;
          setEmotion('HAPPY', 5000);
          setTimeout(fadeSubtitlesIfQuiet, 4000);
          if (isContinuousConversation) setTimeout(startListening, 800);
        };
        window.speechSynthesis.speak(uAr);
      }
    }

    function showSubtitles(speaker, text) {
      const box = document.getElementById('subBox');
      const spk = document.getElementById('subSpeaker');
      const txt = document.getElementById('subText');
      if (box && spk && txt) {
        spk.textContent = speaker;
        txt.textContent = text;
        box.classList.remove('hidden');
      }
    }

    function fadeSubtitlesIfQuiet() {
      if (!window.speechSynthesis.speaking && !isLiveAudioPlaying) {
        const box = document.getElementById('subBox');
        if (box) box.classList.add('hidden');
      }
    }

    function updateSubtitles(speaker, text) {
      showSubtitles(speaker, text);
    }

    /* ==========================================================================
       4. Front Camera Vision & Software Gaze Elevation (No Neck Servo)
       ========================================================================== */
    async function initCamera() {
      const video = document.getElementById('camVideo');
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn('Camera getUserMedia not supported.');
        return;
      }
      try {
        camStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
          audio: false
        });
        video.srcObject = camStream;
        video.onloadedmetadata = () => {
          video.play();
          document.getElementById('camTag').textContent = 'GAZE: ACTIVE';
          requestAnimationFrame(processCameraFrame);
        };
      } catch (err) {
        console.warn('Front camera init notice:', err);
        document.getElementById('camTag').textContent = 'GAZE: LOCAL';
      }
    }

    function processCameraFrame() {
      const video = document.getElementById('camVideo');
      const overlay = document.getElementById('camOverlay');
      if (!video || video.paused || video.ended || !overlay) {
        requestAnimationFrame(processCameraFrame);
        return;
      }

      overlay.width = video.videoWidth || 320;
      overlay.height = video.videoHeight || 240;
      const ctxOv = overlay.getContext('2d');

      // Zero-dependency Optical Centroid & Elevation Tracker
      const faceBox = detectFaceByLuminance(video, overlay.width, overlay.height);

      if (faceBox) {
        const normX = (faceBox.cx / overlay.width - 0.5) * 2;
        const normY = (faceBox.cy / overlay.height - 0.5) * 2;

        targetGazeX = normX * 0.9;
        targetGazeY = normY * 0.9;

        // Elevation Mapping: Tall adult vs Child / Seated
        const gazeText = document.getElementById('gazeText');
        if (normY < -0.2) {
          if (gazeText) gazeText.textContent = 'GAZE: TALL ADULT ↑';
        } else if (normY > 0.2) {
          if (gazeText) gazeText.textContent = 'GAZE: CHILD / SEATED ↓';
        } else {
          if (gazeText) gazeText.textContent = 'GAZE: EYE CONTACT ◉';
        }

        // Proximity detection
        const areaRatio = (faceBox.w * faceBox.h) / (overlay.width * overlay.height);
        if (areaRatio > 0.08) {
          visitorDetectionCount++;
          if (visitorDetectionCount > 15 && !visitorNear) {
            visitorNear = true;
            onVisitorApproached();
          }
        } else {
          visitorDetectionCount = Math.max(0, visitorDetectionCount - 1);
          if (visitorDetectionCount === 0) visitorNear = false;
        }

        ctxOv.clearRect(0, 0, overlay.width, overlay.height);
        ctxOv.strokeStyle = '#00e5ff';
        ctxOv.lineWidth = 2;
        ctxOv.strokeRect(faceBox.x, faceBox.y, faceBox.w, faceBox.h);
      } else {
        targetGazeX = 0;
        targetGazeY = 0;
        const gazeText = document.getElementById('gazeText');
        if (gazeText) gazeText.textContent = 'GAZE: IDLE SCAN';
      }

      requestAnimationFrame(processCameraFrame);
    }

    function detectFaceByLuminance(video, w, h) {
      if (w === 0 || h === 0) return null;
      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = 80;
      tempCanvas.height = 60;
      const tCtx = tempCanvas.getContext('2d');
      tCtx.drawImage(video, 0, 0, 80, 60);

      const imgData = tCtx.getImageData(0, 0, 80, 60);
      const data = imgData.data;

      let sumX = 0, sumY = 0, count = 0;
      for (let y = 10; y < 50; y++) {
        for (let x = 15; x < 65; x++) {
          const idx = (y * 80 + x) * 4;
          const r = data[idx];
          const g = data[idx + 1];
          const b = data[idx + 2];
          // Optical skin tone filter
          if (r > 60 && g > 40 && b > 20 && r > g && (r - g) > 12 && r > b) {
            sumX += x;
            sumY += y;
            count++;
          }
        }
      }

      if (count > 80) {
        const avgX = (sumX / count) / 80 * w;
        const avgY = (sumY / count) / 60 * h;
        const boxSize = Math.max(60, Math.min(w, h) * 0.42);
        return {
          x: avgX - boxSize * 0.5,
          y: avgY - boxSize * 0.5,
          w: boxSize,
          h: boxSize,
          cx: avgX,
          cy: avgY
        };
      }
      return null;
    }

    function onVisitorApproached() {
      const now = Date.now();
      if (now - lastVisitorGreetingTime > 25000) {
        lastVisitorGreetingTime = now;
        setEmotion('ATTENTIVE');
        speakReply("Hello there! Welcome to IEEE RAS at E-JUST. Please tap your NFC badge on the chest reader to begin.", 'HAPPY');
      }
    }

    function toggleCamPip() {
      const pip = document.getElementById('camPip');
      if (pip) pip.classList.toggle('visible');
    }

    /* ==========================================================================
       5. Web Bluetooth (Nordic UART Service) Implementation
       ========================================================================== */
    async function connectBle() {
      logBle('Requesting Bluetooth device (NUS)...');
      try {
        bleDevice = await navigator.bluetooth.requestDevice({
          filters: [{ namePrefix: 'AURA' }, { namePrefix: 'VIP' }, { namePrefix: 'ESP32' }],
          optionalServices: [NORDIC_UART_SERVICE]
        });

        bleDevice.addEventListener('gattserverdisconnected', onBleDisconnected);
        logBle('Connecting to GATT server...');

        bleServer = await bleDevice.gatt.connect();
        const service = await bleServer.getPrimaryService(NORDIC_UART_SERVICE);

        rxChar = await service.getCharacteristic(NORDIC_RX_CHAR);
        txChar = await service.getCharacteristic(NORDIC_TX_CHAR);

        await txChar.startNotifications();
        txChar.addEventListener('characteristicvaluechanged', onBleNotify);

        bleConnected = true;
        updateBleUI(true);
        logBle('Web Bluetooth Nordic UART Link Connected!');
      } catch (err) {
        console.warn('BLE connect error:', err);
        logBle('BLE Connection cancelled or failed: ' + err.message);
        bleConnected = false;
        updateBleUI(false);
      }
    }

    function onBleDisconnected() {
      logBle('ESP32 BLE Disconnected.');
      bleConnected = false;
      updateBleUI(false);
    }

    function updateBleUI(connected) {
      const dot = document.getElementById('bleDot');
      const txt = document.getElementById('bleText');
      const btnTxt = document.getElementById('bleActionText');
      if (dot) dot.className = connected ? 'dot green' : 'dot';
      if (txt) txt.textContent = connected ? 'BLE: ON' : 'BLE: OFF';
      if (btnTxt) btnTxt.textContent = connected ? 'ESP32 CONNECTED' : 'PAIR ESP32 (BLE)';
    }

    function onBleNotify(event) {
      const value = event.target.value;
      const decoder = new TextDecoder('utf-8');
      const text = decoder.decode(value).trim();
      logBle('BLE RX <-- ' + text);

      try {
        const json = JSON.parse(text);
        if (json.event === 'NFC_TAP') {
          handleNfcTap(json.uid, json.name, json.dest, json.markers);
        } else if (json.event === 'ARRIVED') {
          handleEscortArrived(json.dest);
        } else if (json.event === 'OBSTACLE') {
          setEmotion('SURPRISED', 2000);
          showSubtitles('SAFETY STOP', `Obstacle detected at ${json.dist} cm.`);
        }
      } catch (e) {
        // Plain string fallback
        if (text.includes('NFC_TAP')) {
          handleNfcTap('A1:B2:C3:D4', 'Prof. Amr Adly', 'Main Conference Hall', 1);
        }
      }
    }

    // Universal 20-byte BLE chunking for ATT MTU safety
    async function sendBleCommand(jsonObj) {
      if (!rxChar || !bleConnected) {
        logBle('BLE not connected. Command buffered: ' + JSON.stringify(jsonObj));
        return;
      }
      const dataStr = JSON.stringify(jsonObj) + '\n';
      const encoder = new TextEncoder();
      const bytes = encoder.encode(dataStr);

      for (let i = 0; i < bytes.length; i += 20) {
        const chunk = bytes.slice(i, i + 20);
        try {
          await rxChar.writeValueWithoutResponse(chunk);
        } catch (e) {
          try {
            await rxChar.writeValue(chunk);
          } catch (err2) {
            console.warn('BLE chunk write error:', err2);
          }
        }
        await new Promise(r => setTimeout(r, 15));
      }
      logBle('BLE TX --> ' + dataStr.trim());
    }

    function logBle(msg) {
      console.log('[BLE]', msg);
      const box = document.getElementById('bleLogBox');
      if (box) {
        box.textContent = (box.textContent + '\n' + msg).slice(-1000);
        box.scrollTop = box.scrollHeight;
      }
    }

    /* ==========================================================================
       6. VIP Welcoming & Autonomous Escort Sequence
       ========================================================================== */
    function handleNfcTap(uid, name, dest, markers) {
      activeUid = uid;
      currentRobotState = 'VIP_WELCOME';

      const guest = name || 'Distinguished Guest';
      const destination = dest || 'Main Conference Hall';
      const arabicTitle = ARABIC_TITLES[name] || 'أهلاً وسهلاً بضيفنا الكريم في الجامعة المصرية اليابانية';

      setEmotion('HAPPY', 6000);

      const enWelcome = `Welcome ${guest}! It is an absolute honour to receive you at IEEE RAS E-JUST. Please follow me to the ${destination}.`;
      speakWelcome(enWelcome, arabicTitle);

      // Trigger ESP32 line-following motors
      setTimeout(() => {
        currentRobotState = 'ESCORTING';
        sendBleCommand({
          cmd: 'START_ESCORT',
          name: guest,
          dest: destination,
          markers: markers || 1,
          uid: uid
        });
      }, 4500);
    }

    function handleEscortArrived(dest) {
      currentRobotState = 'ARRIVED';
      setEmotion('HAPPY', 8000);
      const arrivalMsg = `We have safely arrived at the ${dest || 'Conference Hall'}. It was my absolute privilege to guide you today!`;
      speakReply(arrivalMsg, 'HAPPY');
    }

    function triggerVIP(name, arTitle, dest, markers, uid) {
      handleNfcTap(uid, name, dest, markers);
    }

    function resetStandby(notifyEsp32 = true) {
      currentRobotState = 'IDLE';
      setEmotion('ATTENTIVE');
      showSubtitles('AURA-EJUST v3.0', 'Welcome to IEEE RAS E-JUST. Please tap your NFC badge on the chest reader to begin escort.');
      if (notifyEsp32) {
        sendBleCommand({ cmd: 'RESET' });
      }
    }

    /* ==========================================================================
       7. Multi-Engine AI Brain (Antigravity Relay, OpenRouter, Gemini Live, Offline)
       ========================================================================== */
    function initLiveWebSocket() {
      if (selectedModel !== 'gemini-3.8-live') {
        if (liveWs) {
          try { liveWs.close(); } catch(e) {}
          liveWs = null;
          isLiveWsConnected = false;
        }
        return;
      }

      if (liveWs && (liveWs.readyState === WebSocket.OPEN || liveWs.readyState === WebSocket.CONNECTING)) {
        return;
      }

      const wsUrl = `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=${apiKey}`;
      logBle('Connecting Gemini Live WebSocket...');

      try {
        liveWs = new WebSocket(wsUrl);
        liveWs.onopen = () => {
          isLiveWsConnected = true;
          document.getElementById('geminiDot').className = 'dot green';
          document.getElementById('geminiText').textContent = 'AI: LIVE WS';
          const setupMsg = {
            setup: {
              model: 'models/gemini-3.8-live',
              generationConfig: {
                responseModalities: ['AUDIO'],
                speechConfig: {
                  voiceConfig: {
                    prebuiltVoiceConfig: {
                      voiceName: selectedVoice === 'native-tts' ? 'Aoede' : selectedVoice
                    }
                  }
                }
              },
              systemInstruction: {
                parts: [{
                  text: 'You are AURA-EJUST v3.0, the flagship autonomous VIP reception humanoid robot developed by IEEE RAS at Egypt-Japan University of Science and Technology (E-JUST). Provide concise, warm, dignified spoken answers (1-2 sentences). When thanked, include [EMOTION: HAPPY]. When asked technical questions, include [EMOTION: CURIOUS].'
                }]
              }
            }
          };
          liveWs.send(JSON.stringify(setupMsg));
        };

        liveWs.onmessage = async (evt) => {
          try {
            let data;
            if (evt.data instanceof Blob) {
              const text = await evt.data.text();
              data = JSON.parse(text);
            } else {
              data = JSON.parse(evt.data);
            }

            const sc = data.serverContent;
            if (!sc) return;

            if (sc.outputTranscription && sc.outputTranscription.text) {
              showSubtitles('AURA-EJUST (LIVE)', sc.outputTranscription.text);
            }

            if (sc.modelTurn && sc.modelTurn.parts) {
              for (const part of sc.modelTurn.parts) {
                if (part.inlineData && part.inlineData.data) {
                  playLivePcmChunk(part.inlineData.data);
                }
              }
            }
          } catch (err) {
            console.warn('Error parsing Live WS message:', err);
          }
        };

        liveWs.onerror = () => {
          document.getElementById('geminiDot').className = 'dot gold';
        };
        liveWs.onclose = () => {
          isLiveWsConnected = false;
        };
      } catch (err) {
        console.warn('WebSocket init exception:', err);
      }
    }

    function playLivePcmChunk(base64Data) {
      try {
        if (!audioCtx) {
          audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
        }
        if (audioCtx.state === 'suspended') {
          audioCtx.resume();
        }

        const binaryString = atob(base64Data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }

        const int16 = new Int16Array(bytes.buffer);
        const float32 = new Float32Array(int16.length);
        for (let i = 0; i < int16.length; i++) {
          float32[i] = int16[i] / 32768.0;
        }

        const audioBuffer = audioCtx.createBuffer(1, float32.length, 24000);
        audioBuffer.copyToChannel(float32, 0);

        const source = audioCtx.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioCtx.destination);

        const now = audioCtx.currentTime;
        if (nextAudioStartTime < now) {
          nextAudioStartTime = now;
        }
        source.start(nextAudioStartTime);
        nextAudioStartTime += audioBuffer.duration;

        setEmotion('SPEAKING');
        lipSyncOpen = 1.0;
        isLiveAudioPlaying = true;

        source.onended = () => {
          if (audioCtx.currentTime >= nextAudioStartTime - 0.05) {
            lipSyncOpen = 0.0;
            isLiveAudioPlaying = false;
            setEmotion('ATTENTIVE', 3000);
            setTimeout(fadeSubtitlesIfQuiet, 3000);
            if (isContinuousConversation) {
              setTimeout(startListening, 600);
            }
          }
        };
      } catch (e) {
        console.warn('PCM decode/playback error:', e);
      }
    }

    function sendLiveRealtimeText(text) {
      if (liveWs && liveWs.readyState === WebSocket.OPEN) {
        liveWs.send(JSON.stringify({ realtimeInput: { text: text } }));
        return true;
      }
      return false;
    }

    // Hands-Free Natural Continuous Conversation Manager
    function toggleContinuousMode() {
      isContinuousConversation = !isContinuousConversation;
      updateContinuousUI();
      if (isContinuousConversation) {
        startListening();
      } else {
        stopListening();
      }
    }

    function updateContinuousUI() {
      const btn = document.getElementById('continuousBtn');
      const txt = document.getElementById('continuousText');
      if (btn && txt) {
        if (isContinuousConversation) {
          txt.textContent = 'AUTO-TALK: ON';
        } else {
          txt.textContent = 'AUTO-TALK: OFF';
        }
      }
    }

    function startListening() {
      if (isListening || (window.speechSynthesis && window.speechSynthesis.speaking) || isLiveAudioPlaying) return;
      if (!recognition) initSpeechRecognition();
      try {
        recognition.start();
      } catch (e) {
        // Recognition already active
      }
    }

    function stopListening() {
      isListening = false;
      const micBtn = document.getElementById('micBtn');
      const micTxt = document.getElementById('micText');
      if (micBtn) micBtn.classList.remove('listening');
      if (micTxt) micTxt.textContent = 'TAP TO SPEAK';
    }

    function toggleMic() {
      unlockAudioAndListen();
      if (!recognition) initSpeechRecognition();
      if (isListening) {
        isContinuousConversation = false;
        updateContinuousUI();
        try { recognition.stop(); } catch(e) {}
        stopListening();
      } else {
        isContinuousConversation = true;
        updateContinuousUI();
        startListening();
      }
    }

    function initSpeechRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        console.warn('Web Speech Recognition API not available.');
        return;
      }

      if (recognition) {
        try { recognition.abort(); } catch(e) {}
      }

      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        isListening = true;
        const micTxt = document.getElementById('micText');
        if (micTxt) micTxt.textContent = 'LISTENING...';
        showSubtitles('YOU', 'Listening...');
        setEmotion('ATTENTIVE');
      };

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results).map(r => r[0].transcript).join('');
        showSubtitles('YOU', transcript);
        if (event.results[0].isFinal) {
          handleUserUtterance(transcript);
        }
      };

      recognition.onerror = (e) => {
        isListening = false;
        if (e.error === 'no-speech' && isContinuousConversation && !window.speechSynthesis.speaking && !isLiveAudioPlaying) {
          setTimeout(() => {
            if (isContinuousConversation && !isListening && !window.speechSynthesis.speaking && !isLiveAudioPlaying) {
              startListening();
            }
          }, 400);
          return;
        }
        stopListening();
      };

      recognition.onend = () => {
        isListening = false;
        if (isContinuousConversation && !window.speechSynthesis.speaking && !isLiveAudioPlaying) {
          setTimeout(() => {
            if (isContinuousConversation && !isListening && !window.speechSynthesis.speaking && !isLiveAudioPlaying) {
              startListening();
            }
          }, 500);
        } else {
          stopListening();
        }
      };
    }

    // Contextual Sentiment & Emotion Extractor
    function extractContextEmotion(text) {
      const lower = text.toLowerCase();
      // Gratitude context -> HAPPY
      if (lower.includes('thank') || lower.includes('thanks') || lower.includes('appreciate') || lower.includes('good job') || lower.includes('awesome') || lower.includes('شكرا') || lower.includes('تسلم')) {
        return 'HAPPY';
      }
      // Question / Inquiring context -> CURIOUS
      if (lower.includes('what') || lower.includes('how') || lower.includes('why') || lower.includes('where') || lower.includes('who') || lower.includes('can you') || lower.includes('tell me') || lower.includes('أين') || lower.includes('كيف') || lower.includes('ما هو')) {
        return 'CURIOUS';
      }
      // Surprise context
      if (lower.includes('wow') || lower.includes('really') || lower.includes('incredible') || lower.includes('amazing')) {
        return 'SURPRISED';
      }
      return 'ATTENTIVE';
    }

    async function handleUserUtterance(userText) {
      const detectedEmotion = extractContextEmotion(userText);
      setEmotion(detectedEmotion === 'HAPPY' ? 'HAPPY' : 'THINKING');
      showSubtitles('AURA (THINKING)', 'Reasoning with conversational brain...');

      let replyText = '';

      if (apiProvider === 'antigravity-relay') {
        try {
          replyText = await callAntigravityRelayAPI(userText);
        } catch (err) {
          console.warn('Antigravity relay bridge failed, falling back to autonomous dialog:', err);
          replyText = generateAutonomousReply(userText);
        }
      } else if (apiProvider === 'openrouter' && openRouterKey && openRouterKey.length > 5) {
        try {
          replyText = await callOpenRouterAPI(userText);
        } catch (err) {
          console.warn('OpenRouter API call failed, falling back to autonomous dialog engine:', err);
          replyText = generateAutonomousReply(userText);
        }
      } else if (apiProvider === 'gemini') {
        if (selectedModel === 'gemini-3.8-live' && isLiveWsConnected && liveWs && liveWs.readyState === WebSocket.OPEN) {
          const liveSent = sendLiveRealtimeText(userText);
          if (liveSent) return;
        }

        if (selectedModel !== 'offline-autonomous' && selectedModel !== 'gemini-3.8-live' && apiKey && apiKey.length > 10) {
          try {
            replyText = await callGeminiAPI(userText);
          } catch (err) {
            console.warn('Gemini API call failed, falling back to autonomous dialog engine:', err);
            replyText = generateAutonomousReply(userText);
          }
        } else {
          replyText = generateAutonomousReply(userText);
        }
      } else {
        replyText = generateAutonomousReply(userText);
      }

      let finalEmotion = detectedEmotion;
      if (replyText.includes('[EMOTION: HAPPY]')) finalEmotion = 'HAPPY';
      if (replyText.includes('[EMOTION: CURIOUS]')) finalEmotion = 'CURIOUS';

      const cleanedReply = replyText.replace(/\[EMOTION:.*?\]/g, '').trim();

      setEmotion('SPEAKING');
      showSubtitles('AURA-EJUST', cleanedReply);

      // Speak using natural neural human voice & animate mouth
      speakReply(cleanedReply, finalEmotion);
    }

    async function callAntigravityRelayAPI(promptText) {
      const systemInstruction = `You are AURA-EJUST v3.0, the autonomous VIP receptionist and humanoid robot developed by IEEE RAS at Egypt-Japan University of Science and Technology (E-JUST). Keep responses very concise (1-2 sentences), dignified, and warm for spoken output. If the guest thanks you, include the tag [EMOTION: HAPPY]. If they ask a technical question, include [EMOTION: CURIOUS].`;

      let cleanBase = '';
      if (window.location && window.location.origin && window.location.origin.startsWith('http')) {
        cleanBase = window.location.origin;
      } else {
        cleanBase = bridgeUrl || 'http://192.168.1.19:8080';
      }
      cleanBase = cleanBase.replace(/\/+$/, '');

      const response = await fetch(`${cleanBase}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Bypass-Tunnel-Reminder': 'true'
        },
        body: JSON.stringify({
          prompt: promptText,
          system_instruction: systemInstruction
        })
      });

      if (!response.ok) {
        throw new Error(`Relay HTTP ${response.status}`);
      }

      const json = await response.json();
      return `[EMOTION: ${json.emotion || 'ATTENTIVE'}] ${json.reply}`;
    }

    async function callOpenRouterAPI(promptText) {
      const systemInstruction = `You are AURA-EJUST v3.0, the autonomous VIP receptionist and humanoid robot developed by IEEE RAS at Egypt-Japan University of Science and Technology (E-JUST). Keep responses very concise (1-2 sentences), dignified, and warm for spoken output. If the guest thanks you, include the tag [EMOTION: HAPPY]. If they ask a technical question, include [EMOTION: CURIOUS].`;

      const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${openRouterKey}`,
          'HTTP-Referer': 'https://aura-ejust.local',
          'X-Title': 'AURA-EJUST v3.0 Humanoid'
        },
        body: JSON.stringify({
          model: openRouterModel,
          messages: [
            { role: 'system', content: systemInstruction },
            { role: 'user', content: promptText }
          ],
          temperature: 0.7,
          max_tokens: 150
        })
      });

      if (!response.ok) {
        throw new Error(`OpenRouter HTTP ${response.status}`);
      }

      const json = await response.json();
      if (json.choices && json.choices.length > 0 && json.choices[0].message) {
        return json.choices[0].message.content;
      }
      throw new Error('Empty OpenRouter response');
    }

    async function callGeminiAPI(promptText) {
      const systemInstruction = `You are AURA-EJUST v3.0, the autonomous VIP receptionist and humanoid robot developed by IEEE RAS at Egypt-Japan University of Science and Technology (E-JUST). Keep responses very concise (1-2 sentences), dignified, and warm for spoken output. If the guest thanks you, include the tag [EMOTION: HAPPY]. If they ask a technical question, include [EMOTION: CURIOUS].`;

      const targetModel = selectedModel === 'gemini-3.8-live' ? 'gemini-3.8-flash' : selectedModel;
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${targetModel}:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [
            { role: 'user', parts: [{ text: `${systemInstruction}\n\nGuest says: "${promptText}"` }] }
          ]
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const json = await response.json();
      return json.candidates[0].content.parts[0].text;
    }

    // High-Fidelity Offline Autonomous Smart Dialog Engine (Guarantees zero-downtime)
    function generateAutonomousReply(userText) {
      const lower = userText.toLowerCase();

      if (lower.includes('thank') || lower.includes('شكرا')) {
        return '[EMOTION: HAPPY] You are most welcome! It is my absolute honor to assist you here at IEEE RAS E-JUST.';
      }
      if (lower.includes('who are you') || lower.includes('your name') || lower.includes('من أنت')) {
        return '[EMOTION: ATTENTIVE] I am AURA-EJUST v3.0, the flagship autonomous VIP reception humanoid created by the IEEE Robotics and Automation Society branch at E-JUST.';
      }
      if (lower.includes('hall') || lower.includes('conference') || lower.includes('theatre') || lower.includes('قاعة')) {
        return '[EMOTION: CURIOUS] The Main Conference Hall is located along the primary floor guide path, and the Grand Theatre is at station marker two. Please follow my lead!';
      }
      if (lower.includes('hello') || lower.includes('hi') || lower.includes('مرحبا') || lower.includes('أهلا')) {
        return '[EMOTION: HAPPY] Hello and welcome to E-JUST! I am ready to guide you to your session. Please feel free to tap your NFC badge.';
      }
      if (lower.includes('robot') || lower.includes('spec') || lower.includes('motor')) {
        return '[EMOTION: CURIOUS] I am powered by an ESP32 DevKit V1 with high-torque geared motors, 5-channel line tracking, front gaze vision, and Nordic UART BLE connectivity.';
      }
      return '[EMOTION: ATTENTIVE] Thank you for your inquiry. I am here to assist your visit and escort you to the IEEE RAS event halls at E-JUST.';
    }

    function sendTypedText() {
      const input = document.getElementById('userTextInput');
      if (!input) return;
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      unlockAudioAndListen();
      showSubtitles('YOU', text);
      handleUserUtterance(text);
    }

    function testEmotion(emotion, sampleSpeech) {
      unlockAudioAndListen();
      handleUserUtterance(sampleSpeech);
    }

    /* ==========================================================================
       8. UI, Drawer, Settings & Fullscreen Helpers
       ========================================================================== */
    function toggleDrawer() {
      const drawer = document.getElementById('controlDrawer');
      if (drawer) drawer.classList.toggle('open');
    }

    function toggleFullScreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    }

    function unlockAudioAndListen() {
      if ('speechSynthesis' in window) {
        try { window.speechSynthesis.resume(); } catch(e) {}
      }
      if (audioCtx && audioCtx.state === 'suspended') {
        try { audioCtx.resume(); } catch(e) {}
      }
      const wakePrompt = document.getElementById('wakePrompt');
      if (wakePrompt) wakePrompt.style.display = 'none';

      if (!isListening && isContinuousConversation) {
        startListening();
      }
    }

    function updateProviderVisibility() {
      const prov = document.getElementById('providerSelect').value;
      const agGroup = document.getElementById('antigravitySettingsGroup');
      const orGroup = document.getElementById('openrouterSettingsGroup');
      const gemGroup = document.getElementById('geminiSettingsGroup');
      if (agGroup) agGroup.style.display = prov === 'antigravity-relay' ? 'block' : 'none';
      if (orGroup) orGroup.style.display = prov === 'openrouter' ? 'block' : 'none';
      if (gemGroup) gemGroup.style.display = prov === 'gemini' ? 'block' : 'none';
    }

    function updateTelemetryPill() {
      const dot = document.getElementById('geminiDot');
      const txt = document.getElementById('geminiText');
      if (!dot || !txt) return;
      if (apiProvider === 'antigravity-relay') {
        dot.className = 'dot green';
        txt.textContent = 'AI: PRO SESSION';
      } else if (apiProvider === 'openrouter') {
        dot.className = openRouterKey ? 'dot green' : 'dot gold';
        txt.textContent = openRouterKey ? 'AI: OPENROUTER' : 'OPENROUTER (NO KEY)';
      } else if (apiProvider === 'gemini') {
        dot.className = isLiveWsConnected ? 'dot green' : 'dot green';
        txt.textContent = selectedModel === 'gemini-3.8-live' ? 'GEMINI: LIVE WS' : 'GEMINI: REST';
      } else {
        dot.className = 'dot cyan';
        txt.textContent = 'AI: OFFLINE SMART';
      }
    }

    function openSettings() {
      document.getElementById('providerSelect').value = apiProvider;
      if (document.getElementById('bridgeUrlInput')) {
        document.getElementById('bridgeUrlInput').value = bridgeUrl;
      }
      document.getElementById('openRouterKeyInput').value = openRouterKey;
      document.getElementById('openRouterModelSelect').value = openRouterModel;
      document.getElementById('apiKeyInput').value = apiKey;
      document.getElementById('modelSelect').value = selectedModel;
      document.getElementById('voiceSelect').value = selectedVoice;
      document.getElementById('esp32IpInput').value = esp32Ip;
      updateProviderVisibility();
      document.getElementById('settingsModal').classList.add('open');
    }

    function closeSettings() {
      document.getElementById('settingsModal').classList.remove('open');
    }

    function saveSettings() {
      apiProvider = document.getElementById('providerSelect').value;
      if (document.getElementById('bridgeUrlInput')) {
        bridgeUrl = document.getElementById('bridgeUrlInput').value.trim() || (window.location.origin.startsWith('http') ? window.location.origin : 'http://192.168.1.19:8080');
        localStorage.setItem('AURA_BRIDGE_URL', bridgeUrl);
      }
      openRouterKey = document.getElementById('openRouterKeyInput').value.trim();
      openRouterModel = document.getElementById('openRouterModelSelect').value;
      apiKey = document.getElementById('apiKeyInput').value.trim() || DEFAULT_API_KEY;
      selectedModel = document.getElementById('modelSelect').value;
      selectedVoice = document.getElementById('voiceSelect').value;
      esp32Ip = document.getElementById('esp32IpInput').value.trim();

      localStorage.setItem('AURA_API_PROVIDER', apiProvider);
      localStorage.setItem('AURA_OPENROUTER_KEY', openRouterKey);
      localStorage.setItem('AURA_OPENROUTER_MODEL', openRouterModel);
      localStorage.setItem('AURA_GEMINI_KEY', apiKey);
      localStorage.setItem('AURA_GEMINI_MODEL', selectedModel);
      localStorage.setItem('AURA_VOICE', selectedVoice);
      localStorage.setItem('AURA_ESP32_IP', esp32Ip);

      if (apiProvider === 'gemini') {
        initLiveWebSocket();
      } else if (liveWs) {
        try { liveWs.close(); } catch(e) {}
        liveWs = null;
        isLiveWsConnected = false;
      }
      updateTelemetryPill();
      closeSettings();
    }

    // Startup Initialization
    window.addEventListener('DOMContentLoaded', () => {
      initCamera();
      initSpeechRecognition();
      if (apiProvider === 'gemini') {
        initLiveWebSocket();
      }
      updateTelemetryPill();
      updateContinuousUI();
      showSubtitles('AURA-EJUST v3.0', 'Welcome to IEEE RAS E-JUST. Tap anywhere to wake up voice & speech.');

      document.addEventListener('click', unlockAudioAndListen, { once: false });
      document.addEventListener('touchstart', unlockAudioAndListen, { once: false });
    });
  </script>
</body>
</html>
'''

with open(r'C:\VIP_Humanoid_Robot\WebApp_Screen\index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Successfully generated horizontal minimalist bionic face index.html ({len(html_content)} bytes)")
