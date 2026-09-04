const $ = (id) => document.getElementById(id);
const fields = ['master', 'masterMode', 'prompts', 'prefix', 'start', 'pad', 'folder', 'delay', 'provider', 'width', 'height', 'ext', 'apiKey', 'model', 'template', 'flowPerPrompt', 'flowTimeout', 'promptSelector', 'generateSelector'];

// Master prompt ko ek single prompt ke saath merge karta hai.
function applyMaster(master, mode, enabled, prompt) {
  const m = (master || '').trim();
  if (!enabled || !m) return prompt;
  if (m.includes('{prompt}')) return m.replaceAll('{prompt}', prompt).trim();
  const join = (a, b) => [a, b].filter(Boolean).join(', ').replace(/\s*,\s*,\s*/g, ', ').trim();
  return mode === 'prefix' ? join(m, prompt) : join(prompt, m);
}

function readConfig() {
  const master = $('master').value;
  const mode = $('masterMode').value;
  const on = $('masterOn').checked;
  const prompts = $('prompts').value
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean)
    .map((p) => applyMaster(master, mode, on, p));
  return {
    prompts,
    master: master.trim(),
    masterMode: mode,
    masterOn: on,
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
    flowPerPrompt: parseInt($('flowPerPrompt').value, 10) || 1,
    flowTimeout: parseInt($('flowTimeout').value, 10) || 180,
    promptSelector: $('promptSelector').value.trim(),
    generateSelector: $('generateSelector').value.trim(),
    useSlug: false,
  };
}

function save() {
  const data = {};
  fields.forEach((f) => (data[f] = $(f).value));
  data.masterOn = $('masterOn').checked;
  chrome.storage.local.set({ settings: data });
}

function restore() {
  chrome.storage.local.get('settings', ({ settings }) => {
    if (!settings) return;
    fields.forEach((f) => {
      if (settings[f] !== undefined) $(f).value = settings[f];
    });
    if (typeof settings.masterOn === 'boolean') $('masterOn').checked = settings.masterOn;
    updatePreview();
    syncProvider();
  });
}

// Pehle prompt ka final (master-merged) roop dikhata hai.
function updatePreview() {
  const first = $('prompts').value.split('\n').map((s) => s.trim()).find(Boolean);
  const box = $('preview');
  if (!first) {
    box.textContent = '';
    return;
  }
  const merged = applyMaster($('master').value, $('masterMode').value, $('masterOn').checked, first);
  const count = $('prompts').value.split('\n').filter((s) => s.trim()).length;
  box.innerHTML = '';
  const b = document.createElement('b');
  b.textContent = `Preview (1/${count}): `;
  box.append(b, document.createTextNode(merged));
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
  if (config.provider === 'flow' && config.delay < 1500) {
    config.delay = 1500; // Flow ko settle hone ka time
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
$('masterOn').addEventListener('change', () => { save(); updatePreview(); });
['master', 'prompts', 'masterMode'].forEach((f) =>
  $(f).addEventListener('input', updatePreview)
);
$('masterMode').addEventListener('change', updatePreview);

// Provider ke hisab se Flow settings dikhao/chhupao
function syncProvider() {
  const isFlow = $('provider').value === 'flow';
  $('flow-box').classList.toggle('hidden', !isFlow);
  if (isFlow) $('details-open').open = true;
}
$('provider').addEventListener('change', syncProvider);

restore();
syncProvider();
chrome.runtime.sendMessage({ type: 'STATUS' }, (res) => {
  if (res && res.ok) {
    setRunning(res.state.running);
    if (res.state.total) {
      $('bar').style.width = `${Math.round((res.state.done / res.state.total) * 100)}%`;
    }
  }
});
