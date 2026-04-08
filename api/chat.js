export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: { message: 'Method not allowed' } });
  }

  const { messages = [], max_tokens = 512 } = req.body;

  // Split system message out (Anthropic requires it separately)
  let system = '';
  const anthropicMessages = messages.filter(m => {
    if (m.role === 'system') { system = m.content; return false; }
    return true;
  });

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens,
        system,
        messages: anthropicMessages,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json({ error: { message: data.error?.message || 'Upstream error' } });
    }

    const text = data.content[0].text;
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(200).json({ choices: [{ message: { role: 'assistant', content: text } }] });
  } catch (err) {
    return res.status(500).json({ error: { message: err.message } });
  }
}
