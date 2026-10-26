
// ---------------------------------------------------------------------------
// Terrain: ground height per square, in whole blocks (one square's size: 0.5 m or 1 m).
// Stored as rows of characters, height = (code − 79) × cell metres; a space is 0 m. Below the
// ground every empty square is earth; anything built or placed there is dug out.
// ---------------------------------------------------------------------------
const TERRAIN_ZERO = 79;                                       // 'O'
const terrainLimits = cell => [(33 - TERRAIN_ZERO) * cell, (126 - TERRAIN_ZERO) * cell];
function terrainFromDoc(t, p) {
  const g = Array.from({ length: p.h }, () => new Array(p.w).fill(0));
  if (!t || !Array.isArray(t.rows)) return g;
  // rows of runs like the level rows (enc 2, since planner v36: a lake bed is one run per row), or one
  // character per square (plans saved before)
  const ox = clampInt(t.ox, 0, p.w, 0), oy = clampInt(t.oy, 0, p.h, 0), bad = { n: 0 };
  const chars = t.enc === 2 ? codeRowsToGrid(t.rows, p.w, p.h, ox, oy, bad) : rowsToGrid(t.rows, p.w, p.h, ox, oy);
  if (bad.n) p.readProblems = (p.readProblems || 0) + bad.n;
  for (let y = 0; y < p.h; y++) for (let x = 0; x < p.w; x++) {
    const c = chars[y][x];
    if (c !== ' ') g[y][x] = (c.charCodeAt(0) - TERRAIN_ZERO) * p.cell;
  }
  return g;
}
function terrainToDoc(p) {
  if (!terrainOn(p)) return null;
  const chars = p.terrain.map(row => row.map(v => {
    const k = clamp(Math.round(v / p.cell), 33 - TERRAIN_ZERO, 126 - TERRAIN_ZERO);
    return k === 0 ? ' ' : String.fromCharCode(TERRAIN_ZERO + k);
  }));
  const c = cropCells(chars);
  return { enc: 2, ox: c.ox, oy: c.oy, rows: c.rows.map(encodeRow) };
}
const terrainOn = p => !!p && !!p.terrain && p.terrain.some(row => row.some(v => v !== 0));
const groundAt = (x, y) => (S.plan && S.plan.terrain && inB(x, y) ? S.plan.terrain[y][x] : 0);
function terrainRange(p) {
  let lo = 0, hi = 0;
  for (const row of p.terrain) for (const v of row) { if (v < lo) lo = v; if (v > hi) hi = v; }
  return [lo, hi];
}

// --- the ground tool --------------------------------------------------------
const TERRAIN_MODES = [
  ['raise', 'Raise', 'Each stroke raises the ground one block. Right-drag lowers'],
  ['lower', 'Lower', 'Each stroke lowers the ground one block. Right-drag raises'],
  ['flatten', 'Level', 'Level the ground to the height where the stroke starts'],
  ['set', 'Set', 'Set the ground to an exact height'],
];
function brushCells(cx, cy) {
  const n = S.terrainSize, r = (n - 1) / 2, out = [];
  for (let dy = -Math.floor(r); dy <= Math.ceil(r); dy++) for (let dx = -Math.floor(r); dx <= Math.ceil(r); dx++) {
    if (S.terrainRound && n > 2 && Math.hypot(dx, dy) > n / 2) continue;
    out.push([cx + dx, cy + dy]);
  }
  return out;
}
function terrainDown(cx, cy, opposite) {
  if (!inB(cx, cy)) return null;
  begin();
  const g = { type: 'terrain', done: new Set(), ref: groundAt(cx, cy), opposite, last: [cx, cy] };
  terrainApply(g, cx, cy);
  return g;
}
function terrainMove(g, cx, cy) {
  if (cx === g.last[0] && cy === g.last[1]) return;
  for (const [x, y] of lineCells(g.last[0], g.last[1], cx, cy)) terrainApply(g, x, y);
  g.last = [cx, cy];
}
function terrainApply(g, cx, cy) {
  const P = S.plan, step = P.cell, [lo, hi] = terrainLimits(step);
  let mode = S.terrainMode;
  if (g.opposite) mode = mode === 'lower' ? 'raise' : mode === 'raise' ? 'lower' : mode;
  for (const [bx, by] of brushCells(cx, cy)) for (const [x, y] of mirrorPts(bx, by)) {
    if (!inB(x, y)) continue;
    const k = y * P.w + x;
    if ((mode === 'raise' || mode === 'lower') && g.done.has(k)) continue;
    g.done.add(k);
    const v = P.terrain[y][x];
    const nv = mode === 'raise' ? v + step : mode === 'lower' ? v - step : mode === 'flatten' ? g.ref : Math.round(S.terrainSet / step) * step;
    P.terrain[y][x] = clamp(Math.round(nv / step) * step, lo, hi);
  }
  mark3d(); req2d();
}
function terrainControls() {
  const seg = h('div', { class: 'seg', role: 'group', 'aria-label': 'Ground tool' });
  for (const [v, lab, tip] of TERRAIN_MODES) seg.append(h('button', { type: 'button', 'aria-pressed': String(S.terrainMode === v), text: lab, title: tip, onclick: () => { S.terrainMode = v; renderOptbar(); } }));
  const size = h('select', { 'aria-label': 'Brush size', title: 'Brush size' }, ...[1, 3, 5, 9, 15].map(n => h('option', { value: String(n), text: `${metres(n)} m brush` })));
  size.value = String(S.terrainSize);
  size.addEventListener('change', () => { S.terrainSize = Number(size.value); req2d(); });
  const shape = h('div', { class: 'seg', role: 'group', 'aria-label': 'Brush shape' });
  for (const [v, lab] of [[false, 'Box'], [true, 'Round']]) shape.append(h('button', { type: 'button', 'aria-pressed': String(S.terrainRound === v), text: lab, onclick: () => { S.terrainRound = v; renderOptbar(); } }));
  const kids = [seg, size, shape];
  if (S.terrainMode === 'set') {
    const cm = S.plan.cell, [lo, hi] = terrainLimits(cm);
    const inp = h('input', { type: 'number', value: String(S.terrainSet), step: String(cm), min: String(lo), max: String(hi), 'aria-label': 'Ground height in metres', title: 'Ground height in metres', style: 'width:5.5em' });
    inp.addEventListener('change', () => { S.terrainSet = clamp(Math.round(Number(inp.value) / cm) * cm || 0, lo, hi); inp.value = String(S.terrainSet); });
    kids.push(h('label', { class: 'inline' }, 'to', inp, 'm'));
  }
  kids.push(h('span', { class: 'hint', id: 'groundOut', text: `Whole blocks of ${fmt(S.plan.cell)} m` }));
  if (terrainOn(S.plan)) kids.push(h('button', { class: 'btn btn-sm', type: 'button', text: 'Flatten all', title: 'Put all the ground back to 0 m (you can undo this)', onclick: () => { begin(); for (const row of S.plan.terrain) row.fill(0); commit(); mark3d(); req2d(); renderOptbar(); } }));
  return kids;
}
function updateGroundOut(cx, cy) {
  const o = $('#groundOut');
  if (o && S.tool === 'terrain') o.textContent = inB(cx, cy) ? `Ground here: ${fmt(groundAt(cx, cy))} m` : `Whole blocks of ${fmt(S.plan.cell)} m`;
}

// --- 2D ----------------------------------------------------------------------
// Soil wherever the ground stands above this level's floor; a faint hatch where it falls away
// below the floor (on levels the ground reaches), so you can see what you're building on.
function drawGround(g, cam, L, x0, x1, y0, y1) {
  const P = S.plan, s = cam.s;
  if (!terrainOn(P)) { if (isUnder(L)) drawSoil(g, cam, x0, x1, y0, y1); return; }
  const [, hi] = terrainRange(P), touches = L.elev <= hi + 0.01;
  g.fillStyle = hexA(SOIL, 0.34);
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) if (P.terrain[y][x] > L.elev + 0.01) g.fillRect(cam.ox + x * s, cam.oy + y * s, s + 0.5, s + 0.5);
  if (touches && s >= 5) {
    g.strokeStyle = hexA(T.muted, 0.28); g.lineWidth = 1; g.beginPath();
    for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) if (P.terrain[y][x] < L.elev - 0.01) {
      const px = cam.ox + x * s, py = cam.oy + y * s;
      g.moveTo(px, py + s); g.lineTo(px + s, py);
    }
    g.stroke();
  }
}
// With the ground tool: heights as a tint (green up, blue-brown down), contour lines, and numbers up close.
function drawTerrainMap(g, cam, x0, x1, y0, y1) {
  const P = S.plan, s = cam.s, [lo, hi] = terrainRange(P), t = P.terrain;
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
    const v = t[y][x];
    if (v === 0) continue;
    const f = v > 0 ? 0.18 + 0.5 * v / Math.max(hi, 0.5) : 0.18 + 0.5 * v / Math.min(lo, -0.5);
    g.fillStyle = v > 0 ? hexA('#5f8f3a', f) : hexA('#4f6f8f', f);
    g.fillRect(cam.ox + x * s, cam.oy + y * s, s + 0.5, s + 0.5);
  }
  if (s >= 4) {
    g.strokeStyle = hexA(T.ink, 0.45); g.lineWidth = 1; g.beginPath();
    for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
      const v = t[y][x], px = cam.ox + x * s, py = cam.oy + y * s;
      if (x + 1 < P.w && t[y][x + 1] !== v) { g.moveTo(px + s, py); g.lineTo(px + s, py + s); }
      if (y + 1 < P.h && t[y + 1][x] !== v) { g.moveTo(px, py + s); g.lineTo(px + s, py + s); }
    }
    g.stroke();
  }
  if (s >= 22) {
    g.fillStyle = hexA(T.ink, 0.75); g.font = `600 ${Math.round(s * 0.32)}px ${FONT_MONO}`; g.textAlign = 'center'; g.textBaseline = 'middle';
    for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) if (t[y][x] !== 0) g.fillText(fmt(t[y][x]), cam.ox + (x + 0.5) * s, cam.oy + (y + 0.5) * s);
  }
}
function drawTerrainBrush(g, cam) {
  if (S.tool !== 'terrain' || !S.hover || !S.hoverIn) return;
  const s = cam.s;
  g.strokeStyle = T.accent; g.lineWidth = 1.5;
  for (const [bx, by] of brushCells(S.hover[0], S.hover[1])) for (const [x, y] of mirrorPts(bx, by)) if (inB(x, y)) g.strokeRect(cam.ox + x * s + 0.75, cam.oy + y * s + 0.75, s - 1.5, s - 1.5);
}

// --- grid size and canvas changes ---------------------------------------------
function terrainRescale(P, to) {
  const t = P.terrain, [lo, hi] = terrainLimits(to);
  if (to === 0.5) {
    const g = Array.from({ length: P.h * 2 }, (_, y) => Array.from({ length: P.w * 2 }, (_, x) => t[y >> 1][x >> 1]));
    P.terrain = g;
  } else {
    const nw = Math.ceil(P.w / 2), nh = Math.ceil(P.h / 2);
    P.terrain = Array.from({ length: nh }, (_, Y) => Array.from({ length: nw }, (_, X) => {
      let s = 0, n = 0;
      for (const [dx, dy] of [[0, 0], [1, 0], [0, 1], [1, 1]]) { const x = 2 * X + dx, y = 2 * Y + dy; if (x < P.w && y < P.h) { s += t[y][x]; n++; } }
      return clamp(Math.round(s / n / to) * to, lo, hi);
    }));
  }
}
function terrainShift(P, nw, nh, dx, dy) {
  const t = P.terrain;
  P.terrain = Array.from({ length: nh }, (_, Y) => Array.from({ length: nw }, (_, X) => {
    const x = X - dx, y = Y - dy;
    return x >= 0 && y >= 0 && x < P.w && y < P.h ? t[y][x] : 0;
  }));
}
