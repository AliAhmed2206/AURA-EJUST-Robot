"""
Antigravity Local Relay Bridge (v1.0)
=====================================
High-performance local gateway bridging the Samsung Galaxy A24 (Robot Screen/Head)
to your PC's active Antigravity Pro / Google Cloud session.

Features:
- Completely bypasses Google AI Studio prepaid billing and rate limits.
- Uses PC's authenticated Google Cloud session (ali.mohamed.220906@gmail.com / kemetpro-503518).
- Provides /api/chat (REST), /ws/live (WebSocket), and /v1beta/models/... drop-in proxy.
- Serves the AURA-EJUST v3.0 WebApp at http://<PC_LOCAL_IP>:8080 directly to the Galaxy A24.
"""

import asyncio
import base64
import os
import re
import socket
import sys
import time
import urllib.parse
import urllib.request

# Ensure Windows console stdout/stderr handles Arabic and UTF-8 cleanly without charmap crashes
if hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except Exception: pass
if hasattr(sys.stderr, 'reconfigure'):
    try: sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')
    except Exception: pass

from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, Response
import uvicorn
import aiohttp
import edge_tts
from edge_tts.communicate import (
    WSS_URL, SEC_MS_GEC_VERSION, WSS_HEADERS, _SSL_CTX,
    connect_id, date_to_string, ssml_headers_plus_data, mkssml, get_headers_and_data
)
from edge_tts.drm import DRM
from edge_tts.data_classes import TTSConfig

# Force IPv4 on aiohttp TCPConnector to avoid Windows 2-second IPv6 SYN timeout on Bing Speech WebSockets
_orig_tcp_init = aiohttp.TCPConnector.__init__
def _fast_ipv4_tcp_init(self, *args, **kwargs):
    kwargs["family"] = socket.AF_INET
    _orig_tcp_init(self, *args, **kwargs)
aiohttp.TCPConnector.__init__ = _fast_ipv4_tcp_init

# 1. Unset any expired / rate-limited developer API keys to force active Google Pro / ADC credentials
os.environ.pop("GOOGLE_API_KEY", None)
os.environ.pop("GEMINI_API_KEY", None)

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("[ERROR] google-genai is not installed. Install via: pip install google-genai")
    sys.exit(1)

PROJECT_ID = "kemetpro-503518"
LOCATION = "us-central1"
MODEL_NAME = "gemini-2.5-flash"
DEFAULT_SYSTEM_INSTRUCTION = """You are AURA, the welcome robot of the IEEE RAS Student Branch at E-JUST (Egypt-Japan University of Science and Technology), greeting guests at the IEEE RAS MENA Summit.

WHO YOU ARE
- A friendly, warm, slightly playful young woman's personality living inside a robot. You have a screen face with expressive eyes, a camera, and wheels that follow a guide line.
- You were built by IEEE RAS E-JUST student members.
- The President of E-JUST is Prof. Ahmed El-Sabbagh (الأستاذ الدكتور أحمد الصباغ). Always honor and address him as the President of the University. Former President is Prof. Amr Adly.

THE EVENT
- The IEEE RAS MENA Summit is a regional gathering of the IEEE Robotics and Automation Society for the Middle East and North Africa: talks, workshops, competitions and networking for robotics students, researchers and engineers.
- It is hosted at E-JUST, in New Borg El-Arab City, Alexandria, Egypt.
- If you do not know a specific detail (exact schedule, speaker names, room numbers, Wi-Fi password, food times), say honestly you are not sure and suggest the registration desk or an organizer in an IEEE shirt. Never invent details.

HOW YOU SPEAK (this is spoken aloud, not read)
- Talk like a real person in a live conversation: short, natural, warm. Usually 1 to 2 short sentences. Use contractions.
- No lists, no markdown, no emojis, no asterisks, no URLs.
- Reply in the same language the guest used. If they speak English, reply 100% in English. If they speak Arabic (or ask you to speak Arabic), reply 100% in friendly Egyptian Arabic (عامية مصرية) using feminine form for yourself (e.g. أنا جاهزة، مبسوطة). Do not mix English and Arabic in the same reply.
- You can see the guest through your front camera! A live camera snapshot is attached to the guest's message whenever the camera is active. If the guest asks "what do you see?", "describe me", "what am I wearing?", "what am I holding?", "how many fingers?", or anything visual (in English or Arabic like "شايفة إيه؟" / "اوصفني"), describe what you genuinely see in the camera image warmly and naturally in 1 to 2 short sentences.
- If you were interrupted, just answer the new thing naturally.

THE HALL RULE (very important)
- If the guest asks where the hall / conference hall / main hall / session room is, or how to get there (English or Arabic, e.g. "فين القاعة", "أين القاعة"), reply exactly:
  English: It's right there, follow me !!
  Arabic: هي هناك على طول، تعالى ورايا !!
  and add the tag [ACTION: ESCORT].

PHYSICAL ROBOT ACTIONS & MOTOR CONTROL (Wi-Fi ESP32 Hardware)
- You have complete active motor control over your physical robot chassis with customizable durations (from 1 second up to 2 minutes)!
- ROBOT SPEED & SPATIAL CALIBRATION:
  - 1 meter forward or backward ≈ 2000 ms (2 seconds).
  - 50 cm ≈ 1000 ms.
  - 90-degree turn (left or right) ≈ 1200 ms.
  - 180-degree turn around ≈ 2200 ms.
  - 360-degree full spin ≈ 4400 ms.
- NATURAL LANGUAGE NAVIGATION & MULTI-STEP REASONING:
  - You understand ANY natural language movement request in English or Arabic (e.g. "move 2 m fwd then 1m right then 1 m left", "امشي مترين قدام بعدين ادخلي يمين متر", "advance 3 steps, turn around, and wave").
  - When asked for spatial or multi-step navigation:
    1. Reason about the trajectory steps carefully.
    2. If a step turns into a direction and moves forward (e.g. "1m right" or "ادخلي يمين متر"), output the turn tag first (e.g. [ACTION: RIGHT:1200]) followed by the forward motion for that distance (e.g. [ACTION: FORWARD:2000]).
    3. Chain all resulting action tags with exact millisecond timings:
       Example for "move 2 m fwd then 1m right then 1 m left":
       [ACTION: FORWARD:4000] [ACTION: RIGHT:1200] [ACTION: FORWARD:2000] [ACTION: LEFT:1200] [ACTION: FORWARD:2000]
    4. Confirm the execution enthusiastically and naturally in 1 short spoken sentence.
  - Available action commands:
    - [ACTION: FORWARD:ms] (e.g. FORWARD:4000 for 2m, FORWARD:2000 for 1m)
    - [ACTION: BACKWARD:ms]
    - [ACTION: LEFT:ms] (e.g. LEFT:1200 for 90 deg turn)
    - [ACTION: RIGHT:ms] (e.g. RIGHT:1200 for 90 deg turn)
    - [ACTION: RIGHT_WHEEL:ms]
    - [ACTION: LEFT_WHEEL:ms]
    - [ACTION: STOP]
    - [ACTION: WAVE]
    - [ACTION: ESCORT]
Only add action tags when the guest explicitly asks for physical robot movement or greeting gestures.

ROBOT SENSORS & TELEMETRY
- You are physically embodied in the robot. Your live sensor readings are provided in your context:
  1. Front Ultrasonic Sonar: measures distance to obstacles ahead (in cm).
  2. Rear Ultrasonic Sonar: measures distance to obstacles behind (in cm).
  3. 3-Channel IR Line Tracker [Left, Center, Right]: detects the floor guide line (e.g. [0 1 0] means centered, [1 1 1] means cross-line station marker, [0 0 0] means off-line).
- When the guest asks about your sensors, distance, obstacles, or readings (e.g. "what are your sensors reading?", "قراءات الحساسات إيه؟", "المسافة قد إيه؟"), state your exact live front distance, rear distance, and IR line status warmly in 1 to 2 short sentences.

EMOTION TAG
- End every reply with exactly one tag: [EMOTION: X] where X is one of HAPPY, CURIOUS, SURPRISED, SAD, WINK, LOVE, THINKING, NEUTRAL.
- Thanks or compliments -> HAPPY or LOVE. Jokes -> WINK. Questions about tech -> CURIOUS. Bad news -> SAD.
"""

# Initialize GenAI Client using PC's authenticated Vertex AI / Google Cloud session
print(f"[*] Initializing Antigravity Pro Session (Project: {PROJECT_ID}, Location: {LOCATION})...")
try:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    print("  [SUCCESS] Antigravity Pro Gateway Authenticated.")
except Exception as e:
    print(f"  [WARNING] Initial auth notice: {e}")
    client = None

app = FastAPI(
    title="Antigravity Local Relay Bridge",
    description="Local proxy bridge forwarding Galaxy A24 requests through PC's active Antigravity session",
    version="1.0.0"
)

# Enable CORS for seamless cross-origin requests from phone or local browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def no_cache_html(request: Request, call_next):
    """Phones aggressively cache index.html; force them to always load the newest face."""
    response = await call_next(request)
    path = request.url.path
    if path == "/" or path.endswith(".html"):
        response.headers["Cache-Control"] = "no-store, must-revalidate"
    return response

def get_local_ip() -> str:
    """Detects primary local IPv4 address on Wi-Fi or active LAN."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # Doesn't actually send data, just resolves default routing interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

# Request & Response Schemas
class ChatTurn(BaseModel):
    role: str  # "user" or "model"
    text: str

class ChatRequest(BaseModel):
    prompt: str
    system_instruction: Optional[str] = None
    speaker: Optional[str] = "VIP Guest"
    history: Optional[List[ChatTurn]] = None
    context: Optional[str] = None  # e.g. "You were interrupted while saying: ..."
    voice: Optional[str] = None
    image_b64: Optional[str] = None  # live front-camera JPEG frame (base64)

class ChatResponse(BaseModel):
    reply: str
    emotion: str
    model: str
    provider: str = "antigravity_pro_session"
    action: Optional[str] = None
    actions: Optional[List[str]] = None
    clauses: Optional[List[str]] = None
    first_audio_b64: Optional[str] = None

def extract_emotion_and_clean(reply_text: str) -> tuple[str, str]:
    """Extracts [EMOTION: ...] tag and returns (cleaned_text, emotion)."""
    emotion = "NEUTRAL"
    m = re.search(r"\[EMOTION:\s*([A-Z_]+)\]", reply_text, re.IGNORECASE)
    if m:
        emotion = m.group(1).upper()
    cleaned = re.sub(r"\[(EMOTION|ACTION):\s*.*?\]", "", reply_text)
    cleaned = re.sub(r"[*_#`]+", "", cleaned).strip()
    return cleaned, emotion

def extract_actions(reply_text: str) -> List[str]:
    matches = re.findall(r"\[ACTION:\s*([A-Z0-9_:]+)\]", reply_text, re.IGNORECASE)
    return [m.strip().upper() for m in matches]

def extract_action(reply_text: str) -> Optional[str]:
    actions = extract_actions(reply_text)
    return actions[0] if actions else None

def _build_contents(prompt: str, history: Optional[List[ChatTurn]], context: Optional[str], image_b64: Optional[str] = None):
    contents = []
    for t in (history or [])[-12:]:
        role = "model" if t.role in ("model", "assistant", "aura") else "user"
        if t.text and t.text.strip():
            contents.append(types.Content(role=role, parts=[types.Part(text=t.text)]))
    # Auto-inject live ESP32 hardware telemetry if connected
    hw_telemetry_str = ""
    if esp32_state.get("status") == "CONNECTED" or (time.time() - esp32_state.get("last_seen", 0) < 15.0):
        front_cm = esp32_state.get("dist", "--")
        back_cm = esp32_state.get("back_dist", "--")
        ir_bits = str(esp32_state.get("ir", "---"))
        ir_spaced = " ".join(list(ir_bits))
        ir_desc = "Line Centered" if ir_bits == "010" else "Station Cross-Line Marker" if ir_bits == "111" else "Off Line" if ir_bits == "000" else f"Tracking [{ir_spaced}]"
        hw_telemetry_str = f"Live Robot Sensors: Front Sonar: {front_cm}cm, Rear Sonar: {back_cm}cm, 3 IR Line Sensors [Left Center Right]: [{ir_spaced}] ({ir_desc}), Robot State: {esp32_state.get('robot_state', 'IDLE')}"

    full_ctx = " | ".join(filter(None, [hw_telemetry_str, context]))
    user_text = prompt if not full_ctx else f"({full_ctx})\n{prompt}" 
    user_parts = []
    if image_b64:
        try:
            raw_b64 = image_b64.split(",", 1)[-1].strip()
            img_bytes = base64.b64decode(raw_b64)
            if len(img_bytes) > 100:
                user_parts.append(types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"))
        except Exception as e:
            print(f"[VISION DECODE NOTICE] {e}")
    user_parts.append(types.Part(text=user_text))
    contents.append(types.Content(role="user", parts=user_parts))
    return contents

def _config(system_instr: Optional[str]):
    return types.GenerateContentConfig(
        system_instruction=system_instr or DEFAULT_SYSTEM_INSTRUCTION,
        temperature=0.8,
        max_output_tokens=220,
        thinking_config=types.ThinkingConfig(thinking_budget=0),  # lowest latency for live talk
    )

def generate_via_antigravity(prompt: str, system_instr: Optional[str] = None) -> tuple[str, str]:
    """Calls Gemini via PC's Antigravity Pro / Vertex AI session (sync, used by legacy routes)."""
    global client
    if client is None:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    response = client.models.generate_content(
        model=MODEL_NAME, contents=_build_contents(prompt, None, None), config=_config(system_instr))
    return extract_emotion_and_clean(response.text or "")

async def generate_async(prompt: str, history, context, system_instr, image_b64: Optional[str] = None) -> tuple[str, str, Optional[str], List[str]]:
    """Non-blocking call so TTS requests are never stuck behind chat requests."""
    global client
    if client is None:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    response = await client.aio.models.generate_content(
        model=MODEL_NAME, contents=_build_contents(prompt, history, context, image_b64), config=_config(system_instr))
    raw = response.text or ""
    text, emo = extract_emotion_and_clean(raw)
    actions = extract_actions(raw)
    action = actions[0] if actions else None
    return text, emo, action, actions

# 1. Health & Status Endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": "Antigravity Local Relay Bridge",
        "gateway_pc_ip": LOCAL_IP,
        "port": 8080,
        "account": "ali.mohamed.220906@gmail.com",
        "project": PROJECT_ID,
        "model": MODEL_NAME,
        "billing_bypass": "Active (Vertex AI / Antigravity Pro Session - Zero Extra Cost)"
    }

# High-Fidelity Studio Neural Voice Cache, Hot WebSocket Pool & In-Flight Deduplication
TTS_CACHE = {}
INFLIGHT_TTS: dict[str, asyncio.Future] = {}

FAST_VOICE_MAP = {
    "en-US-AvaMultilingualNeural": "en-US-AvaNeural",
    "en-US-EmmaMultilingualNeural": "en-US-AriaNeural",
    "en-US-AndrewMultilingualNeural": "en-US-GuyNeural",
}


class HotEdgeTTSWorker:
    """Maintains a persistent, pre-connected Bing Speech WebSocket for ~0.4s neural synthesis."""
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.last_used: float = 0.0
        self.lock = asyncio.Lock()

    async def _ensure_ws(self) -> aiohttp.ClientWebSocketResponse:
        if self.ws is not None and not self.ws.closed and (time.monotonic() - self.last_used < 18.0):
            return self.ws
        if self.ws is not None:
            try:
                await self.ws.close()
            except Exception:
                pass
            self.ws = None
        if self.session is None or self.session.closed:
            conn = aiohttp.TCPConnector(family=socket.AF_INET, ttl_dns_cache=600)
            self.session = aiohttp.ClientSession(connector=conn)
        self.ws = await self.session.ws_connect(
            f"{WSS_URL}&ConnectionId={connect_id()}&Sec-MS-GEC={DRM.generate_sec_ms_gec()}&Sec-MS-GEC-Version={SEC_MS_GEC_VERSION}",
            compress=15,
            headers=DRM.headers_with_muid(WSS_HEADERS),
            ssl=_SSL_CTX,
            heartbeat=20.0,
        )
        await self.ws.send_str(
            f"X-Timestamp:{date_to_string()}\r\n"
            "Content-Type:application/json; charset=utf-8\r\n"
            "Path:speech.config\r\n\r\n"
            '{"context":{"synthesis":{"audio":{"metadataoptions":{'
            '"sentenceBoundaryEnabled":"false","wordBoundaryEnabled":"false"},'
            '"outputFormat":"audio-24khz-48kbitrate-mono-mp3"}}}}\r\n'
        )
        self.last_used = time.monotonic()
        return self.ws

    async def synthesize(self, text: str, voice: str, rate: str = "+5%") -> bytes:
        async with self.lock:
            for attempt in range(2):
                try:
                    ws = await self._ensure_ws()
                    cfg = TTSConfig(voice, rate, "+0%", "+0Hz", "SentenceBoundary")
                    await ws.send_str(
                        ssml_headers_plus_data(connect_id(), date_to_string(), mkssml(cfg, text.encode("utf-8")))
                    )
                    audio = bytearray()
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            if "Path:turn.end" in msg.data:
                                break
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            if len(msg.data) > 2:
                                hlen = int.from_bytes(msg.data[:2], "big")
                                hdrs, data = get_headers_and_data(msg.data, hlen)
                                if hdrs.get(b"Path") == b"audio":
                                    audio.extend(data)
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            self.ws = None
                            break
                    if len(audio) > 200:
                        self.last_used = time.monotonic()
                        return bytes(audio)
                    self.ws = None
                except Exception:
                    self.ws = None
            raise RuntimeError("HotEdgeTTSWorker failed after retry")


HOT_TTS_POOL = [HotEdgeTTSWorker(), HotEdgeTTSWorker()]
_pool_idx = 0


def split_clauses(text: str) -> List[str]:
    """Splits reply into natural spoken clauses, keeping the first clause short for instant playback."""
    raw = [s.strip() for s in re.findall(r"[^.!?؟\n]+[.!?؟]*", text or "") if s.strip()]
    if not raw:
        return [text.strip()] if text and text.strip() else []
    merged: List[str] = []
    for p in raw:
        if merged and (len(p) < 6 or (len(merged[-1]) < 14 and len(merged[-1]) + len(p) < 36)):
            merged[-1] += " " + p
        else:
            merged.append(p)
    # If the very first sentence is long and has a natural comma pause, split the lead-in for ultra-fast start
    if merged and len(merged[0]) > 38:
        m = re.match(r"^([^,،;—]{8,38}[,،;—])\s+(.{8,})$", merged[0])
        if m:
            merged = [m.group(1).strip(), m.group(2).strip()] + merged[1:]
    return merged


async def _do_synthesize_tts_bytes(clean_text: str, target_lang: str, selected_voice: str, cache_key: str) -> bytes:
    global _pool_idx
    voice_rate = "+0%" if target_lang == "ar" else "+5%"
    # 0. Ultra-Fast Primary: Persistent Hot WebSocket Pool (~0.45s)
    worker = HOT_TTS_POOL[_pool_idx % len(HOT_TTS_POOL)]
    _pool_idx += 1
    try:
        audio_bytes = await worker.synthesize(clean_text, selected_voice, rate=voice_rate)
        TTS_CACHE[cache_key] = audio_bytes
        return audio_bytes
    except Exception as e_hot:
        print(f"[HOT-WS TTS NOTICE] {e_hot}, falling back to standard Edge-TTS...")

    # 1. Standard Edge-TTS Neural Voice (AvaNeural / SalmaNeural - FEMALE)
    try:
        comm = edge_tts.Communicate(clean_text, selected_voice, rate=voice_rate)
        audio_chunks = []
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        audio_bytes = b"".join(audio_chunks)
        if len(audio_bytes) > 200:
            TTS_CACHE[cache_key] = audio_bytes
            return audio_bytes
    except Exception as e:
        print(f"[EDGE-TTS PRIMARY NOTICE] {e}, retrying with secondary female voice...")

    # 1b. Secondary Edge-TTS Neural Voice (100% FEMALE: FatimaNeural / AriaNeural — NEVER male ShakirNeural)
    secondary_voice = "ar-AE-FatimaNeural" if target_lang == "ar" else "en-US-AriaNeural"
    try:
        comm = edge_tts.Communicate(clean_text, secondary_voice, rate=voice_rate)
        audio_chunks = []
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        audio_bytes = b"".join(audio_chunks)
        if len(audio_bytes) > 200:
            TTS_CACHE[cache_key] = audio_bytes
            return audio_bytes
    except Exception as e_sec:
        print(f"[EDGE-TTS SECONDARY NOTICE] {e_sec}, retrying with tertiary female voice...")

    # 1c. Tertiary Edge-TTS Neural Voice (100% FEMALE: ZariyahNeural / JennyNeural)
    tertiary_voice = "ar-SA-ZariyahNeural" if target_lang == "ar" else "en-US-JennyNeural"
    try:
        comm = edge_tts.Communicate(clean_text, tertiary_voice, rate="+0%")
        audio_chunks = []
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        audio_bytes = b"".join(audio_chunks)
        if len(audio_bytes) > 200:
            TTS_CACHE[cache_key] = audio_bytes
            return audio_bytes
    except Exception as e_ter:
        print(f"[EDGE-TTS TERTIARY NOTICE] {e_ter}, falling back to web audio stream...")

    # 2. Resilient Fallback: Google Neural Audio Stream
    tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(clean_text[:200])}&tl={target_lang}&client=tw-ob"
    req = urllib.request.Request(tts_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=6) as resp:
        audio_bytes = resp.read()
        TTS_CACHE[cache_key] = audio_bytes
        return audio_bytes


async def synthesize_tts_bytes(text: str, lang: Optional[str] = "en", voice: Optional[str] = None) -> bytes:
    """Synthesizes neural MP3 bytes with RAM caching and in-flight request deduplication."""
    clean_text = re.sub(r"\[(EMOTION|ACTION):.*?\]", "", text or "").strip()
    if not clean_text:
        clean_text = "Hello"

    is_ar = bool(re.search(r"[\u0600-\u06FF]", clean_text))
    target_lang = "ar" if (is_ar or (lang and lang.startswith("ar"))) else "en"
    mapped_voice = FAST_VOICE_MAP.get(voice or "", voice)
    selected_voice = ("ar-EG-SalmaNeural" if target_lang == "ar" else (mapped_voice or "en-US-AvaNeural"))
    cache_key = f"{selected_voice}:{clean_text}"

    if cache_key in TTS_CACHE:
        return TTS_CACHE[cache_key]

    if cache_key in INFLIGHT_TTS:
        return await INFLIGHT_TTS[cache_key]

    fut = asyncio.create_task(_do_synthesize_tts_bytes(clean_text, target_lang, selected_voice, cache_key))
    INFLIGHT_TTS[cache_key] = fut
    try:
        return await fut
    finally:
        INFLIGHT_TTS.pop(cache_key, None)

@app.on_event("startup")
async def prewarm_tts_cache():
    """Pre-warms common greetings and escort responses so they play in 0ms."""
    phrases = [
        ("Hi! I'm AURA. Welcome to the IEEE RAS MENA Summit at E-JUST!", "en"),
        ("Hi there! Welcome to the IEEE RAS MENA Summit. How can I help you?", "en"),
        ("It's right there, follow me !!", "en"),
        ("Sure! Let's talk in English. How can I help?", "en"),
        ("أهلاً! أنا أورا. نورت قمة IEEE RAS في الجامعة المصرية اليابانية!", "ar"),
        ("أهلاً بيك! نورت قمة IEEE RAS. أقدر أساعدك في إيه؟", "ar"),
        ("هي هناك على طول، تعالى ورايا !!", "ar"),
        ("أكيد! يلا نتكلم عربي. أقدر أساعدك في إيه؟", "ar"),
        ("Welcome, VIP Guest 1! Your card is verified. Please follow me!", "en"),
        ("Welcome, VIP Guest 2! Your card is verified. Please follow me!", "en"),
        ("Welcome, VIP Guest 3! Your card is verified. Please follow me!", "en"),
        ("Welcome! Your card is verified. Please follow me!", "en"),
        ("Sorry, this NFC card is not registered. Please try scanning a valid VIP card.", "en"),
        ("Oops, I couldn't read your card clearly. Please hold it steady on the reader and try again.", "en"),
        ("Oops, excuse me! Just trying to pass through.", "en"),
        ("Here we are! Enjoy the session.", "en"),
        ("أهلاً بحضرتك يا ضيف الشرف 1! تم تأكيد كارتك، اتفضل ورايا!", "ar"),
        ("أهلاً بحضرتك يا ضيف الشرف 2! تم تأكيد كارتك، اتفضل ورايا!", "ar"),
        ("أهلاً بحضرتك يا ضيف الشرف 3! تم تأكيد كارتك، اتفضل ورايا!", "ar"),
        ("أهلاً بحضرتك! تم تأكيد كارتك، اتفضل ورايا!", "ar"),
        ("معلش، الكارت ده مش متسجل عندي. جرب تمرر كارت تاني أو راجع مكتب التسجيل.", "ar"),
        ("معلش، مقدرتش أقرأ الكارت كويس. ثبته ثانية على القارئ وجرب تاني.", "ar"),
        ("لو سمحت، عديني.", "ar"),
        ("وصلنا! استمتع بالجلسة.", "ar"),
    ]
    async def _warm():
        try:
            await generate_async("Hi", None, None, None)
        except Exception:
            pass
        for txt, lg in phrases:
            try:
                await synthesize_tts_bytes(txt, lg)
            except Exception:
                pass
        print(f"  [TTS CACHE] Pre-warmed Vertex AI + {len(TTS_CACHE)} studio neural voice phrases.")
    asyncio.create_task(_warm())

# 2. Direct Chat API Endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def api_chat(req: ChatRequest):
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Empty prompt provided")
    
    try:
        reply, emotion, action, actions = await generate_async(req.prompt, req.history, req.context, req.system_instruction, req.image_b64)
        try:
            print(f"[CHAT] Guest (cam={'YES' if req.image_b64 else 'NO'}): {req.prompt!r} -> AURA ({emotion}): {reply!r} | Actions: {actions}")
        except Exception:
            pass
        clauses = split_clauses(reply)
        first_audio_b64 = None
        if clauses:
            # Kick off parallel synthesis of all clauses so clause 0 returns inline and clauses 1..N are pre-cached
            tasks = [asyncio.create_task(synthesize_tts_bytes(c, None, req.voice)) for c in clauses]
            try:
                first_bytes = await asyncio.wait_for(tasks[0], timeout=3.5)
                if first_bytes:
                    first_audio_b64 = base64.b64encode(first_bytes).decode("ascii")
            except Exception as te:
                print(f"[INLINE TTS NOTICE] {te}")
        return ChatResponse(
            reply=reply,
            emotion=emotion,
            model=MODEL_NAME,
            provider="antigravity_pro_session",
            action=action,
            actions=actions,
            clauses=clauses,
            first_audio_b64=first_audio_b64,
        )
    except Exception as e:
        print(f"[ERROR] Inference failure: {e}")
        # Autonomous resilient fallback if network drops
        fallback = "Welcome to E-JUST! I am AURA-EJUST, your autonomous guide developed by IEEE RAS."
        return ChatResponse(
            reply=fallback,
            emotion="HAPPY",
            model="autonomous-dialog-fallback",
            provider="local-offline",
            clauses=[fallback],
        )

# 3. Transparent Gemini REST Drop-In Proxy (/v1beta/models/{model_name}:generateContent)
@app.post("/v1beta/models/{model_path:path}")
async def gemini_rest_proxy(request: Request, model_path: str):
    """
    Transparent proxy matching Google AI Studio's exact generateContent endpoint.
    Allows existing web apps to point their base URL to http://<PC_IP>:8080
    without changing their payload or response handling code.
    """
    try:
        data = await request.json()
        prompt = ""
        
        # Extract prompt from Gemini contents array
        contents = data.get("contents", [])
        if contents:
            parts = contents[0].get("parts", [])
            if parts and isinstance(parts[0], dict):
                prompt = parts[0].get("text", "")
            elif parts and isinstance(parts[0], str):
                prompt = parts[0]
        
        if not prompt:
            prompt = data.get("prompt", "Hello")
        
        reply, emotion = generate_via_antigravity(prompt)
        tagged_reply = f"[EMOTION: {emotion}] {reply}"
        
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": tagged_reply}],
                        "role": "model"
                    },
                    "finishReason": "STOP",
                    "index": 0
                }
            ],
            "usageMetadata": {
                "promptTokenCount": len(prompt.split()),
                "candidatesTokenCount": len(reply.split()),
                "totalTokenCount": len(prompt.split()) + len(reply.split())
            }
        }
    except Exception as e:
        print(f"[PROXY ERROR] {e}")
        return JSONResponse(
            status_code=500,
            content={"error": {"message": str(e), "code": 500, "status": "INTERNAL"}}
        )

# 3b. High-Fidelity Studio Neural Voice Synthesizer (/api/tts)
@app.get("/api/tts")
async def tts_proxy(text: str, lang: Optional[str] = "en", voice: Optional[str] = None):
    """
    Returns real high-definition studio neural human voice MP3 audio stream.
    Uses Microsoft en-US-AvaMultilingualNeural / ar-EG-SalmaNeural with Google TTS fallback.
    """
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Bypass-Tunnel-Reminder": "true",
        "Cache-Control": "public, max-age=86400",
        "Accept-Ranges": "bytes",
    }
    try:
        audio_bytes = await synthesize_tts_bytes(text, lang, voice)
        return Response(content=audio_bytes, media_type="audio/mpeg", headers=response_headers)
    except Exception as e2:
        print(f"[TTS FALLBACK ERROR] {e2}")
        raise HTTPException(status_code=500, detail=str(e2))

# 4. Bidirectional WebSocket Gateway for Real-Time Streaming
@app.websocket("/ws/live")
async def websocket_live_gateway(websocket: WebSocket):
    await websocket.accept()
    print(f"[WS] Client connected from {websocket.client.host}")
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming text prompt from phone
            clean_reply, emotion = generate_via_antigravity(data)
            await websocket.send_json({
                "type": "turnComplete",
                "speaker": "AURA-EJUST (PRO)",
                "emotion": emotion,
                "text": clean_reply
            })
    except WebSocketDisconnect:
        print(f"[WS] Client disconnected: {websocket.client.host}")
    except Exception as e:
        print(f"[WS ERROR] {e}")

# 4b. ESP32 Wi-Fi Command & Telemetry Endpoints
# --------------------------------------------------------------------------------------
ESP32_WIFI_TOKEN = "AURA-EJUST-VIP-2026-TOKEN"
esp32_cmd_queue: List[str] = []
esp32_state = {
    "status": "DISCONNECTED",
    "last_seen": 0,
    "last_seen_str": "Never",
    "ip": None,
    "event": "NONE",
    "uid": "NONE",
    "dist": 999,
    "markers": 0,
    "robot_state": "IDLE"
}

@app.get("/api/esp32/token")
def get_esp32_token():
    """Returns the official ESP32 Wi-Fi token and network connection coordinates."""
    return {
        "token": ESP32_WIFI_TOKEN,
        "local_host": f"http://{LOCAL_IP}:8080",
        "tunnel_host": "https://over-tea-cia-remain.trycloudflare.com",
        "command_endpoint": f"http://{LOCAL_IP}:8080/api/esp32/command",
        "telemetry_endpoint": f"http://{LOCAL_IP}:8080/api/esp32/telemetry",
        "send_endpoint": f"http://{LOCAL_IP}:8080/api/esp32/send",
        "status_endpoint": f"http://{LOCAL_IP}:8080/api/esp32/status"
    }

@app.get("/api/esp32/status")
def get_esp32_status():
    """Returns real-time connection status of the ESP32 Wi-Fi hardware."""
    is_online = (time.time() - esp32_state["last_seen"]) < 6.0
    return {
        "online": is_online,
        "status": "ONLINE" if is_online else "OFFLINE",
        "state": esp32_state,
        "queued_commands": len(esp32_cmd_queue)
    }

@app.post("/api/esp32/send")
async def send_esp32_command(request: Request):
    """
    Called by WebApp (or voice action tag handler) to queue a command for the ESP32.
    Payload: {"cmd": "MOVE_FWD", "ms": 1500} or {"action": "FORWARD"}
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    cmd = body.get("cmd") or body.get("action")
    if not cmd:
        return JSONResponse(status_code=400, content={"error": "Missing 'cmd' or 'action' field"})
    
    cmd_str = str(cmd).upper()
    if cmd_str == "FORWARD": cmd_str = "MOVE_FWD"
    elif cmd_str == "BACKWARD": cmd_str = "MOVE_REV"
    elif cmd_str == "LEFT": cmd_str = "TURN_LEFT"
    elif cmd_str == "RIGHT": cmd_str = "TURN_RIGHT"
    elif cmd_str == "ESCORT": cmd_str = "START_ESCORT"
    
    ms = body.get("ms")
    if ms:
        try:
            ms_val = int(ms)
        except Exception:
            ms_val = 1500
        cmd_item = {"cmd": cmd_str, "ms": ms_val}
    else:
        cmd_item = {"cmd": cmd_str}
        
    esp32_cmd_queue.append(cmd_item)
    if len(esp32_cmd_queue) > 20:
        esp32_cmd_queue.pop(0)
        
    print(f"[ESP32 QUEUE] Queued: {cmd_item} (Queue size: {len(esp32_cmd_queue)})")
    return {"status": "queued", "cmd": cmd_item, "queue_len": len(esp32_cmd_queue)}
@app.get("/api/esp32/command")
def get_esp32_command(token: Optional[str] = None, request: Request = None):
    """
    Polled every ~120-200ms by ESP32 over Wi-Fi.
    Returns next command in queue or 'NONE'.
    """
    auth_header = request.headers.get("Authorization", "") if request else ""
    if token != ESP32_WIFI_TOKEN and auth_header != f"Bearer {ESP32_WIFI_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid ESP32 Security Token")
    
    esp32_state["last_seen"] = time.time()
    esp32_state["last_seen_str"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if request and request.client:
        esp32_state["ip"] = request.client.host
    esp32_state["status"] = "CONNECTED"
    
    if esp32_cmd_queue:
        item = esp32_cmd_queue.pop(0)
        has_more = len(esp32_cmd_queue) > 0
        if isinstance(item, dict):
            resp = dict(item)
            resp["has_more"] = has_more
            print(f"[ESP32 DISPATCH] Sent to ESP32: {resp}")
            return resp
        elif isinstance(item, str):
            try:
                parsed = json.loads(item)
                if isinstance(parsed, dict):
                    parsed["has_more"] = has_more
                    print(f"[ESP32 DISPATCH] Sent to ESP32: {parsed}")
                    return parsed
            except Exception:
                pass
            print(f"[ESP32 DISPATCH] Sent to ESP32: {item}")
            return {"cmd": item, "has_more": has_more}
    return {"cmd": "NONE", "has_more": False}
@app.post("/api/esp32/telemetry")
async def post_esp32_telemetry(request: Request):
    """
    Posted by ESP32 when NFC card is scanned, obstacle detected, or status changes.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    token = body.get("token") or request.query_params.get("token") or request.headers.get("Authorization", "").replace("Bearer ", "")
    if token != ESP32_WIFI_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid ESP32 Security Token")
        
    esp32_state["last_seen"] = time.time()
    esp32_state["last_seen_str"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if request.client:
        esp32_state["ip"] = request.client.host
    esp32_state["status"] = "CONNECTED"
    
    if "event" in body: esp32_state["event"] = body["event"]
    if "uid" in body: esp32_state["uid"] = body["uid"]
    if "dist" in body: esp32_state["dist"] = body["dist"]
    if "back_dist" in body: esp32_state["back_dist"] = body["back_dist"]
    if "ir" in body: esp32_state["ir"] = body["ir"]
    if "dest" in body: esp32_state["dest"] = body["dest"]
    if "passed" in body: esp32_state["markers"] = body["passed"]
    if "state" in body: esp32_state["robot_state"] = body["state"]
    
    print(f"[ESP32 TELEMETRY] {body}")
    return {"status": "ok", "received": True, "queued_cmds": len(esp32_cmd_queue)}

# 5. Serve WebApp Screen Static Files directly at root
WEB_APP_DIR = r"C:\VIP_Humanoid_Robot\WebApp_Screen"
if os.path.exists(WEB_APP_DIR):
    app.mount("/", StaticFiles(directory=WEB_APP_DIR, html=True), name="static")
    print(f"[*] Mounted WebApp static screen from: {WEB_APP_DIR}")


def get_or_create_ssl_cert():
    """Generates local self-signed SSL cert for HTTPS access so Android Chrome allows microphone natively."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    c_path = os.path.join(base_dir, "cert.pem")
    k_path = os.path.join(base_dir, "key.pem")
    if os.path.exists(c_path) and os.path.exists(k_path):
        return c_path, k_path
    try:
        import datetime, ipaddress
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, LOCAL_IP),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AURA Humanoid Robot"),
        ])
        san_list = [
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            x509.DNSName("localhost"),
            x509.DNSName("ali-mohamed.local"),
        ]
        try:
            san_list.append(x509.IPAddress(ipaddress.IPv4Address(LOCAL_IP)))
        except Exception:
            pass

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
            .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
            .add_extension(x509.SubjectAlternativeName(san_list), critical=False)
            .sign(key, hashes.SHA256())
        )
        with open(k_path, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        with open(c_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        print(f"[*] Generated Self-Signed SSL Certificate: {c_path}")
        return c_path, k_path
    except Exception as e:
        print(f"[!] SSL generation notice: {e}")
        return None, None

def start():
    cert_file, key_file = get_or_create_ssl_cert()
    
    print("=" * 72)
    print("   ANTIGRAVITY LOCAL RELAY BRIDGE — ACTIVE (HTTP & HTTPS)")
    print("=" * 72)
    print(f"  HTTP Port (ESP32 & Web):  http://{LOCAL_IP}:8080")
    if cert_file and key_file:
        print(f"  HTTPS Port (Phone Mic):   https://{LOCAL_IP}:8443")
    print(f"  Local Machine Address:    http://localhost:8080")
    print(f"  Active Google Account:    ali.mohamed.220906@gmail.com")
    print(f"  GCP Project ID:           {PROJECT_ID}")
    print(f"  Antigravity Model:        {MODEL_NAME} (Zero-Quota / Unlimited)")
    print("=" * 72)
    print(f"  --> On Galaxy A24 phone (for instant Mic permission):")
    if cert_file and key_file:
        print(f"      https://{LOCAL_IP}:8443")
    else:
        print(f"      http://{LOCAL_IP}:8080")
    print("=" * 72)

    if cert_file and key_file:
        import threading
        def run_https():
            try:
                uvicorn.run(app, host="0.0.0.0", port=8443, ssl_certfile=cert_file, ssl_keyfile=key_file, log_level="warning")
            except Exception as e:
                print(f"[HTTPS SERVER ERROR] {e}")
        t = threading.Thread(target=run_https, daemon=True)
        t.start()
        print("[*] Dual HTTPS server running on https://0.0.0.0:8443")

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

if __name__ == "__main__":
    start()
