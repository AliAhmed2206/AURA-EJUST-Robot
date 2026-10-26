export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Bypass-Tunnel-Reminder');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const TUNNEL_URL = process.env.BRIDGE_URL || 'https://independence-freebsd-expanding-defend.trycloudflare.com';
  try {
    const ctrl = new AbortController();
    const timeout = setTimeout(() => ctrl.abort(), 4000);
    const r = await fetch(`${TUNNEL_URL}/api/esp32/status`, {
      headers: { 'Bypass-Tunnel-Reminder': 'true' },
      signal: ctrl.signal
    });
    clearTimeout(timeout);
    if (r.ok) {
      const data = await r.json();
      return res.status(200).json(data);
    }
  } catch (e) {}

  return res.status(200).json({
    online: false,
    status: 'OFFLINE',
    reason: 'ESP32 has not posted telemetry to bridge yet.',
    state: { status: 'DISCONNECTED', dist: 999, markers: 0 }
  });
}
