// ---------------------------------------------------------------------------
// The Wall tool (W) and the Replace tool (Q), planner v46.
// ---------------------------------------------------------------------------
// A palette symbol for an entry (found, or made if there's room). Entries match on material (name and colour,
// whatever their tag), kind, height, raise, floor underneath and opening.
function samePiece(a, b) {
  return a.kind === b.kind && a.color === b.color && matName(a.name) === matName(b.name)
    && (a.height || 0) === (b.height || 0) && (a.base || 0) === (b.base || 0) && (a.under || null) === (b.under || null)
    && (a.opening || 0) === (b.opening || 0) && (a.sill == null ? null : a.sill) === (b.sill == null ? null : b.sill);
}
function entryKey(want) {
  const pal = S.plan.palette;
  for (const [k, e] of Object.entries(pal)) if (samePiece(e, want)) return k;
  if (Object.keys(pal).length >= MAX_SYMBOLS) return null;
  const k = nextFreeKey();
  if (!k) return null;
  pal[k] = want;
  return k;
}
// Piece e made of material m instead: its height, raise and floor kept.
const swapEntry = (e, m) => entryKey({ ...clone(e), name: matName(m.name).slice(0, 40), color: m.color });

// ---------------------------------------------------------------------------
// Wall: drag a straight run, or click corner to corner (double-click, Enter or right-click finishes; Esc
// cancels; Backspace takes back a corner). Runs lock to 0°, 45° and 90°. The wall is the brush's material, as
// thick as set, centred on the line or to one side of it (F switches), at a set height and raise. Corners
// between runs at right angles are filled square.
// ---------------------------------------------------------------------------
S.wallOpt = Object.assign({ thick: 2, height: 0, base: 0, side: 0 }, LS.get('wallOpt', {}) || {});
const saveWallOpt = () => LS.set('wallOpt', S.wallOpt);
const WALL_SIDES = [[0, 'Centred'], [1, 'Left'], [-1, 'Right']];
function wallSquares(m) { return Math.max(1, Math.round(m / CM())); }
// The squares of a wall along the corner points pts.
function wallCells(pts, closed) {
  const P = S.plan, out = new Map(), T = wallSquares(S.wallOpt.thick), side = S.wallOpt.side;
  const add = (x, y) => { if (inB(x, y)) out.set(y * P.w + x, [x, y]); };
  const offs = t => side === 0 ? Array.from({ length: t }, (_, i) => i - Math.floor((t - 1) / 2)) : Array.from({ length: t }, (_, i) => side > 0 ? -i : i);
  const segs = [];
  for (let i = 0; i + 1 < pts.length; i++) segs.push([pts[i], pts[i + 1]]);
  if (closed && pts.length > 2) segs.push([pts[pts.length - 1], pts[0]]);
  if (pts.length === 1) segs.push([pts[0], pts[0]]);
  const dirs = segs.map(([a, b]) => [Math.sign(b[0] - a[0]), Math.sign(b[1] - a[1])]);
  segs.forEach(([a, b], i) => {
    let [dx, dy] = dirs[i];
    if (!dx && !dy) dx = 1;                                    // a single click: a stub along x
    const nx = -dy, ny = dx, diag = dx && dy;
    const K = offs(diag ? Math.max(1, Math.round(T / Math.SQRT2)) : T);
    for (const [x, y] of lineCells(a[0], a[1], b[0], b[1])) for (const k of K) {
      add(x + k * nx, y + k * ny);
      if (diag) add(x + k * nx + dx, y + k * ny);              // (fills the gaps a diagonal leaves)
    }
  });
  // square corners where runs meet at right angles
  const joints = [];
  for (let i = 0; i + 1 < segs.length; i++) joints.push([segs[i][1], dirs[i], dirs[i + 1]]);
  if (closed && segs.length > 2) joints.push([segs[segs.length - 1][1], dirs[segs.length - 1], dirs[0]]);
  const K = offs(T);
  for (const [J, d1, d2] of joints) {
    if (d1[0] * d2[0] + d1[1] * d2[1] !== 0 || (d1[0] && d1[1]) || (d2[0] && d2[1])) continue;
    const n1 = [-d1[1], d1[0]], n2 = [-d2[1], d2[0]];
    for (const a of K) for (const b of K) add(J[0] + a * n1[0] + b * n2[0], J[1] + a * n1[1] + b * n2[1]);
  }
  return [...out.values()];
}
// The symbol for the wall in square (x, y) on level L: the brush's material at the tool's height and raise,
// over whatever floor is there when it's raised.
function wallSym(L, x, y) {
  const pal = S.plan.palette, m = pal[S.brush], o = S.wallOpt, cur = pal[L.grid[y][x]];
  const want = { name: matName(m.name).slice(0, 40), kind: 'wall', color: m.color };
  if (o.height > 0) want.height = o.height;
  if (o.base > 0) want.base = o.base;
  if (o.base > 0 && isFloorKind(cur)) want.under = L.grid[y][x];
  return entryKey(want);
}
function wallReady() {
  const m = S.plan.palette[S.brush];
  if (m && ['wall', 'block', 'floor', 'roof'].includes(m.kind)) return true;   // (only its material is used)
  toast('The Wall tool builds in the current material: pick a block, floor or roof material first (1–9, or the Materials tab).');
  return false;
}
function wallPreview() {
  const c = S.wallChain;
  S.preview = c ? mirrorGroups([{ cells: wallCells([...c.pts, c.hover]), ch: S.brush }]) : null;
  req2d();
}
function wallDown(cx, cy, right) {
  const c = S.wallChain;
  if (right) { if (c) wallFinish(); return; }
  if (!wallReady()) return;
  if (!c) { S.wallChain = { pts: [[cx, cy]], hover: [cx, cy], start: [cx, cy] }; G = { type: 'wall' }; wallPreview(); return; }
  const last = c.pts[c.pts.length - 1], p = constrainLine(last, [cx, cy]);
  G = { type: 'wall' };
  if (p[0] === last[0] && p[1] === last[1]) return;            // (the second press of a double-click)
  if (c.pts.length >= 3 && p[0] === c.pts[0][0] && p[1] === c.pts[0][1]) { wallFinish(true); G = null; return; }   // back to the start: closed
  c.pts.push(p); c.hover = p; wallPreview();
}
function wallMove(cx, cy) {
  const c = S.wallChain;
  if (!c) return;
  c.hover = constrainLine(c.pts[c.pts.length - 1], [cx, cy]);
  wallPreview();
}
function wallUp() {
  const c = S.wallChain;
  if (!c) return;
  if (c.pts.length === 1 && (c.hover[0] !== c.start[0] || c.hover[1] !== c.start[1])) { c.pts.push(c.hover); wallFinish(); }   // a drag: one run
}
function wallCancel() { S.wallChain = null; S.preview = null; req2d(); }
function wallBack() {
  const c = S.wallChain;
  if (!c) return;
  if (c.pts.length > 1) { c.pts.pop(); wallPreview(); } else wallCancel();
}
function wallFinish(closed) {
  const c = S.wallChain;
  S.wallChain = null; S.preview = null;
  if (!c || c.pts.length < 2) { req2d(); return; }
  const L = lv(), groups = mirrorGroups([{ cells: wallCells(c.pts, closed), ch: S.brush }]);
  let len = 0;
  for (let i = 0; i + 1 < c.pts.length; i++) len += Math.max(Math.abs(c.pts[i + 1][0] - c.pts[i][0]), Math.abs(c.pts[i + 1][1] - c.pts[i][1])) * (c.pts[i + 1][0] !== c.pts[i][0] && c.pts[i + 1][1] !== c.pts[i][1] ? Math.SQRT2 : 1);
  begin(`Wall · ${matName(S.plan.palette[S.brush].name)} · ${fmt(len * CM())} m long, ${fmt(wallSquares(S.wallOpt.thick) * CM())} m thick`);
  let full = false;
  const m = S.plan.palette[S.brush], onLayer = layerOn() && entryKey({ name: matName(m.name).slice(0, 40), kind: 'wall', color: m.color });
  for (const grp of groups) for (const [x, y] of grp.cells) {
    if (onLayer) { paintSquare(L, x, y, onLayer, true); continue; }
    const k = wallSym(L, x, y);
    if (!k) { full = true; break; }
    setCell(L, x, y, k);
  }
  commit();
  if (full) toast('The palette is full (999 symbols), so part of the wall wasn’t drawn. Tidy away unused materials first.', 'bad');
  req2d(); mark3d();
}
function wallControls() {
  const o = S.wallOpt, cm = CM();
  const num = (val, min, max, label, title, set) => {
    const inp = h('input', { type: 'number', value: String(val), min: String(min), max: String(max), step: String(cm), 'aria-label': label, class: 'qty', title });
    inp.addEventListener('change', () => { set(blocksNum(inp.value, val, min, max)); saveWallOpt(); renderOptbar(); wallPreview(); });
    return h('label', { class: 'inline' }, label, inp);
  };
  const seg = h('div', { class: 'seg', role: 'group', 'aria-label': 'Which side of the line', title: 'Which side of the line the thickness goes (F switches)' });
  for (const [v, lab] of WALL_SIDES) seg.append(h('button', { type: 'button', 'aria-pressed': String(o.side === v), text: lab, onclick: () => { o.side = v; saveWallOpt(); renderOptbar(); wallPreview(); } }));
  return [
    brushChip(), hotbarStrip(true),
    num(o.thick, cm, 8, 'Thick (m)', 'How thick the wall is', v => { o.thick = v; }),
    num(o.height, 0, 40, 'Tall (m)', '0 runs it to the top of the level', v => { o.height = v; }),
    num(o.base, 0, 40, 'Raise (m)', 'Lift it off the floor: a wall on a plinth, a lintel course', v => { o.base = v; }),
    seg,
    h('span', { class: 'hint', text: layerOn() ? 'In Layers mode the wall goes on this layer only · drag a run, or click corner to corner · double-click or Enter finishes · Esc cancels'
      : 'Drag a run, or click corner to corner · double-click, Enter or right-click finishes · Backspace takes back a corner · Esc cancels' }),
  ];
}
function cycleWallSide() { const o = S.wallOpt, i = WALL_SIDES.findIndex(([v]) => v === o.side); o.side = WALL_SIDES[(i + 1) % WALL_SIDES.length][0]; saveWallOpt(); renderOptbar(); wallPreview(); }

// ---------------------------------------------------------------------------
// Replace: click a block to make it the current material instead, keeping its kind, height, raise and floor
// underneath (only the material comes from the brush, so any entry of a material will do). Block mode swaps the block clicked, and dragging carries on over blocks of the same material as
// the first. Chunk mode swaps the whole continuous run of that material (any size of it): on this level in
// Levels mode, across every level at this height in Layers mode. Right-click picks up a block's material.
// ---------------------------------------------------------------------------
S.replaceMode = LS.get('replaceMode', 'block') === 'chunk' ? 'chunk' : 'block';
const SWAPPABLE = new Set(['wall', 'block', 'floor', 'water', 'roof']);     // (not doors, windows or digging)
// The piece in square (x, y) to replace: { L, x, y, part: 'main' | 'under', e }. On a block layer, what shows
// on the layer; on a level, the piece there, or the floor under a raised piece when `under` (the brush is a
// floor) or when that's all there is to change.
function replaceTarget(x, y, under) {
  const P = S.plan, pal = P.palette;
  if (!inB(x, y)) return null;
  if (layerOn()) {
    const k = layerView(curLayer())[y][x], e = pal[k];
    if (!e || !SWAPPABLE.has(e.kind)) return null;
    const L = layerOwner(x, y, k);
    if (!L) return null;
    if (L.grid[y][x] === k) return { L, x, y, part: 'main', e };
    const own = pal[L.grid[y][x]];
    return own && own.under === k ? { L, x, y, part: 'under', e } : null;
  }
  const L = lv(), e = pal[L.grid[y][x]];
  if (!e) return null;
  const u = e.under && pal[e.under], main = SWAPPABLE.has(e.kind) ? { L, x, y, part: 'main', e } : null;
  const below = u && SWAPPABLE.has(u.kind) ? { L, x, y, part: 'under', e: u } : null;
  return under ? below || main : main || below;
}
// Make target t material m. true if it changed, false if not, null if the palette is full.
function replaceAt(t, m) {
  const pal = S.plan.palette;
  if (t.part === 'main') { const k = swapEntry(t.e, m); return k ? setCell(t.L, t.x, t.y, k) : null; }
  const own = pal[t.L.grid[t.y][t.x]], nu = swapEntry(t.e, m);
  if (!nu) return null;
  const k = entryKey({ ...clone(own), under: nu });
  return k ? setCell(t.L, t.x, t.y, k) : null;
}
// Every square of the continuous run of material src from (sx, sy), found before anything changes.
function chunkTargets(sx, sy, src, under, part) {
  const P = S.plan, seen = new Set(), stack = [[sx, sy]], out = [];
  while (stack.length) {
    const [x, y] = stack.pop(), key = y * P.w + x;
    if (!inB(x, y) || seen.has(key)) continue;
    seen.add(key);
    const t = replaceTarget(x, y, under);
    if (!t || t.part !== part || !sameMat(t.e, src)) continue;
    out.push(t);
    stack.push([x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]);
  }
  return out;
}
let replaceFull = false;
function replaceList(ts, m) {
  let n = 0;
  for (const t of ts) {
    const r = replaceAt(t, m);
    if (r === null) { replaceFull = true; break; }
    if (r) n++;
  }
  return n;
}
function replaceDown(cx, cy, right) {
  const P = S.plan, pal = P.palette;
  if (right) {                                                 // pick up the block's material
    const here = squareMaterials(cx, cy).filter(r => !r.under && !r.stacked);
    if (here.length) { pickBrush(here[0].k); toast(`${here[0].e.name} is now the material to replace with.`); }
    return;
  }
  const m = pal[S.brush];
  if (!m || !SWAPPABLE.has(m.kind)) { toast('Pick a block, floor or roof material to replace with first (1–9, or the Materials tab).'); return; }
  const under = isFloorKind(m), t = replaceTarget(cx, cy, under);
  if (!t) { toast('There’s nothing there to replace (doors, windows and dug-out squares stay as they are).'); return; }
  if (sameMat(t.e, m)) { toast(`That’s already ${matName(m.name)}.`); return; }
  const src = t.e, label = n => `Replace ${matName(src.name)} → ${matName(m.name)} · ${n.toLocaleString()} square${n === 1 ? '' : 's'}`;
  replaceFull = false;
  if (S.replaceMode === 'chunk') {
    const ts = [], seen = new Set();
    for (const [a, b] of mirrorPts(cx, cy)) for (const q of chunkTargets(a, b, src, under, t.part)) { const k = q.L.id + ':' + q.x + ':' + q.y + q.part; if (!seen.has(k)) { seen.add(k); ts.push(q); } }
    begin(label(ts.length));
    const n = replaceList(ts, m);
    actionLabel = label(n);
    commit();
    if (replaceFull) toast('The palette is full (999 symbols), so not all of it changed. Tidy away unused materials first.', 'bad');
    mark3d(); return;
  }
  begin();
  G = { type: 'replace', src, under, part: t.part, m, last: [cx, cy], n: 0, label };
  replaceSquare(cx, cy);
}
function replaceSquare(x, y) {
  for (const [a, b] of mirrorPts(x, y)) {
    const t = replaceTarget(a, b, G.under);
    if (t && t.part === G.part && sameMat(t.e, G.src)) G.n += replaceList([t], G.m);
  }
  mark3d();
}
function replaceMove(cx, cy) {
  if (cx === G.last[0] && cy === G.last[1]) return;
  for (const [x, y] of lineCells(G.last[0], G.last[1], cx, cy)) replaceSquare(x, y);
  G.last = [cx, cy];
}
function replaceUp() {
  actionLabel = G.label(G.n);
  commit();
  if (replaceFull) toast('The palette is full (999 symbols), so not all of it changed. Tidy away unused materials first.', 'bad');
}
function replaceControls() {
  const seg = h('div', { class: 'seg', role: 'group', 'aria-label': 'Replace what' });
  for (const [v, lab, tip] of [['block', 'Block', 'The block you click; drag to carry on over the same material'], ['chunk', 'Chunk', 'The whole continuous run of that material']])
    seg.append(h('button', { type: 'button', 'aria-pressed': String(S.replaceMode === v), text: lab, title: tip, onclick: () => { S.replaceMode = v; LS.set('replaceMode', v); renderOptbar(); } }));
  return [brushChip(), hotbarStrip(true), seg,
    h('span', { class: 'hint', text: S.replaceMode === 'chunk'
      ? `Click a block to make its whole run ${layerOn() ? 'at this height' : 'on this level'} the current material · right-click picks up a block's material`
      : 'Click a block to make it the current material · drag to carry on over the same material · right-click picks up a block\'s material' })];
}
