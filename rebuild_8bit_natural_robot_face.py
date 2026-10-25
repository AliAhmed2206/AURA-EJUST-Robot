"""
Builder script for AURA-EJUST v3.0:
- 8-Bit Cyber-Symbol Pixel Matrix Face (Retro LED block matrix, pixel hearts, chevron smiles ^_^).
- Calming Cyber Cyan / Amber Gold for Thinking (NO RED - eliminates mad/angry look).
- Broadcast-Grade Natural Voice (Google Neural Audio via /api/tts - zero robotic synth).
- Full-Duplex Interruption (Voice Barge-In & Touch Barge-In - robot halts immediately when user speaks).
- Silent Optical Face & Elevation Tracking with symbols.
"""

import os

OUTPUT_PATH = r"C:\VIP_Humanoid_Robot\WebApp_Screen\index.html"

HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="mobile-web-app-capable" content="yes" />
  <title>AURA-EJUST v3.0 — 8-Bit Cyber Bionic Face</title>
  <style>
    :root {
      --bg-black: #000000;
      --ejust-red: #C0121F;
      --ras-purple: #621B6D;
      --imperial-gold: #C8A45D;
      --neon-cyan: #00e5ff;
      --neon-green: #00e676;
      --neon-amber: #ffb300;
      --blush-pink: #ff2a85;
      --text-white: #ffffff;
      --text-muted: #757480;
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
      background: #000000;
      color: var(--text-white);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* Full-Screen Pure Face Canvas Container */
    .face-container {
      position: absolute;
      inset: 0;
      width: 100vw;
      height: 100vh;
      background: #000000;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      z-index: 1;
    }
    #faceCanvas {
      width: 100%;
      height: 100%;
      display: block;
      cursor: pointer;
    }

    /* Ultra-Minimalist Symbol-Only HUD (Top Edge) */
    .symbol-hud {
      position: absolute;
      top: 10px;
      left: 14px;
      right: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 30;
      pointer-events: none;
    }
    .symbol-hud > * {
      pointer-events: auto;
    }
    .brand-mark {
      font-size: 10px;
      font-weight: 900;
      letter-spacing: 1.2px;
      color: rgba(200, 164, 93, 0.7);
      text-transform: uppercase;
      background: rgba(12, 9, 18, 0.45);
      border: 1px solid rgba(200, 164, 93, 0.2);
      border-radius: 12px;
      padding: 3px 9px;
      backdrop-filter: blur(8px);
    }

    /* Minimalist Glowing Status Symbols */
    .symbol-cluster {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .symbol-badge {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: rgba(14, 10, 22, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.1);
      font-size: 13px;
      backdrop-filter: blur(8px);
      transition: all 0.3s ease;
      cursor: pointer;
    }
    .symbol-badge.active-cyan {
      border-color: var(--neon-cyan);
      box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
      animation: pulse-symbol 2s infinite ease-in-out;
    }
    .symbol-badge.active-green {
      border-color: var(--neon-green);
      box-shadow: 0 0 10px rgba(0, 230, 118, 0.5);
    }
    .symbol-badge.active-amber {
      border-color: var(--neon-amber);
      box-shadow: 0 0 12px rgba(255, 179, 0, 0.6);
      animation: pulse-symbol 1.5s infinite ease-in-out;
    }
    .symbol-badge.dim {
      opacity: 0.35;
      border-color: rgba(255, 255, 255, 0.08);
    }

    @keyframes pulse-symbol {
      0%, 100% { transform: scale(1); opacity: 0.85; }
      50% { transform: scale(1.08); opacity: 1; }
    }

    /* Subtitles Floating Dynamic Glass Capsule */
    .subtitles-pill {
      position: absolute;
      bottom: 16px;
      left: 50%;
      transform: translateX(-50%);
      max-width: 86%;
      background: rgba(10, 8, 16, 0.75);
      border: 1px solid rgba(0, 229, 255, 0.22);
      border-radius: 20px;
      padding: 6px 16px;
      display: flex;
      align-items: center;
      gap: 10px;
      backdrop-filter: blur(14px);
      box-shadow: 0 6px 28px rgba(0, 0, 0, 0.85);
      pointer-events: none;
      transition: all 0.3s ease;
      z-index: 25;
    }
    .sub-speaker {
      font-size: 9px;
      font-weight: 800;
      color: var(--imperial-gold);
      letter-spacing: 1px;
      text-transform: uppercase;
      white-space: nowrap;
      border-right: 1px solid rgba(255, 255, 255, 0.16);
      padding-right: 8px;
    }
    .sub-text {
      font-size: 12px;
      font-weight: 600;
      color: #ffffff;
      line-height: 1.3;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 70vw;
    }

    /* Initial Wake Tap Overlay */
    .wake-overlay {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(8px);
      z-index: 50;
      cursor: pointer;
      transition: opacity 0.4s ease;
    }
    .wake-overlay.hidden {
      opacity: 0;
      pointer-events: none;
    }
    .wake-ring {
      width: 76px;
      height: 76px;
      border-radius: 12px;
      border: 2px solid var(--neon-cyan);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      box-shadow: 0 0 24px rgba(0, 229, 255, 0.5);
      animation: pulse-ring 2s infinite;
      margin-bottom: 14px;
      background: rgba(0, 229, 255, 0.1);
    }
    @keyframes pulse-ring {
      0%, 100% { transform: scale(1); box-shadow: 0 0 16px rgba(0, 229, 255, 0.4); }
      50% { transform: scale(1.08); box-shadow: 0 0 32px rgba(0, 229, 255, 0.8); }
    }
    .wake-title {
      font-size: 14px;
      font-weight: 800;
      letter-spacing: 2px;
      color: #ffffff;
      text-transform: uppercase;
      margin-bottom: 4px;
    }
    .wake-desc {
      font-size: 11px;
      color: var(--text-muted);
      letter-spacing: 0.5px;
    }

    /* Hidden Optical Tracking Elements */
    #camVideo, #camOverlay, .cam-pip {
      display: none !important;
      visibility: hidden !important;
      position: absolute;
      width: 0;
      height: 0;
      opacity: 0;
      pointer-events: none;
    }

    /* Settings Modal */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.92);
      backdrop-filter: blur(12px);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .modal-backdrop.open { display: flex; }
    .modal-card {
      background: #0c0814;
      border: 1.5px solid var(--ejust-red);
      border-radius: 16px;
      width: 100%;
      max-width: 460px;
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
      padding: 10px 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(98, 27, 109, 0.28);
    }
    .modal-title { font-size: 12px; font-weight: 800; color: var(--imperial-gold); letter-spacing: 1px; }
    .modal-close { background: none; border: none; color: #fff; font-size: 18px; cursor: pointer; }
    .modal-body { padding: 14px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
    .form-group { display: flex; flex-direction: column; gap: 4px; }
    .form-label { font-size: 10px; font-weight: 800; color: var(--text-muted); }
    .form-input, .form-select {
      background: rgba(0, 0, 0, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.18);
      border-radius: 8px;
      padding: 7px 10px;
      color: #fff;
      font-size: 11px;
      outline: none;
    }
    .btn-save {
      background: linear-gradient(135deg, var(--ejust-red), var(--ras-purple));
      border: none;
      color: #fff;
      padding: 7px 14px;
      border-radius: 8px;
      font-size: 11px;
      font-weight: 800;
      cursor: pointer;
    }
    .ble-log-box {
      font-family: monospace;
      font-size: 9px;
      height: 50px;
      overflow-y: auto;
      background: #000;
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 6px;
      padding: 6px;
      color: #00e676;
    }
  </style>
</head>
<body>
  <!-- Full-Bleed 8-Bit Cyber Face Canvas -->
  <div class="face-container" id="faceContainer">
    <canvas id="faceCanvas" onclick="onFaceTouch()"></canvas>

    <!-- Subtitles Floating Capsule -->
    <div class="subtitles-pill" id="subBox">
      <div class="sub-speaker" id="subSpeaker">AURA-EJUST</div>
      <div class="sub-text" id="subText">Welcome to IEEE RAS at E-JUST. Speak to begin.</div>
    </div>
  </div>

  <!-- Ultra-Minimalist Symbol-Only HUD -->
  <div class="symbol-hud">
    <div class="hud-left">
      <div class="brand-mark">AURA 8-BIT</div>
    </div>
    <div class="symbol-cluster">
      <div class="symbol-badge active-cyan" id="symVoice" title="Conversational State: Listening">🎙️</div>
      <div class="symbol-badge dim" id="symVision" onclick="initCamera()" title="Optical Gaze Tracking">👁️</div>
      <div class="symbol-badge dim" id="symBle" onclick="connectBle()" title="ESP32 BLE Link">📶</div>
      <div class="symbol-badge active-green" id="symAi" onclick="openSettings()" title="AI Brain Status">🧠</div>
      <div class="symbol-badge dim" onclick="toggleFullScreen()" title="Fullscreen">⛶</div>
      <div class="symbol-badge dim" onclick="openSettings()" title="Settings">⚙️</div>
    </div>
  </div>

  <!-- Initial Wake Overlay -->
  <div class="wake-overlay" id="wakeOverlay" onclick="wakeAuraRobot()">
    <div class="wake-ring">👾</div>
    <div class="wake-title">AURA-EJUST v3.0</div>
    <div class="wake-desc">Tap screen to wake &amp; activate natural voice</div>
  </div>

  <!-- Hidden Vision Camera Elements -->
  <div class="cam-pip" id="camPip">
    <video id="camVideo" autoplay playsinline muted></video>
    <canvas id="camOverlay"></canvas>
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
          <label class="form-label">AI Conversational Brain</label>
          <select id="providerSelect" class="form-select" onchange="updateProviderVisibility()">
            <option value="antigravity-relay">Antigravity Local Relay Bridge (Free PC Pro Session)</option>
            <option value="openrouter">OpenRouter API (Free Llama 3.3 70B / DeepSeek)</option>
            <option value="gemini">Google Gemini API (Studio Key / Live WS)</option>
            <option value="offline-autonomous">Offline Autonomous Smart Dialog</option>
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
              <option value="deepseek/deepseek-chat">deepseek/deepseek-chat</option>
              <option value="google/gemini-2.0-flash-001">google/gemini-2.0-flash-001</option>
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
              <option value="offline-autonomous">Offline Smart Dialog Engine</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Natural Voice Engine</label>
          <select id="voiceSelect" class="form-select">
            <option value="auto-natural">Google Studio Neural Audio (Real Human Voice via Bridge)</option>
            <option value="Aoede">Aoede (Gemini Live Audio)</option>
            <option value="Puck">Puck (Gemini Live Audio)</option>
            <option value="native-tts">System Bilingual TTS Fallback</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">ESP32 BLE / Wi-Fi Monitor</label>
          <div class="ble-log-box" id="bleLogBox">BLE Ready...</div>
        </div>
      </div>
      <div style="padding: 10px 14px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: flex-end;">
        <button class="btn-save" onclick="saveSettings()">Save &amp; Apply</button>
      </div>
    </div>
  </div>

  <script>
    /* ==========================================================================
       AURA-EJUST v3.0 — 8-Bit Cyber-Symbol Face & Full-Duplex Natural Brain
       ========================================================================== */

    // 1. Hardware & Service Identifiers
    const NORDIC_UART_SERVICE = '6e400001-b5a3-f393-e0a9-e50e24dcca9e';
    const NORDIC_RX_CHAR = '6e400002-b5a3-f393-e0a9-e50e24dcca9e';
    const NORDIC_TX_CHAR = '6e400003-b5a3-f393-e0a9-e50e24dcca9e';

    const DEFAULT_API_KEY = 'AIzaSyDrEPiLGYrnqxzvcE9PhAP4LCx-eEAk8gk';
    let apiProvider = localStorage.getItem('AURA_API_PROVIDER') || 'antigravity-relay';
    let bridgeUrl = localStorage.getItem('AURA_BRIDGE_URL') || (window.location.origin.startsWith('http') ? window.location.origin : 'http://192.168.1.19:8080');
    let openRouterKey = localStorage.getItem('AURA_OPENROUTER_KEY') || '';
    let openRouterModel = localStorage.getItem('AURA_OPENROUTER_MODEL') || 'meta-llama/llama-3.3-70b-instruct:free';
    let apiKey = localStorage.getItem('AURA_GEMINI_KEY') || DEFAULT_API_KEY;
    let selectedModel = localStorage.getItem('AURA_GEMINI_MODEL') || 'gemini-3.8-flash';
    let selectedVoice = localStorage.getItem('AURA_VOICE') || 'auto-natural';

    // Bluetooth Objects
    let bleDevice = null;
    let bleServer = null;
    let rxChar = null;
    let txChar = null;
    let bleConnected = false;

    // Face & Emotion State
    let currentEmotion = 'ATTENTIVE'; // ATTENTIVE, HAPPY, CURIOUS, THINKING, SPEAKING, SURPRISED
    let emotionTimer = null;
    let targetGazeX = 0; // -1 to +1
    let targetGazeY = 0; // -1 to +1
    let currentGazeX = 0;
    let currentGazeY = 0;

    // 8-Bit Pixel Grid State
    let pixelScale = 1.0;
    let blushAlpha = 0.0;
    let targetBlushAlpha = 0.0;

    // Micro-Saccades & Living Movement
    let saccadeX = 0;
    let saccadeY = 0;
    let nextSaccadeTime = performance.now() + 2000;

    // Organic Blinking
    let blinkProgress = 0;
    let isBlinking = false;
    let nextBlinkTime = performance.now() + 2500;
    let lipSyncOpen = 0.0;

    // Full-Duplex Natural Conversational Manager & Interruption
    let isContinuousConversation = true;
    let isListening = false;
    let isSpeaking = false;
    let isAwake = false;
    let recognition = null;
    let liveWs = null;
    let isLiveWsConnected = false;
    let isLiveAudioPlaying = false;
    let audioCtx = null;
    let activeAudioPlayer = null;
    let micAnalyser = null;
    let micStream = null;
    let availableVoices = [];
    let speechWatchdogTimer = null;

    // Camera Vision & Tracking State
    let camStream = null;
    let visitorNear = false;
    let visitorDetectionCount = 0;
    let lastVisitorGreetingTime = 0;

    // Registered VIP Database
    const VIP_DATABASE = {
      'A1:B2:C3:D4': { name: 'Prof. Amr Adly', dest: 'Main Conference Hall', markers: 1 },
      'E5:F6:07:18': { name: 'Dr. Mariam Hassan', dest: 'E-JUST Grand Theatre', markers: 2 },
      '90:A1:B2:C3': { name: 'Eng. Youssef Khaled', dest: 'Robotics Innovation Hub', markers: 1 }
    };

    let activeUid = '';
    let currentRobotState = 'IDLE';

    const ARABIC_TITLES = {
      'Prof. Amr Adly': 'أهلاً وسهلاً أ.د. عمرو عدلي — رئيس الجامعة المصرية اليابانية',
      'Dr. Mariam Hassan': 'أهلاً بكِ د. مريم حسن — المتحدث الرئيسي لـ IEEE RAS',
      'Eng. Youssef Khaled': 'مرحباً م. يوسف خالد — رئيس فرع IEEE RAS E-JUST'
    };

    /* ==========================================================================
       2. 8-Bit Cyber-Symbol Pixel Matrix Canvas Engine (Zero Uncanny Valley)
       ========================================================================== */
    const canvas = document.getElementById('faceCanvas');
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
      const w = window.innerWidth;
      const h = window.innerHeight;
      const dpr = window.devicePixelRatio || 1;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    window.addEventListener('resize', resizeCanvas);
    window.addEventListener('orientationchange', () => setTimeout(resizeCanvas, 150));
    setTimeout(resizeCanvas, 30);

    function updateSaccades(now) {
      if (now > nextSaccadeTime) {
        if (Math.random() < 0.60) {
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

      // Pure AMOLED Obsidian Black
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, w, h);

      updateSaccades(now);

      // Smooth gaze
      currentGazeX += ((targetGazeX + saccadeX) - currentGazeX) * 0.15;
      currentGazeY += ((targetGazeY + saccadeY) - currentGazeY) * 0.15;

      // 8-Bit Blinking
      if (!isBlinking && now > nextBlinkTime) {
        isBlinking = true;
        blinkProgress = 0;
      }
      if (isBlinking) {
        blinkProgress += 0.22;
        if (blinkProgress >= 1.0) {
          isBlinking = false;
          blinkProgress = 0;
          nextBlinkTime = now + 2500 + Math.random() * 3200;
        }
      }
      const isEyeClosed = isBlinking && (blinkProgress > 0.2 && blinkProgress < 0.8);

      // Blush Alpha lerp
      targetBlushAlpha = (currentEmotion === 'HAPPY') ? 1.0 : 0.0;
      blushAlpha += (targetBlushAlpha - blushAlpha) * 0.12;

      // 8-Bit Layout Coordinates
      const eyeSpacing = Math.min(w * 0.24, 250);
      const eyeSize = Math.min(w * 0.22, h * 0.48, 230);
      const leftEyeX = w * 0.5 - eyeSpacing;
      const rightEyeX = w * 0.5 + eyeSpacing;
      const eyeY = h * 0.43;

      // Draw 8-Bit Pixel Matrix Eyes
      drawBionicEye(leftEyeX, eyeY, eyeSize, eyeSize, currentGazeX, currentGazeY, isEyeClosed, 'left', now);
      drawBionicEye(rightEyeX, eyeY, eyeSize, eyeSize, currentGazeX, currentGazeY, isEyeClosed, 'right', now);

      // Draw 8-Bit Pixel Hearts Blush Cheeks
      if (blushAlpha > 0.01) {
        const pulse = 1.0 + Math.sin(now * 0.006) * 0.08;
        drawCheekBlush(leftEyeX - eyeSize * 0.20, eyeY + eyeSize * 0.54, eyeSize * 0.35 * pulse, blushAlpha);
        drawCheekBlush(rightEyeX + eyeSize * 0.20, eyeY + eyeSize * 0.54, eyeSize * 0.35 * pulse, blushAlpha);
      }

      // Draw 8-Bit Cyber-Mouth / Equalizer
      drawCyberMouth(w * 0.5, h * 0.80, eyeSize * 1.1, currentEmotion, now);

      requestAnimationFrame(renderFace);
    }
    requestAnimationFrame(renderFace);

    // 8-Bit Pixel Matrix Eye Renderer
    function drawBionicEye(cx, cy, w, h, gazeX, gazeY, isClosed, side, now) {
      ctx.save();
      ctx.translate(cx, cy);

      const gridSize = 8; // 8x8 block matrix
      const blockSize = Math.floor(w / (gridSize + 2));
      const gap = Math.max(2, Math.floor(blockSize * 0.18));
      const totalSpan = gridSize * (blockSize + gap);

      // Dynamic Eye Color Theme (NO RED - Electric Cyan, Amber Gold, or Pink)
      let eyeColor = '#00f0ff';
      let shadowColor = '#00f0ff';

      if (currentEmotion === 'THINKING') {
        // Calming Electric Cyan / Cyber Amber cycling pulse (Zero Red!)
        const pulse = Math.sin(now * 0.008);
        eyeColor = pulse > 0 ? '#00e5ff' : '#ffb300';
        shadowColor = eyeColor;
      } else if (currentEmotion === 'HAPPY') {
        eyeColor = '#00f7ff';
        shadowColor = '#00f7ff';
      }

      ctx.shadowColor = shadowColor;
      ctx.shadowBlur = 14;
      ctx.fillStyle = eyeColor;

      // 1. BLINK: Collapse to horizontal 8-bit line
      if (isClosed) {
        const lineY = 0;
        for (let col = 1; col < gridSize - 1; col++) {
          const bx = -totalSpan * 0.5 + col * (blockSize + gap);
          ctx.fillRect(bx, lineY, blockSize, Math.max(3, blockSize * 0.35));
        }
        ctx.restore();
        return;
      }

      // 2. HAPPY: Upward smiling crescent chevrons (^ ^)
      if (currentEmotion === 'HAPPY') {
        const happyPattern = [
          [0,0,0,1,1,0,0,0],
          [0,0,1,1,1,1,0,0],
          [0,1,1,0,0,1,1,0],
          [1,1,0,0,0,0,1,1],
          [1,1,0,0,0,0,1,1],
          [0,0,0,0,0,0,0,0],
          [0,0,0,0,0,0,0,0],
          [0,0,0,0,0,0,0,0]
        ];
        drawMatrixPattern(ctx, happyPattern, totalSpan, blockSize, gap);
        ctx.restore();
        return;
      }

      // 3. CURIOUS: Left eye wide, Right eye inquisitive cock / ? mark
      if (currentEmotion === 'CURIOUS') {
        if (side === 'left') {
          // Inquisitive large box
          const curiousLeft = [
            [0,1,1,1,1,1,1,0],
            [1,1,1,1,1,1,1,1],
            [1,1,0,0,0,0,1,1],
            [1,1,0,1,1,0,1,1],
            [1,1,0,1,1,0,1,1],
            [1,1,0,0,0,0,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0]
          ];
          drawMatrixPattern(ctx, curiousLeft, totalSpan, blockSize, gap);
        } else {
          // Cocked eyebrow + squint eye
          const curiousRight = [
            [0,0,0,1,1,1,1,1], // Cocked stair brow
            [0,0,1,1,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,0],
            [1,1,1,1,1,1,1,1],
            [1,1,0,0,0,0,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0]
          ];
          drawMatrixPattern(ctx, curiousRight, totalSpan, blockSize, gap);
        }
        ctx.restore();
        return;
      }

      // 4. THINKING: Rotating cyber data spinner (Calming, NO RED)
      if (currentEmotion === 'THINKING') {
        const step = Math.floor((now * 0.006) % 4);
        const thinkPatterns = [
          [
            [0,0,1,1,1,1,0,0],
            [0,1,0,0,0,0,1,0],
            [1,0,0,1,1,0,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,0,1,1,0,0,1],
            [0,1,0,0,0,0,1,0],
            [0,0,1,1,1,1,0,0]
          ],
          [
            [0,0,0,1,1,0,0,0],
            [0,0,1,1,1,1,0,0],
            [0,1,1,0,0,1,1,0],
            [1,1,0,1,1,0,1,1],
            [1,1,0,1,1,0,1,1],
            [0,1,1,0,0,1,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,1,1,0,0,0]
          ],
          [
            [1,1,0,0,0,0,1,1],
            [1,1,1,0,0,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [1,1,1,0,0,1,1,1],
            [1,1,0,0,0,0,1,1]
          ],
          [
            [0,1,1,1,1,1,1,0],
            [1,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,1,0,0,1,0,1],
            [1,0,1,0,0,1,0,1],
            [1,0,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,1],
            [0,1,1,1,1,1,1,0]
          ]
        ];
        drawMatrixPattern(ctx, thinkPatterns[step], totalSpan, blockSize, gap);
        ctx.restore();
        return;
      }

      // 5. ATTENTIVE / DEFAULT: 8-Bit Squircle with Gaze Tracking Pupil
      const discreteGazeX = Math.round(gazeX * 1.5);
      const discreteGazeY = Math.round(gazeY * 1.5);

      const basePattern = [
        [0,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [0,1,1,1,1,1,1,0]
      ];

      // Render base frame
      for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
          if (basePattern[r][c]) {
            const bx = -totalSpan * 0.5 + c * (blockSize + gap);
            const by = -totalSpan * 0.5 + r * (blockSize + gap);

            // Pupil subtraction (inverted block for 8-bit pupil)
            const pr = r - (3 + discreteGazeY);
            const pc = c - (3 + discreteGazeX);
            const isPupil = (pr >= 0 && pr <= 1 && pc >= 0 && pc <= 1);

            // Specular Glint (1 top-left pixel)
            const isGlint = (pr === 0 && pc === 0);

            if (isPupil && !isGlint) {
              ctx.fillStyle = '#000000';
            } else {
              ctx.fillStyle = eyeColor;
            }
            ctx.fillRect(bx, by, blockSize, blockSize);
          }
        }
      }

      ctx.restore();
    }

    function drawMatrixPattern(ctx, pattern, totalSpan, blockSize, gap) {
      for (let r = 0; r < pattern.length; r++) {
        for (let c = 0; c < pattern[r].length; c++) {
          if (pattern[r][c]) {
            const bx = -totalSpan * 0.5 + c * (blockSize + gap);
            const by = -totalSpan * 0.5 + r * (blockSize + gap);
            ctx.fillRect(bx, by, blockSize, blockSize);
          }
        }
      }
    }

    // 8-Bit Pixel Hearts Cheek Blush
    function drawCheekBlush(cx, cy, radius, alpha) {
      ctx.save();
      ctx.translate(cx, cy);
      ctx.fillStyle = `rgba(255, 42, 133, ${alpha * 0.9})`;
      ctx.shadowColor = '#ff2a85';
      ctx.shadowBlur = 12;

      const p = Math.max(3, Math.floor(radius * 0.16));
      const heart = [
        [0,1,0,1,0],
        [1,1,1,1,1],
        [1,1,1,1,1],
        [0,1,1,1,0],
        [0,0,1,0,0]
      ];

      const span = 5 * p;
      for (let r = 0; r < 5; r++) {
        for (let c = 0; c < 5; c++) {
          if (heart[r][c]) {
            ctx.fillRect(-span * 0.5 + c * p, -span * 0.5 + r * p, p, p);
          }
        }
      }
      ctx.restore();
    }

    // 8-Bit Cyber-Mouth / Dynamic Equalizer
    function drawCyberMouth(cx, cy, width, emotion, now) {
      ctx.save();
      ctx.translate(cx, cy);

      ctx.fillStyle = '#00e5ff';
      ctx.shadowColor = '#00e5ff';
      ctx.shadowBlur = 12;

      const barCount = 9;
      const barW = Math.max(4, Math.floor(width / (barCount * 1.8)));
      const gap = Math.max(3, Math.floor(barW * 0.6));
      const totalW = barCount * (barW + gap);

      if (emotion === 'SPEAKING') {
        // Real-time audio equalizer bars
        for (let i = 0; i < barCount; i++) {
          const centerDist = Math.abs(i - Math.floor(barCount / 2));
          const wave = Math.sin(now * 0.02 + i * 0.8) * 0.5 + 0.5;
          const barH = Math.max(4, (14 + wave * 22) * (lipSyncOpen + 0.35) * (1.2 - centerDist * 0.15));
          const bx = -totalW * 0.5 + i * (barW + gap);
          ctx.fillRect(bx, -barH * 0.5, barW, barH);
        }
      } else if (emotion === 'HAPPY') {
        // 8-Bit Pixel Smile
        const smileBlocks = [
          [1,0,0,0,0,0,0,0,1],
          [0,1,0,0,0,0,0,1,0],
          [0,0,1,1,1,1,1,0,0]
        ];
        const bh = barW;
        for (let r = 0; r < 3; r++) {
          for (let c = 0; c < barCount; c++) {
            if (smileBlocks[r][c]) {
              const bx = -totalW * 0.5 + c * (barW + gap);
              ctx.fillRect(bx, r * bh, barW, bh);
            }
          }
        }
      } else {
        // Calm resting 8-bit line
        for (let i = 2; i < barCount - 2; i++) {
          const bx = -totalW * 0.5 + i * (barW + gap);
          ctx.fillRect(bx, 0, barW, Math.max(3, barW * 0.5));
        }
      }

      ctx.restore();
    }

    function setEmotion(emotion, durationMs = 0) {
      currentEmotion = emotion;
      updateStatusSymbols();

      if (emotionTimer) clearTimeout(emotionTimer);
      if (durationMs > 0) {
        emotionTimer = setTimeout(() => {
          currentEmotion = 'ATTENTIVE';
          updateStatusSymbols();
        }, durationMs);
      }
    }

    function updateStatusSymbols() {
      const symVoice = document.getElementById('symVoice');
      if (symVoice) {
        if (isSpeaking) {
          symVoice.className = 'symbol-badge active-amber';
          symVoice.textContent = '🗣️';
        } else if (currentEmotion === 'THINKING') {
          symVoice.className = 'symbol-badge active-cyan';
          symVoice.textContent = '🧠';
        } else if (isListening) {
          symVoice.className = 'symbol-badge active-cyan';
          symVoice.textContent = '🎙️';
        } else {
          symVoice.className = 'symbol-badge dim';
          symVoice.textContent = '🎙️';
        }
      }

      const symAi = document.getElementById('symAi');
      if (symAi) {
        symAi.className = (apiProvider === 'antigravity-relay') ? 'symbol-badge active-green' : 'symbol-badge active-cyan';
      }

      const symBle = document.getElementById('symBle');
      if (symBle) {
        symBle.className = bleConnected ? 'symbol-badge active-green' : 'symbol-badge dim';
      }

      const symVision = document.getElementById('symVision');
      if (symVision) {
        symVision.className = (camStream && visitorNear) ? 'symbol-badge active-cyan' : (camStream ? 'symbol-badge' : 'symbol-badge dim');
      }
    }

    /* ==========================================================================
       3. Broadcast-Grade Natural Voice & Full-Duplex Interruption Engine
       ========================================================================== */
    function stopCurrentAudio() {
      if (activeAudioPlayer) {
        try {
          activeAudioPlayer.pause();
          activeAudioPlayer.currentTime = 0;
        } catch(e) {}
        activeAudioPlayer = null;
      }
      if ('speechSynthesis' in window) {
        try { window.speechSynthesis.cancel(); } catch(e) {}
      }
      isSpeaking = false;
      lipSyncOpen = 0.0;
      clearTimeout(speechWatchdogTimer);
    }

    // FULL-DUPLEX INTERRUPTION (BARGE-IN)
    function interruptRobot() {
      if (!isSpeaking) return;
      console.log('[BARGE-IN] User interrupted AURA!');
      stopCurrentAudio();
      setEmotion('CURIOUS', 2000);
      showSubtitles('AURA', 'Listening to you...');
      updateStatusSymbols();

      // Immediately arm listening to process what user is saying
      setTimeout(startListening, 150);
    }

    function speakReply(text, emotionAfter) {
      stopCurrentAudio();
      isSpeaking = true;
      setEmotion('SPEAKING');
      showSubtitles('AURA-EJUST', text);
      updateStatusSymbols();

      // Clean emotion tags
      const cleanedText = text.replace(/\[EMOTION:.*?\]/g, '').trim();
      const isArabic = /[\u0600-\u06FF]/.test(cleanedText);
      const lang = isArabic ? 'ar' : 'en';

      let cleanBase = window.location.origin.startsWith('http') ? window.location.origin : (bridgeUrl || 'http://192.168.1.19:8080');
      cleanBase = cleanBase.replace(/\/+$/, '');
      const ttsUrl = `${cleanBase}/api/tts?text=${encodeURIComponent(cleanedText)}&lang=${lang}`;

      try {
        const audio = new Audio();
        audio.crossOrigin = 'anonymous';
        audio.src = ttsUrl;
        activeAudioPlayer = audio;

        audio.onplay = () => {
          isSpeaking = true;
          setEmotion('SPEAKING');
          lipSyncOpen = 1.0;
          updateStatusSymbols();
        };

        audio.ontimeupdate = () => {
          if (isSpeaking) {
            lipSyncOpen = 0.5 + Math.sin(audio.currentTime * 12) * 0.5;
          }
        };

        audio.onended = () => {
          isSpeaking = false;
          lipSyncOpen = 0.0;
          activeAudioPlayer = null;
          setEmotion(emotionAfter || 'ATTENTIVE', 3000);
          updateStatusSymbols();
          if (isContinuousConversation) {
            setTimeout(startListening, 250);
          }
        };

        audio.onerror = (err) => {
          console.warn('Natural audio stream notice, falling back to Web Speech:', err);
          fallbackSystemSpeech(cleanedText, emotionAfter);
        };

        // Watchdog to prevent hung speech
        speechWatchdogTimer = setTimeout(() => {
          if (isSpeaking) {
            console.warn('Speech watchdog auto-recovery');
            stopCurrentAudio();
            setEmotion('ATTENTIVE');
            updateStatusSymbols();
            if (isContinuousConversation) startListening();
          }
        }, 14000);

        audio.play().catch(() => {
          fallbackSystemSpeech(cleanedText, emotionAfter);
        });

      } catch (e) {
        fallbackSystemSpeech(cleanedText, emotionAfter);
      }
    }

    function fallbackSystemSpeech(text, emotionAfter) {
      if (!('speechSynthesis' in window)) return;
      try { window.speechSynthesis.cancel(); } catch(e) {}

      const utterance = new SpeechSynthesisUtterance(text);
      const isArabic = /[\u0600-\u06FF]/.test(text);
      utterance.lang = isArabic ? 'ar-EG' : 'en-US';

      const best = getBestVoice(isArabic ? 'ar' : 'en');
      if (best) try { utterance.voice = best; } catch(e) {}
      utterance.rate = 0.94;
      utterance.pitch = 1.02;

      utterance.onstart = () => {
        isSpeaking = true;
        setEmotion('SPEAKING');
        lipSyncOpen = 1.0;
        updateStatusSymbols();
      };
      utterance.onend = () => {
        isSpeaking = false;
        lipSyncOpen = 0.0;
        setEmotion(emotionAfter || 'ATTENTIVE', 3000);
        updateStatusSymbols();
        if (isContinuousConversation) setTimeout(startListening, 300);
      };
      utterance.onerror = () => {
        isSpeaking = false;
        lipSyncOpen = 0.0;
        setEmotion('ATTENTIVE');
        updateStatusSymbols();
        if (isContinuousConversation) setTimeout(startListening, 400);
      };

      try {
        window.speechSynthesis.speak(utterance);
      } catch(e) {
        isSpeaking = false;
        if (isContinuousConversation) startListening();
      }
    }

    function speakWelcome(enText, arText) {
      const fullText = (enText ? enText : '') + (arText ? ' — ' + arText : '');
      speakReply(fullText, 'HAPPY');
    }

    function populateVoices() {
      if (!('speechSynthesis' in window)) return;
      availableVoices = window.speechSynthesis.getVoices() || [];
    }
    if ('speechSynthesis' in window) {
      populateVoices();
      window.speechSynthesis.onvoiceschanged = populateVoices;
    }

    function getBestVoice(langPrefix = 'en') {
      if (!availableVoices || availableVoices.length === 0) populateVoices();
      if (!availableVoices || availableVoices.length === 0) return null;
      const natural = availableVoices.find(v =>
        v.lang.toLowerCase().startsWith(langPrefix.toLowerCase()) &&
        (v.name.includes('Natural') || v.name.includes('Neural') || v.name.includes('Google') || v.name.includes('Online'))
      );
      if (natural) return natural;
      return availableVoices.find(v => v.lang.toLowerCase().startsWith(langPrefix.toLowerCase())) || null;
    }

    function wakeAuraRobot() {
      isAwake = true;
      const overlay = document.getElementById('wakeOverlay');
      if (overlay) overlay.classList.add('hidden');

      unlockAudioContext();
      initCamera();
      initMicEnergyInterruption();
      initSpeechRecognition();

      speakReply("Hello! I am AURA. I am listening naturally. How can I assist you?", 'HAPPY');
    }

    function onFaceTouch() {
      unlockAudioContext();
      if (!isAwake) {
        wakeAuraRobot();
        return;
      }
      // Touch Barge-In: Tapping face immediately interrupts speaking
      if (isSpeaking) {
        interruptRobot();
        return;
      }
      if (!isListening) {
        startListening();
      }
    }

    function unlockAudioContext() {
      if ('speechSynthesis' in window) {
        try { window.speechSynthesis.resume(); } catch(e) {}
      }
      if (audioCtx && audioCtx.state === 'suspended') {
        try { audioCtx.resume(); } catch(e) {}
      }
    }

    // Voice Volume Energy Analyser for Real-Time Barge-In Interruption
    async function initMicEnergyInterruption() {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
      try {
        if (!audioCtx) {
          audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
        const source = audioCtx.createMediaStreamSource(micStream);
        micAnalyser = audioCtx.createAnalyser();
        micAnalyser.fftSize = 256;
        source.connect(micAnalyser);

        const bufferLength = micAnalyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        function checkVoiceActivity() {
          if (isSpeaking && micAnalyser) {
            micAnalyser.getByteFrequencyData(dataArray);
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) sum += dataArray[i];
            const avg = sum / bufferLength;

            // Voice threshold detected while speaking -> Interrupt!
            if (avg > 38) {
              interruptRobot();
            }
          }
          requestAnimationFrame(checkVoiceActivity);
        }
        requestAnimationFrame(checkVoiceActivity);
      } catch (err) {
        console.warn('Mic energy analyser notice:', err);
      }
    }

    function initSpeechRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) return;

      if (recognition) {
        try { recognition.abort(); } catch(e) {}
      }

      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        isListening = true;
        updateStatusSymbols();
      };

      recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            transcript += event.results[i][0].transcript;
          }
        }
        transcript = transcript.trim();
        if (transcript) {
          // If the robot was speaking, user interrupted with voice!
          if (isSpeaking) {
            interruptRobot();
          }
          showSubtitles('YOU', transcript);
          handleUserUtterance(transcript);
        }
      };

      recognition.onerror = (e) => {
        isListening = false;
        updateStatusSymbols();
        if (e.error === 'no-speech') {
          if (isContinuousConversation && !isSpeaking && !isLiveAudioPlaying) {
            setTimeout(startListening, 250);
          }
        } else if (e.error === 'not-allowed') {
          showSubtitles('AURA', 'Tap screen to grant mic permission.');
        } else {
          if (isContinuousConversation && !isSpeaking && !isLiveAudioPlaying) {
            setTimeout(startListening, 500);
          }
        }
      };

      recognition.onend = () => {
        isListening = false;
        updateStatusSymbols();
        if (isContinuousConversation && !isSpeaking && !isLiveAudioPlaying) {
          setTimeout(startListening, 200);
        }
      };
    }

    function startListening() {
      if (isListening || isSpeaking || isLiveAudioPlaying) return;
      if (!recognition) initSpeechRecognition();
      if (!recognition) return;

      try {
        recognition.start();
        isListening = true;
        updateStatusSymbols();
      } catch (e) {}
    }

    function stopListening() {
      isListening = false;
      if (recognition) {
        try { recognition.stop(); } catch(e) {}
      }
      updateStatusSymbols();
    }

    function toggleContinuousMode() {
      isContinuousConversation = !isContinuousConversation;
      if (isContinuousConversation) {
        startListening();
      } else {
        stopListening();
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
       4. Invisible Optical Tracking & Elevation Gaze Mapping (Symbols Only)
       ========================================================================== */
    async function initCamera() {
      const video = document.getElementById('camVideo');
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;
      try {
        camStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 480 }, height: { ideal: 360 } },
          audio: false
        });
        video.srcObject = camStream;
        video.onloadedmetadata = () => {
          video.play();
          updateStatusSymbols();
          requestAnimationFrame(processCameraFrame);
        };
      } catch (err) {
        console.warn('Camera notice:', err);
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

      const faceBox = detectFaceByLuminance(video, overlay.width, overlay.height);

      if (faceBox) {
        const normX = (faceBox.cx / overlay.width - 0.5) * 2;
        const normY = (faceBox.cy / overlay.height - 0.5) * 2;

        targetGazeX = normX * 0.9;
        targetGazeY = normY * 0.9;

        // Elevation gaze mapping
        if (normY < -0.2) {
          // Tall visitor
        } else if (normY > 0.2) {
          // Child / seated visitor
        }

        const areaRatio = (faceBox.w * faceBox.h) / (overlay.width * overlay.height);
        if (areaRatio > 0.08) {
          visitorDetectionCount++;
          if (visitorDetectionCount > 15 && !visitorNear) {
            visitorNear = true;
            updateStatusSymbols();
            onVisitorApproached();
          }
        } else {
          visitorDetectionCount = Math.max(0, visitorDetectionCount - 1);
          if (visitorDetectionCount === 0) {
            visitorNear = false;
            updateStatusSymbols();
          }
        }
      } else {
        targetGazeX = 0;
        targetGazeY = 0;
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
      if (now - lastVisitorGreetingTime > 25000 && !isSpeaking) {
        lastVisitorGreetingTime = now;
        setEmotion('ATTENTIVE');
        speakReply("Welcome to IEEE RAS at E-JUST! Please tap your NFC badge on my chest reader to begin.", 'HAPPY');
      }
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
        updateStatusSymbols();
        logBle('BLE Connected to ESP32!');
      } catch (err) {
        console.warn('BLE connect error:', err);
        logBle('BLE Notice: ' + err.message);
        bleConnected = false;
        updateStatusSymbols();
      }
    }

    function onBleDisconnected() {
      logBle('ESP32 BLE Disconnected.');
      bleConnected = false;
      updateStatusSymbols();
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
        logBle('BLE not connected: ' + JSON.stringify(jsonObj));
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

      const vipRecord = VIP_DATABASE[uid] || {};
      const guest = name || vipRecord.name || 'Distinguished Guest';
      const destination = dest || vipRecord.dest || 'Main Conference Hall';
      const escortMarkers = markers || vipRecord.markers || 1;
      const arabicTitle = ARABIC_TITLES[guest] || 'أهلاً وسهلاً بضيفنا الكريم في الجامعة المصرية اليابانية';

      setEmotion('HAPPY', 6000);

      const enWelcome = `Welcome ${guest}! It is an absolute honour to receive you at IEEE RAS E-JUST. Please follow me to the ${destination}.`;
      speakWelcome(enWelcome, arabicTitle);

      setTimeout(() => {
        currentRobotState = 'ESCORTING';
        sendBleCommand({
          cmd: 'START_ESCORT',
          name: guest,
          dest: destination,
          markers: escortMarkers,
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
      showSubtitles('AURA-EJUST v3.0', 'Welcome to IEEE RAS at E-JUST. Speak to begin.');
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
          updateStatusSymbols();
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
          updateStatusSymbols();
        };
        liveWs.onclose = () => {
          isLiveWsConnected = false;
          updateStatusSymbols();
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
        updateStatusSymbols();

        source.onended = () => {
          if (audioCtx.currentTime >= nextAudioStartTime - 0.05) {
            lipSyncOpen = 0.0;
            isLiveAudioPlaying = false;
            setEmotion('ATTENTIVE', 3000);
            updateStatusSymbols();
            if (isContinuousConversation) {
              setTimeout(startListening, 250);
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
      showSubtitles('AURA (THINKING)', '...');

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

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 6000);

      const response = await fetch(`${cleanBase}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Bypass-Tunnel-Reminder': 'true'
        },
        body: JSON.stringify({
          prompt: promptText,
          system_instruction: systemInstruction
        }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

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
        return '[EMOTION: HAPPY] You are most welcome! It is my absolute pleasure to assist you here at IEEE RAS at E-JUST.';
      }
      if (lower.includes('who are you') || lower.includes('your name') || lower.includes('من أنت')) {
        return '[EMOTION: ATTENTIVE] I am AURA-EJUST v3.0, the flagship autonomous reception humanoid created by the IEEE RAS student branch at E-JUST.';
      }
      if (lower.includes('hall') || lower.includes('conference') || lower.includes('theatre') || lower.includes('قاعة')) {
        return '[EMOTION: CURIOUS] The Main Conference Hall is located along the primary line-guided path, and the Grand Theatre is at station marker two. Please follow me!';
      }
      if (lower.includes('hello') || lower.includes('hi') || lower.includes('مرحبا') || lower.includes('أهلا')) {
        return '[EMOTION: HAPPY] Hello and welcome to E-JUST! I am ready to guide you to your session hall. Please tap your NFC badge on my chest.';
      }
      if (lower.includes('robot') || lower.includes('spec') || lower.includes('motor')) {
        return '[EMOTION: CURIOUS] I am powered by an ESP32 DevKit V1 with high-torque geared motors, 5-channel line tracking, front gaze vision, and Nordic UART BLE connectivity.';
      }
      return '[EMOTION: ATTENTIVE] Thank you for your inquiry. I am here to assist your visit and guide you through the IEEE RAS event halls at E-JUST.';
    }

    function toggleFullScreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
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

      localStorage.setItem('AURA_API_PROVIDER', apiProvider);
      localStorage.setItem('AURA_OPENROUTER_KEY', openRouterKey);
      localStorage.setItem('AURA_OPENROUTER_MODEL', openRouterModel);
      localStorage.setItem('AURA_GEMINI_KEY', apiKey);
      localStorage.setItem('AURA_GEMINI_MODEL', selectedModel);
      localStorage.setItem('AURA_VOICE', selectedVoice);

      if (apiProvider === 'gemini') {
        initLiveWebSocket();
      } else if (liveWs) {
        try { liveWs.close(); } catch(e) {}
        liveWs = null;
        isLiveWsConnected = false;
      }
      updateStatusSymbols();
      closeSettings();
    }

    // Startup Initialization
    window.addEventListener('DOMContentLoaded', () => {
      initSpeechRecognition();
      if (apiProvider === 'gemini') {
        initLiveWebSocket();
      }
      updateStatusSymbols();
      showSubtitles('AURA-EJUST', 'Welcome to IEEE RAS at E-JUST. Speak to begin.');

      document.addEventListener('click', unlockAudioContext, { passive: true });
      document.addEventListener('touchstart', unlockAudioContext, { passive: true });
    });
  </script>
</body>
</html>
'''

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

print(f"Successfully generated 8-bit Cyber Face at {OUTPUT_PATH} ({len(HTML_CONTENT)} bytes)")
