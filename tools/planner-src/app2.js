
// ---------------------------------------------------------------------------
// Storage: the artifact database when available, this browser otherwise
// ---------------------------------------------------------------------------
function dbStore(db) {
  const col = db.collection('plans');
  return {
    subscribe(next, err) { return col.onSnapshot(snap => next(snap.docs.filter(d => d.exists).map(d => ({ id: d.id, data: d.data() }))), err); },
    newId: () => col.doc().id,
    save: (id, data) => col.doc(id).set(data),
    remove: id => col.doc(id).delete(),
    subscribeDoc: (path, next, err) => db.doc(path).onSnapshot(s => next(s.exists ? s.data() : null), err),
    saveDoc: (path, data) => db.doc(path).set(data),
  };
}
function localStore() {
  let docs = LS.get('plans', {}) || {};
  const subs = [];
  const emit = () => { const list = Object.entries(docs).map(([id, data]) => ({ id, data })); subs.forEach(f => f(list)); };
  const persist = () => LS.set('plans', docs);
  return {
    subscribe(next) { subs.push(next); setTimeout(emit, 0); return () => {}; },
    newId: () => uid('p'),
    save(id, data) { docs[id] = clone(data); persist(); setTimeout(emit, 0); return Promise.resolve(); },
    remove(id) { delete docs[id]; persist(); setTimeout(emit, 0); return Promise.resolve(); },
    subscribeDoc(path, next) { setTimeout(() => next(LS.get('doc:' + path, null)), 0); return () => {}; },
    saveDoc(path, data) { LS.set('doc:' + path, data); return Promise.resolve(); },
  };
}
// Big plans are stored packed: everything but their name, project, size and save stamps deflated into `z`
// (base64, with `zip: 1`), so plans like the Laketown site fit in one database document (256 KB). Packing and
// unpacking happen here, at the store, so the rest of the page only ever sees whole plans. Claude's generators
// pack the same way (mage_common.pack_doc).
const PACK_OVER = 64000;                                       // pack a plan whose JSON is longer than this
const PACK_KEEP = ['v', 'fmt', 'name', 'project', 'w', 'h', 'cell', 'altar', 'rev', 'editor', 'updatedAt'];
function bytesToB64(u8) {
  let s = '';
  for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
  return btoa(s);
}
function b64ToBytes(b) { const s = atob(b), u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u; }
function packPlan(d) {
  if (!d || typeof d.z === 'string' || typeof pako === 'undefined') return d;
  if (JSON.stringify(d).length <= PACK_OVER) return d;
  const out = {}, rest = {};
  for (const [k, v] of Object.entries(d)) (PACK_KEEP.includes(k) ? out : rest)[k] = v;
  out.zip = 1; out.z = bytesToB64(pako.deflateRaw(JSON.stringify(rest), { level: 9 }));
  return out;
}
// A packed plan unpacked, or with `packErr` set if it can't be (the page then won't open it, so it can't be
// saved over with an empty plan).
function unpackPlan(d) {
  if (!d || typeof d.z !== 'string') return d;
  try {
    const o = { ...JSON.parse(pako.inflateRaw(b64ToBytes(d.z), { to: 'string' })), ...d };
    delete o.z; delete o.zip;
    return o;
  } catch { const o = { ...d }; delete o.z; o.packErr = true; return o; }
}
function packedStore(st) {
  const cache = new Map();                                     // id -> { z, doc }: unpack each version once
  const un = (id, d) => {
    if (!d || typeof d.z !== 'string') return d;
    const c = cache.get(id);
    if (c && c.z === d.z) return c.doc;
    const doc = unpackPlan(d);
    cache.set(id, { z: d.z, doc });
    return doc;
  };
  return { ...st,
    subscribe: (next, err) => st.subscribe(list => { for (const p of list) STORED.set(p.id, p.data); next(list.map(p => ({ id: p.id, data: un(p.id, p.data) }))); }, err),
    save(id, data) {                                           // never write back a plan it couldn't read
      if (data && data.packErr) return Promise.reject(Object.assign(new Error('packed plan not unpacked'), { code: 'packed' }));
      const out = packPlan(data);
      STORED.set(id, out);                                     // (its stored size, for the Plan tab's limits)
      return st.save(id, out).then(r => { if (id === S.planId) updateLimitChip(); return r; });
    },
  };
}
// Player-measured item sizes, shared with Claude: { sizes: { type: { w, d, h } } } in metres.
function onLibSizes(d) {
  const out = {};
  const sizes = d && d.sizes && typeof d.sizes === 'object' ? d.sizes : {};
  for (const [t, v] of Object.entries(sizes)) {
    if (!LIB_BY_TYPE[t] || !v || typeof v !== 'object') continue;
    out[t] = { w: num(v.w, LIB_BY_TYPE[t].w, 0.5, 64), d: num(v.d, LIB_BY_TYPE[t].d, 0.5, 64), h: num(v.h, LIB_BY_TYPE[t].h, 0.1, 40) };
    if (v.z != null && Number.isFinite(Number(v.z))) out[t].z = num(v.z, 0, 0, 40);
    if (typeof v.mount === 'string' && MOUNTS[v.mount]) out[t].mount = v.mount;
  }
  S.libSizes = out;
  if (S.itemDef && S.itemDef.lib && LIB_BY_TYPE[S.itemDef.type]) armItem(S.itemDef.lib, true);
  renderItemsPane(); renderInspector();
}
async function saveLibSize(type, size) {
  const next = { ...S.libSizes };
  if (size) next[type] = size; else delete next[type];
  S.libSizes = next;
  renderItemsPane(); renderInspector();
  try { await S.store.saveDoc('meta/library', { sizes: next, updatedAt: Date.now() }); }
  catch { toast('Couldn’t save that size. Try again.', 'bad'); }
}

function onPlans(list) {
  S.plans = new Map(list.map(p => [p.id, p.data]));
  S.loaded = true;
  renderPlanSelect();
  if (S.planId) {
    const d = S.plans.get(S.planId);
    if (d) {
      if (S.creating === S.planId) S.creating = null;
      if (d.rev && d.rev !== S.baseRev && !S.myRevs.has(d.rev)) handleRemote(d);
    } else if (S.creating !== S.planId) {
      const wasDirty = S.dirty;
      S.planId = null; S.plan = null; S.dirty = false;
      if (wasDirty) toast('This plan was deleted in another window.');
    }
  }
  if (!S.planId) {
    const last = LS.get('last', null);
    const pick = (last && S.plans.has(last)) ? last : newestPlanId();
    if (pick) openPlan(pick); else showEmpty('none');
  }
}
function onStoreError(e) {
  const code = e && e.code;
  if (code === 'revoked') { S.readOnly = true; S.saveErr = 'revoked'; }
  else if (code === 'unavailable') { setTimeout(() => S.store.subscribe(onPlans, onStoreError), 3000); }
  else S.saveErr = 'load';
  setSync();
}
function newestPlanId() {
  let best = null, t = -1;
  for (const [id, d] of S.plans) { const u = Number(d.updatedAt) || 0; if (u > t) { t = u; best = id; } }
  return best;
}
function sortedPlans() { return [...S.plans.entries()].sort((a, b) => (Number(b[1].updatedAt) || 0) - (Number(a[1].updatedAt) || 0)); }

async function openPlan(id) {
  if (S.dirty) await flushSave();
  const d = S.plans.get(id);
  if (!d) return;
  if (d.packErr) { toast(`“${d.name}” is stored packed and couldn’t be unpacked. Reload the page to try again.`, 'bad'); return; }
  histPark();                                                  // (each plan keeps its last steps while the page is open)
  S.planId = id; S.plan = normalizePlan(d); S.baseRev = d.rev || null; S.dirty = false;
  if (S.project !== '*') S.project = S.plan.project || '';
  warnReadProblems();
  histLoad(id); progSubscribe(id); S.sel = null; S.float = null; S.measure = null; S.preview = null; S.remote = null;
  S.mirror.cx = S.mirror.cy = null; S.mirrorPick = false;
  hideBanner();
  const g = S.plan.levels.findIndex(l => l.elev >= 0);
  S.levelIdx = g < 0 ? 0 : g;
  if (S.layer != null) S.layer = 0;
  ensureBrushes();
  LS.set('last', id);
  S.cam.r = Number(LS.get('turn:' + id, 0)) & 3;                // (each plan keeps its 2D turn in this browser)
  hideEmpty();
  fitView(true);
  V3.fit = true;
  refreshAll();
}
function handleRemote(d) {
  if (d.packErr) return;                                       // (can't read it; keep what's open)
  const who = d.editor === 'claude' ? 'Claude' : 'Another window';
  if (!S.dirty && !S.saving && liveBase == null && !G) adoptRemote(d, `${who} updated this plan. Undo puts your version back.`);
  else { S.remote = d; showBanner(`${who} changed this plan while you were editing.`); }
}
function adoptRemote(d, msg) {
  if (S.plan) { S.hist.push({ s: JSON.stringify(serialize(S.plan, true)), label: d.editor === 'claude' ? 'Claude’s update' : 'Update from another window', t: Date.now() }); S.fut = []; histTrim(); }
  const keep = lv() && lv().id;
  S.plan = normalizePlan(d); S.baseRev = d.rev || null; S.dirty = false; S.remote = null;
  S.levelIdx = levelIndex(keep);
  warnReadProblems();
  validateSel(); ensureBrushes(); hideBanner();
  refreshAll();
  if (msg) toast(msg);
}
function showBanner(text) { $('#bannerText').textContent = text; $('#banner').hidden = false; }
function hideBanner() { $('#banner').hidden = true; }

function markDirty() {
  planVer++;
  if (!S.plan || S.readOnly) return;
  S.dirty = true;
  clearTimeout(S.saveTimer);
  S.saveTimer = setTimeout(flushSave, 800);
  setSync();
}
function flushSave() {
  clearTimeout(S.saveTimer);
  if (!S.plan || !S.dirty || S.readOnly || !S.store) return Promise.resolve();
  if (S.saving) { S.again = true; return S.savingP; }
  const data = serialize(S.plan, false);
  data.rev = uid('r'); data.editor = 'page'; data.updatedAt = Date.now();
  const out = packPlan(data);                                  // (big plans go packed)
  if (JSON.stringify(out).length > 250000) { S.saveErr = 'too_big'; setSync(); return Promise.resolve(); }
  S.saving = true; S.dirty = false; S.baseRev = data.rev; S.myRevs.add(data.rev);
  if (S.myRevs.size > 80) S.myRevs.delete(S.myRevs.values().next().value);
  setSync();
  const id = S.planId;
  S.savingP = (async () => {
    try { await S.store.save(id, out); S.saveErr = null; }
    catch (e) {
      const code = e && e.code;
      if (code === 'invalid_argument') { S.readOnly = true; S.saveErr = 'readonly'; }
      else if (code === 'quota_exceeded') { S.saveErr = 'quota'; S.dirty = true; }
      else { S.saveErr = 'retry'; S.dirty = true; setTimeout(flushSave, 2500 + Math.random() * 1500); }
    } finally {
      S.saving = false;
      if (S.again) { S.again = false; if (S.dirty) flushSave(); }
      setSync();
    }
  })();
  return S.savingP;
}
function setSync() {
  const chip = $('#syncChip'), text = $('#syncText');
  let st = 'idle', t = 'Opening…';
  if (S.saveErr === 'readonly' || (S.readOnly && S.mode === 'db')) { st = 'warn'; t = 'View only'; }
  else if (S.saveErr === 'revoked') { st = 'warn'; t = 'Access changed'; }
  else if (S.saveErr === 'quota') { st = 'bad'; t = 'Storage full'; }
  else if (S.saveErr === 'too_big') { st = 'bad'; t = 'Too large to save'; }
  else if (S.saveErr === 'retry') { st = 'warn'; t = 'Retrying save…'; }
  else if (S.saveErr === 'load') { st = 'bad'; t = 'Couldn’t load plans'; }
  else if (S.mode === 'connecting') { st = 'idle'; t = 'Opening…'; }
  else if (S.saving || S.dirty) { st = 'busy'; t = 'Saving…'; }
  else if (S.mode === 'db') { st = 'ok'; t = 'Saved · shared with Claude'; }
  else { st = 'idle'; t = 'Saved in this browser'; }
  chip.dataset.state = st;
  text.textContent = t;
  chip.title = S.mode === 'db' ? 'Plans are stored with this page. Claude can read and edit them when you ask in chat.' : 'Plans are stored in this browser only.';
}

// ---------------------------------------------------------------------------
// Undo history
// ---------------------------------------------------------------------------
let actionBase = null;   // snapshot before a canvas action
let actionLabel = null;  // what it's called in the history (worked out from the change when not given)
let liveBase = null;     // snapshot before a typed / picked field edit
const snap = () => JSON.stringify(serialize(S.plan, true));
function begin(label) { if (!S.plan) return; if (liveBase != null) liveCommit(); actionBase = snap(); actionLabel = label || null; }
function commit() {
  if (actionBase == null || !S.plan) return false;
  const now = snap(), changed = now !== actionBase;
  if (changed) pushHist(actionBase, actionLabel || describeChange(actionBase, now));
  actionBase = null; actionLabel = null;
  if (changed) afterEdit();
  updateUndo();
  return changed;
}
function cancelAction() { if (actionBase != null) { restoreSnap(actionBase); actionBase = null; } }
function liveBegin() { if (S.plan && liveBase == null) liveBase = snap(); }
function liveCommit() {
  if (liveBase == null || !S.plan) return;
  const base = liveBase; liveBase = null;
  const now = snap();
  if (now !== base) { pushHist(base, describeChange(base, now)); afterEdit(); }
  updateUndo();
}
function pushHist(s, label) { S.hist.push({ s, label: label || 'Edit', t: Date.now() }); S.fut.length = 0; histTrim(); }
function restoreSnap(json) {
  const keep = lv() && lv().id, name = S.plan.name, notes = S.plan.notes;
  const d = JSON.parse(json); d.name = name; d.notes = notes;
  S.plan = normalizePlan(d); planVer++;
  S.levelIdx = levelIndex(keep);
  validateSel(); ensureBrushes();
}
function undo() {
  if (liveBase != null) liveCommit();
  if (!S.hist.length || !S.plan || G) return;
  const e = S.hist.pop(); S.fut.push({ s: snap(), label: e.label, t: e.t }); restoreSnap(e.s); afterEdit(); refreshPanels(); updateUndo();
}
function redo() {
  if (!S.fut.length || !S.plan || G) return;
  const e = S.fut.pop(); S.hist.push({ s: snap(), label: e.label, t: e.t }); histTrim(); restoreSnap(e.s); afterEdit(); refreshPanels(); updateUndo();
}
function afterEdit() { markDirty(); req2d(); mark3d(); scheduleCounts(); updateStatus(); }
let countsTimer = 0;
function scheduleCounts() { clearTimeout(countsTimer); countsTimer = setTimeout(() => { renderMaterials(); renderPlacedList(); renderStats(); }, 250); }

function validateSel() {
  if (!S.sel) return;
  if (S.sel.type === 'item' && !findItem(S.sel.id)) S.sel = null;
  else if (S.sel.type === 'zone' && !findZone(S.sel.id)) S.sel = null;
  else if (S.sel.type === 'cells') {
    const R = S.sel.rect;
    if (R.x >= S.plan.w || R.y >= S.plan.h) S.sel = null;
    else S.sel.rect = { x: R.x, y: R.y, w: Math.min(R.w, S.plan.w - R.x), h: Math.min(R.h, S.plan.h - R.y) };
  }
}
function ensureBrushes() {
  const P = S.plan, keys = Object.keys(P.palette);
  const ofKind = ks => keys.filter(k => ks.includes(P.palette[k].kind));
  if (!P.palette[S.brush]) S.brush = keys[0];
  if (!P.palette[S.roomWall] || !['wall', 'block'].includes(P.palette[S.roomWall].kind)) S.roomWall = ofKind(['wall', 'block'])[0] || keys[0];
  if (S.roomFloor && (!P.palette[S.roomFloor] || !['floor', 'water'].includes(P.palette[S.roomFloor].kind))) S.roomFloor = ofKind(['floor'])[0] || '';
}

// ---------------------------------------------------------------------------
// Editing operations
// ---------------------------------------------------------------------------
// Where the item being placed would go: doors and windows into the wall under the cursor, wall items back
// against the nearest wall, the rest centred on the cursor. Snapped to the block grid.
function ghostFor(gx, gy) {
  const def = S.itemDef, P = S.plan, st = itemStep(P), mount = mountOf(def);
  // in block layers the walls are the ones at the layer's height: a door or window snaps into whichever level's wall
  // is there (that's the wall it cuts, so it goes on that level), a wall item hangs on any wall at that height
  let L = lv(), home = null;
  if (layerOn()) {
    const k = curLayer();
    const B = IN_WALL.has(mount) ? layerWallLevel(Math.floor(gx), Math.floor(gy), k) : null;
    L = B ? { ...B, grid: layerOcc(B, k), anyBase: true } : { ...lv(), grid: layerView(k), anyBase: true };
    home = B && B.id;
  }
  if (IN_WALL.has(mount)) {
    const slot = wallSlot(L, gx, gy, def.w, S.itemRot);
    if (slot) { slot.home = home; return slot; }
  }
  let rot = S.itemRot, wallAt = null;
  if (mount === 'wall') { const f = wallBehind(L, gx, gy); if (f != null) { rot = f; wallAt = [Math.floor(gx), Math.floor(gy)]; } }
  const r = rot % 180 !== 0, w = r ? def.d : def.w, hh = r ? def.w : def.d;
  const g = { x: clamp(snapStep(gx - w / 2, st), 0, Math.max(0, P.w - w)), y: clamp(snapStep(gy - hh / 2, st), 0, Math.max(0, P.h - hh)), w, h: hh, rot };
  if (wallAt) againstWall(g, wallAt[0], wallAt[1]);
  if (IN_WALL.has(mount) || (mount === 'wall' && !wallAt)) g.bad = true;
  return g;
}
function placeItem() {
  const g = S.ghostItem, def = S.itemDef;
  if (!g || !def) return;
  begin();
  const mount = mountOf(def), inWall = IN_WALL.has(mount);
  let L = lv(), z = def.z != null ? def.z : defaultZ(mount, def.h, L);
  if (layerOn()) ({ L, z } = layerItemHome(mount, g, def));     // (in block layers: at the layer's height)
  const it = { id: uid('i'), level: L.id, type: def.type, label: def.name, x: g.x, y: g.y, w: def.w, d: inWall ? 1 : def.d, h: def.h, rot: g.rot != null ? g.rot : S.itemRot, color: def.color };
  if (mount !== 'floor') it.mount = mount;
  if (z > 0) it.z = z;
  S.plan.items.push(it, ...mirrorItems(it));
  commit();
  if (def.lib && def.lib.type) noteRecent(def.lib.type);
  if (g.bad) toast(inWall ? `That isn't all wall: a ${mount} cuts its opening only in wall squares.` : 'There’s no wall beside it to hang on.');
}
function rotateItem(it, dir = 1) {
  if (IN_WALL.has(it.mount)) { it.rot = (it.rot + 180) % 360; return; }    // a door or window: turn it to face the other way
  const R0 = itemRect(it), cx = R0.x + R0.w / 2, cy = R0.y + R0.h / 2, st = itemStep();
  it.rot = (it.rot + 90 * dir + 360) % 360;
  const R1 = itemRect(it);
  it.x = clamp(snapStep(cx - R1.w / 2, st), 0, Math.max(0, S.plan.w - R1.w));
  it.y = clamp(snapStep(cy - R1.h / 2, st), 0, Math.max(0, S.plan.h - R1.h));
}
function addZone(a, b) {
  const R = rectFrom(a, b);
  begin();
  const n = S.plan.zones.length;
  const z = { id: uid('z'), level: lv().id, name: 'Area ' + (n + 1), x: R.x, y: R.y, w: R.w, h: R.h, color: ZONE_COLORS[n % ZONE_COLORS.length] };
  S.plan.zones.push(z);
  commit();
  S.sel = { type: 'zone', id: z.id };
  renderInspector();
  const inp = $('#inspName'); if (inp) { inp.focus(); inp.select(); }
}
function contentIn(R, L) {
  const cells = [];
  for (let y = R.y; y < R.y + R.h; y++) for (let x = R.x; x < R.x + R.w; x++) { const ch = L.grid[y][x]; if (ch !== ' ') cells.push([x - R.x, y - R.y, ch]); }
  const items = S.plan.items.filter(it => it.level === L.id && rectInside(itemRect(it), R));
  const zones = S.plan.zones.filter(z => z.level === L.id && rectInside(z, R));
  return { cells, items, zones };
}
function liftSelection() {
  const R = S.sel.rect, L = lv(), c = contentIn(R, L);
  for (const [dx, dy] of c.cells) L.grid[R.y + dy][R.x + dx] = ' ';
  S.float = { R: { ...R }, cells: c.cells, items: c.items.map(it => ({ it, x: it.x, y: it.y })), zones: c.zones.map(z => ({ z, x: z.x, y: z.y })), dx: 0, dy: 0 };
}
function moveFloat(dx, dy) {
  const F = S.float;
  dx = clamp(dx, -F.R.x, S.plan.w - (F.R.x + F.R.w));
  dy = clamp(dy, -F.R.y, S.plan.h - (F.R.y + F.R.h));
  F.dx = dx; F.dy = dy;
  for (const o of F.items) { o.it.x = o.x + dx; o.it.y = o.y + dy; }
  for (const o of F.zones) { o.z.x = o.x + dx; o.z.y = o.y + dy; }
}
function dropFloat() {
  const F = S.float, L = lv();
  for (const [cx, cy, ch] of F.cells) setCell(L, F.R.x + F.dx + cx, F.R.y + F.dy + cy, ch);
  S.sel = { type: 'cells', rect: { x: F.R.x + F.dx, y: F.R.y + F.dy, w: F.R.w, h: F.R.h } };
  S.float = null;
}
function nudgeSelection(dx, dy) {
  if (!S.sel || S.readOnly) return;
  if (S.sel.type === 'cells') { begin(); liftSelection(); moveFloat(dx, dy); dropFloat(); commit(); }
  else if (S.sel.type === 'item') {
    const it = findItem(S.sel.id); if (!it) return;
    const R = itemRect(it); begin();
    it.x = clamp(it.x + dx, 0, Math.max(0, S.plan.w - R.w)); it.y = clamp(it.y + dy, 0, Math.max(0, S.plan.h - R.h));
    commit();
  } else if (S.sel.type === 'zone') {
    const z = findZone(S.sel.id); if (!z) return;
    begin();
    z.x = clamp(z.x + dx, 0, Math.max(0, S.plan.w - z.w)); z.y = clamp(z.y + dy, 0, Math.max(0, S.plan.h - z.h));
    commit();
  }
  renderInspector();
}
function deleteSelection() {
  if (!S.sel || S.readOnly) return;
  begin();
  if (S.sel.type === 'cells') {
    const R = S.sel.rect, L = lv(), c = contentIn(R, L);
    for (const [dx, dy] of c.cells) L.grid[R.y + dy][R.x + dx] = ' ';
    const iset = new Set(c.items), zset = new Set(c.zones);
    S.plan.items = S.plan.items.filter(i => !iset.has(i));
    S.plan.zones = S.plan.zones.filter(z => !zset.has(z));
  } else if (S.sel.type === 'item') S.plan.items = S.plan.items.filter(i => i.id !== S.sel.id);
  else if (S.sel.type === 'zone') S.plan.zones = S.plan.zones.filter(z => z.id !== S.sel.id);
  if (S.sel.type !== 'cells') S.sel = null;
  commit();
  renderInspector();
}
function copySelection() {
  if (!S.sel) return;
  if (S.sel.type === 'cells') {
    const R = S.sel.rect, c = contentIn(R, lv());
    S.clip = { R: { ...R }, cells: c.cells, items: c.items.map(i => ({ ...i, x: i.x - R.x, y: i.y - R.y })), zones: c.zones.map(z => ({ ...z, x: z.x - R.x, y: z.y - R.y })) };
  } else if (S.sel.type === 'item') {
    const it = findItem(S.sel.id); if (!it) return;
    const R = itemRect(it);
    S.clip = { R, cells: [], items: [{ ...it, x: 0, y: 0 }], zones: [] };
  } else return;
  toast('Copied. Paste with Ctrl+V (at the cursor) or Ctrl+Shift+V (in place).');
}
function pasteClip(inPlace, targetLevelId) {
  const C = S.clip;
  if (!C || !S.plan || S.readOnly) return;
  const P = S.plan;
  let x = C.R.x, y = C.R.y;
  if (!inPlace && S.hover && S.hoverIn) { x = S.hover[0]; y = S.hover[1]; }
  x = clamp(x, 0, Math.max(0, P.w - C.R.w)); y = clamp(y, 0, Math.max(0, P.h - C.R.h));
  const L = targetLevelId ? S.plan.levels.find(l => l.id === targetLevelId) : lv();
  if (!L) return;
  begin();
  for (const [cx, cy, ch] of C.cells) setCell(L, x + cx, y + cy, ch);
  for (const it of C.items) P.items.push({ ...it, id: uid('i'), level: L.id, x: x + it.x, y: y + it.y });
  for (const z of C.zones) P.zones.push({ ...z, id: uid('z'), level: L.id, x: x + z.x, y: y + z.y });
  commit();
  if (!targetLevelId) S.sel = { type: 'cells', rect: { x, y, w: C.R.w, h: C.R.h } };
  renderInspector();
}
function copySelectionToLevel(levelId) {
  if (!S.sel || S.sel.type !== 'cells') return;
  const saved = S.clip;
  const R = S.sel.rect, c = contentIn(R, lv());
  S.clip = { R: { ...R }, cells: c.cells, items: c.items.map(i => ({ ...i, x: i.x - R.x, y: i.y - R.y })), zones: c.zones.map(z => ({ ...z, x: z.x - R.x, y: z.y - R.y })) };
  pasteClip(true, levelId);
  S.clip = saved;
  const L = S.plan.levels.find(l => l.id === levelId);
  toast(`Copied to ${L ? L.name : 'level'}.`);
}
function fillSelection(ch) {
  if (!S.sel || S.sel.type !== 'cells') return;
  const R = S.sel.rect, L = lv();
  begin();
  for (let y = R.y; y < R.y + R.h; y++) for (let x = R.x; x < R.x + R.w; x++) setCell(L, x, y, ch);
  commit();
}

// Levels
function setLevel(i) {
  if (!S.plan) return;
  const n = clamp(i, 0, S.plan.levels.length - 1);
  if (n === S.levelIdx) return;
  if (S.float) return;
  S.levelIdx = n;
  if (S.sel && S.sel.type !== 'cells') S.sel = null;
  renderInspector(); renderLevels(); renderPlacedList(); renderOptbar(); updateStatus(); req2d(); mark3d();
}
function addLevel(where) {
  if (S.plan.levels.length >= MAX_LEVELS) { toast(`A plan can have up to ${MAX_LEVELS} levels.`); return; }
  const P = S.plan;
  begin();
  const below = where === 'below';
  const elev = below ? Math.min(...P.levels.map(l => l.elev)) - GAME.levelH : topOfLevels();
  const n = P.levels.filter(l => l.elev < 0).length;
  const L = { id: uid('L'), name: below ? (n ? `Basement ${n + 1}` : 'Basement') : 'Level ' + (P.levels.length + 1), elev, height: GAME.levelH, hidden: false, grid: blankGrid(P.w, P.h) };
  if (below && !Object.values(P.palette).some(e => e.kind === 'dig')) {        // something to mark open digging with
    const k = nextFreeKey(); if (k) P.palette[k] = { name: 'Dug out (open)', kind: 'dig', color: '#3d332a' };
  }
  P.levels.push(L); P.levels.sort((a, b) => a.elev - b.elev);
  S.levelIdx = P.levels.indexOf(L);
  commit(); refreshPanels();
}
function duplicateLevel() {
  if (S.plan.levels.length >= MAX_LEVELS) { toast(`A plan can have up to ${MAX_LEVELS} levels.`); return; }
  const P = S.plan, src = lv();
  begin();
  const L = { id: uid('L'), name: (src.name + ' copy').slice(0, 80), elev: topOfLevels(), height: src.height, hidden: false, ...(mainLevel(src).group ? { group: mainLevel(src).group } : {}), grid: src.grid.map(r => r.slice()) };
  for (const it of P.items.filter(i => i.level === src.id)) P.items.push({ ...it, id: uid('i'), level: L.id });
  for (const z of P.zones.filter(q => q.level === src.id)) P.zones.push({ ...z, id: uid('z'), level: L.id });
  P.levels.push(L); P.levels.sort((a, b) => a.elev - b.elev);
  S.levelIdx = P.levels.indexOf(L);
  commit(); refreshPanels();
}
async function deleteLevel() {
  const P = S.plan, L = lv();
  if (P.levels.length === 1) { toast('A plan needs at least one level.'); return; }
  const hasContent = L.grid.some(r => r.some(c => c !== ' ')) || P.items.some(i => i.level === L.id);
  if (hasContent && !(await confirmBox('Delete this level?', `“${L.name}” and everything drawn on it will be removed. You can undo this.`, 'Delete level', true))) return;
  begin();
  P.levels = P.levels.filter(l => l !== L);
  P.items = P.items.filter(i => i.level !== L.id);
  P.zones = P.zones.filter(z => z.level !== L.id);
  S.levelIdx = clamp(S.levelIdx - 1, 0, P.levels.length - 1);
  S.sel = null;
  commit(); refreshPanels();
}

// A plan saved in numbered symbols whose runs didn't all read (the unread squares were left empty), or with
// more levels than the planner holds: say so.
function warnReadProblems() {
  const n = S.plan && S.plan.readProblems, d = S.plan && S.plan.droppedLevels;
  if (n) toast(`${n} part${n === 1 ? '' : 's'} of this plan couldn't be read and ${n === 1 ? 'was' : 'were'} left empty. Check it before saving over it.`, 'bad');
  if (d) toast(`This plan has ${MAX_LEVELS + d} levels and the planner holds ${MAX_LEVELS}, so the last ${d} weren't loaded. Saving over it would lose them.`, 'bad');
}

// Materials
// Letters and digits first, then every other visible ASCII character, then the symbols past them (95 to
// 999), which show as their numbers.
const KEY_CANDIDATES = (() => {
  const first = 'ABCEFGHJKLMNPQRSTUVXYZabcdeghijklmnpqrstuvwxyz0123456789*+-/<>?!$%&@^_|';
  let all = first;
  for (let c = 33; c <= 126; c++) { const ch = String.fromCharCode(c); if (!all.includes(ch)) all += ch; }
  const list = [...all];
  for (let n = 95; n <= MAX_SYMBOLS; n++) list.push(symChar(n));
  return list;
})();
function nextFreeKey() { for (const c of KEY_CANDIDATES) if (!S.plan.palette[c]) return c; return null; }
function addMaterial() {
  const k = nextFreeKey();
  if (!k) { toast('No free symbols left.'); return; }
  begin();
  S.plan.palette[k] = { name: 'New material', kind: 'wall', color: '#6d7f8c' };
  commit();
  S.brush = k; S.editMat = k;
  renderMaterials(); renderOptbar();
}
function changeMaterialKey(oldK, newK) {
  const P = S.plan;
  if (newK === oldK || newK === symText(oldK)) return true;
  if (!PRINT.test(newK)) { toast('Use one visible character, like # or W.'); return false; }
  if (P.palette[newK]) { toast(`“${newK}” is already used by ${P.palette[newK].name}.`); return false; }
  begin();
  const pal = {};
  for (const [k, v] of Object.entries(P.palette)) pal[k === oldK ? newK : k] = v;
  P.palette = pal;
  for (const L of P.levels) for (const r of L.grid) for (let x = 0; x < r.length; x++) if (r[x] === oldK) r[x] = newK;
  if (S.brush === oldK) S.brush = newK;
  if (S.roomWall === oldK) S.roomWall = newK;
  if (S.roomFloor === oldK) S.roomFloor = newK;
  S.editMat = newK;
  commit();
  return true;
}
async function deleteMaterial(k) {
  const P = S.plan, e = P.palette[k];
  if (Object.keys(P.palette).length <= 1) { toast('Keep at least one material.'); return; }
  const n = computeCounts()[k] || 0;
  if (n && !(await confirmBox(`Remove ${e.name}?`, `${n} block${n === 1 ? '' : 's'} painted with it will be cleared. You can undo this.`, 'Remove', true))) return;
  begin();
  delete P.palette[k];
  for (const L of P.levels) for (const r of L.grid) for (let x = 0; x < r.length; x++) if (r[x] === k) r[x] = ' ';
  S.editMat = null;
  ensureBrushes();
  commit();
  renderMaterials(); renderOptbar();
}
function addCatalogueBlock(b, kind) {
  const P = S.plan;
  if (!P || S.readOnly) return;
  const have = Object.entries(P.palette).find(([, e]) => e.name === b.n && e.kind === kind);
  if (have) { pickBrush(have[0]); toast(`${b.n} (${kind}) is already in this plan, so it's now your brush.`); return; }
  const k = nextFreeKey();
  if (!k) { toast('This plan has used every symbol. Remove a material first.', 'bad'); return; }
  begin();
  P.palette[k] = { name: b.n.slice(0, 40), kind, color: b.c };
  commit();
  S.brush = k; S.matView = 'plan';
  if (!PAINT_TOOLS.has(S.tool)) setTool('paint'); else renderOptbar();
  renderMaterials();
  toast(`Added ${b.n} as a ${kind}, symbol “${symText(k)}”. Paint away.`);
}
function addUnknownSymbol(k) {
  begin();
  S.plan.palette[k] = { name: 'Symbol ' + symText(k), kind: 'wall', color: '#8a8f96' };
  commit();
  S.editMat = k; renderMaterials();
}

// Canvas size
async function resizePlan(nw, nh) {
  const P = S.plan;
  nw = clampInt(nw, 4, MAX_GRID, P.w); nh = clampInt(nh, 4, MAX_GRID, P.h);
  if (nw === P.w && nh === P.h) return;
  const dx = Math.floor((nw - P.w) / 2), dy = Math.floor((nh - P.h) / 2);
  const B = boundsOf(P.levels);
  const clips = B && (B.x + dx < 0 || B.y + dy < 0 || B.x + B.w + dx > nw || B.y + B.h + dy > nh);
  if (clips && !(await confirmBox('Shrink the canvas?', 'Some of the plan sits outside the new size and will be cut off. You can undo this.', 'Resize', true))) return;
  begin();
  for (const L of P.levels) {
    const g = blankGrid(nw, nh);
    for (let y = 0; y < P.h; y++) for (let x = 0; x < P.w; x++) { const X = x + dx, Y = y + dy; if (X >= 0 && Y >= 0 && X < nw && Y < nh) g[Y][X] = L.grid[y][x]; }
    L.grid = g;
  }
  P.items = P.items.filter(it => { it.x += dx; it.y += dy; const R = itemRect(it); return R.x >= 0 && R.y >= 0 && R.x + R.w <= nw && R.y + R.h <= nh; });
  P.zones = P.zones.filter(z => {
    z.x += dx; z.y += dy;
    const x0 = clamp(z.x, 0, nw), y0 = clamp(z.y, 0, nh), x1 = clamp(z.x + z.w, 0, nw), y1 = clamp(z.y + z.h, 0, nh);
    z.x = x0; z.y = y0; z.w = x1 - x0; z.h = y1 - y0;
    return z.w > 0 && z.h > 0;
  });
  terrainShift(P, nw, nh, dx, dy);
  P.w = nw; P.h = nh;
  S.sel = null;
  commit();
  fitView(false); refreshPanels();
}

// Grid square size: 1 m (layout, matches 1M cubes) or 0.5 m (single blocks, for detail)
async function setResolution(to) {
  const P = S.plan, from = P.cell;
  if (!CELL_SIZES.includes(to) || to === from) return true;
  if (to === 0.5 && (P.w * 2 > MAX_GRID || P.h * 2 > MAX_GRID)) {
    toast(`Half-metre squares fit a canvas up to ${MAX_GRID / 2} × ${MAX_GRID / 2} m. Shrink this canvas first.`);
    return false;
  }
  if (to === 1 && !(await confirmBox('Switch to 1 m squares?', 'Each 2 × 2 group of half-metre squares becomes one square, using its most common material. Fine detail gets simplified. You can undo this.', 'Switch', false))) return false;
  begin();
  if (to === 0.5) {
    for (const L of P.levels) {
      const g = blankGrid(P.w * 2, P.h * 2);
      for (let y = 0; y < P.h; y++) for (let x = 0; x < P.w; x++) {
        const ch = L.grid[y][x];
        g[2 * y][2 * x] = g[2 * y][2 * x + 1] = g[2 * y + 1][2 * x] = g[2 * y + 1][2 * x + 1] = ch;
      }
      L.grid = g;
    }
    for (const it of P.items) { it.x *= 2; it.y *= 2; it.w *= 2; it.d *= 2; }
    for (const z of P.zones) { z.x *= 2; z.y *= 2; z.w *= 2; z.h *= 2; }
    terrainRescale(P, 0.5);
    P.w *= 2; P.h *= 2;
  } else {
    const nw = Math.ceil(P.w / 2), nh = Math.ceil(P.h / 2);
    for (const L of P.levels) {
      const g = blankGrid(nw, nh);
      for (let Y = 0; Y < nh; Y++) for (let X = 0; X < nw; X++) {
        const tally = {};
        let best = ' ', bestN = 0;
        for (const [dx, dy] of [[0, 0], [1, 0], [0, 1], [1, 1]]) {
          const x = 2 * X + dx, y = 2 * Y + dy;
          if (x >= P.w || y >= P.h) continue;
          const ch = L.grid[y][x];
          if (ch === ' ') continue;
          tally[ch] = (tally[ch] || 0) + 1;
          if (tally[ch] > bestN) { bestN = tally[ch]; best = ch; }
        }
        g[Y][X] = best;
      }
      L.grid = g;
    }
    for (const it of P.items) {
      it.x = Math.floor(it.x / 2); it.y = Math.floor(it.y / 2); it.w = Math.max(1, Math.ceil(it.w / 2)); it.d = Math.max(1, Math.ceil(it.d / 2));
      const R = itemRect(it); it.x = clamp(it.x, 0, Math.max(0, nw - R.w)); it.y = clamp(it.y, 0, Math.max(0, nh - R.h));
    }
    for (const z of P.zones) {
      z.x = Math.floor(z.x / 2); z.y = Math.floor(z.y / 2); z.w = Math.max(1, Math.ceil(z.w / 2)); z.h = Math.max(1, Math.ceil(z.h / 2));
      z.w = Math.min(z.w, nw); z.h = Math.min(z.h, nh); z.x = clamp(z.x, 0, nw - z.w); z.y = clamp(z.y, 0, nh - z.h);
    }
    terrainRescale(P, 1);
    P.w = nw; P.h = nh;
  }
  P.cell = to;
  S.sel = null; S.itemDef = null; S.clip = null;
  commit();
  fitView(true); V3.fit = true; refreshPanels();
  toast(to === 0.5 ? 'Now using 0.5 m squares. Each old square became 2 × 2.' : 'Now using 1 m squares.');
  return true;
}
