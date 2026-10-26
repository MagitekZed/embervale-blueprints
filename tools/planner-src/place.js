
// ---------------------------------------------------------------------------
// Plan in plan: place another plan into this one
// ---------------------------------------------------------------------------
// The other plan is simplified (or split) to this plan's squares. On a coarser grid, walls, doors and
// windows always survive, so buildings stay closed and keep their openings; anything else goes by what
// covers most of each square, so scattered moss doesn't thicken. Roof heights are averaged and rounded
// to the square size. Levels line up by elevation and height, or are added. Items and areas come along.
// Mirrors Plan.stamp in tools/drafts/mage_common.py.

// Turn a normalized plan a quarter turn clockwise, k times.
function rotatePlanCW(src, k) {
  let P = src;
  for (let n = 0; n < ((k % 4) + 4) % 4; n++) {
    const W = P.w, H = P.h;
    P = {
      ...P, w: H, h: W,
      levels: P.levels.map(L => {
        const g = blankGrid(H, W);
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) g[x][H - 1 - y] = L.grid[y][x];
        return { ...L, grid: g };
      }),
      items: P.items.map(it => { const R = itemRect(it); return { ...it, x: H - (R.y + R.h), y: R.x, rot: (it.rot + 90) % 360 }; }),
      zones: P.zones.map(z => ({ ...z, x: H - (z.y + z.h), y: z.x, w: z.h, h: z.w })),
      terrain: (() => { const g = Array.from({ length: W }, () => new Array(H).fill(0)); for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) g[x][H - 1 - y] = P.terrain[y][x]; return g; })(),
    };
  }
  return P;
}

// Footprint of the other plan on this plan's squares: any square with something on any level.
function placeMask(src, tc) {
  const sc = src.cell, mw = Math.ceil(src.w * sc / tc), mh = Math.ceil(src.h * sc / tc);
  const m = new Uint8Array(mw * mh);
  let x0 = mw, y0 = mh, x1 = -1, y1 = -1;
  for (const L of src.levels) for (let y = 0; y < src.h; y++) for (let x = 0; x < src.w; x++) {
    if (L.grid[y][x] === ' ') continue;
    const tx = Math.floor(x * sc / tc), ty = Math.floor(y * sc / tc);
    if (!m[ty * mw + tx]) { m[ty * mw + tx] = 1; x0 = Math.min(x0, tx); y0 = Math.min(y0, ty); x1 = Math.max(x1, tx); y1 = Math.max(y1, ty); }
  }
  return { m, mw, mh, box: x1 < 0 ? null : { x: x0, y: y0, w: x1 - x0 + 1, h: y1 - y0 + 1 } };
}

function armPlace(id) {
  const d = S.plans.get(id);
  if (!d || !S.plan) return;
  const src = normalizePlan(d);
  S.placing = { id, name: src.name || 'Plan', src, rot: 0 };
  refreshPlaceMask();
  if (!S.placing.mask.box) { S.placing = null; toast('That plan is empty.'); return; }
  setTool('place');
  toast(`Click to place “${S.placing.name}”. R turns it, Esc cancels.`);
}
function refreshPlaceMask() {
  const pl = S.placing;
  pl.rotated = rotatePlanCW(pl.src, pl.rot / 90);
  pl.mask = placeMask(pl.rotated, S.plan.cell);
}
function rotatePlace() { if (!S.placing) return; S.placing.rot = (S.placing.rot + 90) % 360; refreshPlaceMask(); renderOptbar(); req2d(); }
// Where the other plan's corner goes so its footprint centres on the cursor (in this plan's squares).
function placeOrigin(cx, cy) {
  const b = S.placing.mask.box;
  return [cx - b.x - Math.floor(b.w / 2), cy - b.y - Math.floor(b.h / 2)];
}
function drawPlaceGhost(g, cam) {
  const pl = S.placing;
  if (!pl || !S.hover || !S.hoverIn) return;
  const { m, mw, mh, box } = pl.mask, s = cam.s, [ox, oy] = placeOrigin(S.hover[0], S.hover[1]);
  g.fillStyle = hexA(T.accent, 0.28);
  for (let y = 0; y < mh; y++) for (let x = 0; x < mw; x++) if (m[y * mw + x]) g.fillRect(cam.ox + (ox + x) * s, cam.oy + (oy + y) * s, s + 0.5, s + 0.5);
  g.setLineDash([6, 4]); g.lineWidth = 1.5; g.strokeStyle = T.accent;
  g.strokeRect(cam.ox + (ox + box.x) * s, cam.oy + (oy + box.y) * s, box.w * s, box.h * s); g.setLineDash([]);
  sizeTag(g, `${pl.name} · ${metres(box.w)} × ${metres(box.h)} m`, cam.ox + (ox + box.x + box.w) * s, cam.oy + (oy + box.y) * s);
}
function placeHere(cx, cy) {
  const pl = S.placing;
  if (!pl) return;
  const [ox, oy] = placeOrigin(cx, cy), tc = S.plan.cell;
  const keep = lv() && lv().id;
  begin();
  const r = stampPlan(S.plan, pl.rotated, ox * tc, oy * tc, pl.name);
  const i = S.plan.levels.findIndex(l => l.id === keep);
  if (i >= 0) S.levelIdx = i;
  commit(); refreshPanels();
  toast(`Placed “${pl.name}”` + (r.added ? `, adding ${r.added} level${r.added > 1 ? 's' : ''}` : '') +
    (r.merged.size ? `. The palette was full, so ${r.merged.size} material${r.merged.size > 1 ? 's' : ''} went to the closest match.` : '.'));
  S.placing = null; setTool('select');
}

// Place src (a normalized plan) into T with its north-west corner at (ox, oy) metres. Returns
// { added: levels added, merged: names of materials that had to borrow an existing symbol }.
function stampPlan(T, src, ox, oy, srcName) {
  const sc = src.cell, tc = T.cell, sw = src.w, sh = src.h, spal = src.palette;
  const merged = new Set();
  let added = 0;
  const strip = n => n.replace(/\s+[\d.]+ m$/, '');
  const same = (a, b) => a.name === b.name && a.kind === b.kind && a.color === b.color && (a.height || 0) === (b.height || 0) &&
    (a.base || 0) === (b.base || 0) && (a.under || '') === (b.under || '');
  const cost = (a, b) => {
    if (a.kind !== b.kind) return Infinity;
    const p = parseInt(a.color.slice(1), 16), q = parseInt(b.color.slice(1), 16);
    let dc = 0; for (const k of [16, 8, 0]) dc += Math.abs(((p >> k) & 255) - ((q >> k) & 255)) / 255;
    return dc + Math.abs((a.height || 0) - (b.height || 0)) + Math.abs((a.base || 0) - (b.base || 0)) + (strip(a.name) === strip(b.name) ? 0 : 4);
  };
  const alloc = e => {
    for (const [k, v] of Object.entries(T.palette)) if (same(v, e)) return k;
    const free = [...KEY_CANDIDATES].find(c => !T.palette[c]);
    if (free && Object.keys(T.palette).length < MAX_SYMBOLS) { T.palette[free] = e; return free; }
    let best = null, bc = Infinity;                            // palette full: borrow the closest symbol
    for (const [k, v] of Object.entries(T.palette)) { const c = cost(e, v); if (c < bc) { bc = c; best = k; } }
    if (best) merged.add(e.name);
    return best;
  };
  const cache = new Map();
  const mapChar = (c, hs, hd, top) => {
    const key = `${c}|${hs}|${hd}|${top}`;
    if (!cache.has(key)) cache.set(key, alloc(targetEntry(c, hs, hd, top)));
    return cache.get(key);
  };
  const targetEntry = (c, hs, hd, top) => {
    const e0 = spal[c];
    let e = { ...e0 };
    if (e.kind === 'roof') {
      const own = roofTop(e0, sc), hh = Math.max(tc, Math.round((top != null ? top : own) / tc) * tc);
      e = { name: Math.abs(hh - own) < 1e-6 ? e0.name : `${strip(e0.name)} ${fmt(hh)} m`.slice(0, 40), kind: 'roof', color: e0.color, height: hh };
    } else if ((e.kind === 'wall' || e.kind === 'door' || e.kind === 'window') && !e.height && Math.abs(hs - hd) > 0.01) e.height = hs;   // keep its own storey height
    if (e.under) {
      const u = spal[e.under] ? mapChar(e.under, hs, hd, null) : null;
      if (u) e.under = u; else delete e.under;
    }
    return e;
  };
  const topOf = c => {
    let e = spal[c];
    if (e && e.kind !== 'roof' && e.under && spal[e.under]) e = spal[e.under];
    return e && e.kind === 'roof' ? roofTop(e, sc) : null;
  };
  const PRI = { block: 3, roof: 2, water: 1, floor: 0 };
  const levMap = new Map();
  for (const L of src.levels) {
    let D = T.levels.find(t => Math.abs(t.elev - L.elev) < 0.01 && Math.abs(t.height - L.height) < 0.01);
    if (!D && T.levels.length < MAX_LEVELS) {
      D = { id: uid('L'), name: `${srcName}: ${L.name}`.slice(0, 40), elev: L.elev, height: L.height, hidden: false, grid: blankGrid(T.w, T.h) };
      T.levels.push(D); added++;
    }
    if (!D) D = T.levels.reduce((a, b) => Math.abs(b.elev - L.elev) < Math.abs(a.elev - L.elev) ? b : a);
    levMap.set(L.id, D);
    const whole = new Map();                                   // how common each symbol is on this level
    for (const row of L.grid) for (const c of row) if (c !== ' ') whole.set(c, (whole.get(c) || 0) + 1);
    const tx0 = Math.max(0, Math.floor(ox / tc + 1e-9)), ty0 = Math.max(0, Math.floor(oy / tc + 1e-9));
    const tx1 = Math.min(T.w, Math.ceil((ox + sw * sc) / tc - 1e-9)), ty1 = Math.min(T.h, Math.ceil((oy + sh * sc) / tc - 1e-9));
    for (let ty = ty0; ty < ty1; ty++) for (let tx = tx0; tx < tx1; tx++) {
      const chars = [];
      if (tc >= sc) {
        const i0 = Math.round((tx * tc - ox) / sc), i1 = Math.round(((tx + 1) * tc - ox) / sc);
        const j0 = Math.round((ty * tc - oy) / sc), j1 = Math.round(((ty + 1) * tc - oy) / sc);
        for (let j = j0; j < j1; j++) for (let i = i0; i < i1; i++) chars.push(i >= 0 && j >= 0 && i < sw && j < sh ? L.grid[j][i] : ' ');
      } else {
        const i = Math.floor(((tx + 0.5) * tc - ox) / sc), j = Math.floor(((ty + 0.5) * tc - oy) / sc);
        chars.push(i >= 0 && j >= 0 && i < sw && j < sh ? L.grid[j][i] : ' ');
      }
      const ents = chars.filter(c => c !== ' ' && spal[c]);
      if (!ents.length) continue;
      let pick = null, top = null;
      for (const kd of ['door', 'window', 'wall']) {
        const hits = ents.filter(c => spal[c].kind === kd);
        if (hits.length) { pick = mostCommon(hits); break; }
      }
      if (!pick) {
        if (ents.length * 2 < chars.length) continue;           // mostly empty
        const cnt = new Map(); for (const c of ents) cnt.set(c, (cnt.get(c) || 0) + 1);
        const score = c => [cnt.get(c), PRI[spal[c].kind] || 0, whole.get(c) || 0];
        pick = [...cnt.keys()].reduce((a, b) => { const A = score(a), B = score(b); return B[0] > A[0] || (B[0] === A[0] && (B[1] > A[1] || (B[1] === A[1] && B[2] > A[2]))) ? b : a; });
        if (spal[pick].kind === 'roof') { const tops = ents.map(topOf).filter(v => v != null); if (tops.length) top = tops.reduce((a, b) => a + b, 0) / tops.length; }
      }
      const k = mapChar(pick, L.height, D.height, top);
      if (k) D.grid[ty][tx] = k;
    }
  }
  T.levels.sort((a, b) => a.elev - b.elev);
  if (terrainOn(src)) {                                       // ground: averaged over each square, in whole blocks
    const [lo, hi] = terrainLimits(tc);
    const tx0 = Math.max(0, Math.floor(ox / tc + 1e-9)), ty0 = Math.max(0, Math.floor(oy / tc + 1e-9));
    const tx1 = Math.min(T.w, Math.ceil((ox + sw * sc) / tc - 1e-9)), ty1 = Math.min(T.h, Math.ceil((oy + sh * sc) / tc - 1e-9));
    for (let ty = ty0; ty < ty1; ty++) for (let tx = tx0; tx < tx1; tx++) {
      let s = 0, n = 0, any = false;
      const i0 = Math.floor((tx * tc - ox) / sc), i1 = Math.max(i0 + 1, Math.round(((tx + 1) * tc - ox) / sc));
      const j0 = Math.floor((ty * tc - oy) / sc), j1 = Math.max(j0 + 1, Math.round(((ty + 1) * tc - oy) / sc));
      for (let j = j0; j < j1; j++) for (let i = i0; i < i1; i++) if (i >= 0 && j >= 0 && i < sw && j < sh) { const v = src.terrain[j][i]; s += v; n++; if (v) any = true; }
      if (any) T.terrain[ty][tx] = clamp(Math.round(s / n / tc) * tc, lo, hi);
    }
  }
  const cell = m => Math.floor(m / tc + 0.5);
  const holding = m => Math.floor(m / tc + 1e-9);             // the square holding that point (where a thin wall lands)
  for (const it of src.items) {
    const R = itemRect(it), D = levMap.get(it.level) || T.levels[0];
    let x0 = cell(R.x * sc + ox), y0 = cell(R.y * sc + oy);
    let rw = Math.max(1, cell((R.x + R.w) * sc + ox) - x0), rd = Math.max(1, cell((R.y + R.h) * sc + oy) - y0);
    if (tc > sc && IN_WALL.has(it.mount)) {                   // a door or window stays in the square its wall went to
      if (it.rot % 180 === 0) { y0 = holding(R.y * sc + oy); rd = 1; } else { x0 = holding(R.x * sc + ox); rw = 1; }
    }
    if (x0 < 0 || y0 < 0 || x0 + rw > T.w || y0 + rd > T.h) continue;          // only items wholly on the canvas
    const turned = it.rot === 90 || it.rot === 270;
    T.items.push({ ...it, id: uid('i'), level: D.id, x: x0, y: y0, w: turned ? rd : rw, d: turned ? rw : rd });
  }
  for (const z of src.zones) {
    const D = levMap.get(z.level) || T.levels[0];
    const x0 = cell(z.x * sc + ox), y0 = cell(z.y * sc + oy);
    const w = Math.max(1, cell((z.x + z.w) * sc + ox) - x0), h2 = Math.max(1, cell((z.y + z.h) * sc + oy) - y0);
    const zx = Math.max(0, x0), zy = Math.max(0, y0), zw = Math.min(T.w, x0 + w) - zx, zh = Math.min(T.h, y0 + h2) - zy;
    if (zw < 1 || zh < 1) continue;
    T.zones.push({ ...z, id: uid('z'), level: D.id, x: zx, y: zy, w: zw, h: zh });
  }
  return { added, merged };
}
function mostCommon(list) {
  const cnt = new Map(); let best = list[0], n = 0;
  for (const c of list) { const k = (cnt.get(c) || 0) + 1; cnt.set(c, k); if (k > n) { n = k; best = c; } }
  return best;
}
