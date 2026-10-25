"""
Rebuilds AURA-EJUST v3.0 WebApp with:
1. True Horizontal (Landscape 16:9 / 20:9) Layout:
   - Big, beautiful, expressive bionic face filling the top 75% of the screen.
   - Sleek, semi-transparent minimalist control bar at the bottom:
     [🎙️ TAP TO SPEAK] [💖 Thank You!] [💡 Ask Question] [Type a message... Send]
   - Never confusing: buttons are always visible, easy to touch, and immediately unlock audio/mic!
2. Expressive Face Gestures with Real Emotion & Feelings:
   - Distinctive Eyebrows with high arch for HAPPY, inquisitive tilt for CURIOUS, furrow for THINKING.
   - Large squircle capsule eyes with glowing iris and specular reflection glints.
   - Joyful curved smiling eyes (⌒) + blooming pink blushing cheeks (#FF2A85) when thanked.
   - Organic speaking mouth with syllable lip-sync waves.
3. Natural Human Voice Engine:
   - Auto-detects and prioritizes Google/Microsoft Natural Neural voices.
   - Safe fallbacks so Chrome on Android never mutes or crashes.
   - Calibrated pitch (1.05) and conversational pacing (0.95) with warm phrasing.
4. Preserves 100% of Web Bluetooth NUS, camera gaze tracking, and multi-engine AI (Antigravity Relay, OpenRouter, Gemini Live, Offline).
"""

import os

html_content = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <title>AURA-EJUST v3.0 — Horizontal Bionic Face & Speech Brain</title>
  <style>
    :root {
      --bg-black: #050408;
      --ejust-red: #C0121F;
      --ras-purple: #621B6D;
      --ras-violet: #9c27b0;
      --imperial-gold: #C8A45D;
      --neon-cyan: #00e5ff;
      --neon-magenta: #ff1744;
      --neon-green: #00e676;
      --blush-pink: #ff2a85;
      --text-white: #ffffff;
      --text-muted: #a09fa8;
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

    /* Horizontal Landscape Screen Container */
    .app-container {
      width: 100vw;
      height: 100vh;
      display: flex;
      flex-direction: column;
      position: relative;
      background: radial-gradient(circle at 50% 30%, rgba(98, 27, 109, 0.25), transparent 70%), var(--bg-black);
      overflow: hidden;
    }

    /* Top Subtle Brand & Status Bar */
    .top-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 18px;
      z-index: 20;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      background: rgba(8, 6, 12, 0.6);
      backdrop-filter: blur(8px);
    }
    .brand-tag {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 1.2px;
      color: var(--imperial-gold);
      text-transform: uppercase;
    }
    .badge-chip {
      background: linear-gradient(135deg, var(--ejust-red), var(--ras-purple));
      color: #fff;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 10px;
      font-weight: 900;
      letter-spacing: 0.8px;
    }
    .status-group {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .pill {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
      font-size: 10px;
      font-weight: 700;
      color: var(--text-muted);
      cursor: pointer;
    }
    .dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #666;
    }
    .dot.green { background: #00e676; box-shadow: 0 0 8px #00e676; }
    .dot.cyan { background: #00e5ff; box-shadow: 0 0 8px #00e5ff; }
    .dot.gold { background: var(--imperial-gold); box-shadow: 0 0 8px var(--imperial-gold); }
    .btn-header-icon {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #fff;
      padding: 4px 9px;
      border-radius: 8px;
      font-size: 11px;
      cursor: pointer;
      font-weight: 700;
    }

    /* Central Bionic Face Stage (75% of height) */
    .face-stage {
      flex: 1;
      position: relative;
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }
    #faceCanvas {
      width: 100%;
      height: 100%;
      display: block;
      cursor: pointer;
    }

    /* Subtitles Glass Pill */
    .subtitles-pill {
      position: absolute;
      bottom: 12px;
      left: 50%;
      transform: translateX(-50%);
      max-width: 86%;
      background: rgba(14, 10, 22, 0.78);
      border: 1px solid rgba(0, 229, 255, 0.25);
      border-radius: 20px;
      padding: 6px 18px;
      display: flex;
      align-items: center;
      gap: 10px;
      backdrop-filter: blur(12px);
      box-shadow: 0 6px 25px rgba(0, 0, 0, 0.8);
      pointer-events: none;
      transition: all 0.3s ease;
      z-index: 15;
    }
    .sub-speaker {
      font-size: 10px;
      font-weight: 800;
      color: var(--imperial-gold);
      letter-spacing: 1px;
      text-transform: uppercase;
      white-space: nowrap;
      border-right: 1px solid rgba(255, 255, 255, 0.15);
      padding-right: 8px;
    }
    .sub-text {
      font-size: 13px;
      font-weight: 600;
      color: #fff;
      line-height: 1.3;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 65vw;
    }

    /* Bottom Minimalist Interactive Dock */
    .bottom-dock {
      width: 100%;
      background: rgba(10, 8, 16, 0.88);
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(14px);
      padding: 8px 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      z-index: 20;
    }

    /* Chat input row */
    .chat-row {
      display: flex;
      gap: 8px;
      width: 100%;
    }
    .chat-input {
      flex: 1;
      background: rgba(0, 0, 0, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.18);
      border-radius: 8px;
      padding: 6px 12px;
      color: #fff;
      font-size: 12px;
      outline: none;
    }
    .chat-input:focus {
      border-color: var(--neon-cyan);
    }
    .btn-send {
      background: linear-gradient(135deg, var(--ejust-red), var(--ras-purple));
      border: none;
      color: #fff;
      padding: 6px 16px;
      border-radius: 8px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
    }

    /* Quick action buttons row */
    .action-row {
      display: flex;
      gap: 6px;
      align-items: center;
      overflow-x: auto;
      padding-bottom: 2px;
    }
    .btn-action {
      flex: 1;
      min-width: 100px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 7px 10px;
      border-radius: 8px;
      font-size: 11px;
      font-weight: 800;
      cursor: pointer;
      border: 1px solid transparent;
      white-space: nowrap;
      transition: all 0.2s;
    }
    .btn-mic {
      background: rgba(0, 229, 255, 0.15);
      border-color: var(--neon-cyan);
      color: var(--neon-cyan);
    }
    .btn-mic.listening {
      background: rgba(255, 23, 68, 0.3);
      border-color: var(--neon-magenta);
      color: #fff;
    }
    .btn-emote {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(255, 255, 255, 0.15);
      color: #fff;
    }
    .btn-emote:hover, .btn-emote:active {
      background: rgba(255, 255, 255, 0.18);
    }
    .btn-ble {
      background: rgba(98, 27, 109, 0.3);
      border-color: var(--ras-violet);
      color: #fff;
    }
    .btn-ble.connected {
      background: rgba(0, 230, 118, 0.2);
      border-color: var(--neon-green);
      color: #00e676;
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
      background: #140c1e;
      border: 1.5px solid var(--ejust-red);
      border-radius: 16px;
      width: 100%;
      max-width: 480px;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 10px 40px rgba(192, 18, 31, 0.4);
      overflow: hidden;
    }
    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 18px;
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
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .form-group { display: flex; flex-direction: column; gap: 4px; }
    .form-label { font-size: 10px; font-weight: 800; color: var(--text-muted); }
    .form-input, .form-select {
      background: rgba(0, 0, 0, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.18);
      border-radius: 8px;
      padding: 8px 12px;
      color: #fff;
      font-size: 12px;
      outline: none;
    }
    .ble-log-box {
      font-family: monospace;
      font-size: 10px;
      height: 60px;
      overflow-y: auto;
      background: #000;
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 6px;
      padding: 6px;
      color: #00e676;
    }

    /* Picture-in-picture front camera box */
    .cam-pip {
      position: absolute;
      top: 50px;
      right: 18px;
      width: 90px;
      height: 68px;
      border-radius: 8px;
      border: 1px solid var(--neon-cyan);
      background: #000;
      overflow: hidden;
      z-index: 15;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s;
    }
    .cam-pip.visible { opacity: 0.85; pointer-events: auto; }
    #camVideo { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
    #camOverlay { position: absolute; inset: 0; width: 100%; height: 100%; }
    .cam-tag { position: absolute; bottom: 2px; left: 2px; font-size: 7px; color: var(--neon-cyan); background: rgba(0,0,0,0.7); padding: 1px 3px; border-radius: 2px; }
  </style>
</head>
<body>
  <div class="app-container">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="brand-tag">
        <span class="badge-chip">E-JUST</span>
        <span>AURA-EJUST v3.0</span>
      </div>
      <div class="status-group">
        <div class="pill" id="emotionBadge">
          <span id="emotionIcon">😊</span>
          <span id="emotionText">ATTENTIVE</span>
        </div>
        <div class="pill" id="gazeBadge">
          <span>👁️</span>
          <span id="gazeText">GAZE: SCAN</span>
        </div>
        <div class="pill" id="blePill" onclick="connectBle()" title="ESP32 BLE Link">
          <span class="dot" id="bleDot"></span>
          <span id="bleText">BLE: OFF</span>
        </div>
        <div class="pill" id="aiPill" onclick="openSettings()" title="AI Model Status">
          <span class="dot green" id="geminiDot"></span>
          <span id="geminiText">AI: PRO SESSION</span>
        </div>
        <button class="btn-header-icon" onclick="toggleCamPip()" title="Camera PIP">📹</button>
        <button class="btn-header-icon" onclick="openSettings()" title="Settings">⚙️</button>
        <button class="btn-header-icon" onclick="toggleFullScreen()" title="Fullscreen">⛶</button>
      </div>
    </div>

    <!-- Main Central Face Canvas -->
    <div class="face-stage" id="faceContainer">
      <canvas id="faceCanvas" onclick="unlockAudioAndListen()"></canvas>

      <!-- Subtitles floating pill -->
      <div class="subtitles-pill" id="subBox">
        <div class="sub-speaker" id="subSpeaker">AURA-EJUST</div>
        <div class="sub-text" id="subText">Welcome to IEEE RAS E-JUST. Tap "Thank You" or Mic to speak.</div>
      </div>

      <!-- Camera PIP -->
      <div class="cam-pip" id="camPip">
        <video id="camVideo" autoplay playsinline muted></video>
        <canvas id="camOverlay"></canvas>
        <span class="cam-tag" id="camTag">GAZE: OFF</span>
      </div>
    </div>

    <!-- Bottom Interactive Control Dock -->
    <div class="bottom-dock">
      <!-- Typed message row -->
      <div class="chat-row">
        <input type="text" id="userTextInput" class="chat-input" placeholder="Type a message (e.g. 'Thank you AURA', 'Where is the hall?')..." onkeydown="if(event.key==='Enter') sendTypedText()" />
        <button class="btn-send" onclick="sendTypedText()">Send</button>
      </div>

      <!-- Direct action & emotion buttons -->
      <div class="action-row">
        <button class="btn-action btn-mic" id="micBtn" onclick="toggleMic()">
          <span id="micIcon">🎙️</span>
          <span id="micText">TAP TO SPEAK</span>
        </button>
        <button class="btn-action btn-emote" onclick="testEmotion('HAPPY', 'Thank you so much AURA, you did an amazing job!')">
          💖 Thank You!
        </button>
        <button class="btn-action btn-emote" onclick="testEmotion('CURIOUS', 'Can you tell me about the E-JUST robotics lab?')">
          💡 Ask Question
        </button>
        <button class="btn-action btn-ble" id="bleActionBtn" onclick="connectBle()">
          <span>📶</span>
          <span id="bleActionText">PAIR ESP32</span>
        </button>
        <button class="btn-action btn-emote" id="continuousBtn" onclick="toggleContinuousMode()">
          <span>🔄</span>
          <span id="continuousText">AUTO-TALK: ON</span>
        </button>
        <button class="btn-action btn-emote" onclick="triggerVIP('Prof. Amr Adly', 'أهلاً وسهلاً أ.د. عمرو عدلي — رئيس الجامعة المصرية اليابانية', 'Main Conference Hall', 1, 'A1:B2:C3:D4')">
          🎓 Prof. Amr
        </button>
        <button class="btn-action btn-emote" onclick="triggerVIP('Dr. Mariam Hassan', 'أهلاً بكِ د. مريم حسن — المتحدث الرئيسي لـ IEEE RAS', 'E-JUST Grand Theatre', 2, 'E5:F6:07:18')">
          🤖 Dr. Mariam
        </button>
      </div>
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
            <option value="antigravity-relay">Antigravity Local Relay Bridge (Free PC Pro Session)</option>
            <option value="openrouter">OpenRouter API (Free Models: Llama 3.3 70B, DeepSeek, Claude)</option>
            <option value="gemini">Google Gemini API (Google AI Studio Key / Live WS)</option>
            <option value="offline-autonomous">Offline Autonomous Smart Dialog (Zero Quota Needed)</option>
          </select>
        </div>

        <div id="antigravitySettingsGroup">
          <div class="form-group">
            <label class="form-label">Relay Bridge Address (PC Gateway)</label>
            <input type="text" id="bridgeUrlInput" class="form-input" placeholder="http://192.168.1.19:8080" />
          </div>
        </div>

        <div id="openrouterSettingsGroup" style="display: none;">
          <div class="form-group">
            <label class="form-label">OpenRouter API Key</label>
            <input type="password" id="openRouterKeyInput" class="form-input" placeholder="sk-or-v1-..." />
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
          <label class="form-label">Voice &amp; Persona</label>
          <select id="voiceSelect" class="form-select">
            <option value="auto-natural">Auto-Select Best Natural Voice (Warm &amp; Friendly)</option>
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
      <div class="modal-footer" style="padding: 10px 18px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: flex-end;">
        <button class="btn-send" onclick="saveSettings()">Save &amp; Apply</button>
      </div>
    </div>
  </div>

  <script>
    /* ==========================================================================
       AURA-EJUST v3.0 — Horizontal Bionic Face, Camera Vision, BLE & Speech
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
    let selectedVoice = localStorage.getItem('AURA_VOICE') || 'auto-natural';
    let esp32Ip = localStorage.getItem('AURA_ESP32_IP') || '192.168.4.1';

    // Bluetooth Objects
    let bleDevice = null;
    let bleServer = null;
    let rxChar = null;
    let txChar = null;
    let bleConnected = false;

    // Face & Emotion State
    let currentEmotion = 'ATTENTIVE'; // ATTENTIVE, HAPPY, CURIOUS, THINKING, SPEAKING, SURPRISED
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

    // Blinking
    let blinkProgress = 0;
    let isBlinking = false;
    let nextBlinkTime = performance.now() + 2500;
    let lipSyncOpen = 0.0;
    let speechAudioEnergy = 0.0;

    // Conversational & Live Audio State
    let isContinuousConversation = true;
    let isListening = false;
    let recognition = null;
    let liveWs = null;
    let isLiveWsConnected = false;
    let isLiveAudioPlaying = false;
    let audioCtx = null;
    let nextAudioStartTime = 0;

    // Camera Vision State
    let camStream = null;
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
       2. Expressive Organic Bionic Face Canvas Engine (60 FPS)
       ========================================================================== */
    const canvas = document.getElementById('faceCanvas');
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
      const container = document.getElementById('faceContainer');
      const w = container ? container.clientWidth : window.innerWidth;
      const h = container ? container.clientHeight : window.innerHeight;
      const dpr = window.devicePixelRatio || 1;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    window.addEventListener('resize', resizeCanvas);
    setTimeout(resizeCanvas, 30);

    function updateSaccades(now) {
      if (now > nextSaccadeTime) {
        if (Math.random() < 0.6) {
          saccadeX = (Math.random() - 0.5) * 0.10;
          saccadeY = (Math.random() - 0.5) * 0.06;
        } else {
          saccadeX = 0;
          saccadeY = 0;
        }
        nextSaccadeTime = now + 1800 + Math.random() * 2500;
      }
    }

    function renderFace(now) {
      const container = document.getElementById('faceContainer');
      const w = container ? container.clientWidth : window.innerWidth;
      const h = container ? container.clientHeight : window.innerHeight;

      ctx.clearRect(0, 0, w, h);

      // Living micro-saccades & breathing cycle
      updateSaccades(now);
      const breath = Math.sin(now * 0.0022) * 0.015;

      // Smooth gaze interpolation
      currentGazeX += ((targetGazeX + saccadeX) - currentGazeX) * 0.14;
      currentGazeY += ((targetGazeY + saccadeY) - currentGazeY) * 0.14;

      // Organic Blinking
      if (!isBlinking && now > nextBlinkTime) {
        isBlinking = true;
        blinkProgress = 0;
      }
      if (isBlinking) {
        blinkProgress += 0.16;
        if (blinkProgress >= 1.0) {
          isBlinking = false;
          blinkProgress = 0;
          nextBlinkTime = now + 2400 + Math.random() * 3000;
        }
      }
      const blinkFactor = isBlinking ? Math.sin(blinkProgress * Math.PI) : 0;

      // Glowing Blush Cheeks (Fades in when HAPPY)
      if (currentEmotion === 'HAPPY') {
        blushAlpha = Math.min(1.0, blushAlpha + 0.07);
      } else {
        blushAlpha = Math.max(0.0, blushAlpha - 0.03);
      }

      // Horizontal Geometry (Wide & Expressive)
      const eyeSpacing = Math.min(w * 0.22, 220);
      const eyeW = Math.min(w * 0.20, h * 0.44, 230) * (1.0 + breath);
      const eyeH = Math.min(h * 0.44, w * 0.18, 190) * (1.0 + breath);
      const leftEyeX = w * 0.5 - eyeSpacing;
      const rightEyeX = w * 0.5 + eyeSpacing;
      const eyeY = h * 0.42;

      // Draw Expressive Eyebrows
      drawEyebrow(leftEyeX, eyeY, eyeW, currentEmotion, 'left', now);
      drawEyebrow(rightEyeX, eyeY, eyeW, currentEmotion, 'right', now);

      // Draw Bionic Eyes
      drawBionicEye(leftEyeX, eyeY, eyeW, eyeH, currentGazeX, currentGazeY, blinkFactor, 'left', now);
      drawBionicEye(rightEyeX, eyeY, eyeW, eyeH, currentGazeX, currentGazeY, blinkFactor, 'right', now);

      // Draw Glowing Cherry-Pink Blushing Cheeks
      if (blushAlpha > 0.01) {
        const blushR = eyeW * 0.36;
        drawCheekBlush(leftEyeX - eyeW * 0.28, eyeY + eyeH * 0.56, blushR, blushAlpha);
        drawCheekBlush(rightEyeX + eyeW * 0.28, eyeY + eyeH * 0.56, blushR, blushAlpha);
      }

      // Draw Organic Cyber Mouth with Lip-Sync
      drawCyberMouth(w * 0.5, h * 0.77, eyeW * 0.92, currentEmotion, now);

      requestAnimationFrame(renderFace);
    }
    requestAnimationFrame(renderFace);

    // Expressive Eyebrows
    function drawEyebrow(cx, cy, eyeW, emotion, side, now) {
      ctx.save();
      ctx.translate(cx, cy);

      const sign = (side === 'left' ? -1 : 1);
      let browY = -eyeW * 0.52;
      let browTilt = 0;
      let browArch = 0;
      let browWidth = eyeW * 0.65;

      if (emotion === 'HAPPY') {
        browY -= 14;
        browArch = -16;
        browTilt = sign * 4;
      } else if (emotion === 'CURIOUS') {
        if (side === 'left') {
          browY -= 20;
          browTilt = 10;
          browArch = -12;
        } else {
          browY += 4;
          browTilt = -6;
        }
      } else if (emotion === 'THINKING') {
        browY += 8;
        browTilt = sign * -14;
        browArch = 6;
      } else if (emotion === 'SURPRISED') {
        browY -= 28;
        browArch = -20;
      } else if (emotion === 'SPEAKING') {
        const cadence = Math.sin(now * 0.008) * 3.5;
        browY -= 6 + cadence;
        browTilt = sign * 3;
      } else {
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

      const squircleW = w;
      const squircleH = h;
      const cornerR = Math.min(w, h) * 0.38;

      // 1. HAPPY: Morph into joyous curved crescents (⌒)
      if (currentEmotion === 'HAPPY') {
        ctx.strokeStyle = '#00f0ff';
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 24;
        ctx.lineWidth = 14;
        ctx.lineCap = 'round';

        ctx.beginPath();
        const crescentR = w * 0.42;
        ctx.arc(0, h * 0.10, crescentR, Math.PI * 1.15, Math.PI * 1.85, false);
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.shadowBlur = 10;
        ctx.beginPath();
        ctx.arc(w * 0.36, -h * 0.08, 4, 0, Math.PI * 2);
        ctx.arc(-w * 0.36, -h * 0.08, 4, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
        return;
      }

      let scaleX = 1.0;
      let scaleY = 1.0;
      if (currentEmotion === 'SURPRISED') {
        scaleX = 1.15;
        scaleY = 1.25;
      } else if (currentEmotion === 'THINKING') {
        scaleY = 0.92;
      }

      if (blink > 0) {
        scaleY *= (1.0 - blink * 0.96);
        scaleX *= (1.0 + blink * 0.08);
      }

      ctx.scale(scaleX, scaleY);

      const halfW = squircleW * 0.5;
      const halfH = squircleH * 0.5;

      // Sclera Outer Background
      ctx.shadowColor = currentEmotion === 'THINKING' ? '#ff1744' : '#00e5ff';
      ctx.shadowBlur = 18;

      const outerGrad = ctx.createRadialGradient(0, 0, halfW * 0.4, 0, 0, halfW);
      outerGrad.addColorStop(0, '#060912');
      outerGrad.addColorStop(0.85, '#0c1220');
      outerGrad.addColorStop(1, currentEmotion === 'THINKING' ? 'rgba(255, 23, 68, 0.7)' : 'rgba(0, 229, 255, 0.45)');

      pathSquircle(ctx, -halfW, -halfH, squircleW, squircleH, cornerR);
      ctx.fillStyle = outerGrad;
      ctx.fill();

      ctx.strokeStyle = currentEmotion === 'THINKING' ? 'rgba(255, 23, 68, 0.75)' : 'rgba(0, 229, 255, 0.55)';
      ctx.lineWidth = 3;
      ctx.stroke();

      // Clip for Iris & Highlights
      ctx.save();
      pathSquircle(ctx, -halfW, -halfH, squircleW, squircleH, cornerR);
      ctx.clip();

      const maxGazeX = halfW * 0.40;
      const maxGazeY = halfH * 0.40;
      const px = gazeX * maxGazeX;
      const py = gazeY * maxGazeY;
      const irisR = Math.min(halfW, halfH) * 0.68;

      // Iris Multi-Stop Glow
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

      // Deep Central Pupil
      const pupilR = irisR * (currentEmotion === 'SURPRISED' ? 0.50 : (currentEmotion === 'CURIOUS' ? 0.40 : 0.35));
      ctx.beginPath();
      ctx.arc(px, py, pupilR, 0, Math.PI * 2);
      ctx.fillStyle = '#020306';
      ctx.fill();

      // Specular Living Reflection Glints
      ctx.fillStyle = 'rgba(255, 255, 255, 0.92)';
      ctx.shadowColor = '#ffffff';
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.arc(px - irisR * 0.32, py - irisR * 0.32, pupilR * 0.45, 0, Math.PI * 2);
      ctx.fill();

      ctx.beginPath();
      ctx.arc(px + irisR * 0.28, py + irisR * 0.28, pupilR * 0.22, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();
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
        const waveAmp = (13 + Math.sin(now * 0.024) * 10) * (lipSyncOpen + 0.35);
        ctx.fillStyle = 'rgba(0, 229, 255, 0.16)';

        ctx.beginPath();
        ctx.moveTo(-width * 0.46, 0);
        ctx.quadraticCurveTo(-width * 0.22, -waveAmp * 0.8, 0, waveAmp * 0.6);
        ctx.quadraticCurveTo(width * 0.22, waveAmp * 0.9, width * 0.46, 0);
        ctx.quadraticCurveTo(0, -waveAmp * 0.4, -width * 0.46, 0);
        ctx.stroke();
        ctx.fill();
      } else if (emotion === 'HAPPY') {
        ctx.strokeStyle = '#00f0ff';
        ctx.fillStyle = 'rgba(0, 240, 255, 0.22)';
        ctx.beginPath();
        ctx.moveTo(-width * 0.50, -5);
        ctx.quadraticCurveTo(0, width * 0.40, width * 0.50, -5);
        ctx.quadraticCurveTo(0, width * 0.12, -width * 0.50, -5);
        ctx.stroke();
        ctx.fill();
      } else if (emotion === 'CURIOUS') {
        ctx.beginPath();
        ctx.moveTo(-width * 0.36, 4);
        ctx.quadraticCurveTo(-width * 0.05, 0, width * 0.40, -7);
        ctx.stroke();
      } else if (emotion === 'THINKING') {
        const pulse = Math.sin(now * 0.009) * 2.5;
        ctx.beginPath();
        ctx.ellipse(0, 0, width * 0.20, 5 + pulse, 0, 0, Math.PI * 2);
        ctx.stroke();
      } else if (emotion === 'SURPRISED') {
        ctx.beginPath();
        ctx.ellipse(0, 0, width * 0.22, width * 0.28, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 229, 255, 0.2)';
        ctx.stroke();
        ctx.fill();
      } else {
        ctx.beginPath();
        ctx.moveTo(-width * 0.38, 0);
        ctx.quadraticCurveTo(0, width * 0.13, width * 0.38, 0);
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
       3. Human Natural Voice Engine (Safe & High Quality)
       ========================================================================== */
    function getBestVoice(langPrefix = 'en') {
      if (!('speechSynthesis' in window)) return null;
      const voices = window.speechSynthesis.getVoices();
      if (!voices || voices.length === 0) return null;

      // Look for natural/neural voices
      const natural = voices.find(v =>
        v.lang.toLowerCase().startsWith(langPrefix.toLowerCase()) &&
        (v.name.includes('Natural') || v.name.includes('Neural') || v.name.includes('Google') || v.name.includes('Aria') || v.name.includes('Jenny') || v.name.includes('Samantha'))
      );
      if (natural) return natural;

      const langMatch = voices.find(v => v.lang.toLowerCase().startsWith(langPrefix.toLowerCase()));
      if (langMatch) return langMatch;

      return null;
    }

    function speakReply(text, emotionAfter) {
      if (!('speechSynthesis' in window)) return;

      const utterance = new SpeechSynthesisUtterance(text);
      const isArabic = /[\u0600-\u06FF]/.test(text);

      utterance.lang = isArabic ? 'ar-EG' : 'en-US';
      const best = getBestVoice(isArabic ? 'ar' : 'en');
      if (best) {
        try { utterance.voice = best; } catch(e) {}
      }

      // Warm Human Conversational Prosody
      utterance.rate = 0.95;
      utterance.pitch = 1.05;
      utterance.volume = 1.0;

      utterance.onstart = () => {
        setEmotion('SPEAKING');
        lipSyncOpen = 1.0;
        showSubtitles('AURA-EJUST', text);
      };
      utterance.onerror = (err) => {
        console.warn('Speech synthesis notice:', err);
        lipSyncOpen = 0.0;
        setEmotion('ATTENTIVE');
        if (isContinuousConversation) setTimeout(startListening, 600);
      };
      utterance.onend = () => {
        lipSyncOpen = 0.0;
        setEmotion(emotionAfter || 'ATTENTIVE', 3500);
        if (isContinuousConversation) {
          setTimeout(startListening, 600);
        }
      };

      try {
        window.speechSynthesis.speak(utterance);
      } catch (e) {
        console.warn('Speak error:', e);
      }
    }

    function speakWelcome(enText, arText) {
      if (!('speechSynthesis' in window)) return;

      showSubtitles('AURA-EJUST', (enText ? enText : '') + (arText ? ' — ' + arText : ''));
      setEmotion('SPEAKING');
      lipSyncOpen = 1.0;

      if (enText) {
        const uEn = new SpeechSynthesisUtterance(enText);
        uEn.lang = 'en-US';
        const vEn = getBestVoice('en');
        if (vEn) try { uEn.voice = vEn; } catch(e) {}
        uEn.rate = 0.95;
        uEn.pitch = 1.04;

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
            if (vAr) try { uAr.voice = vAr; } catch(e) {}
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
              if (isContinuousConversation) setTimeout(startListening, 800);
            };
            window.speechSynthesis.speak(uAr);
          } else {
            lipSyncOpen = 0.0;
            setEmotion('HAPPY', 5000);
            if (isContinuousConversation) setTimeout(startListening, 800);
          }
        };
        window.speechSynthesis.speak(uEn);
      } else if (arText) {
        const uAr = new SpeechSynthesisUtterance(arText);
        uAr.lang = 'ar-EG';
        const vAr = getBestVoice('ar');
        if (vAr) try { uAr.voice = vAr; } catch(e) {}
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
          if (isContinuousConversation) setTimeout(startListening, 800);
        };
        window.speechSynthesis.speak(uAr);
      }
    }

    function showSubtitles(speaker, text) {
      const spk = document.getElementById('subSpeaker');
      const txt = document.getElementById('subText');
      if (spk && txt) {
        spk.textContent = speaker;
        txt.textContent = text;
      }
    }

    function updateSubtitles(speaker, text) {
      showSubtitles(speaker, text);
    }

    /* ==========================================================================
       4. Camera Vision & Gaze Elevation
       ========================================================================== */
    async function initCamera() {
      const video = document.getElementById('camVideo');
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
      try {
        camStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
          audio: false
        });
        video.srcObject = camStream;
        video.onloadedmetadata = () => {
          video.play();
          document.getElementById('camTag').textContent = 'GAZE: ON';
          requestAnimationFrame(processCameraFrame);
        };
      } catch (err) {
        document.getElementById('camTag').textContent = 'GAZE: OFF';
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

      const faceBox = detectFaceByLuminance(video, overlay.width, overlay.height);

      if (faceBox) {
        const normX = (faceBox.cx / overlay.width - 0.5) * 2;
        const normY = (faceBox.cy / overlay.height - 0.5) * 2;

        targetGazeX = normX * 0.9;
        targetGazeY = normY * 0.9;

        const gazeText = document.getElementById('gazeText');
        if (normY < -0.2) {
          if (gazeText) gazeText.textContent = 'GAZE: TALL ↑';
        } else if (normY > 0.2) {
          if (gazeText) gazeText.textContent = 'GAZE: CHILD ↓';
        } else {
          if (gazeText) gazeText.textContent = 'GAZE: EYE CONTACT';
        }

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
        if (gazeText) gazeText.textContent = 'GAZE: SCAN';
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
        logBle('BLE Connection notice: ' + err.message);
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
      if (btnTxt) btnTxt.textContent = connected ? 'ESP32 CONNECTED' : 'PAIR ESP32';
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
        if (text.includes('NFC_TAP')) {
          handleNfcTap('A1:B2:C3:D4', 'Prof. Amr Adly', 'Main Conference Hall', 1);
        }
      }
    }

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
            console.warn('BLE write error:', err2);
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
      showSubtitles('AURA-EJUST v3.0', 'Welcome to IEEE RAS E-JUST. Tap "Thank You" or Mic to speak.');
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
      const txt = document.getElementById('continuousText');
      if (txt) {
        txt.textContent = isContinuousConversation ? 'AUTO-TALK: ON' : 'AUTO-TALK: OFF';
      }
    }

    function startListening() {
      if (isListening || (window.speechSynthesis && window.speechSynthesis.speaking) || isLiveAudioPlaying) return;
      if (!recognition) initSpeechRecognition();
      if (!recognition) return;
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
        const micBtn = document.getElementById('micBtn');
        const micTxt = document.getElementById('micText');
        if (micBtn) micBtn.classList.add('listening');
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

    function extractContextEmotion(text) {
      const lower = text.toLowerCase();
      if (lower.includes('thank') || lower.includes('thanks') || lower.includes('appreciate') || lower.includes('good job') || lower.includes('awesome') || lower.includes('شكرا') || lower.includes('تسلم')) {
        return 'HAPPY';
      }
      if (lower.includes('what') || lower.includes('how') || lower.includes('why') || lower.includes('where') || lower.includes('who') || lower.includes('can you') || lower.includes('tell me') || lower.includes('أين') || lower.includes('كيف') || lower.includes('ما هو')) {
        return 'CURIOUS';
      }
      if (lower.includes('wow') || lower.includes('really') || lower.includes('incredible') || lower.includes('amazing')) {
        return 'SURPRISED';
      }
      return 'ATTENTIVE';
    }

    async function handleUserUtterance(userText) {
      const detectedEmotion = extractContextEmotion(userText);
      setEmotion(detectedEmotion === 'HAPPY' ? 'HAPPY' : 'THINKING');
      showSubtitles('AURA (THINKING)', 'Thinking...');

      let replyText = '';

      if (apiProvider === 'antigravity-relay') {
        try {
          replyText = await callAntigravityRelayAPI(userText);
        } catch (err) {
          console.warn('Antigravity relay failed, falling back:', err);
          replyText = generateAutonomousReply(userText);
        }
      } else if (apiProvider === 'openrouter' && openRouterKey && openRouterKey.length > 5) {
        try {
          replyText = await callOpenRouterAPI(userText);
        } catch (err) {
          console.warn('OpenRouter API call failed, falling back:', err);
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
            console.warn('Gemini API call failed, falling back:', err);
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

      speakReply(cleanedReply, finalEmotion);
    }

    async function callAntigravityRelayAPI(promptText) {
      const systemInstruction = `You are AURA-EJUST v3.0, the warm, polite, and friendly autonomous VIP receptionist and humanoid robot developed by IEEE RAS at Egypt-Japan University of Science and Technology (E-JUST). Provide very concise, warm, natural spoken answers (1-2 sentences). Speak in a friendly, conversational human tone. When the guest thanks you, include the tag [EMOTION: HAPPY]. When asked a question, include [EMOTION: CURIOUS].`;

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
      const systemInstruction = `You are AURA-EJUST v3.0, the warm, polite, and friendly autonomous VIP receptionist and humanoid robot developed by IEEE RAS at Egypt-Japan University of Science and Technology (E-JUST). Provide very concise, warm, natural spoken answers (1-2 sentences). Speak in a friendly human tone. When the guest thanks you, include the tag [EMOTION: HAPPY]. When asked a question, include [EMOTION: CURIOUS].`;

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
      const systemInstruction = `You are AURA-EJUST v3.0, the warm and friendly autonomous VIP receptionist and humanoid robot developed by IEEE RAS at Egypt-Japan University of Science and Technology (E-JUST). Keep responses very concise (1-2 sentences), natural, and warm for spoken output. If the guest thanks you, include the tag [EMOTION: HAPPY]. If they ask a technical question, include [EMOTION: CURIOUS].`;

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

    function generateAutonomousReply(userText) {
      const lower = userText.toLowerCase();

      if (lower.includes('thank') || lower.includes('شكرا')) {
        return '[EMOTION: HAPPY] You are most welcome! It is my absolute pleasure to assist you here at IEEE RAS E-JUST.';
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
      showSubtitles('AURA-EJUST', 'Welcome to IEEE RAS E-JUST. Tap "Thank You" or Mic to speak.');

      document.addEventListener('click', unlockAudioAndListen, { passive: true });
      document.addEventListener('touchstart', unlockAudioAndListen, { passive: true });
    });
  </script>
</body>
</html>
'''

with open(r'C:\VIP_Humanoid_Robot\WebApp_Screen\index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Successfully generated rebuild_expressive_horizontal_app ({len(html_content)} bytes)")
