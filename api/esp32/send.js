export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Bypass-Tunnel-Reminder');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const TUNNEL_URL = process.env.BRIDGE_URL || 'https://independence-freebsd-expanding-defend.trycloudflare.com';
  try {
    const r = await fetch(`${TUNNEL_URL}/api/esp32/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Bypass-Tunnel-Reminder': 'true' },
      body: JSON.stringify(req.body || {})
    });
    if (r.ok) {
      const data = await r.json();
      return res.status(200).json(data);
    }
  } catch (e) {}
  return res.status(503).json({ error: 'Bridge unreachable' });
}
