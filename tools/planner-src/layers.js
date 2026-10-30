
// ---------------------------------------------------------------------------
// Block layers: see and edit one course of blocks at a time (a 0.5 m layer on a 0.5 m plan, a 1 m layer
// on a 1 m plan), by height across the whole plan. Levels don't come into it: a layer shows everything at
// its height, whichever level holds it, and painting works out which level each square belongs on.
// The plan keeps its shape underneath: a square holds one symbol per level, which is one unbroken run of
// blocks (from its "Raise by" up to its top), maybe over a floor. Painting a layer starts, grows or trims
// that run, and makes palette entries for new sizes as needed.
// ---------------------------------------------------------------------------
const layerSize = () => S.plan.cell;
const layerOn = () => S.layer != null && !!S.plan && S.plan.levels.length > 0;
// The plan's layers, as [lowest, highest] index; layer k runs from k to k + 1 courses above 0 m.
function layerSpan() {
  const c = layerSize();
  let lo = Infinity, hi = -Infinity;
  for (const L of S.plan.levels) { lo = Math.min(lo, Math.floor((L.elev - FLOOR_T) / c + 1e-6)); hi = Math.max(hi, Math.ceil((L.elev + L.height) / c - 1e-6) - 1); }   // (from the lowest floor course)
  return lo > hi ? [0, 0] : [lo, hi];
}
function curLayer() { const [lo, hi] = layerSpan(); return clamp(S.layer != null ? S.layer : 0, lo, hi); }
const layerZ = k => [k * layerSize(), (k + 1) * layerSize()];
const layerName = k => `Layer ${k >= 0 ? k + 1 : k}`;           // counted from the ground: 1 up, −1 down
const layerOfLevel = L => Math.floor(L.elev / layerSize() + 1e-6);
const holdsZ = (L, Z0, Z1) => L.elev <= Z0 + 1e-6 && L.elev + L.height >= Z1 - 1e-6;

// How far up a square's contents reach, in metres above its level's floor. Roofs come from their columns.
function spanOf(e, L) {
  const cm = S.plan.cell, b = e.base || 0;
  if (e.kind === 'wall') return [b, b + (e.height || Math.max(cm, L.height - b))];
  if (e.kind === 'block') return [b, b + (e.height || 1)];
  if (e.kind === 'floor' || e.kind === 'water') return [-FLOOR_T, 0];    // the course just below the level floor
  if (e.kind === 'door' || e.kind === 'window') return [0, openingWall(e, L)];
  if (e.kind === 'dig') return [0, L.height];
  return null;
}
const isRun = e => !!e && (e.kind === 'wall' || e.kind === 'block');
// a door's or window's opening, in metres above its level's floor (the 3D view's sizes)
const openingOf = openingSpan;
const hits = (sp, z0, z1) => !!sp && sp[0] < z1 - 1e-6 && sp[1] > z0 + 1e-6;
// A roof square's column on its level (as roofColumns works it out, without the gable wall under it).
function roofSpan(L, x, y) {
  const pal = S.plan.palette, cm = S.plan.cell;
  const topAt = (i, j) => { if (!inB(i, j)) return NaN; let e = pal[L.grid[j][i]]; if (e && e.kind !== 'roof' && e.under && pal[e.under]) e = pal[e.under]; return e && e.kind === 'roof' ? roofTop(e, cm) : NaN; };
  const t = topAt(x, y);
  if (t !== t) return null;
  let bot = t - cm;
  for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const u = topAt(x + dx, y + dy); if (u === u && t - u <= 3.01 * cm) bot = Math.min(bot, u); }
  return [Math.max(0, bot), t];
}

// The symbols of level L that occupy [z0, z1) metres above its floor, as a grid like L.grid. A raised piece
// shows its floor underneath on the bottom layer; a roof shows on the layers its column fills, and the
// gable wall carried up under it shows as that wall.
function occupancy(L, z0, z1) {
  const P = S.plan, pal = P.palette, W = P.w, roof = new Map(), cuts = openingCuts(P);
  if (Object.values(pal).some(e => e.kind === 'roof'))
    for (const c of roofColumns(P, L, P.levels.filter(B => B !== L && B.elev < L.elev - 0.01))) roof.set(c.y * W + c.x, c);
  const roofAt = (x, y, ch) => {
    const c = roof.get(y * W + x);
    if (!c) return ' ';
    if (hits([c.bot - L.elev, c.top - L.elev], z0, z1)) return ch;
    if (!(c.fill && c.fillCh && hits([c.fillFrom - L.elev, c.bot - L.elev], z0, z1))) return ' ';
    const f = pal[c.fillCh];                                  // over a door or window it's the wall round it
    return f && (f.kind === 'door' || f.kind === 'window') ? (neighbourWallSymbol(P.levels.find(B => B.grid[y][x] === c.fillCh) || L, x, y) || c.fillCh) : c.fillCh;
  };
  return L.grid.map((row, y) => row.map((ch, x) => {
    if (ch === ' ') return ' ';
    const e = pal[ch];
    if (!e) return ch;
    if (e.kind === 'roof') return roofAt(x, y, ch);
    if (e.kind === 'door' || e.kind === 'window') {          // the opening, with the wall it sits in above and below
      if (!hits([0, openingWall(e, L)], z0, z1)) return ' ';
      return hits(openingOf(e, L), z0, z1) ? ch : (neighbourWallSymbol(L, x, y) || ch);
    }
    if (hits(spanOf(e, L), z0, z1)) {
      const cs = isRun(e) && cuts.get(L.id + ':' + x + ':' + y);      // inside a door's or window's opening: open
      return cs && cutLength(z0, z1, cs) >= z1 - z0 - 1e-6 ? ' ' : ch;
    }
    const u = e.under && pal[e.under];
    if (!u) return ' ';
    return u.kind === 'roof' ? roofAt(x, y, e.under) : hits(spanOf(u, L), z0, z1) ? e.under : ' ';
  }));
}
// Everything on layer k, from every level, as one grid (cached until the plan changes). Every level whose
// floor course starts below the layer's top counts: a tall wall (a chimney) or a roof can rise past its own level.
let layerCache = new Map();
function layerView(k) {
  if (layerCache.plan !== S.plan || layerCache.ver !== planVer) { layerCache = new Map(); layerCache.plan = S.plan; layerCache.ver = planVer; }
  if (layerCache.has(k)) return layerCache.get(k);
  const P = S.plan, [Z0, Z1] = layerZ(k);
  const out = Array.from({ length: P.h }, () => Array(P.w).fill(' '));
  for (const L of P.levels) {
    if (L.elev - FLOOR_T >= Z1 - 1e-6) continue;              // (a level's floor course is just below it)
    const g = occupancy(L, Z0 - L.elev, Z1 - L.elev);
    for (let y = 0; y < P.h; y++) for (let x = 0; x < P.w; x++) if (out[y][x] === ' ' && g[y][x] !== ' ') out[y][x] = g[y][x];
  }
  layerCache.set(k, out);
  return out;
}
// the levels a layer passes through (for their areas and items)
const layerLevels = k => { const [Z0, Z1] = layerZ(k); return S.plan.levels.filter(L => L.elev < Z1 - 1e-6 && L.elev + L.height > Z0 + 1e-6); };

// ---- items in block layers go at the layer's height, not at the floor of whichever level holds the layer (a tall
// level reaching up past the layer used to take them, down at its own floor, out of sight)
let layerOccCache = new Map();
function layerOcc(L, k) {                                     // level L's pieces on layer k (cached until the plan changes)
  if (layerOccCache.plan !== S.plan || layerOccCache.ver !== planVer) { layerOccCache = new Map(); layerOccCache.plan = S.plan; layerOccCache.ver = planVer; }
  const key = L.id + ':' + k;
  if (!layerOccCache.has(key)) { const [Z0, Z1] = layerZ(k); layerOccCache.set(key, occupancy(L, Z0 - L.elev, Z1 - L.elev)); }
  return layerOccCache.get(key);
}
function layerWallLevel(x, y, k) {                            // the level whose wall is in square (x, y) on layer k
  if (!inB(x, y)) return null;
  const pal = S.plan.palette;
  return layerLevels(k).find(B => { const e = pal[layerOcc(B, k)[y][x]]; return !!e && (e.kind === 'wall' || e.kind === 'block'); }) || null;
}
// Where an item placed on the current layer goes: a door or window on the level whose wall it sits in; anything else
// on the level whose floor is at the layer's foot under it (else one whose floor is at that height, else the level
// holding the layer). Its bottom sits at the layer's foot, or for a hanging one its top at the layer's top.
function layerItemHome(mount, g, def) {
  const P = S.plan, k = curLayer(), [Z0, Z1] = layerZ(k);
  const at = L => mount === 'ceiling' ? Math.max(0, Z1 - L.elev - def.h) : Math.max(0, Z0 - L.elev);
  if (g.home) { const L = P.levels.find(B => B.id === g.home); if (L) return { L, z: at(L) }; }
  const cx = clamp(Math.floor(g.x + g.w / 2), 0, P.w - 1), cy = clamp(Math.floor(g.y + g.h / 2), 0, P.h - 1);
  const flat = P.levels.filter(B => Math.abs(B.elev - Z0) < 1e-6 && !trimParent(B) && holdsZ(B, Z0, Z1));
  const L = flat.find(B => floorUnder(P.palette, P.palette[B.grid[cy][cx]])) || (flat.includes(lv()) ? lv() : flat[0]) || lv();
  return { L, z: at(L) };
}

// Materials match when they're the same block in the same colour, whatever their size or tag.
const sameMat = (a, b) => a.color === b.color && matName(a.name) === matName(b.name);
const runName = n => n.replace(/\s+[\d.]+ m$/, '').trim();
// The palette symbol for a run of material m from b0 to b1 metres on level L (over floor u, when it's raised).
function runSymbol(L, m, b0, b1, u) {
  const pal = S.plan.palette;
  for (const [k, e] of Object.entries(pal)) {
    if (!isRun(e) || e.kind !== m.kind || !sameMat(e, m) || (e.under || null) !== (u || null)) continue;
    const sp = spanOf(e, L);
    if (Math.abs(sp[0] - b0) < 1e-6 && Math.abs(sp[1] - b1) < 1e-6) return k;
  }
  pruneRuns(m);
  const k = nextFreeKey();
  if (!k || Object.keys(pal).length >= MAX_SYMBOLS) return null;
  const e = { name: runName(m.name).slice(0, 40), kind: m.kind, color: m.color, height: Math.round((b1 - b0) * 100) / 100 };
  if (b0 > 1e-6) e.base = Math.round(b0 * 100) / 100;
  if (u) e.under = u;
  pal[k] = e;
  if (!layerMade.has(S.planId)) layerMade.set(S.planId, new Set());
  layerMade.get(S.planId).add(k);
  return k;
}
// Growing a run a layer at a time leaves its earlier sizes behind. Before making a new size of a material,
// drop the sizes of it that layer painting made this session and nothing uses any more. (Entries you made,
// and the brush, always stay.)
const layerMade = new Map();                                  // plan id -> symbols made by layer painting
function pruneRuns(m) {
  const P = S.plan, pal = P.palette, mine = layerMade.get(S.planId);
  if (!mine) return;
  const spare = Object.keys(pal).filter(k => mine.has(k) && isRun(pal[k]) && sameMat(pal[k], m) && k !== S.brush && pal[k] !== m);
  if (!spare.length) return;
  const used = new Set();
  for (const L of P.levels) for (const row of L.grid) for (const c of row) used.add(c);
  for (const e of Object.values(pal)) if (e.under) used.add(e.under);
  for (const k of spare) if (!used.has(k)) { delete pal[k]; mine.delete(k); }
}

let layerWarnAt = 0, layerWarnMsg = '';
function layerWarn(msg) {
  const now = Date.now();
  if (msg === layerWarnMsg && now - layerWarnAt < 2500) return;
  layerWarnAt = now; layerWarnMsg = msg; toast(msg);
}

// Set [z0, z1) metres above level L's floor in square (x, y) to `ch` (a material symbol, or ' ' to clear it).
// Returns false, changing nothing, when it can't be done (layerPaint checks first and says why).
function layerSet(L, x, y, ch, z0, z1) {
  const P = S.plan, pal = P.palette, cur = L.grid[y][x], e = pal[cur];
  const m = ch === ' ' ? null : pal[ch];
  // what's there now: a run of blocks [b0, b1), and a floor u or a roof ur under it. (A door, window, roof
  // or dig square counts as neither: painting or clearing over it replaces the whole square.)
  let run = null, u = null, ur = null;
  if (e && isRun(e)) {
    const sp = spanOf(e, L), ue = e.under && pal[e.under];
    run = { m: e, b0: sp[0], b1: sp[1] };
    if (ue && ue.kind === 'roof') ur = e.under; else if (ue && (ue.kind === 'floor' || ue.kind === 'water')) u = e.under;
  } else if (e && (e.kind === 'floor' || e.kind === 'water')) u = cur;
  if (z1 <= 1e-6) {                                         // the floor course, just below the level floor
    if (m && !isFloorKind(m)) return false;
    u = m ? ch : null;
    const out = run ? runSymbol(L, run.m, run.b0, run.b1, u || ur) : (u || ur || ' ');
    if (!out) { layerWarn('The palette is full (999 symbols). Remove unused materials in the Materials tab first.'); return false; }
    return setCell(L, x, y, out);
  }
  if (m && isFloorKind(m)) return false;                      // floors only go in the floor course
  // take this layer out of the run
  if (run && hits([run.b0, run.b1], z0, z1)) {
    if (m && isRun(m) && sameMat(m, run.m)) return false;
    if (run.b0 >= z0 - 1e-6 && run.b1 <= z1 + 1e-6) run = null;
    else if (run.b0 >= z0 - 1e-6) run.b0 = z1;
    else if (run.b1 <= z1 + 1e-6) run.b1 = z0;
    else return false;
  }
  if (m && isRun(m)) {
    if (!run) run = { m, b0: z0, b1: z1 };
    else if (sameMat(m, run.m) && z0 <= run.b1 + 1e-6 && z1 >= run.b0 - 1e-6) run = { m, b0: Math.min(run.b0, z0), b1: Math.max(run.b1, z1) };
    else return false;
  }
  let out = ' ';
  if (run && run.b1 > run.b0 + 1e-6) {
    out = runSymbol(L, run.m, run.b0, run.b1, u || ur);       // (a floor stays under blocks standing on it)
    if (!out) { layerWarn('The palette is full (999 symbols). Remove unused materials in the Materials tab first.'); return false; }
  } else out = u || ur || ' ';
  return setCell(L, x, y, out);
}

// Paint (or clear, with ' ') square (x, y) on the current layer, working out which level it belongs on:
// one that already has something in that square on this layer; then one whose run of the same material
// stops just below or starts just above this layer (it grows); then the current level, or another that
// holds the whole layer, with the square free.
function layerPaint(x, y, ch, quiet) {
  if (!inB(x, y)) return false;
  const P = S.plan, pal = P.palette, [Z0, Z1] = layerZ(curLayer()), m = ch === ' ' ? null : pal[ch];
  if (ch !== ' ' && !m) return false;
  const warn = msg => { if (!quiet) layerWarn(msg); return false; };
  const rel = L => [Z0 - L.elev, Z1 - L.elev];
  const holds = L => holdsZ(L, Z0, Z1);
  const home = lv(), order = [home, ...P.levels.filter(L => L !== home)].filter(Boolean);
  const occupied = L => {
    const e = pal[L.grid[y][x]];
    if (!e || L.elev - FLOOR_T >= Z1 - 1e-6) return false;
    const [z0, z1] = rel(L);
    if (e.kind === 'roof') return hits(roofSpan(L, x, y), z0, z1);
    if (hits(spanOf(e, L), z0, z1)) return true;
    const ue = e.under && pal[e.under];
    return !!ue && (ue.kind === 'roof' ? hits(roofSpan(L, x, y), z0, z1) : hits(spanOf(ue, L), z0, z1));
  };
  const there = order.find(occupied);
  if (there) {
    const e = pal[there.grid[y][x]];
    if (e.kind === 'door' || e.kind === 'window') return warn(`That's a ${e.kind} (with the wall round it) on ${there.name}. Change it in Levels mode.`);
  }
  if (!m) {
    if (!there) return false;
    const e = pal[there.grid[y][x]];
    if (isRun(e)) { const [b0, b1] = spanOf(e, there), [z0, z1] = rel(there); if (b0 < z0 - 1e-6 && b1 > z1 + 1e-6) return splitRun(there, x, y, e, b0, b1, z0, z1) || warn(`Can't cut a gap in the middle of ${runName(e.name)} (${fmt(there.elev + b0)} to ${fmt(there.elev + b1)} m): a square holds one unbroken run per level. Trim it from the top or bottom, or use a door or window.`); }
    return layerSet(there, x, y, ' ', ...rel(there));
  }
  if (isFloorKind(m)) {                                      // floors are the course just below a level's floor
    const L = order.find(L => Math.abs(L.elev - Z1) < 1e-6);
    if (!L) return warn(`Floors and water are the block course just below a level's floor, and no level starts at ${fmt(Z1)} m.`);
    if (there && there !== L && !isFloorKind(pal[there.grid[y][x]])) return warn(`There's already something here on ${there.name}.`);
    return layerSet(L, x, y, ch, ...rel(L));
  }
  if (!isRun(m)) {                                            // doors, windows, roofs, digging: the whole square of one level
    const L = there || order.find(holds);
    if (!L) return warn(`No level holds ${fmt(Z0)} to ${fmt(Z1)} m yet. Add one in Levels mode.`);
    return setCell(L, x, y, ch);
  }
  if (there) {
    const e = pal[there.grid[y][x]], [z0, z1] = rel(there);
    if (z1 <= 1e-6) return warn(`That's the floor of ${there.name}: paint floors here, and blocks on the layers above.`);
    if (!isRun(e)) return layerSet(there, x, y, ch, z0, z1);   // a door, window, roof or dig square: replaced
    const [b0, b1] = spanOf(e, there);
    if (hits([b0, b1], z0, z1)) {
      if (sameMat(e, m)) return false;                         // already this material
      if (b0 < z0 - 1e-6 || b1 > z1 + 1e-6) return warn(`This square already has ${runName(e.name)} here (${fmt(there.elev + b0)} to ${fmt(there.elev + b1)} m). Clear it from this layer first.`);
      return layerSet(there, x, y, ch, z0, z1);                // a one-layer run of something else: replaced
    }
    // only the floor under a raised run is on this layer: the run can grow down onto it
    if (sameMat(e, m) && Math.abs(b0 - z1) < 1e-6) return layerSet(there, x, y, ch, z0, z1);
  }
  // grow a run of the same material that stops just below or starts just above this layer
  const grows = L => { const e = pal[L.grid[y][x]]; if (!isRun(e) || !sameMat(e, m)) return false; const [b0, b1] = spanOf(e, L), [z0, z1] = rel(L); return Math.abs(b1 - z0) < 1e-6 || Math.abs(b0 - z1) < 1e-6; };
  const g = order.find(L => holds(L) && grows(L));
  if (g) return layerSet(g, x, y, ch, ...rel(g));
  // start a run on a level that holds this layer and has the square free (or only a floor there)
  const free = L => { const e = pal[L.grid[y][x]]; return !e || e.kind === 'floor' || e.kind === 'water'; };
  const f = order.filter(holds).sort((a, b) => (a === home ? -1 : b === home ? 1 : a.height - b.height)).find(free);
  if (f) return layerSet(f, x, y, ch, ...rel(f));
  const hl = order.find(holds);                               // every level here has blocks at other heights: a trim level of one
  if (hl) { const T = trimLevelFor(hl, x, y); if (T) return layerSet(T, x, y, ch, ...rel(T)); }
  return warn(order.some(holds)
    ? 'This square already has blocks at other heights on every level here (a square holds one unbroken run per level). Add a level for this part in Levels mode.'
    : `No level holds ${fmt(Z0)} to ${fmt(Z1)} m yet. Add one in Levels mode.`);
}
function paintSquare(L, x, y, ch, quiet) { return layerOn() ? layerPaint(x, y, ch, quiet) : setCell(L, x, y, ch); }

// Fill on a layer: the connected squares that look the same on this layer.
function layerFlood(sx, sy, ch) {
  if (!inB(sx, sy)) return 0;
  const P = S.plan, view = layerView(curLayer()), target = view[sy][sx];
  if (target === ch) return 0;
  const seen = new Uint8Array(P.w * P.h), stack = [sx, sy], cells = [];
  while (stack.length) {
    const y = stack.pop(), x = stack.pop();
    if (!inB(x, y) || seen[y * P.w + x] || view[y][x] !== target) continue;
    seen[y * P.w + x] = 1; cells.push([x, y]);
    stack.push(x + 1, y, x - 1, y, x, y + 1, x, y - 1);
  }
  let n = 0;
  for (const [x, y] of cells) if (layerPaint(x, y, ch)) n++;
  return n;
}

// ---- switching and stepping
// The current level follows the layer (staying put while it still holds the layer, else the smallest level
// that does), so painting prefers it and switching back to Levels lands where you were building.
function followLayer() {
  const [Z0, Z1] = layerZ(curLayer()), L = lv();
  if (L && holdsZ(L, Z0, Z1)) return;
  const best = S.plan.levels.map((B, i) => [B, i]).filter(([B]) => holdsZ(B, Z0, Z1)).sort((a, b) => a[0].height - b[0].height)[0];
  if (best) setLevel(best[1]);
}
function setLayerMode(on) {                                 // back on, it returns to the layer you left, if it's on this level
  if (!S.plan || on === (S.layer != null)) return;
  if (on) {
    const L = lv(), mem = S.layerMem, c = layerSize();
    S.layer = L && mem != null && holdsZ(L, mem * c, (mem + 1) * c) ? mem : L ? layerOfLevel(L) : 0;
    S.layer = curLayer();
  } else { S.layerMem = curLayer(); S.layer = null; }
  layerChanged();
}
function toggleLayers() { setLayerMode(S.layer == null); }
function layerChanged() { closeLevelPop(); renderOptbar(); updateStatus(); req2d(); mark3d(); }
function setLayer(k) { const [lo, hi] = layerSpan(); S.layer = clamp(k, lo, hi); followLayer(); layerChanged(); }
// Up or down by n layers, by height, stopping at the plan's top and bottom.
function stepLayer(n) {
  const [lo, hi] = layerSpan(), k = curLayer();
  if (n > 0 && k >= hi) { layerWarn('That\'s the top of the plan. To build higher, add a level on top in Levels mode.'); return; }
  if (n < 0 && k <= lo) { layerWarn('That\'s the bottom of the plan. To dig deeper, add a level below in Levels mode.'); return; }
  setLayer(k + n);
}
