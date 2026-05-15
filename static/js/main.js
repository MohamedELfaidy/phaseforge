/* ═══════════════════════════════════════════════════════
   PhaseForge — main.js
   Compiler visualiser with SVG tree, collapse/expand,
   AI suggestion, reference Run buttons, friendly errors
═══════════════════════════════════════════════════════ */
'use strict';

// ──────────────────────────────────────────────────────
// STATE
// ──────────────────────────────────────────────────────
const state = {
  symbolTable:     {},
  lastTokens:      [],
  lastTree:        null,   // raw tree JSON from server
  collapsedIds:    new Set(), // IDs of nodes the user collapsed
  treeIsPartial:   false,
  lastCode:        '',
  lastError:       '',
  pendingSuggestion: null,
};

// ──────────────────────────────────────────────────────
// DOM
// ──────────────────────────────────────────────────────
const codeInput      = document.getElementById('codeInput');
const btnRun         = document.getElementById('btnRun');
const btnClear       = document.getElementById('btnClear');
const btnReset       = document.getElementById('btnReset');
const outputArea     = document.getElementById('outputArea');
const tokenStream    = document.getElementById('tokenStream');
const tokenTableBody = document.getElementById('tokenTableBody');
const tokenTableWrap = document.getElementById('tokenTable');
const treeContainer  = document.getElementById('treeContainer');
const symbolArea     = document.getElementById('symbolTableArea');
const nodeTooltip    = document.getElementById('nodeTooltip');
const phaseTabs      = document.getElementById('phaseTabs');
const mobileToggle   = document.getElementById('mobileToggle');
const btnExpandAll   = document.getElementById('btnExpandAll');
const btnCollapseAll = document.getElementById('btnCollapseAll');
const btnCenter      = document.getElementById('btnCenter');
const partialBanner  = document.getElementById('partialBanner');
const aiSuggBanner   = document.getElementById('aiSuggestionBanner');
const aiSuggText     = document.getElementById('aiSuggestionText');
const btnApplySugg   = document.getElementById('btnApplySuggestion');
const btnDismissSugg = document.getElementById('btnDismissSuggestion');

// ──────────────────────────────────────────────────────
// HELPERS
// ──────────────────────────────────────────────────────
const esc = s => String(s)
  .replace(/&/g,'&amp;').replace(/</g,'&lt;')
  .replace(/>/g,'&gt;').replace(/"/g,'&quot;');

const CAT = {
  'token-int':'Integer','token-float':'Float','token-keyword':'Keyword',
  'token-identifier':'Identifier','token-op':'Operator','token-func':'Function',
  'token-bitwise':'Bitwise','token-compare':'Comparison','token-math':'Math Op',
  'token-eq':'Assignment','token-paren':'Punctuation','token-eof':'EOF','token-default':'Other',
};

// Assign a stable unique ID to every node in the tree so we can track collapse state
let _nodeIdCounter = 0;
function assignNodeIds(node) {
  if (!node) return;
  node._id = ++_nodeIdCounter;
  if (node.children) node.children.forEach(assignNodeIds);
}

// ──────────────────────────────────────────────────────
// RUN
// ──────────────────────────────────────────────────────
async function runCode() {
  const code = codeInput.value.trim();
  if (!code) return;
  state.lastCode = code;
  setRunning(true);
  hideAISuggestion();

  try {
    const res  = await fetch('/api/run', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({code}),
    });
    const data = await res.json();
    handleResult(data, code);
  } catch(e) {
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
  // Tokens
  if (data.tokens && data.tokens.length) {
    state.lastTokens = data.tokens;
    renderTokens(data.tokens);
  }

  // Parse tree
  if (data.tree) {
    _nodeIdCounter = 0;
    state.collapsedIds.clear();
    assignNodeIds(data.tree);
    state.lastTree      = data.tree;
    state.treeIsPartial = !!data.tree_partial;
    partialBanner.style.display = state.treeIsPartial ? 'block' : 'none';
    renderTree();
  }

  // Output + AI suggestion on error
  if (data.success) {
    showOutput('ok', 'Result', data.result);
    const vm = code.match(/^\s*VAR\s+(\w+)\s*=/i);
    if (vm) state.symbolTable[vm[1]] = data.result;
    renderSymbolTable();
    hideAISuggestion();
  } else {
    state.lastError = data.error_details || data.error || '';
    showOutput('error', data.error_name || 'Error', state.lastError);
    // Kick off AI suggestion asynchronously
    fetchAISuggestion(code, state.lastError);
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

// ──────────────────────────────────────────────────────
// AI SUGGESTION
// ──────────────────────────────────────────────────────
async function fetchAISuggestion(code, error) {
  // Show a subtle loading state inside the banner area
  aiSuggBanner.style.display = 'flex';
  aiSuggText.textContent = 'Asking AI for a fix\u2026';
  btnApplySugg.style.display = 'none';
  btnDismissSugg.style.display = 'none';
  state.pendingSuggestion = null;

  try {
    const res  = await fetch('/api/suggest', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({code, error}),
    });
    const data = await res.json();
    if (data.suggestion) {
      state.pendingSuggestion = data.suggestion;
      aiSuggText.innerHTML =
        `<strong>${esc(data.suggestion)}</strong>`
        + (data.explanation ? ` <em style="font-family:var(--font-sans);font-size:0.8rem;color:var(--gray-500)">— ${esc(data.explanation)}</em>` : '');
      btnApplySugg.style.display = 'inline-block';
      btnDismissSugg.style.display = 'inline-block';
    } else {
      hideAISuggestion();
    }
  } catch(e) {
    hideAISuggestion();
  }
}

function hideAISuggestion() {
  aiSuggBanner.style.display = 'none';
  state.pendingSuggestion = null;
}

btnApplySugg.addEventListener('click', () => {
  if (state.pendingSuggestion) {
    codeInput.value = state.pendingSuggestion;
    hideAISuggestion();
    codeInput.focus();
  }
});
btnDismissSugg.addEventListener('click', hideAISuggestion);

// ──────────────────────────────────────────────────────
// TOKENS
// ──────────────────────────────────────────────────────
function renderTokens(tokens) {
  tokenStream.innerHTML = '';
  tokens.forEach((tok, i) => {
    const label = tok.value !== '' ? tok.value : tok.type;
    const chip  = document.createElement('div');
    chip.className = 'tok-chip animate-in';
    chip.style.animationDelay = `${Math.min(i * 25, 500)}ms`;
    chip.innerHTML = `
      <div class="tok-value ${esc(tok.color_class)}">${esc(label)}</div>
      <div class="tok-type">${esc(tok.type)}</div>`;
    tokenStream.appendChild(chip);
  });

  tokenTableBody.innerHTML = '';
  tokens.forEach((tok, i) => {
    const label = tok.value !== '' ? tok.value : tok.type;
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${i+1}</td>
      <td><span class="tok-badge ${esc(tok.color_class)}">${esc(tok.type)}</span></td>
      <td><code>${esc(label)}</code></td>
      <td>col&nbsp;${tok.col}${tok.col_end ? '\u2013'+tok.col_end : ''}</td>
      <td>${CAT[tok.color_class] || 'Other'}</td>`;
    tokenTableBody.appendChild(tr);
  });
  tokenTableWrap.style.display = 'block';
}

// ──────────────────────────────────────────────────────
// PARSE TREE — SVG renderer with collapse support
// ──────────────────────────────────────────────────────
const NW   = 92;
const NH   = 36;
const HGAP = 22;
const VGAP = 70;
const RX   = 8;

const FILL   = {'node-number':'#eff6ff','node-var':'#f0fdf4','node-assign':'#faf5ff','node-binop':'#fffbeb','node-unary':'#fff7ed','node-func':'#fdf2f8','node-unknown':'#f8f9fb'};
const STROKE = {'node-number':'#93c5fd','node-var':'#86efac','node-assign':'#d8b4fe','node-binop':'#fcd34d','node-unary':'#fdba74','node-func':'#f9a8d4','node-unknown':'#e4e8f0'};
const TCOLOR = {'node-number':'#1d4ed8','node-var':'#15803d','node-assign':'#7c3aed','node-binop':'#92400e','node-unary':'#c2410c','node-func':'#be185d','node-unknown':'#6b7280'};

/** Re-render the current tree (respecting state.collapsedIds). */
function renderTree() {
  treeContainer.innerHTML = '';
  const root = state.lastTree;
  if (!root) {
    treeContainer.innerHTML = '<div class="tab-empty">Run an expression to see the parse tree</div>';
    return;
  }

  // Layout pass — only expand non-collapsed subtrees
  computeWidth(root);
  const depth = treeDepth(root);
  const svgW  = root._w + 40;
  const svgH  = (depth + 1) * (NH + VGAP) + 50;
  placeNodes(root, 20, 20, root._w);

  const NS  = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('width',  svgW);
  svg.setAttribute('height', svgH);
  svg.setAttribute('viewBox', `0 0 ${svgW} ${svgH}`);
  svg.style.cssText = 'display:block;overflow:visible;';

  // defs
  const defs = document.createElementNS(NS,'defs');
  defs.innerHTML = `<filter id="node-glow" x="-25%" y="-25%" width="150%" height="150%">
    <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="rgba(79,70,229,0.22)"/>
  </filter>`;
  svg.appendChild(defs);

  const eGrp = document.createElementNS(NS,'g');
  paintEdges(root, eGrp, NS);
  svg.appendChild(eGrp);

  const nGrp = document.createElementNS(NS,'g');
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

function isCollapsed(node) {
  return state.collapsedIds.has(node._id);
}

function treeDepth(node) {
  if (!node) return 0;
  if (isCollapsed(node) || !node.children || !node.children.length) return 0;
  return 1 + Math.max(...node.children.map(treeDepth));
}

function computeWidth(node) {
  if (!node) return;
  const collapsed = isCollapsed(node);
  if (collapsed || !node.children || !node.children.length) {
    node._w = NW + HGAP;
    return;
  }
  node.children.forEach(computeWidth);
  node._w = Math.max(NW + HGAP, node.children.reduce((s,c) => s + c._w, 0));
}

function placeNodes(node, xLeft, y, totalW) {
  if (!node) return;
  const collapsed = isCollapsed(node);
  if (collapsed || !node.children || !node.children.length) {
    node._cx = xLeft + node._w / 2;
    node._y  = y;
    return;
  }
  let cx = xLeft;
  node.children.forEach(child => {
    placeNodes(child, cx, y + NH + VGAP, totalW);
    cx += child._w;
  });
  const f = node.children[0]._cx;
  const l = node.children[node.children.length-1]._cx;
  node._cx = (f + l) / 2;
  node._y  = y;
}

function paintEdges(node, g, NS) {
  if (!node || isCollapsed(node)) return;
  if (!node.children) return;
  node.children.forEach(child => {
    const py = node._y + NH;
    const cy = child._y;
    const my = (py + cy) / 2;
    const path = document.createElementNS(NS,'path');
    path.setAttribute('d', `M${node._cx},${py} C${node._cx},${my} ${child._cx},${my} ${child._cx},${cy}`);
    path.setAttribute('fill','none');
    path.setAttribute('stroke','#c8d3e8');
    path.setAttribute('stroke-width','1.8');
    path.setAttribute('stroke-linecap','round');
    g.appendChild(path);
    paintEdges(child, g, NS);
  });
}

function paintNodes(node, g, NS) {
  if (!node) return;
  const x      = Math.round(node._cx - NW/2);
  const y      = Math.round(node._y);
  const cls    = node.class || 'node-unknown';
  const fill   = FILL[cls]   || '#f8f9fb';
  const stroke = STROKE[cls] || '#e4e8f0';
  const tcolor = TCOLOR[cls] || '#374151';
  const collapsed = isCollapsed(node);
  const hasKids   = node.children && node.children.length > 0;

  // Shadow
  const sh = document.createElementNS(NS,'rect');
  sh.setAttribute('x', x+2); sh.setAttribute('y', y+3);
  sh.setAttribute('width', NW); sh.setAttribute('height', NH);
  sh.setAttribute('rx', RX); sh.setAttribute('fill','rgba(0,0,0,0.05)');
  g.appendChild(sh);

  // Box
  const rect = document.createElementNS(NS,'rect');
  rect.setAttribute('x', x); rect.setAttribute('y', y);
  rect.setAttribute('width', NW); rect.setAttribute('height', NH);
  rect.setAttribute('rx', RX);
  rect.setAttribute('fill', collapsed ? '#f0f0f0' : fill);
  rect.setAttribute('stroke', collapsed ? '#a0a0c0' : stroke);
  rect.setAttribute('stroke-width', '1.5');
  rect.style.cursor = hasKids ? 'pointer' : 'default';

  // Hover / tooltip
  rect.addEventListener('mouseenter', e => {
    rect.setAttribute('filter','url(#node-glow)');
    rect.setAttribute('stroke-width','2.2');
    if (node.detail) {
      let tip = node.detail;
      if (hasKids) tip += collapsed ? '\n[click to expand]' : '\n[click to collapse]';
      nodeTooltip.textContent = tip;
      nodeTooltip.style.display = 'block';
    }
    moveTooltip(e);
  });
  rect.addEventListener('mousemove', moveTooltip);
  rect.addEventListener('mouseleave', () => {
    rect.setAttribute('filter','');
    rect.setAttribute('stroke-width','1.5');
    nodeTooltip.style.display = 'none';
  });

  // Click = toggle collapse (only nodes with children)
  if (hasKids) {
    rect.addEventListener('click', e => {
      e.stopPropagation();
      nodeTooltip.style.display = 'none';
      if (collapsed) {
        state.collapsedIds.delete(node._id);
      } else {
        state.collapsedIds.add(node._id);
      }
      renderTree();
    });
  }
  g.appendChild(rect);

  // Label
  const rawLabel  = node.label && node.label.length > 11 ? node.label.slice(0,10)+'\u2026' : (node.label || '');
  const dispLabel = collapsed && hasKids ? rawLabel + ' [+]' : rawLabel;

  const txt = document.createElementNS(NS,'text');
  txt.setAttribute('x', node._cx);
  txt.setAttribute('y', y + NH/2 + 1);
  txt.setAttribute('text-anchor','middle');
  txt.setAttribute('dominant-baseline','middle');
  txt.setAttribute('fill', collapsed ? '#6b7280' : tcolor);
  txt.setAttribute('font-family','DM Mono, monospace');
  txt.setAttribute('font-size','12.5');
  txt.setAttribute('font-weight','500');
  txt.style.pointerEvents = 'none';
  txt.style.userSelect    = 'none';
  txt.textContent = dispLabel;
  g.appendChild(txt);

  // Type badge
  const badge = document.createElementNS(NS,'text');
  badge.setAttribute('x', node._cx);
  badge.setAttribute('y', y + NH + 11);
  badge.setAttribute('text-anchor','middle');
  badge.setAttribute('dominant-baseline','middle');
  badge.setAttribute('fill','#9aa4b8');
  badge.setAttribute('font-family','DM Sans, sans-serif');
  badge.setAttribute('font-size','9');
  badge.style.pointerEvents = 'none';
  badge.style.userSelect    = 'none';
  badge.textContent = (node.class || '').replace('node-','');
  g.appendChild(badge);

  // Recurse — skip children if collapsed
  if (!collapsed && node.children) {
    node.children.forEach(c => paintNodes(c, g, NS));
  }
}

function moveTooltip(e) {
  const x = Math.min(e.clientX + 14, window.innerWidth - 220);
  const y = Math.max(e.clientY - 44, 4);
  nodeTooltip.style.left = `${x}px`;
  nodeTooltip.style.top  = `${y}px`;
}

// ── Tree control buttons ────────────────────────────────────────────────────
/**
 * Expand All: clears the collapsed set and re-renders.
 * Every node that was folded will open up.
 */
btnExpandAll.addEventListener('click', () => {
  if (!state.lastTree) return;
  state.collapsedIds.clear();
  renderTree();
});

/**
 * Collapse All: adds every non-root node that has children to the collapsed set.
 * The root stays visible; its children appear as collapsed boxes with [+].
 */
btnCollapseAll.addEventListener('click', () => {
  if (!state.lastTree) return;
  state.collapsedIds.clear();
  // collapse from depth-1 down (keep root open, collapse its direct children)
  function collapseKids(node) {
    if (!node || !node.children) return;
    node.children.forEach(child => {
      if (child.children && child.children.length) {
        state.collapsedIds.add(child._id);
      }
      collapseKids(child);
    });
  }
  collapseKids(state.lastTree);
  renderTree();
});

/**
 * Center: resets both collapse state and scroll position, giving a fresh view.
 */
btnCenter.addEventListener('click', () => {
  if (!state.lastTree) return;
  state.collapsedIds.clear();
  renderTree();
  // scroll the container back to top-left
  const scroller = treeContainer.querySelector('div');
  if (scroller) { scroller.scrollLeft = 0; scroller.scrollTop = 0; }
});

// ──────────────────────────────────────────────────────
// SYMBOL TABLE
// ──────────────────────────────────────────────────────
const BUILTINS = {PI:'3.14159\u2026',E:'2.71828\u2026',TAU:'6.28318\u2026',INF:'Infinity',NAN:'NaN',null:'0',true:'true',false:'false'};

function renderSymbolTable() {
  symbolArea.innerHTML = '';
  const all  = {...BUILTINS, ...state.symbolTable};
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

// ──────────────────────────────────────────────────────
// TABS
// ──────────────────────────────────────────────────────
phaseTabs.addEventListener('click', e => {
  const btn = e.target.closest('.phase-tab');
  if (!btn) return;
  document.querySelectorAll('.phase-tab').forEach(t  => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p  => p.classList.remove('active'));
  btn.classList.add('active');
  const panel = document.getElementById(`tab-${btn.dataset.tab}`);
  if (panel) panel.classList.add('active');
});

// ──────────────────────────────────────────────────────
// REFERENCE — Run buttons
// ──────────────────────────────────────────────────────
// ── helpers ──────────────────────────────────────────
function decodeHTMLEntities(str) {
  // The browser already decodes &amp; → & in dataset values when the HTML
  // is parsed, but double-encoded sequences like &lt;&lt; need one more pass.
  const d = document.createElement('div');
  d.innerHTML = str;
  return d.textContent;
}

function switchToTab(tabName) {
  document.querySelectorAll('.phase-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  const tab = document.querySelector(`.phase-tab[data-tab="${tabName}"]`);
  const panel = document.getElementById(`tab-${tabName}`);
  if (tab)   tab.classList.add('active');
  if (panel) panel.classList.add('active');
}

// ── Reference "▶ Run" buttons ─────────────────────────
document.querySelectorAll('.ref-run-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    e.preventDefault();
    e.stopPropagation();

    const row  = btn.closest('.ref-row');
    if (!row) return;

    // dataset.run is already decoded by the browser when parsing the HTML.
    const decoded = row.dataset.run || '';
    if (!decoded.trim()) return;

    // 1. Fill the editor
    codeInput.value = decoded;

    // 2. Switch to the tokens tab immediately
    switchToTab('tokens');

    // 3. Scroll the playground into view
    const playground = document.getElementById('playground');
    playground.scrollIntoView({behavior: 'smooth', block: 'start'});

    // 4. Run after scroll settles (smooth scroll takes ~400 ms on most browsers)
    //    We also wait for the tab switch to complete.
    clearTimeout(window._refRunTimer);
    window._refRunTimer = setTimeout(() => {
      codeInput.focus();
      runCode();
    }, 500);
  });
});

// ──────────────────────────────────────────────────────
// OTHER BUTTONS
// ──────────────────────────────────────────────────────
btnRun.addEventListener('click', runCode);
codeInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); runCode(); }
});

btnClear.addEventListener('click', () => {
  codeInput.value = '';
  codeInput.focus();
  outputArea.innerHTML = `<div class="output-placeholder"><div class="placeholder-icon">\u2b21</div><p>Run an expression to see results</p></div>`;
  hideAISuggestion();
});

btnReset.addEventListener('click', async () => {
  if (!confirm('Reset session? All user-defined variables will be cleared.')) return;
  await fetch('/api/reset', {method:'POST'});
  state.symbolTable = {};
  renderSymbolTable();
  outputArea.innerHTML = `<div class="output-placeholder"><div class="placeholder-icon">\u2b21</div><p>Session reset \u2014 variables cleared.</p></div>`;
  hideAISuggestion();
});

// ──────────────────────────────────────────────────────
// EXAMPLE CHIPS
// ──────────────────────────────────────────────────────
document.querySelectorAll('.example-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    codeInput.value = chip.dataset.expr;
    document.getElementById('playground').scrollIntoView({behavior:'smooth'});
    document.querySelectorAll('.phase-tab').forEach(t  => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p  => p.classList.remove('active'));
    document.querySelector('.phase-tab[data-tab="tokens"]').classList.add('active');
    document.getElementById('tab-tokens').classList.add('active');
    setTimeout(runCode, 350);
  });
});

// ──────────────────────────────────────────────────────
// MOBILE NAV
// ──────────────────────────────────────────────────────
mobileToggle.addEventListener('click', () => {
  document.querySelector('.nav-links').classList.toggle('open');
});
document.querySelectorAll('.nav-link').forEach(l =>
  l.addEventListener('click', () => document.querySelector('.nav-links').classList.remove('open'))
);

// ──────────────────────────────────────────────────────
// SCROLL ANIMATIONS
// ──────────────────────────────────────────────────────
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, {threshold: 0.1});

document.querySelectorAll('.phase-card, .ref-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(18px)';
  el.style.transition = 'opacity 0.45s ease, transform 0.45s ease';
  obs.observe(el);
});

// ──────────────────────────────────────────────────────
// ACTIVE NAV LINK ON SCROLL
// ──────────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  const y = window.scrollY + 80;
  document.querySelectorAll('section[id]').forEach(sec => {
    const link = document.querySelector(`.nav-link[href="#${sec.id}"]`);
    if (link) link.classList.toggle('active-link', y >= sec.offsetTop && y < sec.offsetTop + sec.offsetHeight);
  });
}, {passive: true});

// ──────────────────────────────────────────────────────
// INIT
// ──────────────────────────────────────────────────────
renderSymbolTable();
codeInput.focus();
