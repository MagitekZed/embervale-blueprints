
// ---------------------------------------------------------------------------
// Chrome: tool rail, options bar, status, view switching
// ---------------------------------------------------------------------------
function renderToolrail() {
  const rail = $('#toolrail');
  rail.replaceChildren(...TOOLS.map(t => t === 'sep'
    ? h('div', { class: 'rail-sep', role: 'separator' })
    : h('button', { class: 'tool', type: 'button', 'data-tool': t.id, title: `${t.label} (${t.key})`, 'data-tip-desc': t.tip || '', 'aria-label': t.label, 'aria-pressed': String(S.tool === t.id), onclick: () => setTool(t.id), html: svg(t.icon) + `<kbd>${t.key}</kbd>` })));
}
function setTool(id) {
  if (G) abortGesture();
  const was = S.tool;
  S.tool = id;
  if (id !== 'measure') S.measure = null;
  if (id !== 'item') S.ghostItem = null;
  if (id !== 'place') S.placing = null;
  if (id !== 'wall') S.wallChain = null;
  if ((id === 'built') !== (was === 'built') && typeof progDrawCache === 'object') { progDrawCache.key = ''; setTimeout(mark3d, 0); }   // (Mark built shows the progress)
  if (id !== 'paint' && id !== 'erase' && typeof hover3dOff === 'function') hover3dOff();
  S.preview = null;
  if (id === 'item' && !S.itemDef) openTab('items');
  for (const b of document.querySelectorAll('.tool')) b.setAttribute('aria-pressed', String(b.dataset.tool === id));
  renderOptbar(); setCursor(); req2d();
}
function brushChip() {
  const e = S.plan && S.plan.palette[S.brush];
  if (!e) return null;
  return h('button', { class: 'brushchip', type: 'button', title: 'Change material (Materials tab)', onclick: () => openTab('materials') },
    h('span', { class: 'sw', style: `background:${e.color};color:${textOn(e.color)}`, text: symText(S.brush) }), e.name);
}
function paletteSelect(kinds, value, onchange, allowNone) {
  const sel = h('select', { onchange: ev => onchange(ev.target.value) });
  if (allowNone) sel.append(h('option', { value: '', text: 'No floor' }));
  for (const [k, e] of Object.entries(S.plan.palette)) if (kinds.includes(e.kind)) sel.append(h('option', { value: k, text: `${k}  ${e.name}` }));
  sel.value = value;
  return sel;
}
function optToggle(key, label, title) {
  return h('button', { class: 'toggle', type: 'button', 'aria-pressed': String(S.opt[key]), title, onclick: ev => { S.opt[key] = !S.opt[key]; ev.currentTarget.setAttribute('aria-pressed', String(S.opt[key])); LS.set('opt', S.opt); req2d(); mark3d(); }, text: label });
}
function renderOptbar() {
  const bar = $('#optbar');
  const kids = [];
  if (S.plan) {
    const t = S.tool;
    if (t === 'select') kids.push(h('span', { class: 'hint', text: 'Drag to select an area · drag items or area labels to move them · Delete removes · Ctrl+C / Ctrl+V copy' }));
    else if (t === 'paint') kids.push(brushChip(), hotbarStrip(true), h('span', { class: 'hint', text: 'Drag to paint · right-drag erases · 1–9 picks from the hotbar · / finds anything' }));
    else if (t === 'line') kids.push(brushChip(), hotbarStrip(true), h('span', { class: 'hint', text: 'Drag a straight run · Shift locks to 0° / 45° / 90°' }));
    else if (t === 'rect') {
      kids.push(brushChip(), hotbarStrip(true));
      const seg = h('div', { class: 'seg', role: 'group', 'aria-label': 'Rectangle style' });
      for (const [v, lab] of [[false, 'Outline'], [true, 'Filled']]) seg.append(h('button', { type: 'button', 'aria-pressed': String(S.rectFilled === v), text: lab, onclick: () => { S.rectFilled = v; renderOptbar(); } }));
      kids.push(seg, roundSeg(), h('span', { class: 'hint', text: 'Round fits a circle or oval to the box you drag' }));
    } else if (t === 'room') {
      kids.push(h('label', { class: 'inline' }, 'Walls', paletteSelect(['wall', 'block'], S.roomWall, v => { S.roomWall = v; })));
      kids.push(h('label', { class: 'inline' }, 'Floor', paletteSelect(['floor', 'water'], S.roomFloor, v => { S.roomFloor = v; }, true)));
      const th = h('input', { type: 'number', value: String(S.roomThick || CM()), min: String(CM()), max: '8', step: String(CM()), class: 'qty', 'aria-label': 'Wall thickness in metres', title: 'How thick the walls are: they grow inwards from the edge you drag' });
      th.addEventListener('change', () => { S.roomThick = blocksNum(th.value, CM(), CM(), 8); LS.set('roomThick', S.roomThick); renderOptbar(); });
      kids.push(h('label', { class: 'inline' }, 'Thick (m)', th));
      kids.push(roundSeg(), h('span', { class: 'hint', text: 'Drag out a room · walls grow inwards · Round makes a circular room or tower' }));
    } else if (t === 'wall') kids.push(...wallControls());
    else if (t === 'replace') kids.push(...replaceControls());
    else if (t === 'built') kids.push(...builtControls());
    else if (t === 'fill') kids.push(brushChip(), hotbarStrip(true), h('span', { class: 'hint', text: 'Click inside walls to fill the enclosed area · right-click clears it' }));
    else if (t === 'erase') kids.push(h('span', { class: 'hint', text: 'Drag to erase squares on this level' }));
    else if (t === 'item') {
      if (S.itemDef) {
        const m = mountOf(S.itemDef), inWall = IN_WALL.has(m);
        kids.push(h('button', { class: 'brushchip', type: 'button', title: 'Change item (Items tab, or / to find one)', onclick: () => openTab('items') }, mountIcon(S.itemDef), `${S.itemDef.name} · ${metres(S.itemDef.w)}×${metres(inWall ? 1 : S.itemDef.d)} m${m !== 'floor' ? ' · ' + MOUNTS[m].toLowerCase() : ''}`),
          h('button', { class: 'btn btn-sm', type: 'button', text: inWall ? 'Flip (R)' : 'Rotate (R)', onclick: () => { S.itemRot = (S.itemRot + (inWall ? 180 : 90)) % 360; req2d(); } }),
          h('span', { class: 'hint', text: inWall ? 'Hover a wall and click · right-click removes' : m === 'wall' ? 'Hover beside a wall and click · right-click removes' : 'Click to place · right-click removes' }));
      } else kids.push(h('span', { class: 'hint', text: 'Pick an item in the Items tab, or press / to find one' }));
    } else if (t === 'zone') kids.push(h('span', { class: 'hint', text: 'Drag to mark a room or area, then name it' }));
    else if (t === 'terrain') kids.push(...terrainControls());
    else if (t === 'pieces') kids.push(...pieceControls());
    if (MIRROR_TOOLS.has(t)) {                                // mirror controls go before the hint text, which can scroll off
      const at = kids.findIndex(k => k && k.classList && k.classList.contains('hint'));
      kids.splice(at < 0 ? kids.length : at, 0, mirrorControls());
    }
    if (t === 'place' && S.placing) kids.push(h('span', { class: 'brushchip', text: `${S.placing.name}${S.placing.rot ? ` · turned ${S.placing.rot}°` : ''}` }),
      h('button', { class: 'btn btn-sm', type: 'button', text: 'Rotate (R)', onclick: rotatePlace }),
      h('span', { class: 'hint', text: 'Click to place it · Esc cancels' }));
    else if (t === 'measure') kids.push(h('span', { class: 'hint', id: 'measureOut', text: S.measure ? measureText() : 'Drag between two points' }));
    else if (t === 'pan') kids.push(h('span', { class: 'hint', text: 'Drag to move around · scroll to zoom' }));
    kids.push(h('span', { class: 'spacer' }));
    kids.push(optToggle('ghost', isUnder(lv()) ? 'Level above' : 'Level below', isUnder(lv()) ? 'Show the level above as a faint outline, to dig under it' : 'Show the level below as a faint outline'));
    kids.push(optToggle('zones', 'Areas', 'Show named areas'));
    kids.push(optToggle('altar', 'Altar range', 'Show the Flame Altar build area'));
  }
  bar.replaceChildren(...kids.filter(Boolean));
}
function roundSeg() {
  const seg = h('div', { class: 'seg', role: 'group', 'aria-label': 'Shape' });
  for (const [v, lab] of [[false, 'Box'], [true, 'Round']]) seg.append(h('button', { type: 'button', 'aria-pressed': String(S.round === v), text: lab, onclick: () => { S.round = v; renderOptbar(); } }));
  return seg;
}
function updateOptReadout() { const m = $('#measureOut'); if (m && S.measure) m.textContent = measureText(); }
function updateStatus() {
  const L = lv();
  // Reserve exactly the width of the longest coordinate this plan can show, so nothing beside it shifts.
  if (S.plan) $('#stCursor').style.width = `x ${metres(S.plan.w - 1)} m · y ${metres(S.plan.h - 1)} m`.length + 'ch';
  const lay = layerOn(), k = lay ? curLayer() : 0, [lo, hi] = lay ? layerSpan() : [0, 0];
  let text = '–';
  if (L && lay) { const [z0, z1] = layerZ(k); text = `${layerName(k)} · ${fmt(z0)} to ${fmt(z1)} m${z0 < -0.01 ? ' · underground' : ''}`; }
  else if (L) text = `${L.name} · ${fmt(L.elev)} to ${fmt(L.elev + L.height)} m${isUnder(L) ? ' · underground' : ''}`;
  $('#stLevelText').textContent = text;
  $('#stLevel').disabled = !L;
  $('#modeLevels').setAttribute('aria-pressed', String(!lay)); $('#modeLayers').setAttribute('aria-pressed', String(lay));
  $('#modeLevels').disabled = $('#modeLayers').disabled = !L;
  // at the bottom or top, the arrows open the level list instead, ready to dig down or build up
  $('#lvlDown').disabled = !L; $('#lvlUp').disabled = !L;
  if (lay) {
    $('#lvlDown').dataset.tip = k <= lo ? 'Bottom of the plan: add a level below in Levels mode' : 'Layer below ([)';
    $('#lvlUp').dataset.tip = k >= hi ? 'Top of the plan: add a level on top in Levels mode' : 'Layer above (])';
    $('#stLevel').removeAttribute('title'); $('#stLevel').dataset.tip = 'All block layers: jump to one';
  } else {
    const bottom = !L || nextMain(-1) < 0, top = !L || nextMain(1) < 0;
    $('#lvlDown').dataset.tip = bottom ? 'Lowest level: dig a level below…' : 'Level below ([)';
    $('#lvlUp').dataset.tip = top ? 'Top level: add a level on top…' : 'Level above (])';
    $('#stLevel').removeAttribute('title'); $('#stLevel').dataset.tip = 'All levels: jump to one, add one on top or dig one below';
  }
  renderStrip();
}
// ---------------------------------------------------------------------------
// Level list: click the level name in the status bar
// ---------------------------------------------------------------------------
let lvlPop = null;
function toggleLevelPop(focus) { if (lvlPop) closeLevelPop(); else openLevelPop(focus); }
function closeLevelPop(refocus) {
  if (!lvlPop) return;
  lvlPop.remove(); lvlPop = null;
  $('#stLevel').setAttribute('aria-expanded', 'false');
  document.removeEventListener('pointerdown', levelPopOutside, true);
  if (refocus) $('#stLevel').focus();
}
// The level's group: one of the plan's groups or a new name; a trim follows its main level.
function groupField(L) {
  const m = trimParent(L);
  if (m) return h('p', { class: 'note', text: `A trim level of “${m.name}”, so it’s in that level’s group (${levelGroup(L)}).` });
  const names = levelGroups().map(G => G.name), id = 'grp-' + uid('g');
  const inp = h('input', { type: 'text', value: L.group || '', placeholder: autoGroup(L.name), maxlength: '40', list: id, 'aria-label': 'Group', disabled: S.readOnly });
  inp.addEventListener('change', () => { begin(); const v = inp.value.trim().slice(0, 40); if (v) L.group = v; else delete L.group; commit(); renderLevels(); });
  return h('label', { class: 'field', title: 'The group it’s listed under. Left empty, it goes by the part of its name before a colon' },
    h('span', { text: 'Group' }), inp, h('datalist', { id }, ...names.map(n => h('option', { value: n }))));
}
function levelPopOutside(e) { if (lvlPop && !lvlPop.contains(e.target) && !e.target.closest('#stLevel, #lvlUp, #lvlDown')) closeLevelPop(); }
function openLevelPop(focus) {
  if (!S.plan) return;
  closeLevelPop(); hideTip(true);
  if (layerOn()) { openLayerPop(); return; }
  const P = S.plan, rows = [], groups = levelGroups(P), col = groupColours(groups), grouped = groups.length > 1, cur = mainLevel(lv());
  const lpRow = (l, i, trim) => h('button', {
    class: 'lp-row' + (isUnder(l) ? ' lp-under' : '') + (l.hidden ? ' lp-hidden' : '') + (trim ? ' lp-trim' : ''), type: 'button', role: 'option',
    'aria-selected': String(i === S.levelIdx), 'data-i': String(i), title: l.hidden ? 'Hidden in 3D' : '',
    onclick: () => { setLevel(i); closeLevelPop(true); },
  }, h('span', { class: 'lp-name', text: trim ? trimLabel(l) : l.name }), h('span', { class: 'lp-m', text: `${fmt(l.elev)} to ${fmt(l.elev + l.height)} m` }));
  let above = false, ground = false;
  for (const G of groups) {
    if (grouped) rows.push(h('div', { class: 'lp-group', 'aria-hidden': 'true' }, h('i', { style: `background:${col.get(G.name)}` }), h('span', { text: G.name }), h('span', { text: `${fmt(G.lo)} to ${fmt(G.hi)} m` })));
    for (const it of G.items) {
      const l = it.L;
      if (!grouped && isUnder(l) && above && !ground) { rows.push(h('div', { class: 'lp-ground', 'aria-hidden': 'true' }, h('span', { text: 'ground 0 m' }))); ground = true; }
      if (!isUnder(l)) above = true;
      rows.push(lpRow(l, it.i, false));
      if (l === cur && lv() !== cur) for (const t of it.trims) rows.push(lpRow(t.L, t.i, true));   // on a trim: its siblings too
    }
  }
  const full = P.levels.length >= MAX_LEVELS || S.readOnly;
  const upBtn = h('button', { class: 'btn btn-sm', type: 'button', text: 'Add on top', disabled: full, title: 'A new storey above the highest level', onclick: () => { closeLevelPop(true); addLevel('top'); } });
  const digBtn = h('button', { class: 'btn btn-sm', type: 'button', text: 'Dig below', disabled: full, title: 'A new level under the lowest one. Below 0 m it is dug into the ground', onclick: () => { closeLevelPop(true); addLevel('below'); } });
  lvlPop = h('div', { class: 'lvlpop', role: 'listbox', 'aria-label': 'Levels' }, h('div', { class: 'lp-act' }, upBtn), ...rows, h('div', { class: 'lp-act' }, digBtn));
  document.body.append(lvlPop);
  const r = $('#stLevel').getBoundingClientRect();
  lvlPop.style.left = clamp(r.left, 8, innerWidth - lvlPop.offsetWidth - 8) + 'px';
  lvlPop.style.bottom = (innerHeight - r.top + 6) + 'px';
  $('#stLevel').setAttribute('aria-expanded', 'true');
  lvlPop.addEventListener('keydown', e => {
    const list = [...lvlPop.querySelectorAll('button:not(:disabled)')], at = list.indexOf(document.activeElement);
    if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); closeLevelPop(true); }
    else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); e.stopPropagation(); const n = list[clamp(at + (e.key === 'ArrowDown' ? 1 : -1), 0, list.length - 1)]; if (n) n.focus(); }
    else if (e.key === 'Home' || e.key === 'End') { e.preventDefault(); e.stopPropagation(); (e.key === 'Home' ? list[0] : list[list.length - 1]).focus(); }
    else e.stopPropagation();                                  // keep plan shortcuts out of the list
  });
  setTimeout(() => document.addEventListener('pointerdown', levelPopOutside, true), 0);
  const target = focus === 'dig' ? digBtn : focus === 'up' ? upBtn : lvlPop.querySelector('[aria-selected="true"]');
  if (target && !target.disabled) target.focus(); else { const f = lvlPop.querySelector('[aria-selected="true"]'); if (f) f.focus(); }
}
// In block-layer mode the list is every layer of the plan by height, top first, with the ground marked.
function openLayerPop() {
  const [lo, hi] = layerSpan(), cur = curLayer(), rows = [];
  for (let k = hi; k >= lo; k--) {
    if (k === -1 && hi >= 0) rows.push(h('div', { class: 'lp-ground', 'aria-hidden': 'true' }, h('span', { text: 'ground 0 m' })));
    const [z0, z1] = layerZ(k);
    rows.push(h('button', {
      class: 'lp-row' + (z0 < -0.01 ? ' lp-under' : ''), type: 'button', role: 'option', 'aria-selected': String(k === cur),
      onclick: () => { setLayer(k); closeLevelPop(true); },
    }, h('span', { class: 'lp-name', text: layerName(k) }), h('span', { class: 'lp-m', text: `${fmt(z0)} to ${fmt(z1)} m` })));
  }
  lvlPop = h('div', { class: 'lvlpop', role: 'listbox', 'aria-label': 'Block layers' }, ...rows,
    h('p', { class: 'lp-note', text: 'To build higher or dig deeper, add a level in Levels mode.' }));
  document.body.append(lvlPop);
  const r = $('#stLevel').getBoundingClientRect();
  lvlPop.style.left = clamp(r.left, 8, innerWidth - lvlPop.offsetWidth - 8) + 'px';
  lvlPop.style.bottom = (innerHeight - r.top + 6) + 'px';
  $('#stLevel').setAttribute('aria-expanded', 'true');
  lvlPop.addEventListener('keydown', e => {
    const list = [...lvlPop.querySelectorAll('button')], at = list.indexOf(document.activeElement);
    if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); closeLevelPop(true); }
    else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); e.stopPropagation(); const n = list[clamp(at + (e.key === 'ArrowDown' ? 1 : -1), 0, list.length - 1)]; if (n) n.focus(); }
    else if (e.key === 'Home' || e.key === 'End') { e.preventDefault(); e.stopPropagation(); (e.key === 'Home' ? list[0] : list[list.length - 1]).focus(); }
    else e.stopPropagation();
  });
  setTimeout(() => document.addEventListener('pointerdown', levelPopOutside, true), 0);
  const f = lvlPop.querySelector('[aria-selected="true"]');
  if (f) { f.focus(); f.scrollIntoView({ block: 'center' }); }
}

// ---------------------------------------------------------------------------
// Tooltips: one styled tip for anything with a title. Titles move to data-tip, so the browser's own
// tooltip doesn't double up; icon-only buttons use their label. "(B)" at the end shows as a key.
// ---------------------------------------------------------------------------
const TIP = { el: null, timer: 0, warm: 0, target: null };
function initTips() {
  TIP.el = h('div', { class: 'tip', role: 'tooltip', id: 'tip' });
  document.body.append(TIP.el);
  document.addEventListener('pointerover', e => {
    if (e.pointerType === 'touch') return;
    const t = tipTarget(e.target);
    if (t !== TIP.target) { hideTip(); if (t) scheduleTip(t); }
  });
  document.addEventListener('pointerout', e => { if (TIP.target && !(e.relatedTarget && TIP.target.contains(e.relatedTarget))) hideTip(); });
  for (const ev of ['pointerdown', 'keydown', 'wheel']) document.addEventListener(ev, () => hideTip(true), { capture: true, passive: true });
  document.addEventListener('focusin', e => { const t = tipTarget(e.target); if (t && t.matches(':focus-visible')) showTip(t); });
  document.addEventListener('focusout', () => hideTip());
}
function tipTarget(node) {
  const el = node && node.closest && node.closest('[title], [data-tip], button[aria-label]');
  if (!el) return null;
  if (el.hasAttribute('title')) {
    const t = el.getAttribute('title');
    el.removeAttribute('title');
    el.dataset.tip = t;
    if (t && !el.getAttribute('aria-label') && !el.textContent.trim()) el.setAttribute('aria-label', t);
  }
  if (el.dataset.tip) return el;
  return el.matches('button[aria-label]') && !el.textContent.trim() ? el : null;
}
function scheduleTip(el) {
  clearTimeout(TIP.timer);
  TIP.target = el;
  if (performance.now() < TIP.warm) showTip(el); else TIP.timer = setTimeout(() => showTip(el), 450);
}
function showTip(el) {
  const text = el.dataset.tip || el.getAttribute('aria-label') || '';
  if (!text || !el.isConnected) return;
  if (lvlPop && el.closest('.lvl-switch')) return;              // the open level list says it all
  TIP.target = el;
  const m = text.match(/^(.*?)\s*\(((?:(?:Ctrl|Shift|Alt|Cmd)\+)*(?:[A-Z0-9]|[\[\]+=−-]|Space|Esc|Delete))\)$/);
  const desc = el.dataset.tipDesc;
  TIP.el.replaceChildren(...[h('b', { text: m ? m[1] : text }), m && h('kbd', { text: m[2] }), desc && h('span', { class: 'tip-desc', text: desc })].filter(Boolean));
  const r = el.getBoundingClientRect(), t = TIP.el, gap = 7, pad = 8;
  t.style.left = '0px'; t.style.top = '0px';
  const tw = t.offsetWidth, th = t.offsetHeight;
  let x, y;
  if (el.closest('.toolrail')) { x = r.right + gap; y = r.top + r.height / 2 - th / 2; }
  else { x = r.left + r.width / 2 - tw / 2; y = r.bottom + gap; if (y + th > innerHeight - pad) y = r.top - th - gap; }
  t.style.left = clamp(x, pad, innerWidth - tw - pad) + 'px';
  t.style.top = clamp(y, pad, innerHeight - th - pad) + 'px';
  t.classList.add('show');
  el.setAttribute('aria-describedby', 'tip');
}
function hideTip(cold) {
  clearTimeout(TIP.timer);
  if (TIP.el && TIP.el.classList.contains('show')) { TIP.el.classList.remove('show'); if (!cold) TIP.warm = performance.now() + 500; }
  if (TIP.target) TIP.target.removeAttribute('aria-describedby');
  TIP.target = null;
}

function updateUndo() {
  $('#undoBtn').disabled = !S.hist.length; $('#redoBtn').disabled = !S.fut.length; $('#histBtn').disabled = !S.plan;
  const u = S.hist[S.hist.length - 1], r = S.fut[S.fut.length - 1];      // the steps' names, in the buttons' tips
  $('#undoBtn').removeAttribute('title'); $('#undoBtn').dataset.tip = u ? `Undo: ${u.label} (Ctrl+Z)` : 'Undo (Ctrl+Z)';
  $('#redoBtn').removeAttribute('title'); $('#redoBtn').dataset.tip = r ? `Redo: ${r.label} (Ctrl+Shift+Z)` : 'Redo (Ctrl+Shift+Z)';
}
function setView(v, remember = true) {
  S.view = v; if (remember) LS.set('view', v);
  $('#views').dataset.view = v;
  for (const b of document.querySelectorAll('#viewSeg button')) b.setAttribute('aria-pressed', String(b.dataset.view === v));
  requestAnimationFrame(() => { resize2d(); if (remember) fitView(true); if (v !== '2d') { if (init3d()) { resize3d(); if (V3.dirty) build3d(); else camUpdate(); } } });
}
const PANEL_TABS = ['materials', 'items', 'levels', 'build', 'inventory', 'plan'];
function openTab(tab) {
  S.tab = tab;
  for (const b of document.querySelectorAll('#tabs [role="tab"]')) b.setAttribute('aria-selected', String(b.dataset.tab === tab));
  for (const id of PANEL_TABS) $('#pane-' + id).hidden = id !== tab;
  if (tab === 'build') renderBuildPane();
  if (tab === 'inventory') renderInventoryPane();
  if (window.matchMedia('(max-width: 860px)').matches) $('#panel').classList.add('open');
}
function showEmpty(kind) {
  $('#empty').hidden = false;
  const actions = $('#emptyActions');
  if (kind === 'none') {
    $('#emptyTitle').textContent = 'No plans yet';
    $('#emptyText').textContent = S.mode === 'db'
      ? 'Start a plan here, or ask Claude in chat to draft one. Plans saved here show up for both of you.'
      : 'Start a plan. It saves in this browser.';
    actions.replaceChildren(h('button', { class: 'btn btn-accent', type: 'button', text: 'Start a plan', onclick: newPlanDialog }));
  } else actions.replaceChildren();
  req2d();
}
function hideEmpty() { $('#empty').hidden = true; }
function toast(msg, kind) {
  const t = h('div', { class: 'toast' + (kind ? ' ' + kind : ''), text: msg });
  $('#toasts').append(t);
  setTimeout(() => t.classList.add('out'), 3200);
  setTimeout(() => t.remove(), 3600);
}

// ---------------------------------------------------------------------------
// Materials pane
// ---------------------------------------------------------------------------
// Block catalogue: every block, roof, overgrowth and terrain material, added to a plan on demand. Like the Items
// tab (planner v63), it groups by kind (Blocks, Overgrowth, Roofs, Terrain, with the catalogue's groups as
// subheadings) or by region (in the order the Flame opens them), and "Show" (shared with the Items tab) hides
// blocks from later regions. A block's region and maker come from the 1.0 crafting data (the site's
// building-blocks tiers), else the wiki's.
const blockCraft = b => (typeof CRAFT === 'object' && CRAFT ? craftNamed(b.n) || CRAFT.items.find(c => c.catalogueName === b.n) || null : null);
function blockRegion(b) {
  const c = blockCraft(b), t = c && c.tier ? String(c.tier).split(', ').pop() : null;
  return GAME_REGIONS.includes(t) ? t : GAME_REGIONS.includes(b.r) ? b.r : null;
}
const blockKind = b => (/^Terrain/.test(b.g) ? 'Terrain' : b.g === 'Roofs' || b.g === 'Overgrowth' ? b.g : 'Blocks');
const blockSub = b => { const t = b.g.replace(/^Terrain · /, ''); return t === 'other' ? 'Other terrain' : t[0].toUpperCase() + t.slice(1); };
function catalogueSection() {
  const search = h('input', { type: 'text', placeholder: 'Find a block, roof or terrain', 'aria-label': 'Find a block', value: S.catFilter });
  const box = h('div', { class: 'section' });
  const inPlan = new Set(Object.values(S.plan.palette).map(e => e.name + '|' + e.kind));
  const mode = LS.get('blockGroupBy', 'kind') === 'region' ? 'region' : 'kind';
  const cap = itemRegionCap();
  const shown = BLOCKS.filter(b => { const r = blockRegion(b); return cap < 0 || !r || GAME_REGIONS.indexOf(r) <= cap; });
  const row = b => {
    const c = blockCraft(b), maker = c ? (c.crafter || c.station || ((c.inputs || []).length ? 'by hand' : 'gathered')) : null;
    const sub = [maker, blockRegion(b)].filter(Boolean).join(' · ');
    const btn = kind => h('button', { class: 'btn btn-sm' + (inPlan.has(b.n + '|' + kind) ? ' have' : ''), type: 'button', title: `Add ${b.n} to this plan as a ${kind}`, text: kind === 'wall' ? 'Wall' : kind === 'roof' ? 'Roof' : 'Floor', onclick: () => addCatalogueBlock(b, kind) });
    const order = b.g === 'Roofs' ? ['roof', 'wall'] : b.k === 'floor' ? ['floor', 'wall'] : ['wall', 'floor'];
    const recipe = c && (c.inputs || []).length ? `Recipe: ${c.inputs.map(i => `${i.item} ×${i.qty}`).join(', ')}${c.makes > 1 ? ` (makes ${c.makes})` : ''}` : '';
    return h('div', { class: 'catrow', title: b.n, 'data-tip-desc': [recipe, c && c.unlock ? `Unlocks once you ${c.unlock}` : b.u ? `Unlock: ${b.u}` : ''].filter(Boolean).join(' · ') || null },
      h('span', { class: 'swatch sm', style: `background:${b.c}` }),
      h('span', { class: 'catname' }, h('span', { class: 'nm', text: b.n }), h('span', { class: 'sub', text: sub })),
      h('span', { class: 'btnrow' }, ...order.map(btn)));
  };
  const draw = () => {
    const q = S.catFilter.trim().toLowerCase();
    if (q) {
      const hits = shown.filter(b => (b.n + ' ' + b.g + ' ' + (blockRegion(b) || '')).toLowerCase().includes(q));
      box.replaceChildren(hits.length ? h('div', { class: 'catlist' }, ...hits.map(row)) : h('p', { class: 'note', text: 'No blocks match that.' }));
      return;
    }
    const tops = new Map();
    for (const b of shown) {
      const top = mode === 'region' ? (blockRegion(b) || 'Gathered terrain and other') : blockKind(b), sub = blockSub(b);
      if (!tops.has(top)) tops.set(top, new Map());
      if (!tops.get(top).has(sub)) tops.get(top).set(sub, []);
      tops.get(top).get(sub).push(b);
    }
    const order = mode === 'region' ? [...GAME_REGIONS, 'Gathered terrain and other'] : [...tops.keys()].sort();
    box.replaceChildren(...order.filter(t => tops.has(t)).map(top => {
      const subs = [...tops.get(top)].sort((a, b) => a[0].localeCompare(b[0])), all = subs.flatMap(([, bs]) => bs), key = mode + ':' + top;
      const d = h('details', { class: 'catgroup' }, h('summary', null, h('span', { class: 'swatchstrip' }, ...all.slice(0, 8).map(b => h('i', { style: `background:${b.c}` }))), `${top} (${all.length})`));
      const fill = () => { if (d.dataset.filled) return; d.dataset.filled = '1'; for (const [name, bs] of subs) d.append(h('div', { class: 'libsub', text: `${name} (${bs.length})` }), h('div', { class: 'catlist' }, ...bs.map(row))); };
      if (S.catOpen.has(key)) { d.open = true; fill(); }
      d.addEventListener('toggle', () => { if (d.open) { S.catOpen.add(key); fill(); } else S.catOpen.delete(key); });
      return d;
    }));
  };
  search.addEventListener('input', () => { S.catFilter = search.value; draw(); });
  draw();
  const regionSel = h('select', { 'aria-label': 'Show blocks makeable up to a region', title: 'Hide blocks you can’t make until a later region (also sets the Items tab’s)',
    onchange: () => { LS.set('itemRegion', regionSel.value); renderMaterials(); } },
    h('option', { value: '', text: 'Every region' }), ...GAME_REGIONS.map(r => h('option', { value: r, text: `Up to ${r.includes("'") ? '' : 'the '}${r}` })));
  regionSel.value = LS.get('itemRegion', '') || '';
  const groupSeg = h('span', { class: 'seg seg-sm', role: 'group', 'aria-label': 'Group blocks by' },
    ...[['kind', 'Kind', 'Blocks, overgrowth, roofs and terrain'], ['region', 'Region', 'The region where you could first make it']].map(([v, t, tip]) =>
      h('button', { type: 'button', 'aria-pressed': String(mode === v), text: t, title: tip, onclick: () => { LS.set('blockGroupBy', v); renderMaterials(); } })));
  return h('div', { class: 'section' },
    h('p', { class: 'note srcnote' }, 'Every block, roof, overgrowth and terrain material in the game (the ', h('a', { href: 'https://enshrouded.wiki.gg/wiki/Building_Materials', target: '_blank', rel: 'noopener', text: 'wiki' }),
      ', plus the blocks 1.0 added, from enshrouded.tools; colours sampled from the icons). Add one as a wall, floor or roof and it joins this plan, ready to paint. Highlighted buttons are already in the plan.'),
    h('div', { class: 'libsearch' }, search, h('div', { class: 'libopts' }, h('label', { class: 'regionpick' }, h('span', { text: 'Show' }), regionSel),
      h('span', { class: 'groupby' }, h('span', { text: 'Group by' }), groupSeg))), box);
}
function pickBrush(k) {
  S.brush = k;
  if (!PAINT_TOOLS.has(S.tool)) setTool('paint'); else renderOptbar();
  renderMaterials();
}
function materialEditor(k, e) {
  const name = h('input', { type: 'text', value: e.name, maxlength: '40', 'aria-label': 'Material name' });
  name.addEventListener('input', () => { liveBegin(); e.name = name.value.slice(0, 40) || 'Material'; markDirty(); renderOptbar(); });
  name.addEventListener('change', () => { liveCommit(); renderMaterials(); });
  const key = h('input', { type: 'text', value: symText(k), maxlength: '3', 'aria-label': 'Symbol', title: 'How this material is stored. Type one visible character to change it', style: 'font-family:var(--font-mono);text-align:center' });
  key.addEventListener('change', () => { if (!changeMaterialKey(k, key.value.trim())) key.value = k; renderMaterials(); renderOptbar(); });
  const kind = h('select', { 'aria-label': 'Type' }, ...Object.entries(KINDS).map(([v, d]) => h('option', { value: v, text: d.label })));
  kind.value = e.kind;
  kind.addEventListener('change', () => { begin(); e.kind = kind.value; commit(); ensureBrushes(); renderMaterials(); renderOptbar(); });
  const color = h('input', { type: 'color', value: e.color, 'aria-label': 'Colour' });
  color.addEventListener('input', () => { liveBegin(); e.color = color.value; req2d(); mark3d(); });
  color.addEventListener('change', () => { liveCommit(); renderMaterials(); renderOptbar(); });
  let heightField = null;
  if (e.kind === 'wall' || e.kind === 'block') {
    const opts = [['', e.kind === 'wall' ? 'Full level height' : '1 m (default)']];
    for (let v = 0.5; v <= 8; v += 0.5) opts.push([String(v), `${fmt(v)} m`]);
    const hs = h('select', { 'aria-label': 'Height' }, ...opts.map(([v, t]) => h('option', { value: v, text: t })));
    hs.value = e.height ? String(e.height) : '';
    if (e.height && hs.value !== String(e.height)) { hs.append(h('option', { value: String(e.height), text: `${fmt(e.height)} m` })); hs.value = String(e.height); }
    hs.addEventListener('change', () => { begin(); if (hs.value) e.height = Number(hs.value); else delete e.height; commit(); renderMaterials(); });
    const bs = h('select', { 'aria-label': 'Raise by' }, h('option', { value: '', text: 'On the floor' }));
    for (let v = 0.5; v <= 8; v += 0.5) bs.append(h('option', { value: String(v), text: `${fmt(v)} m up` }));
    bs.value = e.base ? String(e.base) : '';
    if (e.base && bs.value !== String(e.base)) { bs.append(h('option', { value: String(e.base), text: `${fmt(e.base)} m up` })); bs.value = String(e.base); }
    bs.addEventListener('change', () => { begin(); if (bs.value) e.base = Number(bs.value); else delete e.base; commit(); renderMaterials(); });
    const us = h('select', { 'aria-label': 'Underneath' }, h('option', { value: '', text: 'Nothing underneath' }),
      ...Object.entries(S.plan.palette).filter(([, f]) => f.kind === 'floor' || f.kind === 'water' || f.kind === 'roof').map(([fk, f]) => h('option', { value: fk, text: `${fk}  ${f.name}` })));
    us.value = e.under && S.plan.palette[e.under] ? e.under : '';
    us.addEventListener('change', () => { begin(); if (us.value) e.under = us.value; else delete e.under; commit(); renderMaterials(); });
    heightField = h('div', { class: 'section' },
      h('div', { class: 'grid2' },
        h('label', { class: 'field' }, h('span', { text: 'Height' }), hs),
        h('label', { class: 'field', title: 'Lift it off the floor: thin stair treads, lintels, corbels, floating slabs' }, h('span', { text: 'Raise by' }), bs)),
      h('label', { class: 'field', title: 'A floor or roof square in the same square, under a raised piece (pergola beams, arches over paving, chimney caps over a roof)' }, h('span', { text: 'Underneath' }), us));
  } else if (e.kind === 'door' || e.kind === 'window') {
    const opts = [['', 'Full level height']];
    for (let v = 2.5; v <= 12; v += 0.5) opts.push([String(v), `${fmt(v)} m`]);
    const hs = h('select', { 'aria-label': 'Wall height' }, ...opts.map(([v, t]) => h('option', { value: v, text: t })));
    hs.value = e.height ? String(e.height) : '';
    if (e.height && hs.value !== String(e.height)) { hs.append(h('option', { value: String(e.height), text: `${fmt(e.height)} m` })); hs.value = String(e.height); }
    hs.addEventListener('change', () => { begin(); if (hs.value) e.height = Number(hs.value); else delete e.height; commit(); renderMaterials(); });
    // the opening's own height (sizes measured in game, in blocks tall x wide)
    const door = e.kind === 'door';
    const open = h('select', { 'aria-label': door ? 'Door height' : 'Window height' }, ...(door
      ? [['', '2.5 m (5 blocks): Crude Wooden, Wooden Door'], ['3', '3 m (6 blocks): Round Wooden Door'], ['3.5', '3.5 m (7 blocks): Wooden Double Door']]
      : [['', '1.5 m (3 blocks): Wooden Window Frame'], ['1', '1 m (2 blocks): Round Wooden'], ['3', '3 m (6 blocks): Large Round Wooden']]).map(([v, t]) => h('option', { value: v, text: t })));
    open.value = e.opening ? String(e.opening) : '';
    if (e.opening && open.value !== String(e.opening)) { open.append(h('option', { value: String(e.opening), text: `${fmt(e.opening)} m` })); open.value = String(e.opening); }
    open.addEventListener('change', () => { begin(); if (open.value) e.opening = Number(open.value); else delete e.opening; commit(); renderMaterials(); });
    // which real door or window it is: the material takes its name (and a measured one its height), and
    // the Crafting list counts one per opening
    const real = (typeof CRAFT === 'object' && CRAFT ? CRAFT.items : []).filter(it => it.opening === e.kind).sort((a, b) => a.name.localeCompare(b.name));
    // grouped by shape (OPENING_GROUPS), each with its measured size, maker and first region
    const byShape = new Map(OPENING_ORDER[e.kind].map(g => [g, []]));
    for (const it of real) byShape.get(openingGroup(e.kind, it.name)).push(it);
    const optText = it => [it.name, it.size ? `${it.size.h}×${it.size.w}` : null,
      it.crafter ? (it.station ? `${it.crafter}, needs ${it.station}` : it.crafter) : it.station || ((it.inputs || []).length ? 'by hand' : 'found'), it.region].filter(Boolean).join(' · ');
    const pick = h('select', { 'aria-label': 'Item' }, h('option', { value: '', text: `Not chosen (a plain ${door ? 'door' : 'window'})` }),
      ...[...byShape].filter(([, its]) => its.length).map(([g, its]) => h('optgroup', { label: `${g} (${its.length})` }, ...its.map(it => h('option', { value: it.name, text: optText(it) })))));
    const item = real.find(it => it.name === e.name);
    pick.value = item ? item.name : '';
    pick.addEventListener('change', () => {
      begin(); const it = real.find(x => x.name === pick.value);
      e.name = it ? it.name : (door ? 'Door' : 'Window');
      if (it && it.size) { const m = it.size.h * VOXEL; if (m === (door ? GAME.doorTop : GAME.winTop - GAME.sillTop)) delete e.opening; else e.opening = m; }
      commit(); renderMaterials(); renderOptbar();
    });
    let sill = null;
    if (!door) {                                                // where the window starts (auto: its top level with a door's)
      const so = [['', `Auto (${fmt(winSill({ opening: e.opening }))} m)`]];
      for (let v = 0; v <= 4; v += 0.5) so.push([String(v), `${fmt(v)} m`]);
      sill = h('select', { 'aria-label': 'Sill at' }, ...so.map(([v, t]) => h('option', { value: v, text: t })));
      sill.value = e.sill != null ? String(e.sill) : '';
      sill.addEventListener('change', () => { begin(); if (sill.value !== '') e.sill = Number(sill.value); else delete e.sill; commit(); renderMaterials(); });
    }
    const sz = item && item.size, span = openingSpan(e, { height: e.height || GAME.levelH });
    heightField = h('div', { class: 'section' },
      real.length ? h('label', { class: 'field', title: `The ${door ? 'door' : 'window'} you'll craft for it: every one in 1.0, grouped by shape, each with who makes it and the first region where you could. The material takes its name, and "Add from this plan" in the Crafting list counts one per opening`, 'data-tip-desc': 'Sizes (blocks tall × wide) are measured in game; the rest still need measuring' }, h('span', { text: 'Item' }), pick) : null,
      h('div', { class: door ? '' : 'grid2' },
        h('label', { class: 'field', title: door ? 'How tall the doorway is' : 'How tall the window is' }, h('span', { text: door ? 'Door height' : 'Window height' }), open),
        sill ? h('label', { class: 'field', title: 'Where the window starts, above the level floor. Auto puts its top level with the top of a normal door (2.5 m), or a tall one 0.5 m up' }, h('span', { text: 'Sill at' }), sill) : null),
      h('label', { class: 'field', title: 'How tall the wall around it is, from the level floor: a door in a 3 m outbuilding on a 4 m level, or a gable window rising past a short loft' }, h('span', { text: 'Wall height' }), hs),
      h('p', { class: 'note', text: (sz ? `${item.name}: ${sz.h} blocks tall, ${sz.w} wide${S.plan.cell === 0.5 ? `, so paint it ${sz.w} squares wide` : ''}. ` : item ? `${item.name}: size not measured yet. ` : '')
        + (door ? `The doorway runs from the floor to ${fmt(span[1])} m; the wall carries on above it.` : `The window runs from ${fmt(span[0])} to ${fmt(span[1])} m; the wall carries on above and below it.`) }),
      h('button', { class: 'btn btn-sm', type: 'button', disabled: S.readOnly, text: 'Turn painted doors & windows into items', title: 'Every painted door or window named after a real one becomes that item, placed in the wall, and the wall closes up behind it. The rest stay painted', onclick: convertPaintedOpenings }));
  } else if (e.kind === 'roof') {
    const cm = S.plan.cell, opts = [['', `${fmt(cm)} m (default)`]];
    for (let v = 0.5; v <= 30; v += 0.5) opts.push([String(v), `${fmt(v)} m`]);
    const hs = h('select', { 'aria-label': 'Top at' }, ...opts.map(([v, t]) => h('option', { value: v, text: t })));
    hs.value = e.height ? String(e.height) : '';
    if (e.height && hs.value !== String(e.height)) { hs.append(h('option', { value: String(e.height), text: `${fmt(e.height)} m` })); hs.value = String(e.height); }
    hs.addEventListener('change', () => { begin(); if (hs.value) e.height = Number(hs.value); else delete e.height; commit(); renderMaterials(); });
    heightField = h('div', { class: 'section' },
      h('label', { class: 'field', title: 'The top of the roof blocks in this square, above the level floor. Where a neighbouring roof square is lower, the column runs down to meet it, so stepped roofs close up.' }, h('span', { text: 'Top at' }), hs),
      h('p', { class: 'note', text: 'One symbol per height. Over a wall in the level below, the roof fills down to the wall top, so gables close up on their own.' }));
  }
  return h('div', { class: 'mat-edit' },
    h('label', { class: 'field' }, h('span', { text: 'Name' }), name),
    h('div', { class: 'grid3' },
      h('label', { class: 'field' }, h('span', { text: 'Symbol' }), key),
      h('label', { class: 'field', style: 'grid-column: span 2' }, h('span', { text: 'Type' }), kind)),
    heightField,
    h('div', { class: 'row' }, h('label', { class: 'field' }, h('span', { text: 'Colour' }), color),
      h('span', { class: 'note', style: 'flex:1', text: KINDS[e.kind].hint }),
      (() => { const i = getHotbar().indexOf(k); return h('button', { class: 'btn btn-sm', type: 'button', text: i >= 0 ? `Unpin (key ${i + 1})` : 'Pin to hotbar', title: i >= 0 ? 'Take it off the hotbar' : 'Put it on the hotbar, in the first empty slot (1–9)', onclick: () => (i >= 0 ? unpinFromHotbar(k) : pinToHotbar(k)) }); })(),
      h('button', { class: 'btn btn-sm btn-danger', type: 'button', text: 'Remove', onclick: () => deleteMaterial(k) })));
}

// ---------------------------------------------------------------------------
// Items pane
// ---------------------------------------------------------------------------
function armItem(base, quiet, guess) {
  // Library sizes are in metres; convert to grid squares for this plan, on the 0.5 m block grid. Something
  // from the catalogue with no size yet asks for one first (unless placing with a guess).
  const cm = CM(), st = itemStep(), def = libDef(base);
  if (!quiet && !guess && def.craft && !def.sized) { askItemSize(base); return; }
  const sq = m => Math.max(st, snapStep(m / cm, st));
  S.itemDef = { ...def, mount: mountOf(def), w: sq(def.w), d: sq(def.d), lib: base };
  if (quiet) { renderOptbar(); req2d(); return; }
  setTool('item');
  renderItemsPane();
  if (window.matchMedia('(max-width: 860px)').matches) $('#panel').classList.remove('open');
}
function renderLevels() {
  const pane = $('#pane-levels');
  if (!S.plan) { pane.replaceChildren(); return; }
  const P = S.plan, L = lv(), cur = mainLevel(L);
  const eyeOpen = '<path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12Z"/><circle cx="12" cy="12" r="2.8"/>';
  const eyeShut = '<path d="M3 3l18 18"/><path d="M10.6 5.6A10 10 0 0 1 12 5.5c6.4 0 10 6.5 10 6.5a17 17 0 0 1-3.3 4M6.3 6.8C3.6 8.6 2 12 2 12s3.6 6.5 10 6.5a9.6 9.6 0 0 0 4.2-1"/>';
  const groups = levelGroups(P), col = groupColours(groups), grouped = groups.length > 1;
  const openG = lvlOpenGroups(groups);
  S.trimOpen = S.trimOpen || new Set();
  if (L !== cur) S.trimOpen.add(cur.id);                      // on a trim: its main level stays open
  const q = (S.lvlQuery || '').trim().toLowerCase();
  const hit = it => !q || it.L.name.toLowerCase().includes(q) || it.trims.some(t => t.L.name.toLowerCase().includes(q));
  const range = (a, b) => `${fmt(a)}–${fmt(b)} m`;
  const row = (l, i, extra = {}) => h('li', { class: 'lvl' + (l.hidden ? ' hiddenlvl' : '') + (extra.trim ? ' trim' : '') + (extra.n ? ' has-trims' : ''), 'aria-current': String(i === S.levelIdx), 'data-lids': [l.id, ...(extra.trim ? [] : trimsOf(l).map(t => t.id))].join(',') },
    h('button', { class: 'eye', type: 'button', title: l.hidden ? 'Show in 3D' : 'Hide in 3D', 'aria-label': `${l.hidden ? 'Show' : 'Hide'} ${l.name} in 3D`,
      onclick: () => { begin(); const v = !l.hidden; l.hidden = v; if (!extra.trim) for (const t of trimsOf(l)) t.hidden = v; commit(); renderLevels(); }, html: svg(l.hidden ? eyeShut : eyeOpen) }),
    h('button', { class: 'pick', type: 'button', onclick: () => setLevel(i) }, h('b', { text: extra.trim ? trimLabel(l) : l.name }), h('span', { text: range(l.elev, l.elev + l.height) })),
    extra.n ? h('button', { class: 'trimbtn', type: 'button', 'aria-expanded': String(!!extra.open), title: extra.open ? 'Hide its trim levels' : 'Show its trim levels',
      'data-tip-desc': 'Trim levels hold the extra pieces stacked in its squares, at the same height',
      onclick: () => { if (S.trimOpen.has(l.id)) S.trimOpen.delete(l.id); else S.trimOpen.add(l.id); renderLevels(); }, text: `+${extra.n} trim${extra.n === 1 ? '' : 's'}` }) : null);
  const items = [];
  for (const G of groups) {
    const shown = G.items.filter(hit);
    if (q && !shown.length) continue;
    const isOpen = !grouped || !!q || openG.has(G.name);
    if (grouped) {
      const all = G.items.flatMap(it => [it.L, ...it.trims.map(t => t.L)]), allHidden = all.every(l => l.hidden);
      const toggle = () => { if (openG.has(G.name)) openG.delete(G.name); else openG.add(G.name); setLvlOpenGroups(openG); renderLevels(); };
      let nameEl;
      if (S.lvlRename === G.name) {
        nameEl = h('input', { class: 'gname-in', type: 'text', value: G.name, maxlength: '40', 'aria-label': 'Group name' });
        const done = ok => {
          if (S.lvlRename !== G.name) return;
          S.lvlRename = null;
          const v = nameEl.value.trim().slice(0, 40);
          if (ok && v !== G.name) {
            begin();
            for (const it of G.items) { if (v) it.L.group = v; else delete it.L.group; }
            commit();
            if (openG.has(G.name)) { openG.delete(G.name); openG.add(v || autoGroup(G.items[0].L.name)); setLvlOpenGroups(openG); }
          }
          renderLevels();
        };
        nameEl.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); done(true); } else if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); done(false); } });
        nameEl.addEventListener('blur', () => done(true));
        setTimeout(() => { nameEl.focus(); nameEl.select(); }, 0);
      } else {
        nameEl = h('button', { class: 'gname', type: 'button', text: G.name, title: isOpen ? 'Fold this group' : 'Open this group', onclick: toggle });
      }
      items.push(h('li', { class: 'lvlgroup' + (allHidden ? ' hiddengrp' : ''), 'data-lids': all.map(l => l.id).join(',') },
        h('button', { class: 'gtoggle', type: 'button', 'aria-expanded': String(isOpen), 'aria-label': `${isOpen ? 'Fold' : 'Open'} ${G.name}`, onclick: toggle, html: svg('<path d="m6 9 6 6 6-6"/>') }),
        h('span', { class: 'gdot', style: `background:${col.get(G.name)}`, 'aria-hidden': 'true' }),
        h('span', { class: 'gtext' }, nameEl, h('span', { class: 'grange', text: `${range(G.lo, G.hi)} · ${G.items.length} level${G.items.length === 1 ? '' : 's'}` })),
        h('button', { class: 'iconbtn sm', type: 'button', title: allHidden ? 'Show the whole group in 3D' : 'Hide the whole group in 3D', 'aria-label': `${allHidden ? 'Show' : 'Hide'} ${G.name} in 3D`,
          onclick: () => { begin(); for (const l of all) l.hidden = !allHidden; commit(); renderLevels(); }, html: svg(allHidden ? eyeShut : eyeOpen) }),
        h('button', { class: 'iconbtn sm', type: 'button', title: 'Rename this group', 'aria-label': `Rename ${G.name}`, disabled: S.readOnly,
          onclick: () => { S.lvlRename = G.name; renderLevels(); }, html: svg('<path d="M4 20l1-4.5L15.5 5 19 8.5 8.5 19Z"/>') })));
    }
    if (!isOpen) continue;
    for (const it of shown) {
      const tOpen = !!q || S.trimOpen.has(it.L.id);
      items.push(row(it.L, it.i, { n: it.trims.length, open: tOpen }));
      if (tOpen) for (const t of it.trims) items.push(row(t.L, t.i, { trim: true }));
    }
  }
  const find = h('input', { class: 'lvlfind', type: 'text', placeholder: 'Find a level', 'aria-label': 'Find a level', value: S.lvlQuery || '' });
  find.addEventListener('input', () => { S.lvlQuery = find.value; renderLevels(); const f = $('#pane-levels .lvlfind'); if (f) { f.focus(); f.setSelectionRange(f.value.length, f.value.length); } });
  const list = h('ul', { class: 'lvllist' }, ...(items.length ? items : [h('li', { class: 'note', text: 'No levels match that.' })]));
  const name = h('input', { type: 'text', value: L.name, maxlength: '80', 'aria-label': 'Level name' });
  name.addEventListener('input', () => { liveBegin(); L.name = name.value.slice(0, 80) || 'Level'; markDirty(); updateStatus(); });
  name.addEventListener('change', () => { liveCommit(); renderLevels(); });
  const elev = h('input', { type: 'number', value: String(L.elev), step: '0.5', min: '-60', max: '400', 'aria-label': 'Base height in metres' });
  const height = h('input', { type: 'number', value: String(L.height), step: '0.5', min: '0.5', max: '40', 'aria-label': 'Level height in metres' });
  const apply = () => {
    begin();
    L.elev = blocksNum(elev.value, L.elev, -60, 400); L.height = blocksNum(height.value, L.height, 0.5, 40);   // whole blocks
    P.levels.sort((a, b) => a.elev - b.elev); S.levelIdx = P.levels.indexOf(L);
    commit(); renderLevels(); updateStatus();
  };
  elev.addEventListener('change', apply); height.addEventListener('change', apply);
  pane.replaceChildren(
    h('div', { class: 'pane-head' }, h('h3', { text: 'Levels' }), h('span', { class: 'note', text: '[ and ] switch levels' })),
    ...(P.levels.length > 8 ? [find] : []),
    list,
    h('div', { class: 'btnrow' },
      h('button', { class: 'btn btn-sm', type: 'button', text: 'Add level on top', onclick: () => addLevel('top') }),
      h('button', { class: 'btn btn-sm', type: 'button', text: 'Copy this level up', onclick: duplicateLevel }),
      h('button', { class: 'btn btn-sm', type: 'button', text: 'Add basement', onclick: () => addLevel('below') })),
    h('div', { class: 'section callout' },
      h('h4', { text: 'This level' }),
      h('label', { class: 'field' }, h('span', { text: 'Name' }), name),
      groupField(L),
      h('div', { class: 'grid2' }, h('label', { class: 'field' }, h('span', { text: 'Base (m)' }), elev), h('label', { class: 'field' }, h('span', { text: 'Height (m)' }), height)),
      h('p', { class: 'note', text: 'Walls on this level rise to its full height in 3D. A 4 m storey matches one 4M wall piece.' }),
      h('div', null, h('button', { class: 'btn btn-sm btn-danger', type: 'button', text: 'Delete level', onclick: deleteLevel }))),
  );
}
