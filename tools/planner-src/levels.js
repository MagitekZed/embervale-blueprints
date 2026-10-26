// ---------------------------------------------------------------------------
// Level groups, trims and the height strip (planner v45).
// A trim level holds a square's extra pieces at the same height as its main level (generators call it
// '<id>_t1' and on, or '… · trim 1'). It folds under that level in the lists, the level keys step over it,
// and its pieces show as a dot in the corner of the main level's squares.
// Levels sit in named groups: a level's own `group`, else its main level's, else the part of its name
// before a colon ("Isle: the crown" → Isle, "Grounds at +4 m: paths" → Grounds; a site plan's merged levels,
// named by their height, → Shared levels), else Other.
// ---------------------------------------------------------------------------
function trimParent(L, P = S.plan) {
  if (!L || !P) return null;
  const same = l => l !== L && l.elev === L.elev && l.height === L.height;
  const m = /^(.+)_t\d+$/.exec(L.id);
  if (m) { const p = P.levels.find(l => l.id === m[1] && same(l)); if (p) return p; }
  const n = /^(.*) · trim \d+$/.exec(L.name);
  if (n) { const p = P.levels.find(l => l.name === n[1] && same(l)); if (p) return p; }
  return null;
}
const mainLevel = L => trimParent(L) || L;
// A trim level's short name in the lists: "trim 2" (from its id, since long names are cut short).
function trimLabel(L) { const m = /_t(\d+)$/.exec(L.id) || / · trim (\d+)$/.exec(L.name); return m ? 'trim ' + m[1] : L.name; }
function trimsOf(L, P = S.plan) { return P ? P.levels.filter(l => l !== L && l.elev === L.elev && trimParent(l, P) === L) : []; }
function autoGroup(name) {
  const i = (name || '').indexOf(':');
  if (i <= 0) return 'Other';
  const g = name.slice(0, i).replace(/\s+at\s+.*$/i, '').trim();
  return /^[+\-−]?\d/.test(g) ? 'Shared levels' : g || 'Other';   // ("+20 m, 2 m tall: Manor, Square": a site plan's merged level)
}
function levelGroup(L, P = S.plan) { const m = trimParent(L, P) || L; return (m.group && m.group.trim()) || autoGroup(m.name); }
// [{ name, items: [{ L, i, trims: [{ L, i }] }], lo, hi, top }]: groups top first (by their highest floor),
// and in each, its main levels highest first with their trims.
function levelGroups(P = S.plan) {
  const by = new Map(), parent = new Map();
  P.levels.forEach(L => parent.set(L, trimParent(L, P)));
  P.levels.forEach((L, i) => {
    if (parent.get(L)) return;
    const g = levelGroup(L, P);
    if (!by.has(g)) by.set(g, { name: g, items: [], lo: Infinity, hi: -Infinity, top: -Infinity });
    const G = by.get(g);
    G.items.push({ L, i, trims: [] });
    G.lo = Math.min(G.lo, L.elev); G.hi = Math.max(G.hi, L.elev + L.height); G.top = Math.max(G.top, L.elev);
  });
  P.levels.forEach((L, i) => {
    const p = parent.get(L);
    if (!p) return;
    const it = (by.get(levelGroup(p, P)) || { items: [] }).items.find(x => x.L === p);
    if (it) it.trims.push({ L, i });
  });
  const out = [...by.values()];
  for (const G of out) G.items.sort((a, b) => b.i - a.i);
  return out.sort((a, b) => b.top - a.top || b.hi - a.hi);
}
// A colour per group, for the strip's ticks and the Levels tab's group headers.
const GROUP_COLOURS = ['#c98a3b', '#5b8fc7', '#6aa56b', '#a873b8', '#c46a6a', '#4aa3a0', '#b5a03f', '#8a8f99'];
function groupColours(groups) { const m = new Map(); groups.forEach((G, n) => m.set(G.name, GROUP_COLOURS[n % GROUP_COLOURS.length])); return m; }

// The next main level above (dir 1) or below (-1) the current one, skipping trims: its index, or -1.
function nextMain(dir) {
  const P = S.plan;
  if (!P) return -1;
  for (let j = P.levels.indexOf(mainLevel(lv())) + dir; j >= 0 && j < P.levels.length; j += dir) if (!trimParent(P.levels[j], P)) return j;
  return -1;
}
function stepLevel(dir) { const j = nextMain(dir); if (j < 0) return false; setLevel(j); return true; }

// A trim level of L's main level with square (x, y) free, made if there's none (after its last trim, with the
// same height and elevation): where a run that can't share the square goes, as the generators do it.
function trimLevelFor(L, x, y) {
  const P = S.plan, main = mainLevel(L), fam = [main, ...trimsOf(main)];
  const free = fam.find(l => l !== L && l.grid[y][x] === ' ');
  if (free) return free;
  if (P.levels.length >= MAX_LEVELS) return null;
  const n = Math.max(0, ...trimsOf(main).map(t => Number((/_t(\d+)$/.exec(t.id) || [0, 0])[1]))) + 1;
  let id = `${main.id}_t${n}`;
  while (P.levels.some(l => l.id === id)) id += 'x';
  const T = { id, name: `${main.name.slice(0, 66)} · trim ${n}`, elev: main.elev, height: main.height, hidden: !!main.hidden, grid: blankGrid(P.w, P.h) };
  const at = Math.max(...fam.map(l => P.levels.indexOf(l))) + 1;
  P.levels.splice(at, 0, T);
  if (at <= S.levelIdx) S.levelIdx++;                          // (the current level stays the same level)
  planVer++;
  return T;
}
// Take [z0, z1) out of the middle of the run e in square (x, y) of level L: the part below stays, the part
// above moves to a trim level.
function splitRun(L, x, y, e, b0, b1, z0, z1) {
  const T = trimLevelFor(L, x, y);
  if (!T) return false;
  const was = L.grid[y][x], lo = runSymbol(L, e, b0, z0, e.under || null);
  if (!lo) return false;
  setCell(L, x, y, lo);                                        // (in place before the next size is made, so tidying sizes no one uses keeps it)
  const hi = runSymbol(T, e, z1, b1, null);
  if (!hi) { setCell(L, x, y, was); return false; }
  setCell(T, x, y, hi);
  return true;
}
// Which groups are open in the Levels tab, kept per plan in this browser. Big plans start with only the
// current level's group open.
function lvlOpenGroups(groups) {
  const key = 'lvlOpen:' + S.planId;
  let v = LS.get(key, null);
  if (!Array.isArray(v)) {
    const cur = levelGroup(lv());
    v = S.plan.levels.length > 24 ? [cur] : groups.map(G => G.name);
  }
  return new Set(v);
}
function setLvlOpenGroups(set) { LS.set('lvlOpen:' + S.planId, [...set]); }

// ---------------------------------------------------------------------------
// The height strip: the plan's whole height to scale beside the 2D view. A tick for each floor (levels on
// the same floor share one, with a count), coloured by group; the current level as a band; the ground; the
// altar's build volume; the current layer in Layers mode. Click a tick for its level, drag in Layers mode
// to move through the layers, scroll to step.
// ---------------------------------------------------------------------------
let stripKey = '';
function renderStrip(force) {
  const box = $('#hstrip');
  if (!box) return;
  const P = S.plan, Hh = box.clientHeight;
  if (!P || !P.levels.length || Hh < 80 || box.offsetParent === null) { if (!P) { box.replaceChildren(); stripKey = ''; } return; }
  const lay = layerOn(), k = lay ? curLayer() : null, L = lv();
  const key = [S.planId, Hh, S.levelIdx, k, P.altar, P.levels.map(l => `${l.id}|${l.elev}|${l.height}|${l.group || ''}|${l.hidden ? 1 : 0}|${l.name}`).join(';'),
    P.items.filter(i => i.type === 'altar').map(i => `${i.level}${i.x}${i.y}`).join()].join('#');
  if (!force && key === stripKey) return;
  stripKey = key;
  const groups = levelGroups(P), col = groupColours(groups);
  const lo = Math.min(...P.levels.map(l => l.elev - FLOOR_T)), hi = Math.max(...P.levels.map(l => l.elev + l.height));
  const pad = 12, span = Math.max(1, hi - lo), y = z => pad + (hi - z) / span * (Hh - 2 * pad);
  const kids = [];
  // the altar's build volume, as the planner draws it (a cube centred on the altar)
  const lvById = new Map(P.levels.map(l => [l.id, l]));
  for (const it of P.items) {
    if (it.type !== 'altar' || !lvById.has(it.level)) continue;
    const el = lvById.get(it.level).elev, a = P.altar || 40;
    const t = Math.min(hi, el + a / 2), b = Math.max(lo, el - a / 2);
    if (t > b) kids.push(h('div', { class: 'hs-altar', style: `top:${y(t)}px;height:${Math.max(2, y(b) - y(t))}px`, title: `The Flame Altar's build volume: ${fmt(el - a / 2)} to ${fmt(el + a / 2)} m` }));
  }
  // the current level, floor to top
  if (L && !lay) kids.push(h('div', { class: 'hs-band', style: `top:${y(L.elev + L.height)}px;height:${Math.max(3, y(L.elev) - y(L.elev + L.height))}px` }));
  // the height scale, in a step that keeps its labels apart
  const pxm = (Hh - 2 * pad) / span, step = [1, 2, 5, 10, 20, 50, 100].find(s => s * pxm >= 34) || 100;
  for (let z = Math.ceil(lo / step) * step; z <= hi; z += step) kids.push(h('span', { class: 'hs-lab', style: `top:${y(z)}px`, text: (z < 0 ? '−' : '') + Math.abs(z) }));
  if (lo < 0 && hi > 0) kids.push(h('div', { class: 'hs-ground', style: `top:${y(0)}px`, title: 'The ground, 0 m' }));
  // floors: main levels by height, those within a few pixels of each other sharing a tick
  const mains = groups.flatMap(G => G.items).sort((a, b) => b.L.elev - a.L.elev || b.i - a.i);
  const clusters = [];
  for (const it of mains) {
    const c = clusters[clusters.length - 1];
    if (c && y(it.L.elev) - c.y0 < 6) c.items.push(it); else clusters.push({ y0: y(it.L.elev), items: [it] });
  }
  const curMain = mainLevel(L);
  for (const c of clusters) {
    const its = c.items, one = its.length === 1, here = its.some(it => it.L === curMain);
    const zs = [...new Set(its.map(it => it.L.elev))];
    const title = one ? its[0].L.name : `${its.length} levels at ${zs.map(fmt).join(', ')} m`;
    const desc = one ? `${fmt(its[0].L.elev)} to ${fmt(its[0].L.elev + its[0].L.height)} m` : its.map(it => it.L.name).join(' · ');
    const allHidden = its.every(it => it.L.hidden);
    kids.push(h('button', {
      class: 'hs-tick' + (here ? ' cur' : '') + (allHidden ? ' off' : ''), type: 'button', style: `top:${c.y0}px`, title, 'data-tip-desc': desc, 'data-lids': its.map(it => it.L.id).join(','),
      'aria-label': title, onclick: e => { e.stopPropagation(); if (one) { if (lay) setLayerMode(false); setLevel(its[0].i); } else openStripPop(its, e.currentTarget); },
    }, h('i', { style: `background:${col.get(levelGroup(its[0].L)) || T.muted}` }), one ? null : h('b', { text: String(its.length) })));
  }
  // the current layer
  if (lay) { const [z0] = layerZ(k); kids.push(h('div', { class: 'hs-layer', style: `top:${y(z0 + layerSize() / 2)}px`, title: `${layerName(k)} · ${fmt(z0)} m` }, h('span', { text: fmt(z0) }))); }
  box.replaceChildren(...kids);
  box.dataset.lo = lo; box.dataset.hi = hi; box.dataset.pad = pad;
}
function stripZ(e) {
  const box = $('#hstrip'), r = box.getBoundingClientRect(), lo = +box.dataset.lo, hi = +box.dataset.hi, pad = +box.dataset.pad;
  return hi - (e.clientY - r.top - pad) / Math.max(1, r.height - 2 * pad) * (hi - lo);
}
// Several levels on one tick: a short list to pick from, beside it.
function openStripPop(its, anchor) {
  closeLevelPop(); hideTip(true);
  const rows = its.map(it => h('button', {
    class: 'lp-row' + (isUnder(it.L) ? ' lp-under' : '') + (it.L.hidden ? ' lp-hidden' : ''), type: 'button', role: 'option', 'aria-selected': String(it.L === mainLevel(lv())),
    onclick: () => { if (layerOn()) setLayerMode(false); setLevel(it.i); closeLevelPop(true); },
  }, h('span', { class: 'lp-name', text: it.L.name }), h('span', { class: 'lp-m', text: `${fmt(it.L.elev)} to ${fmt(it.L.elev + it.L.height)} m` })));
  lvlPop = h('div', { class: 'lvlpop', role: 'listbox', 'aria-label': 'Levels on this floor' }, ...rows);
  document.body.append(lvlPop);
  const r = anchor.getBoundingClientRect();
  lvlPop.style.left = (r.right + 6) + 'px';
  lvlPop.style.top = clamp(r.top - 12, 8, innerHeight - lvlPop.offsetHeight - 8) + 'px';
  lvlPop.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); closeLevelPop(true); } else e.stopPropagation(); });
  setTimeout(() => document.addEventListener('pointerdown', levelPopOutside, true), 0);
  const f = lvlPop.querySelector('[aria-selected="true"]') || lvlPop.querySelector('button');
  if (f) f.focus();
}
function bindStrip() {
  const box = $('#hstrip');
  if (!box) return;
  let drag = false;
  const toLayer = e => { if (!S.plan || !layerOn()) return; const k = Math.floor(stripZ(e) / layerSize() + 1e-6); if (k !== curLayer()) setLayer(k); };
  box.addEventListener('pointerdown', e => {
    if (e.target.closest('.hs-tick') || !layerOn()) return;
    drag = true; try { box.setPointerCapture(e.pointerId); } catch { /* not a live pointer */ }
    toLayer(e); e.preventDefault();
  });
  box.addEventListener('pointermove', e => { if (drag) toLayer(e); });
  const end = () => { drag = false; };
  box.addEventListener('pointerup', end); box.addEventListener('pointercancel', end);
  box.addEventListener('wheel', e => {
    if (!S.plan) return;
    e.preventDefault();
    const dir = e.deltaY < 0 ? 1 : -1;
    if (layerOn()) stepLayer(dir); else stepLevel(dir);
  }, { passive: false });
  new ResizeObserver(() => renderStrip()).observe(box);
}

// ---------------------------------------------------------------------------
// The plan's limits: palette symbols, levels and the stored size, as bars in the Plan tab, and a chip in the
// status bar once one is past 90%.
// ---------------------------------------------------------------------------
const DOC_MAX = 256 * 1024;                                    // the database's limit on one document
const STORED = new Map();                                      // plan id -> its stored document (packed), as last seen or saved
const storedSize = (() => { const memo = new WeakMap(); return d => { if (!d || typeof d !== 'object') return 0; if (!memo.has(d)) memo.set(d, JSON.stringify(d).length); return memo.get(d); }; })();
function planLimits() {
  const P = S.plan;
  if (!P) return [];
  const nTrim = P.levels.filter(l => trimParent(l, P)).length;
  const unused = typeof unusedMaterials === 'function' ? unusedMaterials(P, computeCounts()).length : 0;
  const bytes = storedSize(STORED.get(S.planId));
  const out = [
    { id: 'mat', label: 'Material slots', n: Object.keys(P.palette).length, max: MAX_SYMBOLS, note: unused ? `${unused} unused: Tidy away (Materials tab) frees them` : '' },
    { id: 'lvl', label: 'Levels', n: P.levels.length, max: MAX_LEVELS, note: nTrim ? `${nTrim} of them trims` : '' },
  ];
  if (bytes) out.push({ id: 'size', label: 'Stored size', n: bytes, max: DOC_MAX, kb: true, note: STORED.get(S.planId) && STORED.get(S.planId).zip ? 'packed, as last saved' : 'as last saved' });
  for (const r of out) r.frac = r.n / r.max;
  return out;
}
const limitText = r => r.kb ? `${Math.round(r.n / 1024)} KB of ${Math.round(r.max / 1024)} KB` : `${r.n} of ${r.max}`;
function limitsSection() {
  const rows = planLimits();
  if (!rows.length) return null;
  return h('div', { class: 'section', id: 'limitsBox' }, h('h4', { text: 'Plan limits' }),
    ...rows.map(r => h('div', { class: 'lim', 'data-state': r.frac >= 0.95 ? 'bad' : r.frac >= 0.8 ? 'warn' : 'ok' },
      h('div', { class: 'lim-top' }, h('span', { text: r.label }), h('span', { class: 'mono', text: limitText(r) })),
      h('div', { class: 'lim-bar', role: 'img', 'aria-label': `${r.label}: ${Math.round(r.frac * 100)}% used` }, h('i', { style: `width:${Math.min(100, r.frac * 100).toFixed(1)}%` })),
      r.note ? h('p', { class: 'note', text: r.note }) : null)));
}
function updateLimitChip() {
  const chip = $('#limitChip');
  if (!chip) return;
  const over = planLimits().filter(r => r.frac >= 0.9).sort((a, b) => b.frac - a.frac);
  chip.hidden = !over.length;
  if (!over.length) return;
  const r = over[0];
  chip.dataset.state = r.frac >= 0.95 ? 'bad' : 'warn';
  chip.querySelector('span').textContent = `${r.label} ${Math.round(r.frac * 100)}% full`;
  chip.dataset.tip = over.map(q => `${q.label}: ${limitText(q)}`).join(' · ');
}
