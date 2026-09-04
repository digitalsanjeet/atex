// Background service worker: prompts ko queue karke images generate + serial-wise download karta hai.

const state = {
  running: false,
  stop: false,
  total: 0,
  done: 0,
};

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === 'START') {
    if (state.running) {
      sendResponse({ ok: false, error: 'Job already running' });
      return true;
    }
    runJob(msg.config).catch((e) => log('err', String(e && e.message || e)));
    sendResponse({ ok: true });
    return true;
  }
  if (msg.type === 'STOP') {
    state.stop = true;
    sendResponse({ ok: true });
    return true;
  }
  if (msg.type === 'STATUS') {
    sendResponse({ ok: true, state: { ...state } });
    return true;
  }
});

function emit(payload) {
  chrome.runtime.sendMessage({ type: 'PROGRESS', ...payload }).catch(() => {});
}

function log(level, text) {
  emit({ log: { level, text } });
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function pad(n, digits) {
  return String(n).padStart(digits, '0');
}

function safeSlug(text, max = 40) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, max);
}

function buildUrl(config, prompt, index) {
  const seed = Math.floor(Math.random() * 1e9);
  if (config.provider === 'custom') {
    return (config.template || '')
      .replaceAll('{prompt}', encodeURIComponent(prompt))
      .replaceAll('{width}', config.width)
      .replaceAll('{height}', config.height)
      .replaceAll('{seed}', seed)
      .replaceAll('{index}', index);
  }
  // pollinations
  const params = new URLSearchParams({
    width: config.width,
    height: config.height,
    seed: String(seed),
    nologo: 'true',
  });
  if (config.model) params.set('model', config.model);
  return `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?${params}`;
}

async function openaiImage(config, prompt) {
  const res = await fetch('https://api.openai.com/v1/images/generations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${config.apiKey}`,
    },
    body: JSON.stringify({
      model: config.model || 'gpt-image-1',
      prompt,
      n: 1,
      size: `${config.width}x${config.height}`,
    }),
  });
  if (!res.ok) throw new Error(`OpenAI ${res.status}: ${(await res.text()).slice(0, 160)}`);
  const data = await res.json();
  const item = data.data && data.data[0];
  if (!item) throw new Error('OpenAI: no image returned');
  if (item.b64_json) return `data:image/png;base64,${item.b64_json}`;
  return item.url;
}

async function toDataUrl(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Fetch ${res.status}`);
  const blob = await res.blob();
  if (!blob.size) throw new Error('Empty image');
  return await new Promise((resolve, reject) => {
    const fr = new FileReader();
    fr.onload = () => resolve(fr.result);
    fr.onerror = () => reject(new Error('Read failed'));
    fr.readAsDataURL(blob);
  });
}

function download(url, filename) {
  return new Promise((resolve, reject) => {
    chrome.downloads.download({ url, filename, conflictAction: 'uniquify', saveAs: false }, (id) => {
      if (chrome.runtime.lastError) reject(new Error(chrome.runtime.lastError.message));
      else resolve(id);
    });
  });
}

async function runJob(config) {
  state.running = true;
  state.stop = false;
  state.done = 0;
  state.total = config.prompts.length;
  emit({ running: true, done: 0, total: state.total, status: 'Started...' });

  for (let i = 0; i < config.prompts.length; i++) {
    if (state.stop) {
      log('err', 'Stopped by user.');
      break;
    }
    const prompt = config.prompts[i];
    const serial = config.start + i;
    const name = `${pad(serial, config.pad)}${config.useSlug ? '-' + safeSlug(prompt) : ''}`;
    const folder = config.folder ? config.folder.replace(/^\/+|\/+$/g, '') + '/' : '';
    const filename = `${folder}${config.prefix ? config.prefix + '-' : ''}${name}.${config.ext || 'png'}`;

    emit({ status: `(${i + 1}/${state.total}) ${prompt.slice(0, 50)}` });

    let attempt = 0;
    let ok = false;
    while (attempt < 3 && !ok && !state.stop) {
      attempt++;
      try {
        const src =
          config.provider === 'openai'
            ? await openaiImage(config, prompt)
            : buildUrl(config, prompt, serial);
        const dataUrl = src.startsWith('data:') ? src : await toDataUrl(src);
        await download(dataUrl, filename);
        log('ok', `${filename}`);
        ok = true;
      } catch (e) {
        if (attempt >= 3) log('err', `#${serial} failed: ${e.message}`);
        else await sleep(1000 * attempt);
      }
    }

    state.done = i + 1;
    emit({ done: state.done, total: state.total });
    if (config.delay) await sleep(config.delay);
  }

  state.running = false;
  emit({ running: false, status: state.stop ? 'Stopped.' : 'All done ✅' });
}
