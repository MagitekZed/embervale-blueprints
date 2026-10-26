// ---------------------------------------------------------------------------
// Build tracking (planner v48): mark blocks built, follow the progress, see which chunks you can build with the
// blocks you have; and hover highlighting.
//
// The block index: every piece of the plan as segments of blocks by square, { c, x, y, z0, z1 (absolute metres),
// mat (material: catalogue name and colour), name, lid, core }: walls and blocks (less door and window openings),
// floor courses, roof columns and the gable walls under them.
// A chunk is every connected block of one material that the view shows (blocks connect through faces): in 3D,
// what the 3D view draws; in 2D, the current level and its trims, or the current layer. Alt takes everything
// connected; Shift one square or block. Marking a chunk also marks the hidden-core blocks touching it in its
// squares (you build them with it).
// Progress is kept per block (by square, height and material), so it survives regenerating the plan: a block
// still there in the same material stays built. It's saved in the database as progress/<plan id>. The blocks you
// have are shared by every plan (the Inventory tab's counts, meta/inventory), but each plan only counts them
// against itself.
// ---------------------------------------------------------------------------
const PG = { plan: null, ver: -1, cols: null, segs: null };
const matKeyOf = e => matName(e.name) + '|' + e.color;
const CORE_RE = /\(hidden core\)/i;
const BLOCK_H = 0.5;                                           // a game block: 0.5 m
const blocksIn = (z0, z1) => Math.max(0, Math.round((z1 - z0) / BLOCK_H)) * (CM() / BLOCK_H) ** 2;
function pgIndex() {
  const P = S.plan;
  if (PG.plan === P && PG.ver === planVer) return PG;
  const W = P.w, pal = P.palette, cuts = openingCuts(P), cols = new Map(), segs = [];
  const keyOf = new Map(Object.entries(pal).map(([k, e]) => [e, k]));
  const add = (lid, x, y, z0, z1, e) => {
    if (!e || z1 - z0 < 1e-6) return;
    const c = y * W + x, s = { id: segs.length, c, x, y, z0, z1, mat: matKeyOf(e), name: matName(e.name), color: e.color, lid, core: CORE_RE.test(e.name) };
    segs.push(s);
    let list = cols.get(c);
    if (!list) cols.set(c, list = []);
    list.push(s);
  };
  const hasRoof = Object.values(pal).some(e => e.kind === 'roof');
  for (const L of P.levels) {
    let roofs = false;
    for (let y = 0; y < P.h; y++) {
      const row = L.grid[y];
      for (let x = 0; x < W; x++) {
        const ch = row[x];
        if (ch === ' ') continue;
        const e = pal[ch];
        if (!e) continue;
        const u = e.under && pal[e.under];
        if (e.kind === 'roof' || (u && u.kind === 'roof')) roofs = true;
        if (e.kind === 'floor') add(L.id, x, y, L.elev - FLOOR_T, L.elev, e);
        else if (u && u.kind === 'floor') add(L.id, x, y, L.elev - FLOOR_T, L.elev, u);
        else if (e.kind === 'wall' || e.kind === 'block' || e.kind === 'door' || e.kind === 'window') { const fc = floorCourse(P, L, x, y); if (fc) add(L.id, x, y, L.elev - FLOOR_T, L.elev, fc); }
        if (e.kind === 'wall' || e.kind === 'block') {
          const [b0, b1] = spanOf(e, L);
          for (const [a, b] of minusCuts(b0, b1, cuts.get(L.id + ':' + x + ':' + y))) add(L.id, x, y, L.elev + a, L.elev + b, e);
        }
      }
    }
    if (hasRoof && roofs) for (const c of roofColumns(P, L, P.levels.filter(B => B !== L && B.elev < L.elev - 0.01))) {
      add(L.id, c.x, c.y, c.bot, c.top, c.e);
      if (c.fill && (c.fill.kind === 'wall' || c.fill.kind === 'block') && c.bot > c.fillFrom + 1e-6) add(c.fillLevel, c.x, c.y, c.fillFrom, c.bot, c.fill);
    }
  }
  for (const list of cols.values()) list.sort((a, b) => a.z0 - b.z0);
  Object.assign(PG, { plan: P, ver: planVer, cols, segs, keyOf });
  return PG;
}
// What the view shows: { lv(level id), lo, hi (metres), rect }.
function pgView(where, all) {
  const P = S.plan;
  if (all) return { lv: () => true, lo: -Infinity, hi: Infinity, rect: null };
  if (where === '3d') {
    const layK = layerOn() ? curLayer() : null, clipTop = layK != null && S.opt.cut ? layerZ(layK)[1] : Infinity;
    const cur = mainLevel(lv()), withTrims = [cur, ...trimsOf(cur)].map(l => P.levels.indexOf(l));
    const maxIdx = S.opt.cut && clipTop === Infinity ? Math.max(S.levelIdx, ...withTrims) : P.levels.length - 1;
    const ok = new Set(P.levels.filter((L, i) => i <= maxIdx && !L.hidden).map(L => L.id));
    return { lv: id => ok.has(id), lo: -Infinity, hi: clipTop, rect: S.section || null };
  }
  if (layerOn()) { const [z0, z1] = layerZ(curLayer()); return { lv: () => true, lo: z0, hi: z1, rect: null }; }
  const cur = mainLevel(lv()), ids = new Set([cur, ...trimsOf(cur)].map(l => l.id));
  return { lv: id => ids.has(id), lo: -Infinity, hi: Infinity, rect: null };
}
const inView = (V, s) => V.lv(s.lid) && s.z1 > V.lo + 1e-6 && s.z0 < V.hi - 1e-6 && (!V.rect || (s.x >= V.rect.x && s.x < V.rect.x + V.rect.w && s.y >= V.rect.y && s.y < V.rect.y + V.rect.h));
const clipSeg = (V, s) => [Math.max(s.z0, V.lo), Math.min(s.z1, V.hi)];
// Every connected block of seed's material in the view: [{ s, z0, z1 }].
function pgChunk(seed, V) {
  const I = pgIndex(), P = S.plan, W = P.w, out = [], seen = new Set([seed.id]), stack = [seed];
  while (stack.length) {
    const s = stack.pop(), [a, b] = clipSeg(V, s);
    out.push({ s, z0: a, z1: b });
    const nb = (c, test) => { for (const t of I.cols.get(c) || []) if (!seen.has(t.id) && t.mat === s.mat && inView(V, t) && test(clipSeg(V, t))) { seen.add(t.id); stack.push(t); } };
    nb(s.c, ([c0, c1]) => c0 <= b + 1e-6 && c1 >= a - 1e-6);              // above, below or overlapping in the square
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const x = s.x + dx, y = s.y + dy;
      if (x >= 0 && y >= 0 && x < W && y < P.h) nb(y * W + x, ([c0, c1]) => c0 < b - 1e-6 && c1 > a + 1e-6);   // beside it, sharing a face
    }
  }
  return out;
}
// The hidden-core blocks touching a chunk's blocks in their own squares, above or below.
function pgCores(parts) {
  const I = pgIndex(), out = [], seen = new Set(parts.map(p => p.s.id));
  for (const p of parts) for (const t of I.cols.get(p.s.c) || []) {
    if (!t.core || seen.has(t.id)) continue;
    if (Math.abs(t.z0 - p.z1) < 1e-6 || Math.abs(t.z1 - p.z0) < 1e-6) { seen.add(t.id); out.push({ s: t, z0: t.z0, z1: t.z1 }); }
  }
  return out;
}
// The segment a click means in square (x, y) at height z (or the main piece the view shows there).
function pgSegAt(x, y, V, z) {
  const I = pgIndex(), list = (I.cols.get(y * S.plan.w + x) || []).filter(s => inView(V, s));
  if (!list.length) return null;
  if (z != null) return list.find(s => s.z0 <= z + 1e-6 && s.z1 >= z - 1e-6 && !s.core) || list.find(s => s.z0 <= z + 1e-6 && s.z1 >= z - 1e-6) || null;
  const cur = lv(), own = list.filter(s => s.lid === cur.id || layerOn());
  const pool = own.length ? own : list;
  return pool.slice().reverse().find(s => !s.core && s.z1 - s.z0 > FLOOR_T + 1e-6) || pool[pool.length - 1];
}

// ---------------------------------------------------------------------------
// Progress: built blocks, as runs of half-metre courses per material per square, and placed items.
// ---------------------------------------------------------------------------
const PROG = { planId: null, built: new Map(), items: new Set(), ver: 0, unsub: null, myRevs: new Set(), hist: [] };
const hh = z => Math.round(z / BLOCK_H);
const itemKey = it => `${it.type}|${it.level}|${it.x}|${it.y}|${it.rot}`;
function progRuns(mat, c, make) { let m = PROG.built.get(mat); if (!m) { if (!make) return null; PROG.built.set(mat, m = new Map()); } let iv = m.get(c); if (!iv && make) m.set(c, iv = []); return iv || null; }
function progSet(mat, c, z0, z1, on) {
  const a = hh(z0), b = hh(z1);
  if (b <= a) return;
  const iv = progRuns(mat, c, on);
  if (!iv) return;
  let out = [];
  for (const [p, q] of iv) { if (q <= a || p >= b) out.push([p, q]); else { if (p < a) out.push([p, a]); if (q > b) out.push([b, q]); } }
  if (on) out.push([a, b]);
  out.sort((u, v) => u[0] - v[0]);
  const merged = [];
  for (const r of out) { const l = merged[merged.length - 1]; if (l && r[0] <= l[1]) l[1] = Math.max(l[1], r[1]); else merged.push(r.slice()); }
  const m = PROG.built.get(mat);
  if (merged.length) m.set(c, merged); else m.delete(c);
}
// Built length of [z0, z1) in a square, in blocks.
function progBuilt(mat, c, z0, z1) {
  const iv = progRuns(mat, c, false);
  if (!iv) return 0;
  const a = hh(z0), b = hh(z1);
  let n = 0;
  for (const [p, q] of iv) n += Math.max(0, Math.min(q, b) - Math.max(p, a));
  return n * (CM() / BLOCK_H) ** 2;
}
const partBlocks = p => blocksIn(p.z0, p.z1);
const partBuilt = p => progBuilt(p.s.mat, p.s.c, p.z0, p.z1);
// The progress as a document: runs per material as "square:from-to,from-to;…" in base 36 (heights offset so
// none is negative), packed when it's big.
const PROG_OFF = 2000;
function progEncode() {
  const built = {}, W = S.plan.w;
  for (const [mat, m] of PROG.built) {
    const parts = [];
    for (const [c, iv] of m) if (iv.length) parts.push(c.toString(36) + ':' + iv.map(([a, b]) => (a + PROG_OFF).toString(36) + '-' + (b + PROG_OFF).toString(36)).join(','));
    if (parts.length) built[mat] = parts.join(';');
  }
  const body = { built, items: [...PROG.items] }, json = JSON.stringify(body);
  const doc = { v: 1, w: W, rev: uid('g'), editor: 'page', updatedAt: Date.now() };
  if (json.length > 60000 && typeof pako !== 'undefined') { doc.zip = 1; doc.z = bytesToB64(pako.deflateRaw(json, { level: 9 })); } else Object.assign(doc, body);
  return doc;
}
function progDecode(d) {
  PROG.built = new Map(); PROG.items = new Set();
  if (!d) return;
  let body = d;
  if (typeof d.z === 'string') { try { body = JSON.parse(pako.inflateRaw(b64ToBytes(d.z), { to: 'string' })); } catch { return; } }
  const W = S.plan.w, w0 = Number(d.w) || W;
  for (const [mat, str] of Object.entries(body.built || {})) {
    const m = new Map();
    for (const part of String(str).split(';')) {
      const [cs, rs] = part.split(':');
      if (!rs) continue;
      let c = parseInt(cs, 36);
      if (w0 !== W) { const x = c % w0, y = Math.floor(c / w0); if (x >= W) continue; c = y * W + x; }
      m.set(c, rs.split(',').map(r => r.split('-').map(v => parseInt(v, 36) - PROG_OFF)).filter(([a, b]) => b > a));
    }
    PROG.built.set(mat, m);
  }
  for (const k of body.items || []) PROG.items.add(String(k));
}
function progSubscribe(id) {
  if (PROG.unsub) { try { PROG.unsub(); } catch { /* ignore */ } PROG.unsub = null; }
  PROG.planId = id; PROG.built = new Map(); PROG.items = new Set(); PROG.hist = []; PROG.ver++;
  if (!id || !S.store) return;
  PROG.unsub = S.store.subscribeDoc('progress/' + id, d => {
    if (PROG.planId !== id || !S.plan) return;
    if (d && d.rev && PROG.myRevs.has(d.rev)) return;           // (our own save coming back)
    progDecode(d); progChanged(false);
  }, () => {});
}
let progSaveT = 0;
function progSave() {
  clearTimeout(progSaveT);
  const id = PROG.planId;
  progSaveT = setTimeout(() => {
    if (!S.store || S.readOnly || id !== PROG.planId || !S.plan) return;
    const doc = progEncode();
    PROG.myRevs.add(doc.rev); if (PROG.myRevs.size > 40) PROG.myRevs.delete(PROG.myRevs.values().next().value);
    S.store.saveDoc('progress/' + id, doc).catch(() => toast('Couldn’t save the build progress. Try again.', 'bad'));
  }, 900);
}
// After any change to the progress: redraw what shows it, and save.
function progChanged(save = true) {
  PROG.ver++;
  if (save) progSave();
  affordCache.key = '';
  req2d();
  if (progressShown() && S.view !== '2d') mark3d();
  if (S.tab === 'build') renderBuildPane();
}
function progSnapshot() { PROG.hist.push(JSON.stringify(progEncode())); if (PROG.hist.length > 20) PROG.hist.shift(); }
function progUndo() {
  const s = PROG.hist.pop();
  if (!s) { toast('No marks to undo.'); return; }
  progDecode(JSON.parse(s)); progChanged();
}
const progressShown = () => !!S.plan && (S.tool === 'built' || S.opt.progress || S.opt.afford);

// Mark (or unmark) a list of parts, and placed items.
function progMark(parts, on, label) {
  progSnapshot();
  for (const p of parts) progSet(p.s.mat, p.s.c, p.z0, p.z1, on);
  progChanged();
  const n = parts.reduce((t, p) => t + partBlocks(p), 0);
  if (label !== false) toast(`${on ? 'Marked' : 'Unmarked'} ${n.toLocaleString()} block${n === 1 ? '' : 's'}${label ? ' · ' + label : ''}.`);
}
function toggleItemPlaced(it) {
  progSnapshot();
  const k = itemKey(it), on = !PROG.items.has(k);
  if (on) PROG.items.add(k); else PROG.items.delete(k);
  progChanged();
  toast(`${it.label}: ${on ? 'placed' : 'not placed yet'}.`);
}
// What a click with the tool takes: the chunk, everything connected (Alt), or one square or block (Shift).
function progPartsFor(seg, V, e) {
  if (e.shiftKey) { const [a, b] = clipSeg(V, seg); return [{ s: seg, z0: a, z1: b }]; }
  const parts = pgChunk(seg, V);
  return seg.core ? parts : parts.concat(pgCores(parts));
}
const allBuilt = parts => parts.every(p => partBuilt(p) >= partBlocks(p) - 1e-6);

// ---- the tool in 2D: click a chunk, Shift one square, Alt everything connected, drag over squares, right-click unmarks
function builtDown(gx, gy, cx, cy, e) {
  if (!S.plan || S.readOnly) return;
  const it = hitItem(gx, gy);
  if (it && it.type !== 'spawn') { toggleItemPlaced(it); return; }
  const V = pgView('2d', e.altKey), seg = inB(cx, cy) && pgSegAt(cx, cy, V);
  if (!seg) return;
  const parts = progPartsFor(seg, V, e), on = e.button === 2 ? false : !allBuilt(parts);
  progMark(parts, on, seg.name);
  if (!e.shiftKey && !e.altKey) G = { type: 'built', mat: seg.mat, on, last: [cx, cy], V };
}
function builtMove(cx, cy) {
  if (cx === G.last[0] && cy === G.last[1]) return;
  const parts = [];
  for (const [x, y] of lineCells(G.last[0], G.last[1], cx, cy)) {
    if (!inB(x, y)) continue;
    for (const s of pgIndex().cols.get(y * S.plan.w + x) || []) if (s.mat === G.mat && inView(G.V, s)) { const [a, b] = clipSeg(G.V, s); parts.push({ s, z0: a, z1: b }); }
  }
  G.last = [cx, cy];
  if (!parts.length) return;
  for (const p of parts) progSet(p.s.mat, p.s.c, p.z0, p.z1, G.on);
  progChanged();
}
// ---- the tool in 3D
function built3dClick(cx, cy, e, unmark) {
  if (!S.plan || S.readOnly) return;
  const hit = bmHit(cx, cy);
  if (!hit) return;
  if (hit.type === 3) { const it = item3dAt(cx, cy); if (it) toggleItemPlaced(it); return; }
  if (hit.type !== 1) return;
  const V = pgView('3d', e.altKey), seg = pgSegAt(hit.x, hit.z, V, (hit.k + 0.5) * CM());
  if (!seg) return;
  const parts = progPartsFor(seg, V, e.shiftKey ? { shiftKey: true } : e);
  const one = e.shiftKey ? [{ s: seg, z0: Math.max(seg.z0, hit.k * CM()), z1: Math.min(seg.z1, (hit.k + 1) * CM()) }] : parts;
  progMark(one, unmark ? false : !allBuilt(one), seg.name);
}
function item3dAt(cx, cy) {
  const THREE = window.THREE, r = c3d.getBoundingClientRect(), ray = new THREE.Raycaster();
  ray.setFromCamera(new THREE.Vector2((cx - r.left) / r.width * 2 - 1, -(cy - r.top) / r.height * 2 + 1), V3.camera);
  const m = V3.meshes.filter(o => o.isInstancedMesh && o.material === V3.matItem && o.userData.meta);
  const hit = ray.intersectObjects(m, false)[0], src = hit && hit.object.userData.meta[hit.instanceId];
  return src && src.item ? findItem(src.item) : null;
}

// ---------------------------------------------------------------------------
// What you can afford: the chunks the view shows, by material, given blocks largest first while whole chunks
// fit what you have (green); then any you're close to (three-quarters or more of it covered: amber); the rest
// red. Built chunks are left out.
// ---------------------------------------------------------------------------
const affordCache = { key: '', status: null, chunks: null };
const AFFORD_COL = { ok: '#3fae5a', craft: '#2fa7b8', near: '#d9a23a', no: '#d45050' };
const haveOf = name => invHave(name);                   // (the Inventory tab's counts)
function affordStatus(where) {
  const key = [S.planId, planVer, PROG.ver, where, layerOn() ? curLayer() : 'L' + S.levelIdx, S.opt.cut, S.section ? JSON.stringify(S.section) : '', INV.ver].join('#');
  if (affordCache.key === key) return affordCache;
  const I = pgIndex(), V = pgView(where, false), seen = new Set(), chunks = [];
  for (const s of I.segs) {
    if (seen.has(s.id) || s.core || !inView(V, s)) continue;
    const parts = pgChunk(s, V);
    for (const p of parts) seen.add(p.s.id);
    const need = parts.reduce((t, p) => t + partBlocks(p) - partBuilt(p), 0);
    chunks.push({ name: s.name, parts, need: Math.max(0, Math.round(need)) });
  }
  const status = new Map(), byName = new Map();
  for (const c of chunks) { if (!byName.has(c.name)) byName.set(c.name, []); byName.get(c.name).push(c); }
  for (const [name, list] of byName) {
    let left = haveOf(name);
    const todo = list.filter(c => c.need > 0).sort((a, b) => b.need - a.need);
    for (const c of todo) if (c.need <= left) { c.st = 'ok'; left -= c.need; }
    // then what you could craft now from what you have (the smart count), for the chunks still waiting
    const wait = todo.filter(c => !c.st), more = wait.length ? smartCount(name, wait.reduce((t, c) => t + c.need, 0) + left).craftable : 0;
    left += more;
    for (const c of wait) if (c.need <= left) { c.st = 'craft'; left -= c.need; }
    for (const c of todo) if (!c.st) c.st = left >= 0.75 * c.need ? 'near' : 'no';
    for (const c of list) { if (!c.st) c.st = 'built'; for (const p of c.parts) status.set(p.s.id, c.st); }
  }
  Object.assign(affordCache, { key, status, chunks });
  return affordCache;
}

// ---------------------------------------------------------------------------
// Drawing: in 2D, built squares faded with a tick (a bar along the bottom when only part is built), and, with
// "what I can afford" on, the chunks green, amber or red. In 3D the blocks are recoloured as build3d draws them.
// ---------------------------------------------------------------------------
const progDrawCache = { key: '', frac: null, st: null };
function drawProgress2d(g, cam, x0, x1, y0, y1) {
  if (!progressShown()) return;
  const P = S.plan, W = P.w, s = cam.s;
  const key = [S.planId, planVer, PROG.ver, layerOn() ? 'k' + curLayer() : 'L' + S.levelIdx, S.opt.afford, INV.ver].join('#');
  if (progDrawCache.key !== key) {
    const I = pgIndex(), V = pgView('2d', false), frac = new Float32Array(W * P.h).fill(-1), st = new Uint8Array(W * P.h);
    const A = S.opt.afford ? affordStatus('2d') : null, code = { ok: 1, near: 2, no: 3, built: 4, craft: 5 };
    for (const [c, list] of I.cols) {
      let tot = 0, done = 0, big = -1;
      for (const sg of list) {
        if (!inView(V, sg)) continue;
        const [a, b] = clipSeg(V, sg), n = blocksIn(a, b);
        tot += n; done += progBuilt(sg.mat, c, a, b);
        if (A && !sg.core && n > big) { big = n; st[c] = code[A.status.get(sg.id)] || 0; }   // (the square shows its biggest piece's chunk)
      }
      if (tot) frac[c] = done / tot;
    }
    Object.assign(progDrawCache, { key, frac, st });
  }
  const { frac, st } = progDrawCache, tick = s >= 12;
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
    const c = y * W + x, f = frac[c];
    if (f < 0) continue;
    const px = cam.ox + x * s, py = cam.oy + y * s, k = st[c];
    if (S.opt.afford && k && k !== 4) { g.fillStyle = hexA(k === 1 ? AFFORD_COL.ok : k === 5 ? AFFORD_COL.craft : k === 2 ? AFFORD_COL.near : AFFORD_COL.no, 0.42); g.fillRect(px, py, s, s); }
    if (f >= 0.999) {
      g.fillStyle = hexA(T.sheet, 0.55); g.fillRect(px, py, s, s);
      if (tick) { g.strokeStyle = hexA(T.ink, 0.8); g.lineWidth = Math.max(1.2, s * 0.09); g.beginPath(); g.moveTo(px + s * 0.25, py + s * 0.52); g.lineTo(px + s * 0.43, py + s * 0.7); g.lineTo(px + s * 0.76, py + s * 0.32); g.stroke(); }
    } else if (f > 0) { g.fillStyle = hexA(T.accent, 0.9); g.fillRect(px + 1, py + s - Math.max(2, s * 0.14), (s - 2) * f, Math.max(2, s * 0.14)); }
  }
}
// The colours build3d gives blocks while the progress shows: greyed when built; green, amber or red by what you
// can afford. Worked out once per drawing; null when the progress isn't showing.
const progGrey = c => tint(c, 0.55);
function progColourFn() {
  if (!progressShown() || WALK.on) return null;
  const P = S.plan, I = pgIndex(), A = S.opt.afford ? affordStatus('3d') : null;
  const matOf = new Map(Object.entries(P.palette).map(([k, e]) => [k, matKeyOf(e)]));
  const placed = new Set(P.items.filter(it => PROG.items.has(itemKey(it))).map(it => it.id));
  const tints = new Map();
  const mix = (c, st) => { const k = c + st; if (!tints.has(k)) tints.set(k, st === 'built' ? progGrey(c) : mixHex(c, AFFORD_COL[st], 0.55)); return tints.get(k); };
  return (src, y0, sy, c) => {
    if (!src || src.earth) return c;
    if (src.item) return placed.has(src.item) ? mix(c, 'built') : c;
    const mat = matOf.get(src.k);
    if (!mat) return c;
    const col = src.y * P.w + src.x;
    if (progBuilt(mat, col, y0, y0 + sy) >= blocksIn(y0, y0 + sy) - 1e-6) return mix(c, 'built');
    if (!A) return c;
    const seg = (I.cols.get(col) || []).find(q => q.mat === mat && q.z0 <= y0 + 1e-6 && q.z1 >= y0 + sy - 1e-6), st = seg && A.status.get(seg.id);
    return st === 'ok' || st === 'craft' || st === 'near' || st === 'no' ? mix(c, st) : c;
  };
}
function mixHex(a, b, t) {
  const p = h2 => [parseInt(h2.slice(1, 3), 16), parseInt(h2.slice(3, 5), 16), parseInt(h2.slice(5, 7), 16)];
  const A = p(a.length === 4 ? '#' + [...a.slice(1)].map(q => q + q).join('') : a), B = p(b);
  return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, '0')).join('');
}

// ---------------------------------------------------------------------------
// The Build tab: progress overall, by group of levels, and by material, with the blocks you have (shared by all
// your plans) and what's left to place; switches for showing the progress and what you can afford.
// ---------------------------------------------------------------------------
function progHaveChanged() { affordCache.key = ''; progDrawCache.key = ''; req2d(); if (S.opt.afford && S.view !== '2d') mark3d(); if (S.tab === 'build') renderBuildPane(); }
const statsCache = { key: '', v: null };
function buildStats() {
  const key = [S.planId, planVer, PROG.ver].join('#');
  if (statsCache.key === key) return statsCache.v;
  const P = S.plan, I = pgIndex(), byMat = new Map(), byLevel = new Map();
  let tot = 0, done = 0;
  for (const s of I.segs) {
    const n = blocksIn(s.z0, s.z1), b = progBuilt(s.mat, s.c, s.z0, s.z1);
    tot += n; done += b;
    const m = byMat.get(s.name) || { name: s.name, color: s.color, n: 0, b: 0 };
    m.n += n; m.b += b; byMat.set(s.name, m);
    const l = byLevel.get(s.lid) || { n: 0, b: 0 };
    l.n += n; l.b += b; byLevel.set(s.lid, l);
  }
  const real = P.items.filter(it => it.type !== 'spawn' && !it.type.startsWith('npc-'));
  const placed = real.filter(it => PROG.items.has(itemKey(it))).length;
  const v = { tot, done, byMat: [...byMat.values()].sort((a, b) => (b.n - b.b) - (a.n - a.b)), byLevel, items: real.length, placed };
  statsCache.key = key; statsCache.v = v;
  return v;
}
function renderBuildPane() {
  const pane = $('#pane-build');
  if (!pane) return;
  if (!S.plan) { pane.replaceChildren(); return; }
  const P = S.plan, st = buildStats(), pct = (b, n) => (n ? Math.floor(b / n * 100) : 0);
  const bar = (b, n) => h('div', { class: 'lim-bar' }, h('i', { style: `width:${n ? Math.min(100, b / n * 100).toFixed(1) : 0}%` }));
  const sw = (key, label, tip) => h('button', { type: 'button', class: 'toggle', 'aria-pressed': String(!!S.opt[key]), title: tip, onclick: () => { S.opt[key] = !S.opt[key]; LS.set('opt', S.opt); progDrawCache.key = ''; req2d(); mark3d(); renderBuildPane(); renderOptbar(); } }, label);
  const groups = levelGroups(P);
  const groupRows = groups.map(G => {
    let n = 0, b = 0;
    for (const it of G.items) for (const L of [it.L, ...it.trims.map(t => t.L)]) { const v = st.byLevel.get(L.id); if (v) { n += v.n; b += v.b; } }
    return n ? h('div', { class: 'lim' }, h('div', { class: 'lim-top' }, h('span', { text: G.name }), h('span', { class: 'mono', text: `${pct(b, n)}% · ${(n - b).toLocaleString()} left` })), bar(b, n)) : null;
  }).filter(Boolean);
  const matRows = st.byMat.map(m => smartRow(m.name, Math.round(m.n - m.b), m.color, `${Math.round(m.b).toLocaleString()} of ${Math.round(m.n).toLocaleString()} blocks built`, 'block'));
  const items = planItemNeeds(), itemRows = items.filter(n => n.left > 0).map(n => smartRow(n.name, n.left, '#8a7a6a', `${n.total - n.left} of ${n.total} placed`, 'item'));
  const legend = S.opt.afford ? h('div', { class: 'afford-legend' }, ...[['ok', 'ready'], ['craft', 'craft first'], ['near', 'close'], ['no', 'short']].map(([k, t]) => h('span', null, h('i', { style: `background:${AFFORD_COL[k]}` }), t))) : null;
  pane.replaceChildren(...[
    h('div', { class: 'pane-head' }, h('h3', { text: 'Build' }), h('span', { class: 'note', text: 'J marks blocks built' })),
    h('div', { class: 'btnrow' }, sw('progress', 'Show progress', 'Fade what’s built, in 2D and 3D'), sw('afford', 'What I can afford', 'Colour the chunks you can build with the blocks you have green; ones you could craft the blocks for now teal; amber when you’re close; red when you’re short')),
    legend,
    h('div', { class: 'section' },
      h('div', { class: 'lim' }, h('div', { class: 'lim-top' }, h('b', { text: `${pct(st.done, st.tot)}% built` }), h('span', { class: 'mono', text: `${Math.round(st.done).toLocaleString()} of ${Math.round(st.tot).toLocaleString()} blocks` })), bar(st.done, st.tot)),
      st.items ? h('div', { class: 'lim' }, h('div', { class: 'lim-top' }, h('span', { text: 'Items placed' }), h('span', { class: 'mono', text: `${st.placed} of ${st.items}` })), bar(st.placed, st.items)) : null),
    stepsSection(),
    groupRows.length > 1 ? h('div', { class: 'section' }, h('h4', { text: 'By area' }), ...groupRows) : null,
    h('div', { class: 'section' }, h('h4', { text: 'Blocks: what you have, can craft, and still need' }),
      h('p', { class: 'note', text: 'Have counts come from the Inventory tab, shared by all your plans: click one to change it there. Each plan counts them against its own needs. Open a row for what it’s made from. Each row counts everything you have, so rows sharing a material both show what they could make: update the counts after crafting and the rest follow.' }),
      h('div', { class: 'bmat-head' }, h('span'), h('span', { text: 'Block' }), h('span', { text: 'Left' }), h('span', { text: 'Have' })),
      h('ul', { class: 'plainlist bmats' }, ...matRows)),
    itemRows.length ? h('div', { class: 'section' }, h('h4', { text: `Items still to place · ${items.reduce((t, n) => t + n.left, 0)}` }),
      h('div', { class: 'bmat-head' }, h('span'), h('span', { text: 'Item' }), h('span', { text: 'Left' }), h('span', { text: 'Have' })),
      h('ul', { class: 'plainlist bmats' }, ...itemRows)) : null,
    h('div', { class: 'btnrow' }, h('button', { class: 'btn btn-sm btn-danger', type: 'button', disabled: S.readOnly, text: 'Clear this plan’s progress', onclick: async () => {
      if (!(await confirmBox('Clear the progress?', `Every block and item marked built in “${P.name}” goes back to not built. Ctrl+Z with the Mark built tool undoes it.`, 'Clear progress', true))) return;
      progSnapshot(); PROG.built = new Map(); PROG.items = new Set(); progChanged();
    } })),
  ].filter(Boolean));
}
// A row of the smart count: what's left, what you have, what you can craft now, what's still to gather; opened,
// what it's made from (the whole chain), each with its own Have box.
function smartRow(name, left, color, tip, kind) {
  const sc = smartCount(name, left), have = haveOf(name);
  S.bmOpen = S.bmOpen || new Set();
  const open = S.bmOpen.has(name), noun = kind === 'item' ? '' : ' blocks';
  const crafts = n => `${n} craft${n === 1 ? '' : 's'}`;
  const bits = [];
  if (left === 0) bits.push(['done', kind === 'item' ? 'all placed' : 'all built']);
  else {
    bits.push([have >= left ? 'ok' : '', `${Math.min(have, left).toLocaleString()} / ${left.toLocaleString()} in inventory`]);
    if (have < left) {
      if (sc.finishes) bits.push(['craft', `craft the rest: ${crafts(sc.runs)}${sc.craftable > sc.rest ? ` (makes ${sc.craftable.toLocaleString()})` : ''}`]);
      else if (sc.craftable) bits.push(['craft', `${sc.craftable.toLocaleString()} craftable (${crafts(sc.runs)})`]);
      else if (sc.recipe) bits.push(['', 'nothing craftable yet']);
      if (!sc.recipe && kind === 'item') bits.push(['', 'no recipe in the 1.0 data']);
      else if (sc.gather.size) bits.push(['short', `gather ${[...sc.gather].map(([k, v]) => `${Math.ceil(v).toLocaleString()} ${k}`).join(', ')}`]);
    }
  }
  const made = sc.recipe && left > 0 ? h('button', { class: 'iconbtn sm btn-ghost bm-open', type: 'button', 'aria-expanded': String(open), title: open ? 'Hide what it’s made from' : 'What it’s made from, with what you have',
    onclick: () => { if (open) S.bmOpen.delete(name); else S.bmOpen.add(name); renderBuildPane(); }, html: svg(open ? '<path d="m6 15 6-6 6 6"/>' : '<path d="m6 9 6 6 6-6"/>') }) : h('span');
  const li = h('li', { class: 'bmat', 'data-mat': kind === 'block' ? name : null },
    h('span', { class: 'swatch sm', style: `background:${color}` }),
    h('span', { class: 'bm-text' }, h('span', { class: 'bm-name', text: name, title: tip }),
      h('span', { class: 'bm-sub' }, ...bits.flatMap(([c, t], i) => [i ? ' · ' : null, h('span', { class: 'bm-st ' + c, text: t })]).filter(x => x !== null))),
    h('span', { class: 'mono bm-left', text: left ? left.toLocaleString() : '✓' }),
    h('span', { class: 'bm-have' }, haveBtn(name), made));
  if (!open || !sc.recipe || !left) return li;
  const seen = new Set(), rows = [];
  for (const c of chainOf(name)) {
    if (seen.has(c.item)) continue;
    seen.add(c.item);
    const part = !!recipeFor(c.item), runs = sc.parts.get(c.item), short = sc.gather.get(c.item);
    rows.push(h('li', { class: 'bm-ing', style: `padding-left:${8 + c.depth * 14}px` },
      h('span', { class: 'bm-name', text: c.item }),
      h('span', { class: 'note', text: `${fmt(c.qty)} a craft${part ? ' · made from the ones below' : ''}${runs ? ` · make ${crafts(runs)}` : ''}${short ? ` · short ${Math.ceil(short).toLocaleString()}` : ''}` }),
      haveBtn(c.item)));
  }
  return h('li', { class: 'bmat-wrap' }, li, h('ul', { class: 'plainlist bm-ings' }, ...rows));
}
function builtControls() {
  const sw = (key, label) => h('button', { type: 'button', class: 'toggle', 'aria-pressed': String(!!S.opt[key]), onclick: () => { S.opt[key] = !S.opt[key]; LS.set('opt', S.opt); progDrawCache.key = ''; req2d(); mark3d(); renderOptbar(); if (S.tab === 'build') renderBuildPane(); } }, label);
  return [sw('afford', 'What I can afford'), h('button', { class: 'btn btn-sm', type: 'button', text: 'Build tab', onclick: () => { openTab('build'); LS.set('tab', 'build'); } }),
    h('span', { class: 'hint', text: 'Click marks a chunk built · Shift one block · Alt everything connected · drag over squares · right-click unmarks · Ctrl+Z undoes a mark' })];
}

// ---------------------------------------------------------------------------
// Hover highlighting: a material, item or level hovered in the panel lights up in 2D and 3D, the rest dimmed.
// { type: 'mat', keys: Set of symbols } | { type: 'items', ids: Set } | { type: 'level', ids: Set of level ids }
// ---------------------------------------------------------------------------
let hlT = 0, STEP_M = null;
function hlSet(hl, fromStep) {
  if (!hl && !fromStep && S.stepHl) hl = S.stepHl;            // (the step being followed stays highlighted)
  const same = JSON.stringify(hl && { ...hl, keys: hl.keys && [...hl.keys], ids: hl.ids && [...hl.ids] }) === JSON.stringify(S.hl && { ...S.hl, keys: S.hl.keys && [...S.hl.keys], ids: S.hl.ids && [...S.hl.ids] });
  if (same) return;
  S.hl = hl;
  req2d();
  clearTimeout(hlT); hlT = setTimeout(hl3d, hl ? 60 : 0);
}
function hl3d() {
  if (!V3.ok) return;
  if (V3.hlMesh) { V3.group.remove(V3.hlMesh); V3.hlMesh.dispose && V3.hlMesh.dispose(); V3.hlMesh = null; }
  const dim = !!S.hl;
  for (const m of [V3.matSolid, V3.matItem]) { m.transparent = dim; m.opacity = dim ? 0.16 : 1; m.depthWrite = !dim; m.needsUpdate = true; }
  if (!S.hl) { render3d(); return; }
  const THREE = window.THREE, P = S.plan, hl = S.hl, src = [];
  if (!STEP_M) STEP_M = new THREE.Matrix4();
  for (const mesh of V3.meshes) {
    if (!mesh.isInstancedMesh || !mesh.userData.meta) continue;
    const meta = mesh.userData.meta;
    for (let i = 0; i < meta.length; i++) {
      const m = meta[i];
      if (!m) continue;
      let hit = hl.type === 'mat' ? (m.k && hl.keys.has(m.k)) : hl.type === 'items' ? (m.item && hl.ids.has(m.item)) : hl.type === 'level' ? (m.lid && hl.ids.has(m.lid)) : false;
      if (hl.type === 'step' && m.lid && hl.lids.has(m.lid) && hl.cells.has(m.y * P.w + m.x)) { mesh.getMatrixAt(i, STEP_M); const y0 = STEP_M.elements[13]; hit = y0 >= hl.z0 - 1e-6 && y0 < hl.z1 - 1e-6; }
      if (hit) src.push([mesh, i]);
    }
  }
  if (!src.length) { render3d(); return; }
  const mesh = new THREE.InstancedMesh(V3.box, new THREE.MeshLambertMaterial({ emissive: new THREE.Color(T.accent), emissiveIntensity: 0.25 }), src.length);
  const M = new THREE.Matrix4(), c = new THREE.Color();
  src.forEach(([m, i], j) => { m.getMatrixAt(i, M); mesh.setMatrixAt(j, M); if (m.instanceColor) { m.getColorAt(i, c); mesh.setColorAt(j, c); } });
  mesh.instanceMatrix.needsUpdate = true; if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  V3.hlMesh = mesh; V3.group.add(mesh);
  render3d();
}
// In 2D: the highlighted squares outlined, everything else dimmed.
function drawHighlight2d(g, cam, x0, x1, y0, y1, grid) {
  const hl = S.hl;
  if (!hl || !S.plan) return;
  const P = S.plan, s = cam.s;
  if (hl.type === 'items') {
    g.strokeStyle = T.accent; g.lineWidth = 2.5;
    for (const it of P.items) if (hl.ids.has(it.id) && it.level === lv().id) { const R = itemRect(it); g.strokeRect(cam.ox + R.x * s - 2, cam.oy + R.y * s - 2, R.w * s + 4, R.h * s + 4); }
    return;
  }
  let match;
  if (hl.type === 'mat') match = (x, y) => { const c = grid[y][x]; if (c === ' ') return false; const e = P.palette[c]; return hl.keys.has(c) || (e && e.under && hl.keys.has(e.under)); };
  else if (hl.type === 'level') { const Ls = P.levels.filter(l => hl.ids.has(l.id)); match = (x, y) => Ls.some(L => L.grid[y][x] !== ' '); }
  else if (hl.type === 'step') match = (x, y) => hl.cells.has(y * P.w + x);
  else return;
  g.fillStyle = hexA(T.sheet, 0.62);
  const on = [];
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) { if (match(x, y)) on.push([x, y]); else if (grid[y][x] !== ' ') g.fillRect(cam.ox + x * s, cam.oy + y * s, s, s); }
  if (!on.length) return;
  const set = new Set(on.map(([x, y]) => y * P.w + x));
  g.beginPath();
  for (const [x, y] of on) {
    const px = cam.ox + x * s, py = cam.oy + y * s;
    if (!set.has((y - 1) * P.w + x)) { g.moveTo(px, py); g.lineTo(px + s, py); }
    if (!set.has((y + 1) * P.w + x)) { g.moveTo(px, py + s); g.lineTo(px + s, py + s); }
    if (!set.has(y * P.w + x - 1)) { g.moveTo(px, py); g.lineTo(px, py + s); }
    if (!set.has(y * P.w + x + 1)) { g.moveTo(px + s, py); g.lineTo(px + s, py + s); }
  }
  g.strokeStyle = T.accent; g.lineWidth = 1.8; g.stroke();
}
// The panel's rows say what they stand for; hovering one highlights it.
function bindHighlights() {
  const keysOfName = name => new Set(Object.entries(S.plan.palette).filter(([, e]) => matName(e.name) === name).map(([k]) => k));
  const on = (root, pick) => {
    root.addEventListener('pointerover', e => { if (!S.plan || e.pointerType === 'touch') return; const h0 = pick(e.target); if (h0 !== undefined) hlSet(h0); });
    root.addEventListener('pointerleave', () => hlSet(null));
  };
  on($('#pane-materials'), t => {
    const v = t.closest('.variant[data-k]');
    if (v) return { type: 'mat', keys: new Set([v.dataset.k]) };
    const li = t.closest('li.mat');
    if (!li) return null;
    return { type: 'mat', keys: new Set(li.dataset.ks ? [...li.dataset.ks] : li.dataset.k ? [li.dataset.k] : []) };
  });
  on($('#pane-build'), t => { const li = t.closest('li.bmat'); return li && li.dataset.mat ? { type: 'mat', keys: keysOfName(li.dataset.mat) } : null; });
  on($('#pane-items'), t => { const b = t.closest('[data-items]'); return b ? { type: 'items', ids: new Set(b.dataset.items.split(',')) } : null; });
  on($('#pane-levels'), t => { const b = t.closest('[data-lids]'); return b ? { type: 'level', ids: new Set(b.dataset.lids.split(',')) } : null; });
  on($('#hstrip'), t => { const b = t.closest('[data-lids]'); return b ? { type: 'level', ids: new Set(b.dataset.lids.split(',')) } : null; });
}
