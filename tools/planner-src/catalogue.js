// ---------------------------------------------------------------------------
// The item catalogue, and how items sit. Real doors, windows and decorations from the crafting data (craft.js)
// join the item library under their game names, with sizes in blocks where measured. Anything without a size
// is asked for once and saved in meta/library for everyone (askItemSize).
// An item's mount says how it sits:
//   floor (the default, not stored) · door / window: in a wall, cutting its opening there ·
//   wall: hung on a wall face · ceiling: hung from above.
// Its z is its bottom above its level's floor: a window's sill, how high a wall item hangs.
// ---------------------------------------------------------------------------
const MOUNTS = { floor: 'On the floor', door: 'Door, in a wall', window: 'Window, in a wall', wall: 'On a wall', ceiling: 'From the ceiling' };
const IN_WALL = new Set(['door', 'window']);
// Real doors and windows by shape (planner v62), for the material editor's Item picker: [label, test on the name],
// first match wins, listed in this order.
const OPENING_GROUPS = {
  door: [['Secret doors', n => /\bSecret\b/.test(n)], ['Fake doors (they don’t open)', n => /^Fake /.test(n)], ['Door frames', n => /Frame$/.test(n)],
    ['Double doors', n => /Double Door/.test(n)], ['Large doors', n => /^(Huge|Large) |Vault Door|Portcullis/.test(n)],
    ['Round doors', n => /Round/.test(n)], ['Doors', () => true]],
  window: [['Bamboo windows', n => /Bamboo/.test(n)], ['Large round window frames', n => /^Large Round /.test(n)], ['Round window frames', n => /^Round /.test(n)],
    ['High window frames', n => /^High /.test(n)], ['Large and wide window frames', n => /^(Large|Wide) /.test(n)], ['Window frames', () => true]],
};
const OPENING_ORDER = { door: ['Doors', 'Double doors', 'Round doors', 'Large doors', 'Door frames', 'Secret doors', 'Fake doors (they don’t open)'],
  window: ['Window frames', 'High window frames', 'Large and wide window frames', 'Round window frames', 'Large round window frames', 'Bamboo windows'] };
const openingGroup = (kind, name) => (OPENING_GROUPS[kind] || []).find(([, t]) => t(name))[0];
const mountOf = it => (it && it.mount && MOUNTS[it.mount] ? it.mount : 'floor');
const slugOf = n => String(n).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
// placeholders (metres) for things nobody has measured yet
const SIZE_GUESS = { door: { w: 2, d: 0.5, h: 2.5 }, window: { w: 1, d: 0.5, h: 1.5 }, wall: { w: 1, d: 0.5, h: 1 }, ceiling: { w: 1, d: 1, h: 1 }, floor: { w: 1, d: 1, h: 1 } };
const MOUNT_COLOR = { door: '#6b4a2e', window: '#8fc3df', wall: '#b08a4a', ceiling: '#c9a23a', floor: '#8a7a6a' };
// Where an item sits unless told otherwise, in metres above its level's floor: a window's top level with a
// normal door's (a tall one 0.5 m up), wall items 1.5 m up, ceiling items hanging from the level's top.
function defaultZ(mount, h, L) {
  if (mount === 'window') return Math.max(0.5, GAME.winTop - h);
  if (mount === 'wall') return 1.5;
  if (mount === 'ceiling') return Math.max(0, (L ? L.height : GAME.levelH) - h);
  return 0;
}
// Item positions and sizes snap to the 0.5 m block grid: whole squares on a 0.5 m plan, halves on a 1 m one.
const itemStep = P => VOXEL / ((P || S.plan || { cell: 1 }).cell || 1);
const snapStep = (v, st) => Math.round(v / st + 1e-9) * st;

// The categories of the catalogue batches (tools/craft-src: structural.json listed as "Structure · …", lights.json
// as "Lights · …"), and the regions. Storage is only what holds items (its chests are library items already),
// Displays what shows items (weapon racks, showcases, mounts, mannequins); Furniture beds, seats and tables (they
// give comfort, and survivors need beds); storage-style pieces that hold nothing (cabinets, shelves, barrels, vases)
// and anything else purely decorative list as decoration. in the order the Flame opens them: an item's region is the first one where you
// could make it.
const STRUCTURE_CATS = new Set(['Gates', 'Trapdoors', 'Stairs', 'Ladders', 'Fences', 'Railings', 'Grates', 'Supports', 'Columns', 'Wall pieces', 'Walkways', 'Awnings', 'Arches']);
const LIGHT_CATS = new Set(['Torches', 'Lanterns', 'Lamps', 'Candles', 'Chandeliers', 'Braziers and fire bowls', 'Fireplaces and campfires', 'Coloured lights', 'Beacons', 'Pumpkins']);
const LIGHT_COLOR = '#e3a94a';
const STORAGE_CATS = new Set(['Chests', 'Magic chests']);
const DISPLAY_CATS = new Set(['Weapon racks', 'Showcases', 'Wall mounts', 'Mannequins', 'Display stands', 'Platters']);
const FURNITURE_CATS = new Set(['Beds', 'Chairs and stools', 'Benches and sofas', 'Thrones', 'Tables', 'Desks and counters', 'Bathroom']);
const FARM_CATS = new Set(['Seedlings', 'Farming', 'Animal care', 'Farm animals', 'Pets']);
const STATION_CATS = new Set(['Crafting stations', 'Kitchen stations', 'Station parts', 'Mill power']);
// In the crafting data but not offered as items to place: tools, reward bundles, and survivors (the library has
// their stand-ins).
const UNPLACED_CATS = new Set(['Building tools', 'Reward bundles', 'Survivors']);
const BASE_CATS = new Set(['Water', 'Buff shrines']);     // base utilities (water, the Vukah Shrine's buff)
const GAME_REGIONS = ['Springlands', 'Revelwood', 'Nomad Highlands', 'Kindlewastes', 'Albaneve Summits', 'Veilwater Basin', "Cinder's Cradle"];
(function extendLibrary() {
  if (typeof CRAFT !== 'object' || !CRAFT || !Array.isArray(CRAFT.items)) return;
  const cats = new Map();
  for (const c of CRAFT.items) {
    const mount = c.opening || c.mount;
    if (!mount || c.libraryType || !MOUNTS[mount] || UNPLACED_CATS.has(c.category)) continue;   // (stations and chests are in the library already)
    const type = slugOf(c.name).slice(0, 64);
    if (LIB_BY_TYPE[type]) continue;
    const g = SIZE_GUESS[mount], sz = c.size;
    const light = LIGHT_CATS.has(c.category);
    const e = { type, name: c.name, mount, color: light ? LIGHT_COLOR : MOUNT_COLOR[mount], src: true, craft: true, sized: !!sz,
      w: sz ? sz.w * VOXEL : g.w, d: sz && sz.d ? sz.d * VOXEL : g.d, h: sz ? sz.h * VOXEL : g.h,
      by: c.crafter ? `${c.crafter}${c.station ? `, needs ${c.station}` : ''}` : c.station || (c.found ? 'found, not crafted' : (c.inputs || []).length ? 'by hand' : ''),
      crafter: c.crafter || null, station: c.station || null, hasRecipe: (c.inputs || []).length > 0, role: MOUNTS[mount], region: c.region || null, regionBy: c.regionBy || null, found: !!c.found,
      comfort: c.comfort || null, resist: c.resist || null, unlock: c.unlock || null, holdsNothing: !!c.holdsNothing,
      recipe: (c.inputs || []).map(i => `${i.item} ×${i.qty}`).join(', ') };
    const cat = c.category === 'Doors' || c.category === 'Windows' ? c.category : (STRUCTURE_CATS.has(c.category) ? 'Structure · ' : light ? 'Lights · ' : STORAGE_CATS.has(c.category) ? 'Storage · ' : DISPLAY_CATS.has(c.category) ? 'Displays · ' : FURNITURE_CATS.has(c.category) ? 'Furniture · ' : BASE_CATS.has(c.category) ? 'Base · '
      : FARM_CATS.has(c.category) ? 'Farm · ' : STATION_CATS.has(c.category) ? 'Stations · ' : c.category === 'Sparkworks' ? '' : 'Decor · ') + c.category;
    const own = STORAGE_CATS.has(c.category) && LIBRARY.find(g => g.cat === c.category);
    if (own) { own.items.push(e); continue; }             // (a storage piece joins the library's own Chests or Magic chests)
    if (!cats.has(cat)) cats.set(cat, []);
    cats.get(cat).push(e);
  }
  const rank = c => (c === 'Doors' ? 0 : c === 'Windows' ? 1 : c.startsWith('Structure') ? 2 : c.startsWith('Lights') ? 3 : c.startsWith('Storage') ? 4 : c.startsWith('Displays') ? 5 : c.startsWith('Furniture') ? 6 : 7);
  for (const cat of [...cats.keys()].sort((a, b) => rank(a) - rank(b) || a.localeCompare(b)))
    LIBRARY.push({ cat, src: true, craft: true, items: cats.get(cat) });
  indexLibrary();
})();

// ---- where things go: wall slots for doors and windows, the wall behind a wall item
const wallSq = (L, x, y) => { if (!inB(x, y)) return false; const e = S.plan.palette[L.grid[y][x]]; return !!e && (e.kind === 'wall' || e.kind === 'block') && (!(e.base > 0) || !!L.anyBase); };
// A door or window `along` squares wide in the wall under (gx, gy): it covers the wall squares, one square
// thick, turned to the wall's run. rot keeps its facing (R flips it). null when there's no wall there.
function wallSlot(L, gx, gy, along, rot) {
  const P = S.plan, st = itemStep(P), cx = Math.floor(gx), cy = Math.floor(gy);
  if (!wallSq(L, cx, cy)) return null;
  const horiz = wallRunsHorizontally(L, cx, cy);
  const r = horiz ? (rot % 180 === 0 ? rot : (rot === 90 ? 0 : 180)) : (rot % 180 === 90 ? rot : (rot === 0 ? 90 : 270));
  const g = horiz
    ? { x: clamp(snapStep(gx - along / 2, st), 0, Math.max(0, P.w - along)), y: cy, w: along, h: 1, rot: r }
    : { x: cx, y: clamp(snapStep(gy - along / 2, st), 0, Math.max(0, P.h - along)), w: 1, h: along, rot: r };
  for (let y = Math.floor(g.y); y < Math.ceil(g.y + g.h - 1e-6); y++) for (let x = Math.floor(g.x); x < Math.ceil(g.x + g.w - 1e-6); x++) if (!wallSq(L, x, y)) g.bad = true;
  return g;
}
// The facing for a wall item hung in square (cx, cy): away from the nearest wall beside it (null if none).
function wallBehind(L, gx, gy) {
  const cx = Math.floor(gx), cy = Math.floor(gy), fx = gx - cx, fy = gy - cy;
  const sides = [[fy, 0, -1, 0], [1 - fy, 0, 1, 180], [fx, -1, 0, 270], [1 - fx, 1, 0, 90]].sort((a, b) => a[0] - b[0]);
  for (const [, dx, dy, rot] of sides) if (wallSq(L, cx + dx, cy + dy)) return rot;
  return null;
}
// Snap a wall item's footprint (w x h squares, facing rot) back against its wall in square (cx, cy).
function againstWall(g, cx, cy) {
  if (g.rot === 0) g.y = cy;                           // wall to the north, facing south
  else if (g.rot === 180) g.y = cy + 1 - g.h;
  else if (g.rot === 270) g.x = cx;                    // wall to the west, facing east
  else g.x = cx + 1 - g.w;
  return g;
}

// ---- openings: the wall squares each door or window item cuts, from its z to its top
// Map 'level:x:y' -> [[z0, z1], ...] in metres above that level's floor.
function openingCuts(P) {
  const m = new Map();
  for (const it of P.items) {
    if (!IN_WALL.has(it.mount)) continue;
    const R = itemRect(it), z0 = it.z || 0, z1 = z0 + it.h;
    for (let y = Math.floor(R.y); y < Math.ceil(R.y + R.h - 1e-6); y++) for (let x = Math.floor(R.x); x < Math.ceil(R.x + R.w - 1e-6); x++) {
      const k = it.level + ':' + x + ':' + y;
      if (!m.has(k)) m.set(k, []);
      m.get(k).push([z0, z1]);
    }
  }
  return m;
}
// What's left of [a, b] once the cuts are taken out (all in metres above the level floor).
function minusCuts(a, b, cuts) {
  let out = [[a, b]];
  for (const [c0, c1] of cuts || []) out = out.flatMap(([s, e]) => (c1 <= s + 1e-6 || c0 >= e - 1e-6) ? [[s, e]] : [[s, Math.max(s, c0)], [Math.min(e, c1), e]].filter(([u, v]) => v - u > 1e-6));
  return out;
}
const cutLength = (a, b, cuts) => (b - a) - minusCuts(a, b, cuts).reduce((t, [s, e]) => t + (e - s), 0);

// ---- sizes: ask once for anything nobody has measured, save it for everyone
function askItemSize(base) {
  const def = libDef(base), L = lv();
  const blocksOf = m => Math.max(1, Math.round(m / VOXEL));
  const numIn = (v, label) => h('input', { type: 'number', min: '1', max: '64', step: '1', value: String(v), 'aria-label': label });
  const tall = numIn(blocksOf(def.h), 'Tall, in blocks'), wide = numIn(blocksOf(def.w), 'Wide, in blocks'), deep = numIn(blocksOf(def.d), 'Deep, in blocks');
  const mount = h('select', { 'aria-label': 'How it sits' }, ...Object.entries(MOUNTS).map(([v, t]) => h('option', { value: v, text: t })));
  mount.value = mountOf(def);
  const up = h('input', { type: 'number', min: '0', max: '80', step: '1', 'aria-label': 'Blocks above the floor' });
  const upField = h('label', { class: 'field' }, h('span', { text: 'Blocks above the floor' }), up);
  const sync = () => {
    const m = mount.value, hb = Math.max(1, Number(tall.value) || 1);
    upField.hidden = !(m === 'window' || m === 'wall');
    if (!up.dataset.touched) up.value = String(Math.round(defaultZ(m, hb * VOXEL, L) / VOXEL));
  };
  up.addEventListener('input', () => { up.dataset.touched = '1'; });
  mount.addEventListener('change', sync); tall.addEventListener('input', sync); sync();
  const read = () => {
    const m = mount.value, v = { w: Math.max(1, Number(wide.value) || 1) * VOXEL, d: Math.max(1, Number(deep.value) || 1) * VOXEL, h: Math.max(1, Number(tall.value) || 1) * VOXEL, mount: m };
    if (m === 'window' || m === 'wall') v.z = Math.max(0, Number(up.value) || 0) * VOXEL;
    return v;
  };
  openModal(`How big is the ${def.name}?`, [
    h('p', { class: 'note', style: 'font-size:14px', text: `Its size isn't published anywhere. Measure it in game, in blocks (0.5 m each), and it's saved for every plan.${def.by ? ` Made at the ${def.by}.` : ''}` }),
    h('div', { class: 'grid3' }, h('label', { class: 'field' }, h('span', { text: 'Tall' }), tall), h('label', { class: 'field' }, h('span', { text: 'Wide' }), wide), h('label', { class: 'field' }, h('span', { text: 'Deep' }), deep)),
    h('div', { class: 'grid2' }, h('label', { class: 'field' }, h('span', { text: 'How it sits' }), mount), upField),
    h('p', { class: 'note', text: 'Wide is across its front. A door or window sits in a wall, so its depth is the wall. You can change all of this later from a placed one.' }),
  ], [
    { label: 'Cancel', onClick: closeModal },
    { label: 'Place with a guess', onClick: () => { closeModal(); armItem(base, false, true); toast(`Placing the ${def.name} at a guessed size. Measure it when you can.`); } },
    { label: 'Save size and place', primary: true, onClick: () => { const v = read(); closeModal(); saveLibSize(base.type, v); setTimeout(() => armItem(base), 0); } },
  ]);
}

// The wall a painted run sits in: the wall carrying on beyond either end of the run, preferring one as tall
// as the run's own wall (a gable window's 4 m wall, not the kneewall beside it), never what's across it.
function wallAlong(L, x0, y0, x1, y1, horiz, want) {
  const P = S.plan, top = k => { const w = P.palette[k]; return w ? (w.base || 0) + (w.height || L.height) : 0; };
  const ends = horiz ? [[x0 - 1, y0, -1, 0], [x1 + 1, y0, 1, 0]] : [[x0, y0 - 1, 0, -1], [x0, y1 + 1, 0, 1]];
  let any = null;
  for (let d = 0; d < 8; d++) for (const [ex, ey, dx, dy] of ends) {
    const x = ex + dx * d, y = ey + dy * d;
    if (!wallSq(L, x, y)) continue;
    const k = L.grid[y][x];
    if (Math.abs(top(k) - want) < 1e-6) return k;
    any = any || k;
  }
  return any;
}
// ---- painted doors and windows into placed items
// Each connected run of a door or window material named after a catalogue item becomes that item, in the
// same squares and at the same height, and the wall round it closes up behind it.
function convertPaintedOpenings() {
  const P = S.plan;
  if (!P || S.readOnly) return;
  const runs = [];
  for (const L of P.levels) {
    const g = L.grid, seen = new Set(), at = (x, y) => (g[y] || [])[x];
    for (let y = 0; y < g.length; y++) for (let x = 0; x < g[y].length; x++) {
      const ch = g[y][x], e = P.palette[ch];
      if (!e || (e.kind !== 'door' && e.kind !== 'window') || seen.has(y * 4096 + x)) continue;
      const cells = [], todo = [[x, y]]; seen.add(y * 4096 + x);
      while (todo.length) {
        const [cx, cy] = todo.pop(); cells.push([cx, cy]);
        for (const [nx, ny] of [[cx + 1, cy], [cx - 1, cy], [cx, cy + 1], [cx, cy - 1]])
          if (at(nx, ny) === ch && !seen.has(ny * 4096 + nx)) { seen.add(ny * 4096 + nx); todo.push([nx, ny]); }
      }
      runs.push({ L, ch, e, cells });
    }
  }
  let made = 0, left = 0;
  const used = new Set();
  begin();
  for (const { L, ch, e, cells } of runs) {
    const def = LIB_BY_TYPE[slugOf(e.name)];
    const xs = cells.map(c => c[0]), ys = cells.map(c => c[1]);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    const horiz = x1 - x0 >= y1 - y0, wall = wallAlong(L, x0, y0, x1, y1, horiz, openingWall(e, L));
    if (!def || !IN_WALL.has(def.mount) || !wall || (x1 > x0 && y1 > y0)) { left++; continue; }
    const [z0, z1] = openingSpan(e, L);
    const it = { id: uid('i'), level: L.id, type: def.type, label: def.name, x: x0, y: y0, w: horiz ? x1 - x0 + 1 : y1 - y0 + 1, d: 1, h: z1 - z0, rot: horiz ? 0 : 90, color: e.color || def.color, mount: def.mount };
    if (z0 > 0) it.z = z0;
    for (const [cx, cy] of cells) L.grid[cy][cx] = wall;
    P.items.push(it); used.add(ch); made++;
  }
  for (const ch of used) if (!P.levels.some(L => L.grid.some(r => r.includes(ch)))) delete P.palette[ch];
  planVer++;
  commit();
  renderMaterials(); renderPlacedList();
  toast(made ? `Turned ${made} painted door${made === 1 ? '' : 's'} and windows into placed items.${left ? ` ${left} stay painted: name them after a door or window first (Materials tab, Item).` : ''}`
    : left ? `No painted doors or windows are named after a real one yet (${left} found). Pick each one's Item in the Materials tab first.` : 'No painted doors or windows in this plan.');
}
