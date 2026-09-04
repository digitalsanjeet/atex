// Content script: Google Flow (labs.google/fx/tools/flow) par prompt type karke
// Generate click karta hai aur nayi images ke URLs wapas bhejta hai.

(() => {
  if (window.__bulkFlowInjected) return;
  window.__bulkFlowInjected = true;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const log = (text, level = 'info') =>
    chrome.runtime.sendMessage({ type: 'PROGRESS', log: { level, text: `[Flow] ${text}` } }).catch(() => {});

  const visible = (el) => {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && s.opacity !== '0';
  };

  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim().toLowerCase();

  /* ---------------- prompt input ---------------- */

  function findPromptInput(customSel) {
    if (customSel) {
      const el = document.querySelector(customSel);
      if (el && visible(el)) return el;
    }
    const candidates = [
      ...document.querySelectorAll('textarea, [contenteditable="true"], [role="textbox"]'),
    ].filter(visible);
    if (!candidates.length) return null;

    const hintRe = /prompt|describe|idea|generate|create|type|imagine|scene/i;
    const scored = candidates.map((el) => {
      const meta = [
        el.getAttribute('placeholder'),
        el.getAttribute('aria-label'),
        el.getAttribute('data-placeholder'),
        el.getAttribute('name'),
        el.id,
      ].join(' ');
      const r = el.getBoundingClientRect();
      let score = 0;
      if (hintRe.test(meta)) score += 100;
      score += Math.min(r.width, 900) / 10;          // wider = more likely main prompt bar
      score += r.top > window.innerHeight * 0.4 ? 30 : 0; // Flow ka prompt bar niche hota hai
      return { el, score };
    });
    scored.sort((a, b) => b.score - a.score);
    return scored[0].el;
  }

  // React/Angular controlled inputs ke liye native setter + real events.
  async function setPromptText(el, text) {
    el.focus();
    el.click();
    await sleep(60);

    if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
      const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
      setter.call(el, '');
      el.dispatchEvent(new Event('input', { bubbles: true }));
      await sleep(40);
      setter.call(el, text);
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
      // contenteditable
      const sel = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(el);
      sel.removeAllRanges();
      sel.addRange(range);
      document.execCommand('delete');
      const inserted = document.execCommand('insertText', false, text);
      if (!inserted) {
        el.textContent = text;
        el.dispatchEvent(new InputEvent('input', { bubbles: true, data: text, inputType: 'insertText' }));
      }
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }
    await sleep(150);
    const now = el.value !== undefined ? el.value : el.textContent;
    return norm(now).includes(norm(text).slice(0, 25));
  }

  /* ---------------- generate button ---------------- */

  function findGenerateButton(customSel) {
    if (customSel) {
      const el = document.querySelector(customSel);
      if (el && visible(el)) return el;
    }
    const btns = [...document.querySelectorAll('button, [role="button"]')].filter(visible);
    const labelOf = (b) =>
      norm([b.innerText, b.getAttribute('aria-label'), b.title, b.getAttribute('data-testid')].join(' '));

    // exact-ish text match pehle
    const exact = btns.find((b) => /^(generate|create|run)\b/.test(labelOf(b)) && !b.disabled);
    if (exact) return exact;

    const loose = btns.find((b) => /generate|create image|submit/.test(labelOf(b)) && !b.disabled);
    if (loose) return loose;

    // arrow / send icon button prompt bar ke paas
    const icons = btns.filter((b) => /send|arrow|submit/.test(labelOf(b)) && !b.disabled);
    if (icons.length) return icons[icons.length - 1];

    return null;
  }

  async function clickGenerate(sel) {
    // button enable hone ka thoda wait
    let btn = null;
    for (let i = 0; i < 20; i++) {
      btn = findGenerateButton(sel);
      if (btn && !btn.disabled && btn.getAttribute('aria-disabled') !== 'true') break;
      await sleep(250);
    }
    if (!btn) {
      // fallback: Enter key
      const input = findPromptInput();
      if (input) {
        input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
        input.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
        log('Generate button nahi mila — Enter key try ki.');
        return true;
      }
      return false;
    }
    btn.scrollIntoView({ block: 'center' });
    await sleep(80);
    btn.click();
    return true;
  }

  /* ---------------- result images ---------------- */

  const isCandidateImg = (src) =>
    !!src &&
    !src.startsWith('data:image/svg') &&
    !/\.svg(\?|$)/i.test(src) &&
    (src.startsWith('blob:') ||
      src.startsWith('data:image') ||
      /googleusercontent|lh3\.google|storage\.googleapis|labs\.google/.test(src));

  function snapshotImages() {
    const set = new Set();
    document.querySelectorAll('img').forEach((img) => {
      const src = img.currentSrc || img.src;
      if (isCandidateImg(src) && img.naturalWidth >= 200) set.add(src);
    });
    return set;
  }

  async function waitForNewImages(before, expected, timeoutMs) {
    const deadline = Date.now() + timeoutMs;
    let stableSince = 0;
    let last = [];
    while (Date.now() < deadline) {
      const now = [...snapshotImages()].filter((s) => !before.has(s));
      if (now.length >= expected) return now.slice(0, expected);
      if (now.length && now.length === last.length) {
        if (!stableSince) stableSince = Date.now();
        // 6s tak count nahi badha to jitna mila usi se kaam chala lo
        if (Date.now() - stableSince > 6000) return now;
      } else {
        stableSince = 0;
      }
      last = now;
      await sleep(700);
    }
    return last;
  }

  // blob:/cross-origin images ko page context me hi dataURL bana lo
  async function toDataUrl(src) {
    if (src.startsWith('data:')) return src;
    const res = await fetch(src, { credentials: 'include' });
    if (!res.ok) throw new Error(`fetch ${res.status}`);
    const blob = await res.blob();
    if (!blob.size) throw new Error('empty blob');
    return await new Promise((resolve, reject) => {
      const fr = new FileReader();
      fr.onload = () => resolve(fr.result);
      fr.onerror = () => reject(new Error('read failed'));
      fr.readAsDataURL(blob);
    });
  }

  /* ---------------- message handling ---------------- */

  chrome.runtime.onMessage.addListener((msg, _s, sendResponse) => {
    if (msg.type === 'FLOW_PING') {
      const input = findPromptInput(msg.promptSelector);
      sendResponse({ ok: true, ready: !!input, url: location.href });
      return true;
    }

    if (msg.type === 'FLOW_RUN') {
      (async () => {
        try {
          const input = findPromptInput(msg.promptSelector);
          if (!input) throw new Error('Prompt box nahi mila. Flow project page khula hai?');

          const before = snapshotImages();

          const typed = await setPromptText(input, msg.prompt);
          if (!typed) log('Prompt set to hua par verify nahi hua.', 'err');
          await sleep(msg.typeDelay || 400);

          const clicked = await clickGenerate(msg.generateSelector);
          if (!clicked) throw new Error('Generate button nahi mila.');

          const srcs = await waitForNewImages(before, msg.perPrompt || 1, msg.timeout || 180000);
          if (!srcs.length) throw new Error('Timeout — koi nayi image detect nahi hui.');

          const dataUrls = [];
          for (const s of srcs) {
            try {
              dataUrls.push(await toDataUrl(s));
            } catch (e) {
              log(`image read fail: ${e.message}`, 'err');
            }
          }
          if (!dataUrls.length) throw new Error('Images read nahi ho payi.');
          sendResponse({ ok: true, images: dataUrls });
        } catch (e) {
          sendResponse({ ok: false, error: String((e && e.message) || e) });
        }
      })();
      return true; // async
    }
  });

  log('automation ready ✅');
})();
