// DOM behavior checks, not a browser layout or accessibility audit.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { JSDOM } = require('jsdom');

const source = () => fs.readFileSync(path.join(__dirname, 'prototype.html'), 'utf8');

function open(t) {
  const dom = new JSDOM(source(), { runScripts: 'outside-only', pretendToBeVisual: true });
  t.after(() => dom.window.close());
  const { window } = dom;
  const attempts = [];
  const blocked = name => () => { attempts.push(name); throw Error(`Unexpected ${name}`); };
  window.fetch = blocked('fetch');
  window.XMLHttpRequest = blocked('XMLHttpRequest');
  window.WebSocket = blocked('WebSocket');
  window.navigator.sendBeacon = blocked('sendBeacon');
  window.document.querySelectorAll('script').forEach(s => window.eval(s.textContent));
  const $ = id => window.document.getElementById(id);
  const search = value => {
    $('search').value = value;
    $('search').dispatchEvent(new window.Event('input', { bubbles: true }));
  };
  return { window, document: window.document, $, search, attempts };
}

test('default selection and simulated check expose the expected demo and paths', t => {
  const { $, attempts } = open(t);
  assert.equal($('demo-id').textContent, 'code-to-screen');
  assert.equal($('run-check').disabled, false);
  $('run-check').click();
  assert.equal($('result').hidden, false);
  assert.match($('result').textContent, /Simuloitu tarkistus valmis/);
  assert.equal($('props-path').textContent, 'remotion-composer/public/demo-props/code-to-screen.json');
  assert.equal($('output-path').textContent, 'projects/demos/renders/code-to-screen.mp4');
  assert.deepEqual(attempts, []);
});

test('choosing a different demo updates details and clears the previous result', t => {
  const { document, $ } = open(t);
  $('run-check').click();
  document.querySelector('[data-demo="focusflow-pitch"]').click();
  assert.equal($('demo-id').textContent, 'focusflow-pitch');
  assert.equal($('demo-title').textContent, 'FocusFlow Pitch');
  assert.equal($('result').hidden, true);
  assert.equal(document.querySelectorAll('[data-demo][aria-pressed="true"]').length, 1);
  $('run-check').click();
  assert.match($('output-path').textContent, /focusflow-pitch\.mp4$/);
  assert.match($('announcement').textContent, /FocusFlow Pitch/);
});

test('searching the description selects the matching demo', t => {
  const { document, $, search } = open(t);
  search('  TILASTO  ');
  assert.equal($('demo-id').textContent, 'world-in-numbers');
  assert.equal($('count').textContent, '1 demo');
  assert.equal([...document.querySelectorAll('#demo-list li')].filter(li => !li.hidden).length, 1);
});

test('no matches shows an empty state and reset restores the list and search focus', t => {
  const { document, $, search, attempts } = open(t);
  $('run-check').click();
  search('<img src=x onerror=alert(1)>');
  assert.equal($('empty-state').hidden, false);
  assert.equal($('demo-content').hidden, true);
  assert.equal($('result').hidden, true);
  assert.equal($('run-check').disabled, true);
  assert.equal(document.querySelectorAll('img').length, 0);
  $('clear-search').click();
  assert.equal($('empty-state').hidden, true);
  assert.equal($('demo-content').hidden, false);
  assert.equal($('count').textContent, '3 demoa');
  assert.equal(document.activeElement, $('search'));
  assert.deepEqual(attempts, []);
});

test('a search that keeps the current selection preserves a valid result', t => {
  const { $, search } = open(t);
  $('run-check').click();
  search('code');
  assert.equal($('demo-id').textContent, 'code-to-screen');
  assert.equal($('result').hidden, false);
});

test('all demos simulate without attempting network access', t => {
  const { document, $, attempts } = open(t);
  for (const button of document.querySelectorAll('[data-demo]')) {
    button.click();
    $('run-check').click();
    assert.match($('command').textContent, new RegExp(button.dataset.demo + '$'));
  }
  assert.deepEqual(attempts, []);
});

test('controls have labels and the live announcement identifies simulated work', t => {
  const { document, $ } = open(t);
  assert.ok(document.querySelector('label[for="search"]').textContent.trim());
  for (const button of document.querySelectorAll('button')) assert.ok(button.textContent.trim());
  assert.equal($('announcement').getAttribute('role'), 'status');
  assert.equal($('announcement').getAttribute('aria-live'), 'polite');
  $('run-check').click();
  assert.match($('announcement').textContent, /Simuloitu/);
});

test('CSP hashes match the local code; no external resources or inline handlers', t => {
  const { document } = open(t);
  const csp = document.querySelector('meta[http-equiv="Content-Security-Policy"]').content;
  assert.match(csp, /default-src 'none'/);
  assert.match(csp, /connect-src 'none'/);
  assert.match(csp, /form-action 'none'/);
  assert.ok(!csp.includes('unsafe-inline'));
  for (const tag of ['style', 'script']) {
    for (const element of document.querySelectorAll(tag)) {
      const hash = crypto.createHash('sha256').update(element.textContent).digest('base64');
      assert.ok(csp.includes(`'sha256-${hash}'`), `${tag} hash mismatch`);
    }
  }
  for (const element of document.querySelectorAll('*')) {
    for (const attribute of element.attributes) {
      assert.ok(!/^on/i.test(attribute.name), 'inline event handler');
      if (['src', 'srcset', 'action'].includes(attribute.name)) assert.fail('external resource/action');
      if (attribute.name === 'href') assert.ok(attribute.value.startsWith('#'));
    }
  }
});

test('declared text palette retains at least 4.5:1 contrast on its backgrounds', () => {
  const colors = Object.fromEntries([...source().matchAll(/--([a-z-]+):\s*(#[0-9a-f]{6})/g)].map(m => [m[1], m[2]]));
  function luminance(hex) {
    const [r, g, b] = hex.slice(1).match(/../g).map(c => {
      const value = parseInt(c, 16) / 255;
      return value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4;
    });
    return .2126 * r + .7152 * g + .0722 * b;
  }
  function ratio(foreground, background) {
    const a = luminance(foreground), b = luminance(background);
    return (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
  }
  assert.equal(ratio('#000000', '#ffffff'), 21);
  for (const [fg, bg] of [['ink', 'paper'], ['muted', 'paper'], ['ink', 'white'], ['muted', 'white'], ['muted', 'soft'], ['green', 'soft'], ['white', 'green']]) {
    assert.ok(ratio(colors[fg], colors[bg]) >= 4.5, `${fg}/${bg}`);
  }
});
