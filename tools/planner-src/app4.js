
// ---------------------------------------------------------------------------
// 3D preview (three.js r128, instanced unit cubes; 1 unit = 1 m)
// ---------------------------------------------------------------------------
const V3 = { ok: false, failed: false, dirty: true, fit: true, raf: 0, t: 0, meshes: [], orbit: { th: -0.72, ph: 0.95, r: 60, tx: 0, ty: 0, tz: 0 } };
const c3d = $('#c3d');
function msg3d(text) { const m = $('#msg3d'); m.textContent = text; m.hidden = !text; }
function init3d() {
  if (V3.ok) return true;
  if (V3.failed) return false;
  if (!window.THREE) { V3.failed = true; msg3d('The 3D preview couldn’t load. The 2D editor still works.'); return false; }
  try {
    const THREE = window.THREE;
    const r = new THREE.WebGLRenderer({ canvas: c3d, antialias: true });
    r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFSoftShadowMap;
    V3.renderer = r;
    V3.scene = new THREE.Scene();
    V3.camera = new THREE.PerspectiveCamera(40, 1, 0.1, 5000);
    V3.hemi = new THREE.HemisphereLight(0xffffff, 0x6a6a6a, 0.7); V3.scene.add(V3.hemi);
    V3.sun = new THREE.DirectionalLight(0xffffff, 0.75);
    V3.sun.castShadow = true; V3.sun.shadow.mapSize.set(2048, 2048); V3.sun.shadow.bias = -0.0006; V3.sun.shadow.normalBias = 0.02;
    V3.scene.add(V3.sun); V3.scene.add(V3.sun.target);
    V3.group = new THREE.Group(); V3.scene.add(V3.group);
    V3.box = new THREE.BoxGeometry(1, 1, 1); V3.box.translate(0.5, 0.5, 0.5);
    // Face textures: an outline per cube, plus faint half lines so 1 m cubes show their 0.5 m blocks.
    const makeTex = halves => {
      const cv = document.createElement('canvas'); cv.width = cv.height = 64;
      const g = cv.getContext('2d'); g.fillStyle = '#ffffff'; g.fillRect(0, 0, 64, 64);
      if (halves) { g.strokeStyle = 'rgba(0,0,0,0.09)'; g.lineWidth = 2; g.beginPath(); g.moveTo(32, 0); g.lineTo(32, 64); g.moveTo(0, 32); g.lineTo(64, 32); g.stroke(); }
      g.strokeStyle = 'rgba(0,0,0,0.2)'; g.lineWidth = 3; g.strokeRect(1.5, 1.5, 61, 61);
      const t = new THREE.CanvasTexture(cv); t.anisotropy = 4; return t;
    };
    V3.tex = makeTex(false); V3.texHalves = makeTex(true);
    V3.matSolid = new THREE.MeshLambertMaterial({ map: V3.texHalves });
    V3.matGlass = new THREE.MeshLambertMaterial({ transparent: true, opacity: 0.45, depthWrite: false });
    V3.matItem = new THREE.MeshLambertMaterial({});           // furniture, stations, door leaves: objects, not blocks
    V3.ok = true;
    resize3d();
    return true;
  } catch (err) {
    V3.failed = true; msg3d('3D preview needs WebGL, which isn’t available here. The 2D editor still works.');
    return false;
  }
}
function resize3d() {
  if (!V3.ok) return;
  const r = $('#view3d').getBoundingClientRect();
  const w = Math.max(1, Math.floor(r.width)), hh = Math.max(1, Math.floor(r.height));
  V3.renderer.setSize(w, hh, false);
  V3.camera.aspect = w / hh; V3.camera.updateProjectionMatrix();
  render3d();
}
function render3d() {
  if (!V3.ok || V3.raf) return;
  V3.raf = requestAnimationFrame(() => { V3.raf = 0; V3.renderer.render(V3.scene, V3.camera); });
}
function mark3d() {
  V3.dirty = true;
  if (V3.hold) return;                                         // (a Ctrl+drag in 3D redraws when it ends)
  if (S.view === '2d') return;
  clearTimeout(V3.t);
  V3.t = setTimeout(build3d, 90);
}
function camUpdate() {
  if (!V3.ok) return;
  if (WALK.on) { render3d(); return; }               // (walk mode steers the camera itself)
  const o = V3.orbit, sp = Math.sin(o.ph), cp = Math.cos(o.ph);
  V3.camera.position.set(o.tx + o.r * sp * Math.sin(o.th), o.ty + o.r * cp, o.tz + o.r * sp * Math.cos(o.th));
  V3.camera.near = Math.max(0.1, o.r / 400); V3.camera.far = o.r * 30 + 800;
  V3.camera.lookAt(o.tx, o.ty, o.tz);
  V3.camera.updateProjectionMatrix();
  render3d();
}
function fit3d() {
  const P = S.plan; if (!P) return;
  const B = boundsOf(P.levels) || { x: 0, y: 0, w: P.w, h: P.h };
  const top = Math.max(GAME.levelH, topOfLevels());
  const o = V3.orbit;
  const cm = P.cell;
  o.tx = (B.x + B.w / 2 - P.w / 2) * cm; o.tz = (B.y + B.h / 2 - P.h / 2) * cm; o.ty = top * 0.3;
  o.r = Math.max(B.w * cm, B.h * cm, top) * 1.35 + 12;
  o.th = -0.72; o.ph = 0.95;
  camUpdate();
}
function build3d() {
  if (WALK.on && S.planId !== WALK.planId) { stopWalk(); return; }   // (another plan opened mid-walk)
  if ((S.view === '2d' && !WALK.on) || !init3d()) return;
  const walking = WALK.on;                           // walk mode: the whole build, hidden levels and cutaway or not
  const THREE = window.THREE;
  V3.dirty = false;
  for (const m of V3.meshes) {
    V3.group.remove(m);
    if (m.isInstancedMesh && m.dispose) m.dispose();
    if (m.geometry && m.geometry !== V3.box) m.geometry.dispose();
    if (m.userData.ownMat) m.material.dispose();
  }
  V3.meshes = [];
  const P = S.plan;
  V3.scene.background = new THREE.Color(T.sheet);
  if (!P) { render3d(); return; }
  const cm = P.cell;
  V3.group.scale.set(cm, 1, cm);
  V3.group.position.set(-P.w * cm / 2, 0, -P.h * cm / 2);
  bmStart(P);                                                 // (the block map 3D building traces the pointer through)
  const map = cm === 1 ? V3.texHalves : V3.tex;
  if (V3.matSolid.map !== map) { V3.matSolid.map = map; V3.matSolid.needsUpdate = true; }
  const solids = [], glass = [], objects = [];
  // what each block drawn is: { lid, x, y, k } for a square's material, { item } for an item, { earth } for
  // the ground. Clicking in 3D reads it back (pick3d).
  const metas = new Map([[solids, []], [glass, []], [objects, []]]);
  let src = null;
  const keyOf = e => Object.keys(P.palette).find(k => P.palette[k] === e) || null;
  const layK = !walking && layerOn() ? curLayer() : null, layZ = layK != null ? layerZ(layK)[0] : null;
  const clipTop = layK != null && S.opt.cut ? layerZ(layK)[1] : Infinity;
  const recolour = progColourFn();                            // (the build progress, when it's showing)
  const push = (arr, x, y, z, sx, sy, sz, c) => {
    if (y >= clipTop - 1e-6) return;
    sy = Math.min(sy, clipTop - y);
    if (sx > 0.001 && sy > 0.001 && sz > 0.001) {
      if (recolour) c = recolour(src, y, sy, c);
      arr.push(x, y, z, sx, sy, sz, c); const m = metas.get(arr); if (m) m.push(src);
      const t = !src ? 1 : src.earth ? 2 : src.item ? 3 : arr === glass ? (src.k && P.palette[src.k] && P.palette[src.k].kind === 'water' ? 0 : 4) : 1;
      bmMark(x, y, z, sx, sy, sz, t);
    }
  };
  // Stack cubes one course at a time: 1 m courses on a 1 m grid, 0.5 m courses on a 0.5 m grid.
  const stack = (x, z, base, H, c) => { for (let k = 0; k < H - 1e-6; k += cm) push(solids, x, base + k, z, 1, Math.min(cm, H - k), 1, c); };
  // a wall column with the door and window items' openings taken out (heights above the level floor)
  const cuts = openingCuts(P);
  const stackCut = (L, x, z, lo, H, c) => {
    const cs = cuts.get(L.id + ':' + x + ':' + z);
    if (!cs) { stack(x, z, L.elev + lo, H, c); return; }
    for (const [a, b] of minusCuts(lo, lo + H, cs)) stack(x, z, L.elev + a, b - a, c);
  };
  const cur = mainLevel(lv()), withTrims = [cur, ...trimsOf(cur)].map(l => P.levels.indexOf(l));   // (the current level's trims show with it)
  const maxIdx = !walking && S.opt.cut && clipTop === Infinity ? Math.max(S.levelIdx, ...withTrims) : P.levels.length - 1;   // (a layer slice cuts through every level)
  const shown = L => walking || !L.hidden;
  P.levels.forEach((L, li) => {
    if (li > maxIdx || !shown(L)) return;
    const base = L.elev, H = L.height;
    let hasRoof = false;
    for (let y = 0; y < P.h; y++) {
      const row = L.grid[y];
      for (let x = 0; x < P.w; x++) {
        const ch = row[x];
        if (ch === ' ') continue;
        const e = P.palette[ch], at = { lid: L.id, x, y };
        src = { ...at, k: ch };
        if (!e) { push(solids, x, base, y, 1, 0.25, 1, '#d0368a'); continue; }
        // `base` raises a material off the level floor (floating treads, lintels, corbels)
        if (e.under && (e.kind === 'wall' || e.kind === 'block')) {   // a floor tile in the same square, under a raised piece
          const u = P.palette[e.under];
          src = { ...at, k: e.under };
          if (u && u.kind === 'floor') push(solids, x, base - FLOOR_T, y, 1, FLOOR_T, 1, u.color);
          else if (u && u.kind === 'water') push(glass, x, base - FLOOR_T, y, 1, FLOOR_T, 1, u.color);
          src = { ...at, k: ch };
        }
        if (e.under && (e.kind === 'wall' || e.kind === 'block') && P.palette[e.under] && P.palette[e.under].kind === 'roof') hasRoof = true;
        { const fc = floorCourse(P, L, x, y); if (fc) { src = { ...at, k: keyOf(fc) }; push(solids, x, base - FLOOR_T, y, 1, FLOOR_T, 1, fc.color); src = { ...at, k: ch }; } }   // the floor runs on under it
        if (e.kind === 'wall') { const lift = e.base || 0; stackCut(L, x, y, lift, e.height ? e.height : Math.max(cm, H - lift), e.color); }
        else if (e.kind === 'block') stackCut(L, x, y, e.base || 0, e.height || 1, e.color);
        else if (e.kind === 'floor') push(solids, x, base - FLOOR_T, y, 1, FLOOR_T, 1, e.color);   // a course of blocks, its top the level floor
        else if (e.kind === 'water') push(glass, x, base - FLOOR_T, y, 1, FLOOR_T, 1, e.color);
        else if (e.kind === 'roof') hasRoof = true;
        else if (e.kind === 'dig') continue;                    // dug out: open air (the earth model leaves it empty)
        else {
          const horiz = wallRunsHorizontally(L, x, y);
          const wc = neighbourWallColour(L, x, y) || '#8a8f96';
          const HW = openingWall(e, L);                         // the wall it sits in
          const wallSrc = { ...at, k: neighbourWallSymbol(L, x, y) || ch, around: ch }, ownSrc = src;
          if (e.kind === 'door') {
            const top = openingSpan(e, L)[1];
            src = wallSrc; if (HW > top) stack(x, y, base + top, HW - top, wc); src = ownSrc;
            if (horiz) push(objects, x + 0.04, base, y + 0.44, 0.92, top, 0.12, e.color);   // the door leaf in its opening
            else push(objects, x + 0.44, base, y + 0.04, 0.12, top, 0.92, e.color);
          } else {
            const [sill, top] = openingSpan(e, L);
            src = wallSrc; stack(x, y, base, sill, wc);
            if (HW > top) stack(x, y, base + top, HW - top, wc); src = ownSrc;
            if (horiz) push(glass, x, base + sill, y + 0.45, 1, top - sill, 0.1, e.color);
            else push(glass, x + 0.45, base + sill, y, 0.1, top - sill, 1, e.color);
          }
        }
      }
    }
    if (hasRoof) {
      // lower levels: walls there that reach this level's floor run up to meet the roof (gables fill in)
      const below = P.levels.filter((B, bi) => B !== L && bi <= maxIdx && shown(B) && B.elev < L.elev - 0.01);
      for (const c of roofColumns(P, L, below)) {
        if (c.fill) {
          const B = P.levels.find(l => l.id === c.fillLevel), f = P.palette[c.fillCh];
          src = { lid: c.fillLevel, x: c.x, y: c.y, k: f && (f.kind === 'door' || f.kind === 'window') ? (neighbourWallSymbol(B, c.x, c.y) || c.fillCh) : c.fillCh, gable: true };
          stack(c.x, c.y, c.fillFrom, c.bot - c.fillFrom, c.fillColor);
        }
        src = { lid: L.id, x: c.x, y: c.y, k: keyOf(c.e) };
        stack(c.x, c.y, c.bot, c.top - c.bot, c.e.color);
      }
    }
  });
  for (const it of P.items) {
    const li = P.levels.findIndex(l => l.id === it.level);
    if (li < 0 || li > maxIdx || !shown(P.levels[li])) continue;
    const base = P.levels[li].elev, R = itemRect(it);
    src = { item: it.id };
    if (it.type === 'spawn') { if (!walking) push(objects, R.x, base, R.y, R.w, 0.1, R.h, it.color); continue; }   // a marker on the floor
    if (/^tree-/.test(it.type)) {                            // a tree: its trunk on the footprint, the canopy round it in tiers
      const z0 = base + (it.z || 0), H = it.h, cx = R.x + R.w / 2, cz = R.y + R.h / 2;
      const tiers = it.type === 'tree-evergreen' ? [[3.5, 0.25, 0.45], [2.5, 0.45, 0.65], [1.5, 0.65, 0.85], [0.5, 0.85, 1]]
        : [[3, 0.35, 0.55], [4, 0.55, 0.8], [3, 0.8, 0.95], [1.5, 0.95, 1]];
      push(objects, R.x, z0, R.y, R.w, H * tiers[0][1], R.h, '#6b4f36');
      src = { item: it.id, canopy: true };
      for (const [wm, a, b] of tiers) { const s = wm / cm; push(objects, cx - s / 2, z0 + H * a, cz - s / 2, s, H * (b - a), s, it.color); }
      continue;
    }
    if (it.type === 'stairs') {
      // Built from blocks: each step one block (0.5 m) higher, and each step's front edge on the block grid,
      // so a stair that's steeper than one block per block climbs two at a time somewhere.
      const n = Math.max(1, Math.round(it.h / VOXEL)), alongY = it.rot === 0 || it.rot === 180, len = alongY ? R.h : R.w;
      const u = VOXEL / cm, edge = i => Math.round(i * len / n / u) * u;          // in squares, on the block grid
      for (let i = 0; i < n; i++) {
        const a = edge(i), b = i === n - 1 ? len : edge(i + 1), hh = VOXEL * (i + 1);
        if (b - a < 1e-6) continue;                          // (merged into the next step up)
        if (it.rot === 0) push(solids, R.x, base, R.y + R.h - b, R.w, hh, b - a, it.color);
        else if (it.rot === 180) push(solids, R.x, base, R.y + a, R.w, hh, b - a, it.color);
        else if (it.rot === 90) push(solids, R.x + a, base, R.y, b - a, hh, R.h, it.color);
        else push(solids, R.x + R.w - b, base, R.y, b - a, hh, R.h, it.color);
      }
    } else if (IN_WALL.has(it.mount)) {                     // a door leaf or a pane, set in the middle of the wall
      const z = base + (it.z || 0), arr = it.mount === 'window' ? glass : objects, t = it.mount === 'window' ? 0.1 : 0.14;
      if (R.w >= R.h) push(arr, R.x + 0.02, z, R.y + (R.h - t) / 2, R.w - 0.04, it.h, t, it.color);
      else push(arr, R.x + (R.w - t) / 2, z, R.y + 0.02, t, it.h, R.h - 0.04, it.color);
    } else push(objects, R.x, base + (it.z || 0), R.y, R.w, it.h, R.h, it.color);   // an object: exactly its squares, plain
  }
  // with Cutaway on, the ground is sliced at the top of the current level, so you can see into hills and cellars
  const curL = P.levels[S.levelIdx];
  src = { earth: true };
  const dig = earth3d(P, cm, push, solids, !walking && S.opt.cut && curL ? Math.min(clipTop, curL.elev + curL.height) : Infinity);
  addInstanced(solids, V3.matSolid, true, metas.get(solids));
  addInstanced(glass, V3.matGlass, false, metas.get(glass));
  const objMesh = addInstanced(objects, V3.matItem, true, metas.get(objects));
  if (walking) walkCollide(P, cm, solids, glass, objects, metas, dig, objMesh);
  pickOutline();
  if (S.hl && !walking) hl3d();

  // ground and drawing sheet; where there's digging, the earth block replaces them (so pits stay open)
  const flat = (x, z, w, d, y, color) => {
    if (w <= 0 || d <= 0) return;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshLambertMaterial({ color }));
    m.rotation.x = -Math.PI / 2; m.position.set(x + w / 2, y, z + d / 2); m.receiveShadow = true; m.userData.ownMat = true; addObj(m);
  };
  const around = (x0, z0, x1, z1, y, color) => {           // the rectangle minus the dig site
    if (!dig) { flat(x0, z0, x1 - x0, z1 - z0, y, color); return; }
    const R = dig, rx0 = Math.max(x0, R.x), rz0 = Math.max(z0, R.y), rx1 = Math.min(x1, R.x + R.w), rz1 = Math.min(z1, R.y + R.h);
    flat(x0, z0, x1 - x0, rz0 - z0, y, color); flat(x0, rz1, x1 - x0, z1 - rz1, y, color);
    flat(x0, rz0, rx0 - x0, rz1 - rz0, y, color); flat(rx1, rz0, x1 - rx1, rz1 - rz0, y, color);
  };
  around(-20, -20, P.w + 20, P.h + 20, -0.03, T.off);
  around(0, 0, P.w, P.h, -0.015, T.sheet);
  if (!terrainOn(P)) { addObj(gridLines(P, 1, 0.07)); addObj(gridLines(P, 5, 0.18)); }      // (they'd float over valleys)
  const L = lv();
  if (L && !walking) addObj(rectLine(0, (layZ != null ? layZ : L.elev) + 0.03, 0, P.w, P.h, T.accent, 0.9));   // the current level, or layer
  if (S.opt.altar && !walking) for (const it of P.items) if (it.type === 'altar') {
    const A = altarRect(it), li = P.levels.findIndex(l => l.id === it.level);
    addObj(rectLine(A.x, (li >= 0 ? P.levels[li].elev : 0) + 0.05, A.y, A.w, A.h, T.shroud, 0.9));
  }
  if (S.opt.altar && !walking) for (const v of altarVolumes(P)) addObj(altarBox(v, T.shroud));     // up and down too (unconfirmed)
  const R = Math.max(P.w, P.h) * cm * 0.75 + 20;
  V3.sun.position.set(R * 0.55, R * 1.3, R * 0.75); V3.sun.target.position.set(0, 0, 0);
  const sc = V3.sun.shadow.camera; sc.left = -R; sc.right = R; sc.top = R; sc.bottom = -R; sc.near = 1; sc.far = R * 4; sc.updateProjectionMatrix();
  V3.sun.castShadow = S.opt.shadows;
  if (walking) { V3.scene.background = new THREE.Color(T.sky || '#a9c8de'); return; }
  if (V3.fit) { V3.fit = false; fit3d(); } else camUpdate();
}
// The ground as a block of earth. Without terrain it only appears around underground levels: the built
// area plus 2 m, with its top at 0 m. With terrain it covers the whole canvas, each square's column rising
// to that square's ground height under a grassy top course. Any square of a level the ground reaches that
// holds something (or an item) is dug out for that level's height. Earth goes down to 1 m under the
// deepest floor or valley. Returns the area covered, or null.
function earth3d(P, cm, push, solids, slice = Infinity) {
  const hasT = terrainOn(P), under = P.levels.filter(isUnder);
  if (!under.length && !hasT) return null;
  let R;
  if (hasT) R = { x: 0, y: 0, w: P.w, h: P.h };
  else {
    const B = boundsOf(P.levels);
    if (!B) return null;
    const m = Math.round(2 / cm);
    R = { x: Math.max(0, B.x - m), y: Math.max(0, B.y - m) };
    R.w = Math.min(P.w, B.x + B.w + m) - R.x; R.h = Math.min(P.h, B.y + B.h + m) - R.y;
  }
  const [lo, hi] = hasT ? terrainRange(P) : [0, 0];
  const deep = Math.min(-1, lo - 1, ...under.map(l => l.elev - 1));
  const reach = P.levels.filter(l => l.elev - FLOOR_T < hi - 1e-6);
  const cover = new Map(reach.map(L => [L.id, new Set()]));     // squares items sit on, per level
  for (const it of P.items) if (cover.has(it.level) && mountOf(it) === 'floor') { const Q = itemRect(it); for (let y = Math.floor(Q.y); y < Math.ceil(Q.y + Q.h - 1e-6); y++) for (let x = Math.floor(Q.x); x < Math.ceil(Q.x + Q.w - 1e-6); x++) cover.get(it.level).add(y * P.w + x); }
  const shade = d => tint(SOIL, -0.12 - 0.25 * Math.min(1, -d / 20));   // darker the deeper below the surface
  const GRASS = '#6e8a46';
  for (let y = R.y; y < R.y + R.h; y++) for (let x = R.x; x < R.x + R.w; x++) {
    const ground = hasT ? P.terrain[y][x] : 0, top = Math.min(ground, slice), cutHere = top < ground - 1e-6, air = [];
    for (const L of reach) {
      const fl = floorUnder(P.palette, P.palette[L.grid[y][x]]) ? FLOOR_T : 0;   // a floor's course replaces the earth under it
      if (L.elev - fl < top - 1e-6 && (L.grid[y][x] !== ' ' || cover.get(L.id).has(y * P.w + x))) air.push([L.elev - fl, Math.min(top, L.elev + L.height)]);
    }
    air.sort((a, b) => a[0] - b[0]);
    let z = deep;
    for (const [a, b] of air) { if (a > z + 1e-6) push(solids, x, z, y, 1, a - z, 1, shade((z + a) / 2 - top)); z = Math.max(z, b); }
    if (z < top - 1e-6) {
      const cap = Math.min(cm, top - z);
      if (top - cap > z + 1e-6) push(solids, x, z, y, 1, top - cap - z, 1, shade((z + top - cap) / 2 - top));
      push(solids, x, top - cap, y, 1, cap, 1, cutHere ? tint(SOIL, -0.3) : hasT ? GRASS : tint(SOIL, 0.06));
    }
  }
  return R;
}
function addObj(o) { V3.group.add(o); V3.meshes.push(o); }
function addInstanced(list, mat, shadows, meta) {
  const n = list.length / 7;
  if (!n) return;
  const THREE = window.THREE, m = new THREE.InstancedMesh(V3.box, mat, n);
  if (meta) m.userData.meta = meta;
  const M = new THREE.Matrix4(), c = new THREE.Color();
  for (let i = 0; i < n; i++) {
    const k = i * 7;
    M.makeScale(list[k + 3], list[k + 4], list[k + 5]);
    M.setPosition(list[k], list[k + 1], list[k + 2]);
    m.setMatrixAt(i, M);
    c.set(list[k + 6]); m.setColorAt(i, c);
  }
  m.instanceMatrix.needsUpdate = true;
  if (m.instanceColor) m.instanceColor.needsUpdate = true;
  m.castShadow = shadows; m.receiveShadow = shadows;
  addObj(m);
  return m;
}
function gridLines(P, step, opacity) {
  const THREE = window.THREE, pts = [];
  for (let x = 0; x <= P.w; x += step) pts.push(x, 0.004, 0, x, 0.004, P.h);
  for (let y = 0; y <= P.h; y += step) pts.push(0, 0.004, y, P.w, 0.004, y);
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  const l = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: T.ink, transparent: true, opacity }));
  l.userData.ownMat = true; return l;
}
function rectLine(x, y, z, w, d, color, opacity) {
  const THREE = window.THREE;
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute([x, y, z, x + w, y, z, x + w, y, z + d, x, y, z + d], 3));
  const l = new THREE.LineLoop(geo, new THREE.LineBasicMaterial({ color, transparent: true, opacity }));
  l.userData.ownMat = true; return l;
}
// Roofs are blocks, like everything else: each roof square is a column of blocks whose top is its "Top at"
// height. Where a neighbouring roof square is lower (by up to three courses), the column runs down to that
// square's top, so the steps close up with no gaps; otherwise it's one course thick. Squares more than three
// courses apart are separate roofs, a step. A roof square over a wall, door or window in a lower level that
// reaches the roof level's floor is carried down to the top of that wall in its material, which closes gables.
// The 3D view and the shopping list both count from here, so they always agree.
function roofColumns(P, L, below) {
  const W = P.w, D = P.h, pal = P.palette, cm = P.cell, top = new Float64Array(W * D).fill(NaN), ent = [];
  for (let y = 0; y < D; y++) {
    const row = L.grid[y];
    for (let x = 0; x < W; x++) {
      let e = pal[row[x]];
      if (e && e.kind !== 'roof' && e.under && pal[e.under] && pal[e.under].kind === 'roof') e = pal[e.under];   // a raised piece over a roof square
      if (e && e.kind === 'roof') { top[y * W + x] = L.elev + roofTop(e, cm); ent[y * W + x] = e; }
    }
  }
  // the top of a lower level's wall, door or window in this square, if it stands up to the roof level's
  // floor (a full-height wall, or a kneewall or raised piece whose top is there); null if it doesn't
  const wallTop = (B, e) => {
    if (!e) return null;
    const lift = e.base || 0;
    let t;
    if (e.kind === 'door' || e.kind === 'window') t = B.elev + openingWall(e, B);
    else if (e.kind === 'wall') t = B.elev + lift + (e.height || Math.max(cm, B.height - lift));
    else if (e.kind === 'block') t = B.elev + lift + (e.height || 1);
    else return null;
    return t >= L.elev - 0.01 && B.elev + lift < L.elev ? t : null;
  };
  const jump = 3.01 * cm, out = [];
  for (let y = 0; y < D; y++) for (let x = 0; x < W; x++) {
    const t = top[y * W + x];
    if (t !== t) continue;
    let bot = t - cm;
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const i = x + dx, j = y + dy;
      if (i < 0 || j < 0 || i >= W || j >= D) continue;
      const u = top[j * W + i];
      if (u === u && t - u <= jump) bot = Math.min(bot, u);
    }
    bot = Math.max(bot, L.elev);
    let fill = null, fillColor = null, fillFrom = L.elev;
    const B = below.find(B => wallTop(B, pal[B.grid[y][x]]) != null);
    if (B) fillFrom = Math.max(L.elev, wallTop(B, pal[B.grid[y][x]]));   // from the wall's own top (a taller gable wall, a gable window)
    if (B && bot > fillFrom + 1e-6) {
      fill = pal[B.grid[y][x]];                            // the gable takes the material of the wall it continues
      fillColor = fill.kind === 'wall' || fill.kind === 'block' ? fill.color : (neighbourWallColour(B, x, y) || '#8a8f96');
    }
    out.push({ x, y, top: t, bot, e: ent[y * W + x], fill, fillColor, fillFrom, fillCh: fill ? B.grid[y][x] : null, fillLevel: fill ? B.id : null });
  }
  return out;
}
// Colour of the wall a door or window sits in: the nearest wall square along the row or column
// (wide doors and window bands have no wall right beside their middle squares).
function neighbourWallColour(L, x, y) { const k = neighbourWallSymbol(L, x, y); return k ? S.plan.palette[k].color : null; }
function neighbourWallSymbol(L, x, y) {
  for (let d = 1; d <= 8; d++) {
    for (const [dx, dy] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
      if (!inB(x + dx * d, y + dy * d)) continue;
      const k = L.grid[y + dy * d][x + dx * d], e = S.plan.palette[k];
      if (e && (e.kind === 'wall' || e.kind === 'block')) return k;
    }
  }
  return null;
}

// Orbit controls
const P3 = new Map();
let G3 = null;
c3d.addEventListener('pointerdown', e => {
  if (!V3.ok || WALK.on) return;                      // (walk mode looks around with its own drag)
  try { c3d.setPointerCapture(e.pointerId); } catch { /* ignore */ }
  P3.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (P3.size === 1 && e.ctrlKey && (S.tool === 'paint' || S.tool === 'erase') && (e.button === 0 || e.button === 2)) {
    const D = drag3dStart(e.clientX, e.clientY, S.tool === 'erase' || e.button === 2);
    if (D) { G3 = { mode: 'paint3d', D }; return; }
  }
  if (P3.size === 2) { const [a, b] = [...P3.values()]; G3 = { mode: 'pinch', d: Math.hypot(a.x - b.x, a.y - b.y) || 1, m: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 } }; return; }
  G3 = { mode: (e.button === 2 || e.button === 1 || e.shiftKey) ? 'pan' : 'orbit', x: e.clientX, y: e.clientY, x0: e.clientX, y0: e.clientY, button: e.button };
});
c3d.addEventListener('pointermove', e => {
  if (!G3) { if (!WALK.on) { if (S.tool === 'paint' || S.tool === 'erase') hover3d(e.clientX, e.clientY); altar3dHover(e.clientX, e.clientY); } return; }
  if (!P3.has(e.pointerId)) return;
  if (G3.mode === 'paint3d') { drag3dAt(G3.D, e.clientX, e.clientY); return; }
  P3.set(e.pointerId, { x: e.clientX, y: e.clientY });
  const o = V3.orbit;
  if (G3.mode === 'pinch') {
    if (P3.size < 2) return;
    const [a, b] = [...P3.values()], d = Math.hypot(a.x - b.x, a.y - b.y) || 1, m = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
    o.r = clamp(o.r * G3.d / d, 3, 1200);
    panBy(m.x - G3.m.x, m.y - G3.m.y);
    G3.d = d; G3.m = m; camUpdate(); return;
  }
  const dx = e.clientX - G3.x, dy = e.clientY - G3.y;
  G3.x = e.clientX; G3.y = e.clientY;
  if (G3.mode === 'orbit') { o.th -= dx * 0.008; o.ph = clamp(o.ph - dy * 0.008, 0.08, 1.52); }
  else panBy(dx, dy);
  camUpdate();
});
function panBy(dx, dy) {
  const o = V3.orbit, k = o.r * 0.0016;
  const rx = Math.cos(o.th), rz = -Math.sin(o.th), fx = -Math.sin(o.th), fz = -Math.cos(o.th);
  o.tx += (-rx * dx + fx * dy) * k; o.tz += (-rz * dx + fz * dy) * k;
}
const end3 = e => {
  if (G3 && G3.mode === 'paint3d') { const D = G3.D; P3.delete(e.pointerId); G3 = null; drag3dEnd(D); return; }
  const still = G3 && P3.size === 1 && Math.hypot(e.clientX - G3.x0, e.clientY - G3.y0) < 5 && e.type === 'pointerup';
  const click = still && G3.mode === 'orbit' && G3.button === 0;
  const rclick = still && G3.mode === 'pan' && G3.button === 2;
  P3.delete(e.pointerId); if (P3.size === 0) G3 = null; else if (G3 && G3.mode === 'pinch') G3 = null;
  const building = S.tool === 'paint' || S.tool === 'erase';
  if (S.tool === 'built' && (click || rclick)) built3dClick(e.clientX, e.clientY, e, rclick);
  else if (click) { if (building) click3d(e.clientX, e.clientY, S.tool === 'erase'); else pick3d(e.clientX, e.clientY); }
  else if (rclick && building) click3d(e.clientX, e.clientY, true);
};
c3d.addEventListener('pointerleave', () => { if (!G3) hover3dOff(); altarReadout(null); });
// Click a block in 3D to see what it is: the nearest thing under the pointer. Items select as items; the
// ground clears the selection.
function pick3d(cx, cy) {
  if (!V3.ok || !S.plan) return;
  const THREE = window.THREE, r = c3d.getBoundingClientRect();
  const ray = new THREE.Raycaster();
  ray.setFromCamera(new THREE.Vector2((cx - r.left) / r.width * 2 - 1, -(cy - r.top) / r.height * 2 + 1), V3.camera);
  const hit = ray.intersectObjects(V3.meshes.filter(m => m.isInstancedMesh && m.userData.meta), false)[0];
  const src = hit && hit.object.userData.meta[hit.instanceId];
  if (!src || src.earth) { S.sel = null; renderInspector(); return; }
  if (src.item) { S.sel = { type: 'item', id: src.item }; renderInspector(); req2d(); return; }
  const M = new THREE.Matrix4(); hit.object.getMatrixAt(hit.instanceId, M);
  const y0 = M.elements[13], y1 = y0 + M.elements[5];
  S.sel = { type: 'block', lid: src.lid, x: src.x, y: src.y, k: src.k, z0: y0, z1: y1, box: [M.elements[12], y0, M.elements[14], M.elements[0], M.elements[5], M.elements[10]], gable: !!src.gable, around: src.around || null };
  renderInspector();
  if (src.k && S.plan.palette[src.k]) showMaterial(src.k);
}
// An outline round the block picked in 3D (it stays until the selection changes).
function pickOutline() {
  if (!V3.ok) return;
  if (V3.hl) { V3.group.remove(V3.hl); V3.hl.geometry.dispose(); V3.hl.material.dispose(); V3.hl = null; }
  const s = S.sel;
  if (s && s.type === 'block' && s.box) {
    const THREE = window.THREE, [x, y, z, sx, sy, sz] = s.box;
    const g = new THREE.EdgesGeometry(new THREE.BoxGeometry(sx, sy, sz));
    V3.hl = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: T.accent, depthTest: false, transparent: true }));
    V3.hl.position.set(x + sx / 2, y + sy / 2, z + sz / 2); V3.hl.renderOrder = 10;
    V3.group.add(V3.hl);
  }
  render3d();
}
c3d.addEventListener('pointerup', end3);
c3d.addEventListener('pointercancel', end3);
c3d.addEventListener('contextmenu', e => e.preventDefault());
c3d.addEventListener('wheel', e => {
  if (!V3.ok || WALK.on) return;
  e.preventDefault();
  V3.orbit.r = clamp(V3.orbit.r * Math.exp(e.deltaY * 0.0012), 3, 1200);
  camUpdate();
}, { passive: false });
