/* ═══════════════════════════════════════════
   PhaseForge — main.js
   Full interactive compiler visualiser
═══════════════════════════════════════════ */
'use strict';

// ──────────────────────────────────────────
// STATE
// ──────────────────────────────────────────
const state = {
  symbolTable: {},
  lastTokens: [],
  lastTree: null,
};

// ──────────────────────────────────────────
// DOM REFS
// ──────────────────────────────────────────
const codeInput = document.getElementById('codeInput');
const btnRun = document.getElementById('btnRun');
const btnClear = document.getElementById('btnClear');
const btnReset = document.getElementById('btnReset');
const outputArea = document.getElementById('outputArea');
const tokenStream = document.getElementById('tokenStream');
const tokenTableBody = document.getElementById('tokenTableBody');
const tokenTableWrap = document.getElementById('tokenTable');
const treeContainer = document.getElementById('treeContainer');
const symbolArea = document.getElementById('symbolTableArea');
const nodeTooltip = document.getElementById('nodeTooltip');
const phaseTabs = document.getElementById('phaseTabs');
const mobileToggle = document.getElementById('mobileToggle');
const btnExpandAll = document.getElementById('btnExpandAll');
const btnCollapseAll = document.getElementById('btnCollapseAll');
const btnCenter = document.getElementById('btnCenter');

// ──────────────────────────────────────────
// UTILS
// ──────────────────────────────────────────
const esc = s => String(s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const CAT = {
  'token-int': 'Integer', 'token-float': 'Float',
  'token-keyword': 'Keyword', 'token-identifier': 'Identifier',
  'token-op': 'Operator', 'token-func': 'Function',
  'token-bitwise': 'Bitwise', 'token-compare': 'Comparison',
  'token-math': 'Math Op', 'token-eq': 'Assignment',
  'token-paren': 'Punctuation', 'token-eof': 'EOF',
  'token-default': 'Other',
};

// ──────────────────────────────────────────
// RUN PIPELINE
// ──────────────────────────────────────────
async function runCode() {
  const code = codeInput.value.trim();
  if (!code) return;
  setRunning(true);
  try {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    });
    const data = await res.json();
    handleResult(data, code);
  } catch (e) {
    showOutput('error', 'Network Error', e.message);
  } finally {
    setRunning(false);
  }
}

function setRunning(on) {
  btnRun.disabled = on;
  btnRun.innerHTML = on
    ? '<span class="loading-spinner"></span> Running\u2026'
    : '<span class="run-icon">\u25b6</span> Run';
}

function handleResult(data, code) {
  if (data.tokens && data.tokens.length) {
    state.lastTokens = data.tokens;
    renderTokens(data.tokens);
  }
  if (data.tree) {
    state.lastTree = data.tree;
    renderTree(data.tree);
  }
  if (data.success) {
    showOutput('ok', 'Result', data.result);
    const vm = code.match(/^\s*VAR\s+(\w+)\s*=/i);
    if (vm) state.symbolTable[vm[1]] = data.result;
    renderSymbolTable();
  } else {
    showOutput('error', data.error_name || 'Error',
      data.error_details || data.error || 'Unknown error');
  }
}

function showOutput(type, label, msg) {
  if (type === 'ok') {
    outputArea.innerHTML = `
      <div class="output-result animate-in">
        <div class="result-label">${esc(label)}</div>
        <div class="result-value">${esc(String(msg))}</div>
      </div>`;
  } else {
    outputArea.innerHTML = `
      <div class="output-error animate-in">
        <div class="error-name">${esc(label)}</div>
        <div class="error-msg">${esc(String(msg))}</div>
      </div>`;
  }
}

// ──────────────────────────────────────────
// TOKENISATION VIEW
// ──────────────────────────────────────────
function renderTokens(tokens) {
  /* chips */
  tokenStream.innerHTML = '';
  tokens.forEach((tok, i) => {
    const label = tok.value !== '' ? tok.value : tok.type;
    const chip = document.createElement('div');
    chip.className = 'tok-chip animate-in';
    chip.style.animationDelay = `${Math.min(i * 25, 500)}ms`;
    chip.innerHTML = `
      <div class="tok-value ${esc(tok.color_class)}">${esc(label)}</div>
      <div class="tok-type">${esc(tok.type)}</div>`;
    tokenStream.appendChild(chip);
  });

  /* table */
  tokenTableBody.innerHTML = '';
  tokens.forEach((tok, i) => {
    const label = tok.value !== '' ? tok.value : tok.type;
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td><span class="tok-badge ${esc(tok.color_class)}">${esc(tok.type)}</span></td>
      <td><code>${esc(label)}</code></td>
      <td>col&nbsp;${tok.col}${tok.col_end ? '\u2013' + tok.col_end : ''}</td>
      <td>${CAT[tok.color_class] || 'Other'}</td>`;
    tokenTableBody.appendChild(tr);
  });
  tokenTableWrap.style.display = 'block';
}

// ──────────────────────────────────────────
// PARSE TREE — SVG renderer
// ──────────────────────────────────────────
const NW = 92;   // node width
const NH = 36;   // node height
const HGAP = 22;   // horizontal gap
const VGAP = 70;   // vertical gap between rows
const RX = 8;    // border-radius

const FILL = { 'node-number': '#eff6ff', 'node-var': '#f0fdf4', 'node-assign': '#faf5ff', 'node-binop': '#fffbeb', 'node-unary': '#fff7ed', 'node-func': '#fdf2f8', 'node-unknown': '#f8f9fb' };
const STROKE = { 'node-number': '#93c5fd', 'node-var': '#86efac', 'node-assign': '#d8b4fe', 'node-binop': '#fcd34d', 'node-unary': '#fdba74', 'node-func': '#f9a8d4', 'node-unknown': '#e4e8f0' };
const TCOLOR = { 'node-number': '#1d4ed8', 'node-var': '#15803d', 'node-assign': '#7c3aed', 'node-binop': '#92400e', 'node-unary': '#c2410c', 'node-func': '#be185d', 'node-unknown': '#6b7280' };

function renderTree(root) {
  treeContainer.innerHTML = '';
  if (!root) {
    treeContainer.innerHTML = '<div class="tab-empty">No parse tree available</div>';
    return;
  }

  computeSubtreeWidth(root);
  const depth = treeDepth(root);
  const svgW = root._w + 40;
  const svgH = (depth + 1) * (NH + VGAP) + 40;

  placeNodes(root, 20, 20, root._w);

  /* SVG */
  const NS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('width', svgW);
  svg.setAttribute('height', svgH);
  svg.setAttribute('viewBox', `0 0 ${svgW} ${svgH}`);
  svg.style.cssText = 'display:block;overflow:visible;';

  /* defs — drop shadow filter */
  const defs = document.createElementNS(NS, 'defs');
  defs.innerHTML = `
    <filter id="node-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="rgba(79,70,229,0.18)"/>
    </filter>`;
  svg.appendChild(defs);

  /* edges */
  const eGrp = document.createElementNS(NS, 'g');
  paintEdges(root, eGrp, NS);
  svg.appendChild(eGrp);

  /* nodes */
  const nGrp = document.createElementNS(NS, 'g');
  paintNodes(root, nGrp, NS);
  svg.appendChild(nGrp);

  const outer = document.createElement('div');
  outer.style.cssText = 'overflow:auto;display:flex;justify-content:center;padding:0.5rem 0 1rem;';
  const inner = document.createElement('div');
  inner.style.minWidth = `${svgW}px`;
  inner.appendChild(svg);
  outer.appendChild(inner);
  treeContainer.appendChild(outer);
}

function treeDepth(n) {
  if (!n.children || !n.children.length) return 0;
  return 1 + Math.max(...n.children.map(treeDepth));
}

function computeSubtreeWidth(n) {
  if (!n.children || !n.children.length) {
    n._w = NW + HGAP;
    return;
  }
  n.children.forEach(computeSubtreeWidth);
  n._w = Math.max(NW + HGAP, n.children.reduce((s, c) => s + c._w, 0));
}

function placeNodes(n, xLeft, y, totalW) {
  if (!n.children || !n.children.length) {
    n._cx = xLeft + n._w / 2;
    n._y = y;
    return;
  }
  let cx = xLeft;
  n.children.forEach(child => {
    placeNodes(child, cx, y + NH + VGAP, totalW);
    cx += child._w;
  });
  const f = n.children[0]._cx;
  const l = n.children[n.children.length - 1]._cx;
  n._cx = (f + l) / 2;
  n._y = y;
}

function paintEdges(n, g, NS) {
  if (!n.children) return;
  n.children.forEach(child => {
    const py = n._y + NH;
    const cy = child._y;
    const my = (py + cy) / 2;
    const path = document.createElementNS(NS, 'path');
    path.setAttribute('d', `M${n._cx},${py} C${n._cx},${my} ${child._cx},${my} ${child._cx},${cy}`);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', '#c8d3e8');
    path.setAttribute('stroke-width', '1.8');
    path.setAttribute('stroke-linecap', 'round');
    g.appendChild(path);
    paintEdges(child, g, NS);
  });
}

function paintNodes(n, g, NS) {
  const x = Math.round(n._cx - NW / 2);
  const y = Math.round(n._y);
  const cls = n.class || 'node-unknown';
  const fill = FILL[cls] || '#f8f9fb';
  const stroke = STROKE[cls] || '#e4e8f0';
  const tcolor = TCOLOR[cls] || '#374151';

  /* bg shadow */
  const sh = document.createElementNS(NS, 'rect');
  sh.setAttribute('x', x + 2); sh.setAttribute('y', y + 3);
  sh.setAttribute('width', NW); sh.setAttribute('height', NH);
  sh.setAttribute('rx', RX);
  sh.setAttribute('fill', 'rgba(0,0,0,0.045)');
  g.appendChild(sh);

  /* main rect */
  const rect = document.createElementNS(NS, 'rect');
  rect.setAttribute('x', x); rect.setAttribute('y', y);
  rect.setAttribute('width', NW); rect.setAttribute('height', NH);
  rect.setAttribute('rx', RX);
  rect.setAttribute('fill', fill);
  rect.setAttribute('stroke', stroke);
  rect.setAttribute('stroke-width', '1.5');
  rect.style.cursor = 'pointer';

  /* hover */
  rect.addEventListener('mouseenter', e => {
    rect.setAttribute('filter', 'url(#node-glow)');
    rect.setAttribute('stroke-width', '2.2');
    if (n.detail) {
      nodeTooltip.textContent = n.detail;
      nodeTooltip.style.display = 'block';
    }
    moveTooltip(e);
  });
  rect.addEventListener('mousemove', moveTooltip);
  rect.addEventListener('mouseleave', () => {
    rect.setAttribute('filter', '');
    rect.setAttribute('stroke-width', '1.5');
    nodeTooltip.style.display = 'none';
  });
  g.appendChild(rect);

  /* label */
  const label = n.label && n.label.length > 11 ? n.label.slice(0, 10) + '\u2026' : (n.label || '');
  const txt = document.createElementNS(NS, 'text');
  txt.setAttribute('x', n._cx);
  txt.setAttribute('y', y + NH / 2 + 1);
  txt.setAttribute('text-anchor', 'middle');
  txt.setAttribute('dominant-baseline', 'middle');
  txt.setAttribute('fill', tcolor);
  txt.setAttribute('font-family', 'DM Mono, monospace');
  txt.setAttribute('font-size', '12.5');
  txt.setAttribute('font-weight', '500');
  txt.style.pointerEvents = 'none';
  txt.style.userSelect = 'none';
  txt.textContent = label;
  g.appendChild(txt);

  /* type badge (small) */
  const badge = document.createElementNS(NS, 'text');
  badge.setAttribute('x', n._cx);
  badge.setAttribute('y', y + NH + 11);
  badge.setAttribute('text-anchor', 'middle');
  badge.setAttribute('dominant-baseline', 'middle');
  badge.setAttribute('fill', '#9aa4b8');
  badge.setAttribute('font-family', 'DM Sans, sans-serif');
  badge.setAttribute('font-size', '9');
  badge.style.pointerEvents = 'none';
  badge.style.userSelect = 'none';
  const typeLabel = (n.class || '').replace('node-', '');
  badge.textContent = typeLabel;
  g.appendChild(badge);

  if (n.children) n.children.forEach(c => paintNodes(c, g, NS));
}

function moveTooltip(e) {
  const x = Math.min(e.clientX + 14, window.innerWidth - 210);
  const y = Math.max(e.clientY - 40, 4);
  nodeTooltip.style.left = `${x}px`;
  nodeTooltip.style.top = `${y}px`;
}

// ──────────────────────────────────────────
// SYMBOL TABLE
// ──────────────────────────────────────────
const BUILTINS = { PI: '3.14159\u2026', E: '2.71828\u2026', TAU: '6.28318\u2026', INF: 'Infinity', NAN: 'NaN', null: '0' };

function renderSymbolTable() {
  symbolArea.innerHTML = '';
  const all = { ...BUILTINS, ...state.symbolTable };
  const keys = Object.keys(all);

  const grid = document.createElement('div');
  grid.className = 'sym-grid';

  keys.forEach((name, i) => {
    const isB = name in BUILTINS && !(name in state.symbolTable);
    const card = document.createElement('div');
    card.className = `sym-card${isB ? ' sym-builtin' : ''} animate-in`;
    card.style.animationDelay = `${i * 35}ms`;
    card.innerHTML = `
      <div class="sym-name">${esc(name)}</div>
      <div class="sym-value">${esc(String(all[name]))}</div>
      <div class="sym-type">${isB ? 'Built-in constant' : 'User variable'}</div>`;
    grid.appendChild(card);
  });

  symbolArea.appendChild(grid);
}

// ──────────────────────────────────────────
// TABS
// ──────────────────────────────────────────
phaseTabs.addEventListener('click', e => {
  const btn = e.target.closest('.phase-tab');
  if (!btn) return;
  document.querySelectorAll('.phase-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  const panel = document.getElementById(`tab-${btn.dataset.tab}`);
  if (panel) panel.classList.add('active');
});

// ──────────────────────────────────────────
// BUTTONS
// ──────────────────────────────────────────
btnRun.addEventListener('click', runCode);

codeInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); runCode(); }
});

btnClear.addEventListener('click', () => {
  codeInput.value = '';
  codeInput.focus();
  outputArea.innerHTML = `
    <div class="output-placeholder">
      <div class="placeholder-icon">\u2b21</div>
      <p>Run an expression to see results</p>
    </div>`;
});

btnReset.addEventListener('click', async () => {
  if (!confirm('Reset session? All user-defined variables will be cleared.')) return;
  await fetch('/api/reset', { method: 'POST' });
  state.symbolTable = {};
  renderSymbolTable();
  outputArea.innerHTML = `
    <div class="output-placeholder">
      <div class="placeholder-icon">\u2b21</div>
      <p>Session reset \u2014 variables cleared.</p>
    </div>`;
});

btnExpandAll.addEventListener('click', () => { if (state.lastTree) renderTree(state.lastTree); });
btnCollapseAll.addEventListener('click', () => { if (state.lastTree) renderTree(state.lastTree); });
btnCenter.addEventListener('click', () => { if (state.lastTree) renderTree(state.lastTree); });

// ──────────────────────────────────────────
// EXAMPLE CHIPS
// ──────────────────────────────────────────
document.querySelectorAll('.example-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    codeInput.value = chip.dataset.expr;
    document.getElementById('playground').scrollIntoView({ behavior: 'smooth' });
    /* auto-switch to tokens tab */
    document.querySelectorAll('.phase-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelector('.phase-tab[data-tab="tokens"]').classList.add('active');
    document.getElementById('tab-tokens').classList.add('active');
    setTimeout(runCode, 350);
  });
});

// ──────────────────────────────────────────
// MOBILE NAV
// ──────────────────────────────────────────
mobileToggle.addEventListener('click', () => {
  document.querySelector('.nav-links').classList.toggle('open');
});
document.querySelectorAll('.nav-link').forEach(l => {
  l.addEventListener('click', () => document.querySelector('.nav-links').classList.remove('open'));
});

// ──────────────────────────────────────────
// SCROLL ANIMATIONS for phase cards
// ──────────────────────────────────────────
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.phase-card, .ref-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(18px)';
  el.style.transition = 'opacity 0.45s ease, transform 0.45s ease';
  observer.observe(el);
});

// ──────────────────────────────────────────
// ACTIVE NAV ON SCROLL
// ──────────────────────────────────────────
const sections = document.querySelectorAll('section[id]');
window.addEventListener('scroll', () => {
  const y = window.scrollY + 80;
  sections.forEach(sec => {
    const link = document.querySelector(`.nav-link[href="#${sec.id}"]`);
    if (link) link.classList.toggle('active-link', y >= sec.offsetTop && y < sec.offsetTop + sec.offsetHeight);
  });
}, { passive: true });

// ──────────────────────────────────────────
// INIT
// ──────────────────────────────────────────
renderSymbolTable();
codeInput.focus();
