// ---------------------------------------------------------------------------
// Building in 3D, ghost previews, camera presets and the section box (planner v47).
// With Paint, a click on a block face in 3D puts a block of the brush's material against it (on the ground, on
// the ground); right-click (or a click with Erase) takes one away; Ctrl+drag does either along the surface you
// started on. Each block goes through layer painting (layerPaint), so it lands on the right level, and a block
// taken from the middle of a run splits the run onto a trim level. Select still inspects.
// The block map: every course drawn in 3D, one byte a square (1 a block, 2 the ground, 3 an item, 4 glass),
// filled as build3d draws, so the pointer's ray can be traced square by square however big the plan is.
// ---------------------------------------------------------------------------
function bmStart(P) {
  const cm = P.cell;
  const lo = Math.min(0, ...P.levels.map(l => l.elev)) - 8, hi = Math.max(GAME.levelH, ...P.levels.map(l => l.elev + l.height)) + 8;
  const k0 = Math.floor(lo / cm), K = Math.ceil(hi / cm) - k0;
  V3.bm = { W: P.w, H: P.h, k0, K, cm, a: new Uint8Array(P.w * P.h * K) };
}
function bmMark(x, y, z, sx, sy, sz, t) {
  const B = V3.bm;
  if (!B || !t) return;
  const x0 = Math.max(0, Math.floor(x + 1e-6)), x1 = Math.min(B.W, Math.ceil(x + sx - 1e-6));
  const z0 = Math.max(0, Math.floor(z + 1e-6)), z1 = Math.min(B.H, Math.ceil(z + sz - 1e-6));
  const k0 = Math.max(0, Math.floor(y / B.cm + 1e-6) - B.k0), k1 = Math.min(B.K, Math.ceil((y + sy) / B.cm - 1e-6) - B.k0);
  for (let k = k0; k < k1; k++) for (let zz = z0; zz < z1; zz++) {
    const row = (k * B.H + zz) * B.W;
    for (let xx = x0; xx < x1; xx++) if (!B.a[row + xx] || t === 1) B.a[row + xx] = t;
  }
}
const bmAt = (x, k, z) => { const B = V3.bm; if (!B) return 0; const kk = k - B.k0; return x < 0 || z < 0 || x >= B.W || z >= B.H || kk < 0 || kk >= B.K ? 0 : B.a[(kk * B.H + z) * B.W + x]; };
function bmSet(x, k, z, t) { const B = V3.bm; if (!B) return; const kk = k - B.k0; if (x >= 0 && z >= 0 && x < B.W && z < B.H && kk >= 0 && kk < B.K) B.a[(kk * B.H + z) * B.W + x] = t; }
// The pointer's ray in grid units: x and z in squares, y in courses.
function bmRayAt(cx, cy) {
  const B = V3.bm;
  if (!B || !V3.ok) return null;
  const THREE = window.THREE, r = c3d.getBoundingClientRect(), rc = new THREE.Raycaster();
  rc.setFromCamera(new THREE.Vector2((cx - r.left) / r.width * 2 - 1, -(cy - r.top) / r.height * 2 + 1), V3.camera);
  const gp = V3.group.position, cm = B.cm, ro = rc.ray.origin, rd = rc.ray.direction;
  return { o: [(ro.x - gp.x) / cm, ro.y / cm, (ro.z - gp.z) / cm], d: [rd.x / cm, rd.y / cm, rd.z / cm] };
}
// The first thing the ray meets: { x, k, z, type, face } (face points back at the camera: [dx, dk, dz]), or the
// ground at 0 m where nothing's drawn.
function bmHit(cx, cy) {
  const B = V3.bm, R = bmRayAt(cx, cy);
  if (!R) return null;
  const o = [R.o[0], R.o[1] - B.k0, R.o[2]], d = R.d, dims = [B.W, B.K, B.H];
  let tmin = 0, tmax = Infinity, entry = -1;
  for (let i = 0; i < 3; i++) {
    if (Math.abs(d[i]) < 1e-12) { if (o[i] < 0 || o[i] > dims[i]) return groundHit(R); continue; }
    let t1 = -o[i] / d[i], t2 = (dims[i] - o[i]) / d[i];
    if (t1 > t2) [t1, t2] = [t2, t1];
    if (t1 > tmin) { tmin = t1; entry = i; }
    tmax = Math.min(tmax, t2);
  }
  if (tmin > tmax) return groundHit(R);
  const p = o.map((v, i) => v + d[i] * (tmin + 1e-7));
  const c = p.map((v, i) => clamp(Math.floor(v), 0, dims[i] - 1));
  const step = d.map(v => (v > 0 ? 1 : v < 0 ? -1 : 0)), tDelta = d.map(v => (v ? Math.abs(1 / v) : Infinity));
  const tNext = c.map((ci, i) => (d[i] > 0 ? (ci + 1 - o[i]) / d[i] : d[i] < 0 ? (ci - o[i]) / d[i] : Infinity));
  let face = null;
  if (entry >= 0) { face = [0, 0, 0]; face[entry] = -step[entry]; }
  for (let n = 0; n < 6000; n++) {
    const v = B.a[(c[1] * B.H + c[2]) * B.W + c[0]];
    if (v) return { x: c[0], k: c[1] + B.k0, z: c[2], type: v, face: face || [0, 1, 0] };
    const ax = tNext[0] < tNext[1] ? (tNext[0] < tNext[2] ? 0 : 2) : (tNext[1] < tNext[2] ? 1 : 2);
    if (tNext[ax] > tmax) break;
    c[ax] += step[ax];
    if (c[ax] < 0 || c[ax] >= dims[ax]) break;
    face = [0, 0, 0]; face[ax] = -step[ax];
    tNext[ax] += tDelta[ax];
  }
  return groundHit(R);
}
function groundHit(R) {
  if (R.d[1] >= 0) return null;
  const t = -R.o[1] / R.d[1], x = Math.floor(R.o[0] + R.d[0] * t), z = Math.floor(R.o[2] + R.d[2] * t);
  return inB(x, z) ? { x, k: -1, z, type: 2, face: [0, 1, 0] } : null;
}
// Where the ray crosses the plane of a face (axis ax at position v, in grid units): [x, k, z] as numbers.
function bmPlane(cx, cy, ax, v) {
  const R = bmRayAt(cx, cy);
  if (!R || Math.abs(R.d[ax]) < 1e-9) return null;
  const t = (v - R.o[ax]) / R.d[ax];
  return t > 0 ? [R.o[0] + R.d[0] * t, R.o[1] + R.d[1] * t, R.o[2] + R.d[2] * t] : null;
}

// The symbol 3D building paints with: the brush when it's a run of blocks, else a block of its material.
function block3dSym() {
  const m = S.plan.palette[S.brush];
  if (!m || !['wall', 'block', 'floor', 'roof'].includes(m.kind)) return null;
  return isRun(m) ? S.brush : entryKey({ name: matName(m.name).slice(0, 40), kind: 'block', color: m.color });
}
// Paint (or clear, ' ') square (x, z) on layer k, and its mirrored copies, as Layers mode does.
function paint3d(x, z, k, ch) {
  const [lo, hi] = layerSpan();
  if (k < lo || k > hi) { layerWarn(`No level reaches ${fmt(k * CM())} m. Add one in the Levels tab first.`); return 0; }
  const keep = S.layer;
  let n = 0;
  S.layer = k;                                                 // (layerPaint works on the current layer)
  try { for (const [a, b] of mirrorPts(x, z)) if (layerPaint(a, b, ch)) { n++; bmSet(a, k, b, ch === ' ' ? 0 : 1); } }
  finally { S.layer = keep; }
  return n;
}
const nounAt = k => `${fmt(k * CM())} m`;
function cannotRemove(t) {
  return t === 2 ? 'That’s the ground: shape it with the ground tool (T).' : t === 3 ? 'That’s an item: select it to move or delete it.' : t === 4 ? 'That’s a window: change it in 2D.' : '';
}
// A click in 3D with Paint or Erase.
function click3d(cx, cy, remove) {
  if (!S.plan || S.readOnly) return;
  const hit = bmHit(cx, cy);
  if (!hit) return;
  if (remove) {
    if (hit.type !== 1) { toast(cannotRemove(hit.type)); return; }
    begin(`Remove a block · ${nounAt(hit.k)}`);
    paint3d(hit.x, hit.z, hit.k, ' ');
    commit(); ghost3d([]); mark3d(); req2d(); return;
  }
  const ch = block3dSym();
  if (!ch) { toast('Pick a block, floor or roof material to build with first (1–9, or the Materials tab).'); return; }
  const x = hit.x + hit.face[0], k = hit.k + hit.face[1], z = hit.z + hit.face[2];
  if (!inB(x, z) || bmAt(x, k, z)) return;
  begin(`Place ${matName(S.plan.palette[ch].name)} · ${nounAt(k)}`);
  paint3d(x, z, k, ch);
  commit(); ghost3d([]); mark3d(); req2d();
}
// Ctrl+drag: along the plane of the face it started on.
function drag3dStart(cx, cy, remove) {
  if (!S.plan || S.readOnly) return null;
  const hit = bmHit(cx, cy), ch = remove ? ' ' : block3dSym();
  if (!hit || (!remove && !ch)) return null;
  if (remove && hit.type !== 1) { toast(cannotRemove(hit.type)); return null; }
  const ax = hit.face[0] ? 0 : hit.face[1] ? 1 : 2, sgn = hit.face[ax];
  const cell = [hit.x, hit.k, hit.z], at = remove ? cell[ax] : cell[ax] + sgn;          // the layer of squares it works on
  const D = { remove, ch, ax, at, plane: remove ? (sgn > 0 ? cell[ax] + 1 : cell[ax]) : (sgn > 0 ? cell[ax] + 1 : cell[ax]), done: new Set(), cells: [], n: 0 };
  V3.hold = true;
  begin();
  drag3dAt(D, cx, cy, hit);
  return D;
}
function drag3dAt(D, cx, cy, first) {
  let x, k, z;
  if (first) { x = first.x; k = first.k; z = first.z; if (!D.remove) { x += first.face[0]; k += first.face[1]; z += first.face[2]; } }
  else {
    const p = bmPlane(cx, cy, D.ax, D.plane);
    if (!p) return;
    const c = [Math.floor(p[0]), Math.floor(p[1]), Math.floor(p[2])];
    c[D.ax] = D.at;
    [x, k, z] = c;
  }
  const key = `${x},${k},${z}`;
  if (D.done.has(key) || !inB(x, z)) return;
  D.done.add(key);
  if (D.remove ? bmAt(x, k, z) !== 1 : bmAt(x, k, z)) return;
  const n = paint3d(x, z, k, D.ch);
  if (n) { D.n += n; D.cells.push([x, k, z]); ghost3d(D.cells, D.remove ? '#d24b4b' : S.plan.palette[D.ch].color); }
}
function drag3dEnd(D) {
  V3.hold = false;
  actionLabel = D.remove ? `Remove ${D.n} block${D.n === 1 ? '' : 's'}` : `Place ${D.n} × ${matName(S.plan.palette[D.ch].name)}`;
  commit(); ghost3d([]); mark3d(); req2d();
}

// The ghost: see-through blocks where a click would build (the brush's colour), or red over what it would remove.
function ghost3d(cells, color) {
  if (!V3.ok) return;
  const THREE = window.THREE;
  if (!V3.ghost || V3.ghost.userData.cap < cells.length) {
    if (V3.ghost) { V3.group.remove(V3.ghost); V3.ghost.dispose && V3.ghost.dispose(); }
    const cap = Math.max(64, cells.length * 2);
    V3.ghost = new THREE.InstancedMesh(V3.box, new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.5, depthWrite: false }), cap);
    V3.ghost.userData.cap = cap; V3.ghost.renderOrder = 5; V3.ghost.frustumCulled = false;
    V3.group.add(V3.ghost);
  }
  const g = V3.ghost, cm = CM(), M = new THREE.Matrix4();
  g.count = cells.length;
  if (cells.length) {
    g.material.color.set(color || T.accent);
    cells.forEach(([x, k, z], i) => { M.makeScale(1, cm, 1); M.setPosition(x, k * cm, z); g.setMatrixAt(i, M); });
    g.instanceMatrix.needsUpdate = true;
  }
  render3d();
}
let hover3dRaf = 0, hover3dXY = null;
function hover3d(cx, cy) {
  hover3dXY = [cx, cy];
  if (hover3dRaf) return;
  hover3dRaf = requestAnimationFrame(() => {
    hover3dRaf = 0;
    const tool = S.tool;
    if (!S.plan || WALK.on || !hover3dXY || (tool !== 'paint' && tool !== 'erase')) { ghost3d([]); return; }
    const hit = bmHit(...hover3dXY);
    if (!hit) { ghost3d([]); return; }
    if (tool === 'erase') { ghost3d(hit.type === 1 ? [[hit.x, hit.k, hit.z]] : [], '#d24b4b'); return; }
    const x = hit.x + hit.face[0], k = hit.k + hit.face[1], z = hit.z + hit.face[2], m = S.plan.palette[S.brush];
    ghost3d(inB(x, z) && !bmAt(x, k, z) && m ? mirrorPts(x, z).map(([a, b]) => [a, k, b]) : [], m && m.color);
  });
}
function hover3dOff() { hover3dXY = null; ghost3d([]); }

// ---------------------------------------------------------------------------
// The 2D ghost: before you click, the brush's colour where it would go (and its mirrored copies), the wall's
// thickness, or, for Replace, the block or the whole run that would change.
// ---------------------------------------------------------------------------
let chunkGhost = { key: '', cells: [] };
function drawHoverGhost(g, cam) {
  const hv = S.hover, t = S.tool, P = S.plan, pal = P.palette, s = cam.s;
  if (!hv || !S.hoverIn || G || !inB(hv[0], hv[1])) return;
  const fill = (cells, color, a) => { g.fillStyle = hexA(color, a); for (const [x, y] of cells) g.fillRect(cam.ox + x * s, cam.oy + y * s, s, s); };
  const brush = pal[S.brush];
  if (['paint', 'line', 'rect', 'fill'].includes(t) && brush) fill(mirrorPts(hv[0], hv[1]), brush.color, 0.55);
  else if (t === 'room' && pal[S.roomWall]) fill(mirrorPts(hv[0], hv[1]), pal[S.roomWall].color, 0.55);
  else if (t === 'erase') fill(mirrorPts(hv[0], hv[1]), '#d24b4b', 0.35);
  else if (t === 'wall' && !S.wallChain && brush) { const c = wallCells([hv]); fill(mirrorGroups([{ cells: c, ch: S.brush }]).flatMap(q => q.cells), brush.color, 0.45); }
  else if (t === 'replace' && brush) {
    const key = [hv, planVer, S.brush, S.replaceMode, layerOn() ? 'k' + curLayer() : 'L' + S.levelIdx, S.mirror.mode].join('|');
    if (chunkGhost.key !== key) {
      const under = isFloorKind(brush), tg = replaceTarget(hv[0], hv[1], under);
      let cells = [];
      if (tg && !sameMat(tg.e, brush)) {
        if (S.replaceMode === 'chunk') { const seen = new Set(); for (const [a, b] of mirrorPts(hv[0], hv[1])) for (const q of chunkTargets(a, b, tg.e, under, tg.part)) { const kk = q.y * P.w + q.x; if (!seen.has(kk)) { seen.add(kk); cells.push([q.x, q.y]); } } }
        else cells = mirrorPts(hv[0], hv[1]).filter(([a, b]) => { const q = replaceTarget(a, b, under); return q && sameMat(q.e, tg.e); });
      }
      chunkGhost = { key, cells };
    }
    if (chunkGhost.cells.length) {
      fill(chunkGhost.cells, brush.color, 0.5);
      const on = new Set(chunkGhost.cells.map(([x, y]) => y * P.w + x));
      g.beginPath();
      for (const [x, y] of chunkGhost.cells) {
        const px = cam.ox + x * s, py = cam.oy + y * s;
        if (!on.has((y - 1) * P.w + x)) { g.moveTo(px, py); g.lineTo(px + s, py); }
        if (!on.has((y + 1) * P.w + x)) { g.moveTo(px, py + s); g.lineTo(px + s, py + s); }
        if (!on.has(y * P.w + x - 1)) { g.moveTo(px, py); g.lineTo(px, py + s); }
        if (!on.has(y * P.w + x + 1)) { g.moveTo(px + s, py); g.lineTo(px + s, py + s); }
      }
      g.strokeStyle = T.accent; g.lineWidth = 1.5; g.stroke();
    }
  }
}

// ---------------------------------------------------------------------------
// Camera presets (the View menu in the 3D view): the four elevations, the top, the isometric; framing what's
// selected; and the section box, which clips the 3D view to the 2D selection's squares.
// ---------------------------------------------------------------------------
function planFrame() {
  const P = S.plan, B = boundsOf(P.levels) || { x: 0, y: 0, w: P.w, h: P.h }, top = Math.max(GAME.levelH, topOfLevels()), cm = P.cell;
  return { tx: (B.x + B.w / 2 - P.w / 2) * cm, tz: (B.y + B.h / 2 - P.h / 2) * cm, ty: top * 0.3, r: Math.max(B.w * cm, B.h * cm, top) * 1.35 + 12 };
}
const VIEWS = [
  ['iso', 'Isometric', -0.72, 0.95], ['top', 'Top', 0, 0.08],
  ['n', 'North side', Math.PI, 1.35], ['e', 'East side', Math.PI / 2, 1.35], ['s', 'South side', 0, 1.35], ['w', 'West side', -Math.PI / 2, 1.35],
];
let camAnim = 0;
function camTo(to, ms = 350) {
  if (!V3.ok) return;
  const o = V3.orbit, from = { ...o };
  let dth = (to.th - from.th) % (Math.PI * 2);
  if (dth > Math.PI) dth -= Math.PI * 2; else if (dth < -Math.PI) dth += Math.PI * 2;
  const t0 = performance.now(), ease = u => (u < 0.5 ? 2 * u * u : 1 - (-2 * u + 2) ** 2 / 2);
  cancelAnimationFrame(camAnim);
  const step = now => {
    const u = Math.min(1, (now - t0) / ms), e = ease(u);
    for (const k of ['ph', 'r', 'tx', 'ty', 'tz']) o[k] = from[k] + (to[k] - from[k]) * e;
    o.th = from.th + dth * e;
    camUpdate();
    if (u < 1) camAnim = requestAnimationFrame(step);
  };
  camAnim = requestAnimationFrame(step);
}
function viewPreset(id) {
  const v = VIEWS.find(q => q[0] === id), f = planFrame();
  if (!v) return;
  camTo({ ...f, th: v[2], ph: v[3], r: id === 'top' ? f.r * 1.05 : f.r });
}
// The box round what's selected, in metres: [x0, y0, z0, x1, y1, z1] (y up).
function selectionBox() {
  const P = S.plan, s = S.sel, cm = P.cell, L = lv();
  const flat = (x, y, w, h, z0, z1) => [(x - P.w / 2) * cm, z0, (y - P.h / 2) * cm, (x + w - P.w / 2) * cm, z1, (y + h - P.h / 2) * cm];
  if (!s) return null;
  if (s.type === 'cells') { const R = s.rect; return layerOn() ? flat(R.x, R.y, R.w, R.h, layerZ(curLayer())[0] - 2, layerZ(curLayer())[1] + 2) : flat(R.x, R.y, R.w, R.h, L.elev, L.elev + L.height); }
  if (s.type === 'block' && s.box) { const [x, y, z, sx, sy, sz] = s.box; return flat(x, z, sx, sz, y, y + sy); }
  if (s.type === 'item') { const it = findItem(s.id); if (!it) return null; const R = itemRect(it), el = (P.levels.find(l => l.id === it.level) || L).elev; return flat(R.x, R.y, R.w, R.h, el, el + it.h); }
  if (s.type === 'zone') { const z = findZone(s.id); if (!z) return null; const el = (P.levels.find(l => l.id === z.level) || L).elev; return flat(z.x, z.y, z.w, z.h, el, el + 4); }
  return null;
}
function frameSelection() {
  const b = selectionBox();
  if (!b) { toast('Select something first: drag over squares in 2D, or click a block or an item.'); return; }
  const o = V3.orbit, size = Math.max(b[3] - b[0], b[4] - b[1], b[5] - b[2], 2);
  camTo({ th: o.th, ph: o.ph, tx: (b[0] + b[3]) / 2, ty: (b[1] + b[4]) / 2, tz: (b[2] + b[5]) / 2, r: size * 1.7 + 4 });
}
function applySection() {
  if (!V3.ok) return;
  const THREE = window.THREE, P = S.plan, R = S.section;
  V3.renderer.localClippingEnabled = !!R;
  const planes = R && P ? (() => {
    const cm = P.cell, x0 = (R.x - P.w / 2) * cm, x1 = (R.x + R.w - P.w / 2) * cm, z0 = (R.y - P.h / 2) * cm, z1 = (R.y + R.h - P.h / 2) * cm;
    return [new THREE.Plane(new THREE.Vector3(1, 0, 0), -x0), new THREE.Plane(new THREE.Vector3(-1, 0, 0), x1), new THREE.Plane(new THREE.Vector3(0, 0, 1), -z0), new THREE.Plane(new THREE.Vector3(0, 0, -1), z1)];
  })() : [];
  for (const m of [V3.matSolid, V3.matGlass, V3.matItem]) { m.clippingPlanes = planes; m.clipShadows = true; m.needsUpdate = true; }
  const b = $('#viewBtn');
  if (b) { b.textContent = R ? 'View · section' : 'View'; b.setAttribute('aria-pressed', String(!!R)); }
  render3d();
}
function toggleSection() {
  if (S.section) { S.section = null; applySection(); return; }
  const s = S.sel;
  const R = s && s.type === 'cells' ? s.rect : s && s.type === 'zone' && findZone(s.id) ? (z => ({ x: z.x, y: z.y, w: z.w, h: z.h }))(findZone(s.id)) : null;
  if (!R) { toast('Drag over some squares in 2D (or select an area), then show only that.'); return; }
  S.section = { ...R };
  applySection();
}
let viewPop = null;
function closeViewPop() { if (!viewPop) return; viewPop.remove(); viewPop = null; document.removeEventListener('pointerdown', viewPopOutside, true); }
function viewPopOutside(e) { if (viewPop && !viewPop.contains(e.target) && !e.target.closest('#viewBtn')) closeViewPop(); }
function toggleViewPop() {
  if (viewPop) { closeViewPop(); return; }
  if (!V3.ok) return;
  hideTip(true);
  const item = (label, fn, opts = {}) => h('button', { class: 'vp-row', type: 'button', disabled: !!opts.disabled, title: opts.title || '', onclick: () => { closeViewPop(); fn(); } }, label);
  const hasSel = !!selectionBox(), canSection = !!(S.sel && (S.sel.type === 'cells' || S.sel.type === 'zone'));
  viewPop = h('div', { class: 'viewpop', role: 'menu', 'aria-label': 'View' },
    h('div', { class: 'vp-grid' }, ...VIEWS.map(([id, label]) => item(label, () => viewPreset(id)))),
    h('div', { class: 'vp-sep' }),
    item('Frame the selection', frameSelection, { disabled: !hasSel, title: hasSel ? 'Zoom the 3D view to what’s selected' : 'Select something first' }),
    item(S.section ? 'Show everything again' : 'Show only the selection', toggleSection, { disabled: !S.section && !canSection, title: 'Clip the 3D view to the squares selected in 2D (a section box)' }));
  document.body.append(viewPop);
  const r = $('#viewBtn').getBoundingClientRect();
  viewPop.style.top = (r.bottom + 6) + 'px';
  viewPop.style.left = clamp(r.right - viewPop.offsetWidth, 8, innerWidth - viewPop.offsetWidth - 8) + 'px';
  viewPop.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); closeViewPop(); } else e.stopPropagation(); });
  setTimeout(() => document.addEventListener('pointerdown', viewPopOutside, true), 0);
  const f = viewPop.querySelector('button:not(:disabled)');
  if (f) f.focus();
}
