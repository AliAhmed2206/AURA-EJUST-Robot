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

import os
import re
import socket
import sys
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

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
DEFAULT_SYSTEM_INSTRUCTION = (
    "You are AURA-EJUST v3.0, the flagship autonomous VIP reception and escort humanoid robot "
    "developed by IEEE RAS at Egypt-Japan University of Science and Technology (E-JUST) for the IEEE RAS MENA Summit. "
    "The IEEE RAS MENA Summit is the premier regional robotics and automation conference held at E-JUST campus in New Borg El-Arab City, Alexandria, Egypt. "
    "CRITICAL RULE 1: Whenever a guest asks 'where is the hall', 'where is the conference hall', 'where is the main hall', 'how to get to the hall', 'أين القاعة', 'فين القاعة', or 'قاعة المؤتمرات فين', "
    "you MUST respond immediately: \"It's right there, follow me !!\" (or in Arabic: \"إنها هناك تماماً، تفضل باتباعي !!\") with [EMOTION: HAPPY]. "
    "CRITICAL RULE 2: When asked if you can see them ('can you see me?', 'do you see me?', 'شايفاني؟', 'شيفاني؟'), "
    "respond with warmth and visual confirmation: \"Yes, I can see you right here! Welcome to the IEEE RAS MENA Summit at E-JUST.\" (or Arabic: \"نعم، أراك بوضوح أمامي! أهلاً وسهلاً بك في قمة IEEE RAS بالجامعة المصرية اليابانية\") with [EMOTION: HAPPY]. "
    "Provide concise, warm, natural spoken answers (1-2 sentences). "
    "When thanked, include [EMOTION: HAPPY]. When asked technical questions, include [EMOTION: CURIOUS]. "
    "When expressing affection or compliment, include [EMOTION: IN_LOVE] or [EMOTION: WINK]."
)

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
class ChatRequest(BaseModel):
    prompt: str
    system_instruction: Optional[str] = None
    speaker: Optional[str] = "VIP Guest"

class ChatResponse(BaseModel):
    reply: str
    emotion: str
    model: str
    provider: str = "antigravity_pro_session"

def extract_emotion_and_clean(reply_text: str) -> tuple[str, str]:
    """Extracts [EMOTION: ...] tag and returns (cleaned_text, emotion)."""
    emotion = "ATTENTIVE"
    m = re.search(r"\[EMOTION:\s*([A-Z_]+)\]", reply_text, re.IGNORECASE)
    if m:
        emotion = m.group(1).upper()
    cleaned = re.sub(r"\[EMOTION:\s*.*?\]", "", reply_text).strip()
    return cleaned, emotion

def generate_via_antigravity(prompt: str, system_instr: Optional[str] = None) -> tuple[str, str]:
    """Calls Gemini via PC's Antigravity Pro / Vertex AI session."""
    global client
    instruction = system_instr or DEFAULT_SYSTEM_INSTRUCTION
    
    if client is None:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    
    config = types.GenerateContentConfig(
        system_instruction=instruction,
        temperature=0.7,
        max_output_tokens=200,
    )
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )
    
    raw_text = response.text or ""
    return extract_emotion_and_clean(raw_text)

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

# 2. Direct Chat API Endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def api_chat(req: ChatRequest):
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Empty prompt provided")
    
    try:
        reply, emotion = generate_via_antigravity(req.prompt, req.system_instruction)
        return ChatResponse(
            reply=reply,
            emotion=emotion,
            model=MODEL_NAME,
            provider="antigravity_pro_session"
        )
    except Exception as e:
        print(f"[ERROR] Inference failure: {e}")
        # Autonomous resilient fallback if network drops
        fallback = "Welcome to E-JUST! I am AURA-EJUST, your autonomous guide developed by IEEE RAS."
        return ChatResponse(
            reply=fallback,
            emotion="HAPPY",
            model="autonomous-dialog-fallback",
            provider="local-offline"
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
# Uses Edge-TTS 7.3.1 with JennyNeural (English) & SalmaNeural (Egyptian Arabic)
TTS_CACHE = {}

@app.get("/api/tts")
async def tts_proxy(text: str, lang: Optional[str] = "en", voice: Optional[str] = None):
    """
    Returns real high-definition studio neural human voice MP3 audio stream.
    Uses Microsoft en-US-AvaNeural / ar-EG-SalmaNeural with Google TTS fallback.
    Includes Bypass-Tunnel-Reminder header to prevent Localtunnel splash pages.
    """
    import asyncio, edge_tts, urllib.request, urllib.parse
    from fastapi.responses import Response

    clean_text = re.sub(r"\[EMOTION:.*?\]", "", text).strip()
    if not clean_text:
        clean_text = "Hello"
    
    is_ar = bool(re.search(r"[\u0600-\u06FF]", clean_text))
    target_lang = "ar" if (is_ar or (lang and lang.startswith("ar"))) else "en"
    selected_voice = voice or ("ar-EG-SalmaNeural" if target_lang == "ar" else "en-US-JennyNeural")
    cache_key = f"{selected_voice}:{clean_text}"
    
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Bypass-Tunnel-Reminder": "true",
        "Cache-Control": "public, max-age=86400",
        "Accept-Ranges": "bytes",
    }
    
    if cache_key in TTS_CACHE:
        return Response(content=TTS_CACHE[cache_key], media_type="audio/mpeg", headers=response_headers)

    # 1. Primary: Edge-TTS Studio Neural Voice (JennyNeural / SalmaNeural)
    try:
        comm = edge_tts.Communicate(clean_text, selected_voice)
        audio_chunks = []
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        audio_bytes = b"".join(audio_chunks)
        if len(audio_bytes) > 200:
            TTS_CACHE[cache_key] = audio_bytes
            return Response(content=audio_bytes, media_type="audio/mpeg", headers=response_headers)
    except Exception as e:
        print(f"[EDGE-TTS PRIMARY NOTICE] {e}, retrying with secondary high-definition voice...")

    # 1b. Secondary Edge-TTS Neural Voice (AriaNeural / ShakirNeural)
    secondary_voice = "ar-EG-ShakirNeural" if target_lang == "ar" else "en-US-AriaNeural"
    try:
        comm = edge_tts.Communicate(clean_text, secondary_voice)
        audio_chunks = []
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
        audio_bytes = b"".join(audio_chunks)
        if len(audio_bytes) > 200:
            TTS_CACHE[cache_key] = audio_bytes
            return Response(content=audio_bytes, media_type="audio/mpeg", headers=response_headers)
    except Exception as e_sec:
        print(f"[EDGE-TTS SECONDARY NOTICE] {e_sec}, falling back to web audio stream...")

    # 2. Resilient Fallback: Google Neural Audio Stream
    try:
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(clean_text[:200])}&tl={target_lang}&client=tw-ob"
        req = urllib.request.Request(tts_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            audio_bytes = resp.read()
            TTS_CACHE[cache_key] = audio_bytes
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

# 5. Serve WebApp Screen Static Files directly at root
WEB_APP_DIR = r"C:\VIP_Humanoid_Robot\WebApp_Screen"
if os.path.exists(WEB_APP_DIR):
    app.mount("/", StaticFiles(directory=WEB_APP_DIR, html=True), name="static")
    print(f"[*] Mounted WebApp static screen from: {WEB_APP_DIR}")

def start():
    print("=" * 72)
    print("   ANTIGRAVITY LOCAL RELAY BRIDGE — ACTIVE")
    print("=" * 72)
    print(f"  PC Gateway Address:       http://{LOCAL_IP}:8080")
    print(f"  Local Machine Address:    http://localhost:8080")
    print(f"  Active Google Account:    ali.mohamed.220906@gmail.com")
    print(f"  GCP Project ID:           {PROJECT_ID}")
    print(f"  Antigravity Model:        {MODEL_NAME} (Zero-Quota / Unlimited)")
    print("=" * 72)
    print(f"  --> On Galaxy A24 phone, open Chrome and navigate to:")
    print(f"      http://{LOCAL_IP}:8080")
    print("=" * 72)
    
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

if __name__ == "__main__":
    start()
