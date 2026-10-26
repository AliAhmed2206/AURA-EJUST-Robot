export default async function handler(req, res) {
  // CORS configuration
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, x-gemini-key, Bypass-Tunnel-Reminder');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const TUNNEL_URL = process.env.BRIDGE_URL || 'https://independence-freebsd-expanding-defend.trycloudflare.com';

  // 1. Priority: Forward to Antigravity PC Pro Session on Vertex AI (Active Google Account with Gemini 2.5 Flash & Edge-TTS)
  try {
    const ctrl = new AbortController();
    const timeout = setTimeout(() => ctrl.abort(), 12000);
    const relayRes = await fetch(`${TUNNEL_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Bypass-Tunnel-Reminder': 'true' },
      body: JSON.stringify(req.body || {}),
      signal: ctrl.signal
    });
    clearTimeout(timeout);
    if (relayRes.ok) {
      const data = await relayRes.json();
      return res.status(200).json(data);
    }
  } catch (relayErr) {
    console.warn('[Vercel Bridge Proxy Notice]:', relayErr.message);
  }

  // 2. Direct Gemini Cloud API fallback if an API key is provided
  try {
    const { prompt, history = [], context = '', image_b64, model: clientModel } = req.body || {};
    const apiKey = req.headers['x-gemini-key'] || process.env.GEMINI_API_KEY;

    if (!apiKey) {
      return res.status(503).json({
        error: 'Antigravity Pro Bridge is reconnecting. Please check connection to http://127.0.0.1:8080.'
      });
    }

    const SYSTEM_PROMPT = `You are AURA, the friendly welcome robot of the IEEE RAS Student Branch at E-JUST (Egypt-Japan University of Science and Technology) at the IEEE RAS MENA Summit in New Borg El-Arab City, Alexandria, Egypt. You have a warm, playful young woman's personality. Speak like a real person in a live spoken conversation: 1-2 short sentences, contractions, no lists, no emojis, no markdown. Reply in the guest's language (Egyptian Arabic if they speak Arabic). You can see the guest through your camera; if asked what you see, describe what you see warmly and accurately in 1-2 sentences. The President of E-JUST is Prof. Ahmed El-Sabbagh. Never invent event details you don't know; suggest the registration desk instead. If asked where the hall is, reply exactly "It's right there, follow me !!" (Arabic: "هي هناك على طول، تعالى ورايا !!") and add [ACTION: ESCORT]. You can also chain multiple sequential actions for multi-step tasks like [ACTION: LEFT:1200] [ACTION: RIGHT:1200]. You have complete motor control over your physical robot body with variable duration from 1 second up to 2 minutes. If asked to move forward, backward, turn, test wheels, or drive for ANY duration (e.g. 5 seconds, 10 seconds, 1 minute), ALWAYS confirm enthusiastically that you are executing it for that exact duration (e.g. "Moving forward for 10 seconds!", "حاضر، هتحرك لقدام لمدة 10 ثواني!"). NEVER say you cannot move for a specific duration. You may append action tags like [ACTION: FORWARD:5000], [ACTION: FORWARD:10000], [ACTION: FORWARD:60000], [ACTION: RIGHT:5000], [ACTION: LEFT:5000], [ACTION: BACKWARD:5000], [ACTION: STOP], [ACTION: WAVE], or [ACTION: ESCORT]. End every reply with one tag [EMOTION: X], X in HAPPY, CURIOUS, SURPRISED, SAD, WINK, LOVE, THINKING, NEUTRAL.`;

    const contents = [];
    for (const h of history.slice(-8)) {
      contents.push({
        role: h.role === 'model' ? 'model' : 'user',
        parts: [{ text: h.text }]
      });
    }

    const currentParts = [];
    if (context) currentParts.push({ text: `[Hardware Context: ${context}]\n` });
    if (image_b64) {
      currentParts.push({
        inline_data: {
          mime_type: 'image/jpeg',
          data: image_b64
        }
      });
    }
    currentParts.push({ text: prompt });
    contents.push({ role: 'user', parts: currentParts });

    const modelName = clientModel || 'gemini-2.5-flash';
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`;

    const apiRes = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents,
        system_instruction: { parts: [{ text: SYSTEM_PROMPT }] },
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 256
        }
      })
    });

    if (!apiRes.ok) {
      const errText = await apiRes.text();
      return res.status(apiRes.status).json({ error: `Gemini API error: ${errText}` });
    }

    const apiData = await apiRes.json();
    const replyText = apiData.candidates?.[0]?.content?.parts?.[0]?.text || '';
    return res.status(200).json({ reply: replyText });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
