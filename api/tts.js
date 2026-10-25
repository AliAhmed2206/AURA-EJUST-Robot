export default async function handler(req, res) {
  // CORS configuration
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Bypass-Tunnel-Reminder');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const TUNNEL_URL = process.env.BRIDGE_URL || 'https://put-properties-voltage-attacks.trycloudflare.com';
  const query = req.url.includes('?') ? req.url.slice(req.url.indexOf('?')) : '';

  try {
    const ctrl = new AbortController();
    const to = setTimeout(() => ctrl.abort(), 8000);
    const ttsRes = await fetch(`${TUNNEL_URL}/api/tts${query}`, {
      headers: { 'Bypass-Tunnel-Reminder': 'true' },
      signal: ctrl.signal
    });
    clearTimeout(to);
    if (ttsRes.ok) {
      const audioBuffer = await ttsRes.arrayBuffer();
      res.setHeader('Content-Type', 'audio/mpeg');
      return res.status(200).send(Buffer.from(audioBuffer));
    }
  } catch (e) {
    console.warn('[Vercel TTS Proxy Notice]', e.message);
  }

  return res.status(502).json({ error: 'TTS unavailable' });
}
