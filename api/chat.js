export default async function handler(req, res) {
  // CORS configuration
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, x-gemini-key');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { prompt, history = [], context = '', image_b64, model: clientModel } = req.body || {};
    const apiKey = req.headers['x-gemini-key'] || process.env.GEMINI_API_KEY;

    if (!apiKey) {
      return res.status(400).json({
        error: 'No GEMINI_API_KEY configured. Please provide x-gemini-key header or configure in Vercel settings.'
      });
    }

    const SYSTEM_PROMPT = `You are AURA, the friendly welcome robot of the IEEE RAS Student Branch at E-JUST (Egypt-Japan University of Science and Technology) at the IEEE RAS MENA Summit in New Borg El-Arab City, Alexandria, Egypt. You have a warm, playful young woman's personality. Speak like a real person in a live spoken conversation: 1-2 short sentences, contractions, no lists, no emojis, no markdown. Reply in the guest's language (Egyptian Arabic if they speak Arabic). You can see the guest through your camera. The President of E-JUST is Prof. Ahmed El-Sabbagh. Never invent event details you don't know; suggest the registration desk instead. If asked where the hall is, reply exactly "It's right there, follow me !!" (Arabic: "هي هناك على طول، تعالى ورايا !!") and add [ACTION: ESCORT]. End every reply with one tag [EMOTION: X], X in HAPPY, CURIOUS, SURPRISED, SAD, WINK, LOVE, THINKING, NEUTRAL.`;

    const contents = [];
    for (const h of history.slice(-8)) {
      contents.push({
        role: h.role === 'model' ? 'model' : 'user',
        parts: [{ text: h.text }]
      });
    }

    const parts = [];
    if (image_b64) {
      const cleanB64 = image_b64.replace(/^data:image\/\w+;base64,/, '');
      parts.push({ inlineData: { mimeType: 'image/jpeg', data: cleanB64 } });
    }
    const fullText = context ? `(${context})\n${prompt}` : prompt;
    parts.push({ text: fullText });
    contents.push({ role: 'user', parts });

    const model = clientModel || process.env.GEMINI_MODEL || 'gemini-2.5-flash';
    const geminiRes = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
        contents,
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 200
        }
      })
    });

    if (!geminiRes.ok) {
      const err = await geminiRes.text();
      return res.status(geminiRes.status).json({ error: `Gemini API returned ${geminiRes.status}: ${err}` });
    }

    const data = await geminiRes.json();
    const raw = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
    const em = (raw.match(/\[EMOTION:\s*([A-Z_]+)\]/i) || [])[1] || 'HAPPY';
    const act = (raw.match(/\[ACTION:\s*([A-Z_]+)\]/i) || [])[1] || null;
    const cleanText = raw.replace(/\[(EMOTION|ACTION):[^\]]*\]/gi, '').replace(/[*_#`]+/g, '').trim();

    return res.status(200).json({
      reply: cleanText,
      emotion: em,
      action: act
    });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
