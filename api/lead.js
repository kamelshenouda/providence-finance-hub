export default function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const lead = req.body;
  const tag = lead.qualified ? 'QUALIFIED' : 'FOLLOW UP';
  console.log(`\n${'='.repeat(48)}`);
  console.log(`[${tag}] New lead from Providence AI`);
  console.log(`Name   : ${lead.name || '—'}`);
  console.log(`Email  : ${lead.email || '—'}`);
  console.log(`Phone  : ${lead.phone || '—'}`);
  console.log(`Time   : ${lead.ts || '—'}`);
  console.log(`${'='.repeat(48)}\n`);

  res.setHeader('Access-Control-Allow-Origin', '*');
  return res.status(200).json({ ok: true });
}
