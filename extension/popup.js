const $ = (id) => document.getElementById(id);
const fields = ['prompts', 'prefix', 'start', 'pad', 'folder', 'delay', 'provider', 'width', 'height', 'ext', 'apiKey', 'model', 'template'];

function readConfig() {
  const prompts = $('prompts').value
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean);
  return {
    prompts,
    prefix: $('prefix').value.trim(),
    start: parseInt($('start').value, 10) || 0,
    pad: parseInt($('pad').value, 10) || 3,
    folder: $('folder').value.trim(),
    delay: parseInt($('delay').value, 10) || 0,
    provider: $('provider').value,
    width: parseInt($('width').value, 10) || 1024,
    height: parseInt($('height').value, 10) || 1024,
    ext: ($('ext').value.trim() || 'png').replace(/^\./, ''),
    apiKey: $('apiKey').value.trim(),
    model: $('model').value.trim(),
    template: $('template').value.trim(),
    useSlug: false,
  };
}

function save() {
  const data = {};
  fields.forEach((f) => (data[f] = $(f).value));
  chrome.storage.local.set({ settings: data });
}

function restore() {
  chrome.storage.local.get('settings', ({ settings }) => {
    if (!settings) return;
    fields.forEach((f) => {
      if (settings[f] !== undefined) $(f).value = settings[f];
    });
  });
}

function addLog(level, text) {
  const li = document.createElement('li');
  li.className = level;
  li.textContent = text;
  $('log').prepend(li);
}

function setRunning(running) {
  $('start-btn').disabled = running;
  $('stop-btn').disabled = !running;
}

$('start-btn').addEventListener('click', () => {
  const config = readConfig();
  if (!config.prompts.length) {
    $('status').textContent = 'Kam se kam ek prompt daalo.';
    return;
  }
  if (config.provider === 'openai' && !config.apiKey) {
    $('status').textContent = 'OpenAI ke liye API key chahiye.';
    return;
  }
  if (config.provider === 'custom' && !config.template.includes('{prompt}')) {
    $('status').textContent = 'Custom template me {prompt} hona chahiye.';
    return;
  }
  save();
  $('log').innerHTML = '';
  setRunning(true);
  $('status').textContent = 'Starting...';
  chrome.runtime.sendMessage({ type: 'START', config }, (res) => {
    if (!res || !res.ok) {
      setRunning(false);
      $('status').textContent = (res && res.error) || 'Start nahi hua.';
    }
  });
});

$('stop-btn').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'STOP' });
  $('status').textContent = 'Stopping...';
});

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type !== 'PROGRESS') return;
  if (msg.log) addLog(msg.log.level, msg.log.text);
  if (msg.status) $('status').textContent = msg.status;
  if (typeof msg.total === 'number' && msg.total > 0) {
    $('bar').style.width = `${Math.round((msg.done / msg.total) * 100)}%`;
  }
  if (typeof msg.running === 'boolean') setRunning(msg.running);
});

fields.forEach((f) => $(f).addEventListener('change', save));

restore();
chrome.runtime.sendMessage({ type: 'STATUS' }, (res) => {
  if (res && res.ok) {
    setRunning(res.state.running);
    if (res.state.total) {
      $('bar').style.width = `${Math.round((res.state.done / res.state.total) * 100)}%`;
    }
  }
});
