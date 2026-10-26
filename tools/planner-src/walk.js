
// ---------------------------------------------------------------------------
// Walk mode: explore the build at eye height. WASD to move (Shift turns running on and off), drag to look,
// Space to jump (held longer, higher; in water it swims up), E for the door in front of you, F for full
// screen, Enter back to the spawn point, Esc to stop. It starts at the plan's Spawn point item and walks the whole build, hidden levels and
// cutaway or not. Everything the 3D view draws is solid (blocks, roofs, windows, closed doors, furniture),
// except the survivors' stand-ins and the spawn point; water is for swimming. Collisions run on a grid of
// 0.5 m blocks built from the 3D view's own boxes (walkCollide), so walking always matches what's drawn.
// ---------------------------------------------------------------------------
const WALK = { on: false, keys: new Set(), col: null, doors: [], p: null, raf: 0, last: 0, prevView: null, prevFov: 40, look: null, run: false };
const WK = {
  eye: 1.7, height: 1.8, half: 0.3,                 // the body: eyes 1.7 m up, 1.8 m tall, 0.6 m across
  walk: 6.75, run: 12, swim: 3.3, swimRun: 5.1,     // metres a second
  g: 20, jumpMin: 1.2, jumpMax: 2.5,                // a tap jumps 1.2 m, held all the way 2.5 m
  step: 0.5, reach: 3, look: 0.0035,                // walk up one block; doors within 3 m; drag sensitivity
};
WK.v0 = Math.sqrt(2 * WK.g * WK.jumpMin);           // take-off speed for the shortest jump
WK.gHold = WK.v0 * WK.v0 / (2 * WK.jumpMax);        // lighter gravity while Space is held on the way up
const AIR = 0, SOLID = 1, WATER = 2, DOOR = 3;

function spawnItem(P) { return P && P.items.find(it => it.type === 'spawn'); }

function startWalk() {
  const P = S.plan;
  if (!P || WALK.on) return;
  const sp = spawnItem(P);
  if (!sp) { toast('Place a Spawn point first: it’s in the Items tab, under Walk mode.', 'bad'); return; }
  if (!init3d()) { toast('Walking needs the 3D view, which isn’t available here.', 'bad'); return; }
  if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
  WALK.on = true; WALK.planId = S.planId; WALK.keys.clear(); setRun(false);
  WALK.prevView = S.view; WALK.prevFov = V3.camera.fov;
  document.body.classList.add('walking'); $('#walkHud').hidden = false;
  V3.camera.fov = 70; V3.camera.near = 0.05; V3.camera.far = 2500; V3.camera.updateProjectionMatrix();
  if (S.view !== '3d') setView('3d', false);
  build3d();                                         // everything, hidden levels and all; builds the collision grid too
  if (!WALK.col) { stopWalk(); return; }
  respawn();
  WALK.last = performance.now();
  WALK.raf = requestAnimationFrame(walkFrame);
}
function stopWalk() {
  if (!WALK.on) return;
  WALK.on = false; cancelAnimationFrame(WALK.raf); WALK.raf = 0;
  WALK.keys.clear(); WALK.col = null; WALK.doors = []; WALK.look = null;
  setFull(false); WDRAG = null;
  if (locked() && document.exitPointerLock) document.exitPointerLock();
  document.body.classList.remove('walking', 'underwater'); $('#walkHud').hidden = true;
  V3.camera.fov = WALK.prevFov; V3.camera.updateProjectionMatrix();
  V3.renderer.shadowMap.autoUpdate = true;
  if (WALK.prevView && WALK.prevView !== S.view) setView(WALK.prevView, false);
  V3.dirty = true; build3d();                        // back to the editing view (levels hidden, cutaway, the orbit camera)
}
// Back to the spawn point, facing the way it faces (rot 0 south, 90 west, 180 north, 270 east).
function respawn() {
  const P = S.plan, sp = spawnItem(P), C = WALK.col;
  if (!sp || !C) return;
  const L = P.levels.find(l => l.id === sp.level), R = itemRect(sp), cm = P.cell;
  const p = { x: (R.x + R.w / 2) * cm, y: (L ? L.elev : 0) + (sp.z || 0), z: (R.y + R.h / 2) * cm, vx: 0, vy: 0, vz: 0,
              yaw: -(sp.rot || 0) * Math.PI / 180, pitch: 0, ground: false, water: false, hold: false, coyote: 0, camY: 0 };
  for (let n = 0; n < 80 && boxBlocked(p.x, p.y, p.z); n++) p.y += VOXEL;     // (lifted clear if something's there)
  p.camY = p.y + WK.eye;
  WALK.p = p;
}

// ---- the collision grid, built from the 3D view's boxes (squares across, metres up)
function walkCollide(P, cm, solids, glass, objects, metas, dig, objMesh) {
  const V = VOXEL, NX = Math.round(P.w * cm / V), NZ = Math.round(P.h * cm / V);
  let lo = -1, hi = 0;
  for (const a of [solids, glass, objects]) for (let k = 0; k < a.length; k += 7) { lo = Math.min(lo, a[k + 1]); hi = Math.max(hi, a[k + 1] + a[k + 4]); }
  const ymin = Math.floor(lo / V) * V - V, NY = Math.round((Math.ceil(hi / V) * V + 12 - ymin) / V);
  if (NX * NY * NZ > 80e6) { toast('This plan is too big to walk.', 'bad'); WALK.col = null; return; }
  const grid = new Uint8Array(NX * NY * NZ), doorVox = new Map();
  const idx = (i, j, k) => (j * NZ + k) * NX + i;
  const fill = (a, k, v, door) => {
    const x = a[k], y = a[k + 1], z = a[k + 2];
    const i0 = Math.max(0, Math.floor(x * cm / V + 1e-6)), i1 = Math.min(NX, Math.ceil((x + a[k + 3]) * cm / V - 1e-6));
    const k0 = Math.max(0, Math.floor(z * cm / V + 1e-6)), k1 = Math.min(NZ, Math.ceil((z + a[k + 5]) * cm / V - 1e-6));
    const j0 = Math.max(0, Math.floor((y - ymin) / V + 1e-6)), j1 = Math.min(NY, Math.ceil((y + a[k + 4] - ymin) / V - 1e-6));
    for (let j = j0; j < j1; j++) for (let kk = k0; kk < k1; kk++) for (let i = i0; i < i1; i++) {
      const n = idx(i, j, kk);
      if (v === SOLID) grid[n] = SOLID;
      else if (grid[n] === AIR || (v === DOOR && grid[n] === WATER)) { grid[n] = v; if (v === DOOR) doorVox.set(n, door); }
    }
  };
  const itemOf = new Map(P.items.map(it => [it.id, it]));
  // solids: blocks, floors, walls, roofs, stairs, the ground
  for (let k = 0; k < solids.length; k += 7) fill(solids, k, SOLID);
  // glass: windows are solid, water is for swimming
  const gm = metas.get(glass);
  for (let k = 0, n = 0; k < glass.length; k += 7, n++) {
    const s = gm[n], e = s && s.k ? P.palette[s.k] : null;
    fill(glass, k, e && e.kind === 'water' ? WATER : SOLID);
  }
  // objects: furniture and stations are solid; door leaves open; the survivors' stand-ins and the spawn don't stop you
  const om = metas.get(objects), doors = [], byKey = new Map();
  for (let k = 0, n = 0; k < objects.length; k += 7, n++) {
    const s = om[n] || {};
    if (s.item) {
      const it = itemOf.get(s.item);
      if (!it || /^npc-/.test(it.type) || it.type === 'spawn' || s.canopy) continue;   // (and you walk under trees' canopies)
      if (it.mount === 'door') {
        let d = byKey.get('i:' + it.id);
        if (!d) { d = { key: 'i:' + it.id, boxes: [], open: false, swing: 0, target: 0, slide: /portcullis/i.test(it.type + ' ' + (it.label || '')) }; byKey.set(d.key, d); doors.push(d); }
        d.boxes.push(n); continue;
      }
      fill(objects, k, SOLID); continue;
    }
    const e = s.k ? P.palette[s.k] : null;
    if (e && e.kind === 'door') {                     // a painted door: one leaf a square, joined into runs below
      const d = { key: `p:${s.lid}:${s.x}:${s.y}`, lid: s.lid, k: s.k, x: s.x, y: s.y, boxes: [n], open: false, swing: 0, target: 0, painted: true };
      byKey.set(d.key, d); doors.push(d); continue;
    }
    fill(objects, k, SOLID);
  }
  // painted door squares next to each other, of one material on one level, open as one door
  const merged = [], seen = new Set();
  for (const d of doors) {
    if (seen.has(d.key)) continue;
    seen.add(d.key);
    if (!d.painted) { merged.push(d); continue; }
    const run = d, q = [d];
    while (q.length) {
      const c = q.pop();
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const o = byKey.get(`p:${c.lid}:${c.x + dx}:${c.y + dy}`);
        if (o && o.k === c.k && !seen.has(o.key)) { seen.add(o.key); run.boxes.push(...o.boxes); q.push(o); }
      }
    }
    merged.push(run);
  }
  // each door's footprint (plan metres) and its leaves' matrices, for opening and for E to find it
  const THREE = window.THREE, M = new THREE.Matrix4();
  merged.forEach((d, di) => {
    d.box = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity];
    d.base = [];
    for (const n of d.boxes) {
      const k = n * 7, x = objects[k] * cm, y = objects[k + 1], z = objects[k + 2] * cm;
      const x1 = (objects[k] + objects[k + 3]) * cm, y1 = y + objects[k + 4], z1 = (objects[k + 2] + objects[k + 5]) * cm;
      d.box = [Math.min(d.box[0], x), Math.min(d.box[1], y), Math.min(d.box[2], z), Math.max(d.box[3], x1), Math.max(d.box[4], y1), Math.max(d.box[5], z1)];
      fill(objects, k, DOOR, di);
      if (objMesh) { objMesh.getMatrixAt(n, M); d.base.push(M.clone()); }
    }
  });
  // the ground plane, where there's no earth model: solid below 0 m
  if (!terrainOn(P)) {
    const jTop = Math.round((0 - ymin) / V);
    for (let k = 0; k < NZ; k++) for (let i = 0; i < NX; i++) {
      const sx = i * V / cm, sz = k * V / cm;
      if (dig && sx >= dig.x && sx < dig.x + dig.w && sz >= dig.y && sz < dig.y + dig.h) continue;
      for (let j = 0; j < jTop; j++) grid[idx(i, j, k)] = SOLID;
    }
  }
  // water fills down from its surface course to whatever's under it (the lake bed)
  for (let k = 0; k < NZ; k++) for (let i = 0; i < NX; i++) {
    let wet = false;
    for (let j = NY - 1; j >= 0; j--) {
      const n = idx(i, j, k), v = grid[n];
      if (v === WATER) wet = true;
      else if (v === AIR) { if (wet) grid[n] = WATER; }
      else wet = false;
    }
  }
  WALK.col = { grid, NX, NY, NZ, ymin, doorVox, cm };
  WALK.doors = merged; WALK.objMesh = objMesh;
  V3.renderer.shadowMap.autoUpdate = false; V3.renderer.shadowMap.needsUpdate = true;   // (the build stands still: shadows once, and when a door moves)
}
function voxAt(i, j, k) {
  const C = WALK.col;
  if (i < 0 || k < 0 || i >= C.NX || k >= C.NZ || j < 0) return SOLID;   // the canvas's edge, the bottom of the world
  if (j >= C.NY) return AIR;
  const n = (j * C.NZ + k) * C.NX + i, v = C.grid[n];
  if (v === DOOR) return WALK.doors[C.doorVox.get(n)].open ? AIR : SOLID;
  return v;
}
// Is a body standing at (x, y, z) (feet, plan metres) inside anything solid?
function boxBlocked(x, y, z, h = WK.height) {
  const C = WALK.col, V = VOXEL, r = WK.half;
  const i0 = Math.floor((x - r) / V + 1e-6), i1 = Math.ceil((x + r) / V - 1e-6);
  const k0 = Math.floor((z - r) / V + 1e-6), k1 = Math.ceil((z + r) / V - 1e-6);
  const j0 = Math.floor((y - C.ymin) / V + 1e-6), j1 = Math.ceil((y + h - C.ymin) / V - 1e-6);
  for (let j = j0; j < j1; j++) for (let k = k0; k < k1; k++) for (let i = i0; i < i1; i++) if (voxAt(i, j, k) === SOLID) return true;
  return false;
}
// The water's surface above someone swimming: the top of the water in their column.
function waterTop(p) {
  const C = WALK.col, V = VOXEL, i = Math.floor(p.x / V), k = Math.floor(p.z / V);
  let j = Math.floor((p.y + 0.1 - C.ymin) / V);
  while (j < C.NY && voxAt(i, j, k) === WATER) j++;
  return C.ymin + j * V;
}
function wetAt(x, y, z) {
  const C = WALK.col, V = VOXEL;
  return voxAt(Math.floor(x / V), Math.floor((y - C.ymin) / V), Math.floor(z / V)) === WATER;
}

// ---- one frame: input, movement, collisions, doors, the camera
function walkFrame(now) {
  if (!WALK.on) return;
  const dt = Math.min(0.05, Math.max(0, (now - WALK.last) / 1000));
  WALK.last = now;
  if (WALK.col && WALK.p) { edgeTurn(dt); stepWalk(dt); animateDoors(dt); placeCamera(dt); }
  V3.renderer.render(V3.scene, V3.camera);
  WALK.raf = requestAnimationFrame(walkFrame);
}
function stepWalk(dt) {
  const p = WALK.p, K = WALK.keys;
  const fwd = (K.has('KeyW') ? 1 : 0) - (K.has('KeyS') ? 1 : 0), side = (K.has('KeyD') ? 1 : 0) - (K.has('KeyA') ? 1 : 0);
  const run = WALK.run, space = K.has('Space');
  p.water = wetAt(p.x, p.y + 0.1, p.z);              // feet in the water: swimming
  const headOut = !wetAt(p.x, p.y + WK.eye, p.z);
  // where WASD points, from the way you're facing (yaw 0 looks south)
  const fx = Math.sin(p.yaw), fz = Math.cos(p.yaw), rx = -Math.cos(p.yaw), rz = Math.sin(p.yaw);
  let mx = fx * fwd + rx * side, mz = fz * fwd + rz * side;
  const len = Math.hypot(mx, mz) || 1; mx /= len; mz /= len;
  const speed = p.water ? (run ? WK.swimRun : WK.swim) : (run ? WK.run : WK.walk);
  const tx = (fwd || side) ? mx * speed : 0, tz = (fwd || side) ? mz * speed : 0;
  const grip = p.ground ? 1 - Math.exp(-dt * 18) : 1 - Math.exp(-dt * (p.water ? 6 : 3));   // less control in the air
  p.vx += (tx - p.vx) * grip; p.vz += (tz - p.vz) * grip;
  // jumping: a tap is a short hop, holding Space carries it higher (lighter gravity on the way up)
  p.coyote = p.ground ? 0.1 : Math.max(0, p.coyote - dt);
  if (WALK.jumpPress) {
    WALK.jumpPress = false;
    if ((p.coyote > 0 || (p.water && headOut)) && !boxBlocked(p.x, p.y + 0.05, p.z)) { p.vy = WK.v0; p.hold = true; p.ground = false; p.coyote = 0; }
  }
  if (!space || p.vy <= 0) p.hold = false;
  const vy0 = p.vy;
  if (p.water && !p.hold) {
    // holding Space swims up and floats with your eyes just above the surface; otherwise you sink slowly.
    // The water slows a plunge hard.
    const want = space ? clamp((waterTop(p) - WK.eye + 0.5 - p.y) * 4, -2.2, 2.2) : -0.9;
    p.vy += (want - p.vy) * (1 - Math.exp(-dt * (p.vy < want - 1 ? 10 : space ? 9 : 5)));
  } else {
    p.vy -= (p.hold ? WK.gHold : WK.g) * dt;
    p.vy = Math.max(p.vy, -30);
  }
  const vyMove = (vy0 + p.vy) / 2;                   // (the average over the frame, so jumps reach their full height)
  // move a little at a time so nothing's skipped through, one axis at a time
  const n = Math.max(1, Math.ceil(Math.max(Math.abs(p.vx), Math.abs(vyMove), Math.abs(p.vz)) * dt / 0.2));
  const h = dt / n;
  let wasGround = p.ground;
  p.ground = false;
  for (let s = 0; s < n; s++) {
    moveAxis(p, 'x', p.vx * h, wasGround);
    moveAxis(p, 'z', p.vz * h, wasGround);
    if (!moveAxis(p, 'y', vyMove * h, false)) {
      if (p.vy < 0) { p.ground = true; wasGround = true; }
      p.vy = 0; p.hold = false;
    }
  }
  if (!p.ground && p.vy <= 0 && boxBlocked(p.x, p.y - 0.02, p.z)) p.ground = true;
  if (p.y < WALK.col.ymin - 4) respawn();            // fell out of the world
}
// Move along one axis; blocked sideways, step up one block if there's room. Returns false if it stopped.
function moveAxis(p, ax, d, canStep) {
  if (!d) return true;
  const V = VOXEL;
  const at = (v) => ax === 'x' ? boxBlocked(v, p.y, p.z) : ax === 'z' ? boxBlocked(p.x, p.y, v) : boxBlocked(p.x, v, p.z);
  const cur = p[ax], nxt = cur + d;
  if (!at(nxt)) { p[ax] = nxt; return true; }
  if (ax !== 'y' && canStep) {                       // a step, a kerb, a stair: up one block
    const up = Math.floor((p.y - WALK.col.ymin) / V + 1e-3) * V + WALK.col.ymin + WK.step + 1e-4;   // one block above the floor you're on
    const lift = up - p.y;
    if (lift <= WK.step + 0.02 && !boxBlocked(p.x, up, p.z) && !(ax === 'x' ? boxBlocked(nxt, up, p.z) : boxBlocked(p.x, up, nxt))) {
      p.y = up; p[ax] = nxt; return true;
    }
  }
  // stop against it: flush with the block face
  const half = ax === 'y' ? 0 : WK.half, off = ax === 'y' ? WALK.col.ymin : 0;
  if (d > 0) {
    const edge = ax === 'y' ? cur + WK.height : cur + half;
    const face = Math.floor((edge + d - off) / V) * V + off;
    p[ax] = Math.max(cur, face - (ax === 'y' ? WK.height : half) - 1e-4);
  } else {
    const edge = cur - half;
    const face = Math.ceil((edge + d - off) / V) * V + off;
    p[ax] = Math.min(cur, face + half + 1e-4);
  }
  if (at(p[ax])) p[ax] = cur;                        // (not flush-able: stay put)
  return false;
}
function placeCamera(dt) {
  const p = WALK.p, P = S.plan, cm = P.cell;
  const want = p.y + WK.eye;
  p.camY = p.camY < want ? p.camY + (want - p.camY) * (1 - Math.exp(-dt * 22)) : want;   // eases up steps, never lags a fall
  if (want - p.camY > 1) p.camY = want - 1;
  const ox = -P.w * cm / 2, oz = -P.h * cm / 2;
  const cp = Math.cos(p.pitch);
  V3.camera.position.set(p.x + ox, p.camY, p.z + oz);
  V3.camera.lookAt(p.x + ox + Math.sin(p.yaw) * cp, p.camY + Math.sin(p.pitch), p.z + oz + Math.cos(p.yaw) * cp);
  document.body.classList.toggle('underwater', wetAt(p.x, p.camY, p.z));
  // the door you're looking at, if one's in reach
  const d = lookedAtDoor();
  if (d !== WALK.look) { WALK.look = d; const tip = $('#walkTip'); tip.hidden = !d; if (d) tip.textContent = d.open ? 'E · close the door' : 'E · open the door'; }
}

// ---- doors: the one you're looking at, opening and closing
function lookedAtDoor() {
  const p = WALK.p;
  const cp = Math.cos(p.pitch), dx = Math.sin(p.yaw) * cp, dy = Math.sin(p.pitch), dz = Math.cos(p.yaw) * cp;
  const ex = p.x, ey = p.camY, ez = p.z;
  let best = null, bt = WK.reach;
  for (const d of WALK.doors) {
    const b = d.box, g = 0.2;
    let t0 = 0, t1 = bt;
    for (const [o, v, a, c] of [[ex, dx, b[0] - g, b[3] + g], [ey, dy, b[1], b[4]], [ez, dz, b[2] - g, b[5] + g]]) {
      if (Math.abs(v) < 1e-9) { if (o < a || o > c) { t0 = Infinity; break; } continue; }
      let ta = (a - o) / v, tb = (c - o) / v;
      if (ta > tb) [ta, tb] = [tb, ta];
      t0 = Math.max(t0, ta); t1 = Math.min(t1, tb);
      if (t0 > t1) break;
    }
    if (t0 <= t1 && t0 < bt) { bt = t0; best = d; }
  }
  return best;
}
function toggleDoor() {
  const d = lookedAtDoor(), p = WALK.p;
  if (!d) return;
  if (d.open) {
    d.open = false;
    if (boxBlocked(p.x, p.y, p.z)) { d.open = true; toast('Step out of the doorway first.'); return; }
    d.target = 0;
  } else {
    d.open = true;
    // swing it away from you, about the end it's hinged at (a portcullis lifts instead)
    const b = d.box, wide = b[3] - b[0] >= b[5] - b[2];
    d.side = wide ? (p.z < (b[2] + b[5]) / 2 ? 1 : -1) : (p.x < (b[0] + b[3]) / 2 ? 1 : -1);
    d.wide = wide; d.target = 1;
  }
  WALK.look = null;
}
function animateDoors(dt) {
  const m = WALK.objMesh;
  if (!m) return;
  const THREE = window.THREE, cm = S.plan.cell, R = new THREE.Matrix4(), T1 = new THREE.Matrix4(), T2 = new THREE.Matrix4(), M = new THREE.Matrix4();
  let any = false;
  for (const d of WALK.doors) {
    if (d.swing === d.target) continue;
    d.swing = d.target > d.swing ? Math.min(d.target, d.swing + dt * 4) : Math.max(d.target, d.swing - dt * 4);
    any = true;
    d.boxes.forEach((n, i) => {
      const B = d.base[i];
      if (!B) return;
      if (d.slide) { M.makeTranslation(0, d.swing * Math.max(0, (d.box[4] - d.box[1]) - 0.5), 0).multiply(B); }
      else if (d.painted && d.boxes.length > 1) { M.copy(B); if (d.swing > 0.5) M.scale(new THREE.Vector3(1, 0.001, 1)); }    // a painted run just opens up
      else {
        // the hinge: the leaf's west end (or north end), in the 3D view's squares
        const hx = d.wide ? B.elements[12] : B.elements[12] + B.elements[0] / 2, hz = d.wide ? B.elements[14] + B.elements[10] / 2 : B.elements[14];
        const a = (d.wide ? -d.side : d.side) * d.swing * Math.PI / 2;
        T1.makeTranslation(hx, 0, hz); R.makeRotationY(a); T2.makeTranslation(-hx, 0, -hz);
        M.copy(T1).multiply(R).multiply(T2).multiply(B);
      }
      m.setMatrixAt(n, M);
    });
  }
  if (any) { m.instanceMatrix.needsUpdate = true; V3.renderer.shadowMap.needsUpdate = true; }
}

// ---- input: keys while walking never reach the editor's shortcuts
window.addEventListener('keydown', e => {
  if (!WALK.on) return;
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const c = e.code;
  e.preventDefault(); e.stopImmediatePropagation();
  if (c === 'Escape') { stopWalk(); return; }
  if (c === 'Enter' || c === 'NumpadEnter') { respawn(); return; }
  if (c === 'KeyE') { if (!e.repeat) toggleDoor(); return; }
  if (c === 'ShiftLeft' || c === 'ShiftRight' || e.key === 'Shift') { if (!e.repeat) setRun(!WALK.run); return; }
  if (c === 'KeyF') { if (!e.repeat) setFull(!WALK.full); return; }
  if (c === 'Space' && !e.repeat) WALK.jumpPress = true;
  WALK.keys.add(c);
}, true);
window.addEventListener('keyup', e => {
  if (!WALK.on) return;
  WALK.keys.delete(e.code);
  e.preventDefault(); e.stopImmediatePropagation();
}, true);
window.addEventListener('blur', () => { WALK.keys.clear(); });
// Shift turns running on and off; a tag on screen says when it's on
function setRun(on) { WALK.run = on; $('#walkRun').hidden = !on; }
// F: full screen. The 3D view takes the whole screen; where the page isn't allowed to (inside some frames), it
// fills the whole page instead. Esc leaves full screen first (the browser's own key), then walk mode.
function setFull(on) {
  const v = $('#view3d');
  WALK.full = on;
  if (on) {
    document.body.classList.add('walk-full');
    if (v.requestFullscreen && !document.fullscreenElement) v.requestFullscreen().catch(() => { /* (fills the page instead) */ });
  } else {
    document.body.classList.remove('walk-full');
    if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(() => {});
  }
  requestAnimationFrame(resize3d);
}
document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement && WALK.full) setFull(false); });
// Drag to look, all the way round. While the button's held the pointer is locked (hidden, and it reports how
// far the mouse moves, not where the cursor is), so the screen's edge never stops a turn. Where the page
// isn't allowed to lock it (inside some frames), holding the drag near the view's left or right edge keeps
// turning that way instead (edgeTurn).
let WDRAG = null;
const locked = () => document.pointerLockElement === c3d;
c3d.addEventListener('pointerdown', e => {
  if (!WALK.on) return;
  try { c3d.setPointerCapture(e.pointerId); } catch { /* ignore */ }
  WDRAG = { id: e.pointerId, x: e.clientX, y: e.clientY };
  if (e.pointerType === 'mouse' && c3d.requestPointerLock) {
    try { const r = c3d.requestPointerLock(); if (r && r.catch) r.catch(() => {}); } catch { /* not allowed here: edge turning */ }
  }
});
c3d.addEventListener('pointermove', e => {
  if (!WALK.on || !WDRAG || !WALK.p) return;
  const lk = locked();
  if (!lk && WDRAG.id !== e.pointerId) return;
  const p = WALK.p, cap = v => clamp(v, -250, 250);   // (the first locked move can jump)
  const dx = lk ? cap(e.movementX || 0) : e.clientX - WDRAG.x, dy = lk ? cap(e.movementY || 0) : e.clientY - WDRAG.y;
  p.yaw -= dx * WK.look;
  p.pitch = clamp(p.pitch - dy * WK.look, -1.5, 1.5);
  if (!lk) { WDRAG.x = e.clientX; WDRAG.y = e.clientY; }
});
const endDrag = e => {
  if (!WDRAG || (WDRAG.id !== e.pointerId && !locked())) return;
  WDRAG = null;
  if (locked() && document.exitPointerLock) document.exitPointerLock();
};
c3d.addEventListener('pointerup', endDrag);
c3d.addEventListener('pointercancel', endDrag);
document.addEventListener('pointerlockchange', () => { if (!locked() && WDRAG && WDRAG.wasLocked) WDRAG = null; if (locked() && WDRAG) WDRAG.wasLocked = true; });
// without the lock: the drag held near the view's left or right edge keeps turning, faster nearer the edge
function edgeTurn(dt) {
  if (!WDRAG || locked() || !WALK.p) return;
  const r = c3d.getBoundingClientRect(), band = Math.max(24, r.width * 0.08);
  const into = WDRAG.x < r.left + band ? (r.left + band - WDRAG.x) / band : WDRAG.x > r.right - band ? -(WDRAG.x - (r.right - band)) / band : 0;
  if (into) WALK.p.yaw += clamp(into, -1, 1) * 2.6 * dt;     // up to 2.6 radians a second
}
$('#walkBtn').addEventListener('click', startWalk);
$('#walkExit').addEventListener('click', stopWalk);
