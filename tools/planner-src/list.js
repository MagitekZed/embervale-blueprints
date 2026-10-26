
// ---------------------------------------------------------------------------
// Shopping list: how many 0.5 m blocks of each material the plan uses, and what to gather and craft for
// them (recipes from the wiki, recipes.js). Furniture and stations are counted by name; raised ground is
// dirt to place.
// ---------------------------------------------------------------------------
const baseName = n => n.replace(/\s+[\d.]+ m$/, '').replace(/\s+\((?:step|tread|arch|newel|merlon|chimney|chimney cap|vent post|kneewall|column top|column stump|pavilion|lintel|broken lintel|broken lintel end|stage|corbel|pool coping|architrave|arch haunch|arch crown|pylon cap|pergola post|pergola beam|bed edging|fountain tier)[^)]*\)$/i, '').trim();
// The catalogue name for a material: drop a size suffix and a known tag, then, if that still isn't a
// catalogue block, any note in brackets at the end ("Fired Bricks Block (garden wall, 3 m)"), and try it
// with "Block" on the end ("Highly Polished Stone (tread 2 m)"). Catalogue blocks are the wiki's (RECIPES)
// and the 1.0 building materials in the Crafting list's data, so blocks new in 1.0 ("Moonstone Block
// (paving)") count too. Cached by name, since the counts ask for every square.
let MAT_BOOK = null;
const MAT_NAMES = new Map();
function matBook() {
  if (MAT_BOOK) return MAT_BOOK;
  const book = new Set(Object.keys(typeof RECIPES === 'object' ? RECIPES : {}));
  if (typeof CRAFT !== 'object' || !CRAFT) return book;                   // (not loaded yet: don't cache)
  for (const it of CRAFT.items) if (BUILD_CATS.has(it.category)) { book.add(it.name); if (it.catalogueName) book.add(it.catalogueName); }
  return (MAT_BOOK = book);
}
function matName(n) {
  const hit = MAT_NAMES.get(n);
  if (hit !== undefined) return hit;
  const b = baseName(n), book = matBook();
  const known = s => book.has(s) ? s : book.has(s + ' Block') ? s + ' Block' : null;
  let out = b;
  for (let s = b; s;) {
    const k = known(s);
    if (k) { out = k; break; }
    if (!/\([^()]*\)?$/.test(s)) break;                                  // (a note cut off at 40 letters has no ")")
    s = s.replace(/\s*\([^()]*\)?$/, '').trim();
  }
  if (MAT_BOOK) MAT_NAMES.set(n, out);
  return out;
}
function blockCounts(P) {
  const a = (P.cell / 0.5) ** 2, out = new Map(), cuts = openingCuts(P);     // voxels per square of floor area
  const cutIn = (L, x, y, lo, hi) => { const cs = cuts.get(L.id + ':' + x + ':' + y); return cs ? cutLength(lo, hi, cs) : 0; };
  const add = (e, vox) => { if (!(vox > 0)) return; const k = matName(e.name); const r = out.get(k) || { name: k, color: e.color, vox: 0 }; r.vox += vox; out.set(k, r); };
  for (const L of P.levels) for (let y = 0; y < P.h; y++) for (let x = 0; x < P.w; x++) {
    const c = L.grid[y][x];
    if (c === ' ') continue;
    const e = P.palette[c];
    if (!e) continue;
    if (e.under && P.palette[e.under] && P.palette[e.under].kind === 'floor') add(P.palette[e.under], a);
    { const fc = floorCourse(P, L, x, y); if (fc) add(fc, a); }   // the floor course under walls on upper storeys
    if (e.kind === 'wall') { const lo = e.base || 0, hi = lo + (e.height || Math.max(P.cell, L.height - lo)); add(e, a * (hi - lo - cutIn(L, x, y, lo, hi)) / 0.5); }
    else if (e.kind === 'block') { const lo = e.base || 0, hi = lo + (e.height || 1); add(e, a * (hi - lo - cutIn(L, x, y, lo, hi)) / 0.5); }
    else if (e.kind === 'floor') add(e, a);
  }
  // roofs: the same block columns the 3D view draws, and the gable walls carried up under them
  for (const L of P.levels) {
    const below = P.levels.filter(B => B !== L && B.elev < L.elev - 0.01);
    for (const c of roofColumns(P, L, below)) {
      add(c.e, a * (c.top - c.bot) / 0.5);
      if (c.fill && (c.fill.kind === 'wall' || c.fill.kind === 'block')) add(c.fill, a * (c.bot - c.fillFrom) / 0.5);
    }
  }
  return [...out.values()].sort((p, q) => q.vox - p.vox);
}
function itemCounts(P) {
  const m = new Map();
  for (const it of P.items) {
    if (/^npc-/.test(it.type) || /^tree-/.test(it.type) || ['stairs', 'spiral', 'tree', 'spire', 'altar', 'spawn', 'shrub'].includes(it.type) || IN_WALL.has(it.mount)) continue;   // not things you craft (doors and windows are listed with the painted ones)
    const k = it.label || it.type; m.set(k, (m.get(k) || 0) + 1);
  }
  return [...m.entries()].sort((a, b) => b[1] - a[1]);
}
// Doors and windows: one per opening, that is each connected run of squares of one door or window material
// on a level. Named by material, so one named after a real door or window (Wooden Door) counts as that.
function openingCounts(P) {
  const m = new Map();
  for (const L of P.levels) {
    const g = L.grid, seen = new Set(), at = (x, y) => (g[y] || [])[x];
    for (let y = 0; y < g.length; y++) for (let x = 0; x < g[y].length; x++) {
      const ch = g[y][x], e = P.palette[ch];
      if (!e || (e.kind !== 'door' && e.kind !== 'window') || seen.has(y * 4096 + x)) continue;
      const todo = [[x, y]]; seen.add(y * 4096 + x);
      while (todo.length) {
        const [cx, cy] = todo.pop();
        for (const [nx, ny] of [[cx + 1, cy], [cx - 1, cy], [cx, cy + 1], [cx, cy - 1]])
          if (at(nx, ny) === ch && !seen.has(ny * 4096 + nx)) { seen.add(ny * 4096 + nx); todo.push([nx, ny]); }
      }
      const r = m.get(e.name) || { name: e.name, kind: e.kind, n: 0 }; r.n++; m.set(e.name, r);
    }
  }
  return [...m.values()].sort((a, b) => a.kind.localeCompare(b.kind) || b.n - a.n);
}
function groundCounts(P) {
  if (!terrainOn(P)) return null;
  const a = (P.cell / 0.5) ** 2;
  let up = 0, down = 0;
  for (const row of P.terrain) for (const v of row) { if (v > 0) up += a * v / 0.5; else down += a * -v / 0.5; }
  return { up: Math.round(up), down: Math.round(down) };
}
// Turn block counts into crafting runs, then expand crafted parts (planks, glass, bars…) down to raw
// resources with INTERMEDIATES. Recipes and the per-block cost are from the wiki (recipes.js).
const BUILD_CATS = new Set(['Stone blocks', 'Wood blocks', 'Luminescent blocks', 'Other blocks', 'Roof blocks', 'Overgrowth', 'Roads', 'Soil & terrain']);
// The recipe book for blocks and the parts they're made of: 1.0 recipes from the Crafting list's data
// (craft.js) where it has them, the older wiki recipes (recipes.js) for the rest.
function recipeBook() {
  const book = { ...(typeof RECIPES === 'object' ? RECIPES : {}) }, parts = { ...(typeof INTERMEDIATES === 'object' ? INTERMEDIATES : {}) };
  let v1 = 0;
  if (typeof CRAFT === 'object' && CRAFT) {
    for (const it of CRAFT.items) {
      if (!(it.inputs || []).length) continue;
      const rec = { s: it.station || null, c: it.crafter || null, i: it.inputs.map(x => [x.item, x.qty]), m: it.makes || 1, v1: true };
      if (BUILD_CATS.has(it.category)) { book[it.name] = rec; if (it.catalogueName) book[it.catalogueName] = rec; v1++; }
    }
    for (const [name, r] of Object.entries(CRAFT.resources || {}))
      if (r.recipe && (r.recipe.inputs || []).length) parts[name] = { s: r.recipe.station || null, c: r.recipe.crafter || null, i: r.recipe.inputs.map(x => [x.item, x.qty]), m: r.recipe.makes || 1 };
  }
  return { book, parts, v1 };
}
// The note on where the recipes come from: 1.0 ones once the Crafting list has block recipes.
function recipeNote() {
  if (!recipeBook().v1) return typeof RECIPE_NOTE === 'string' ? RECIPE_NOTE : '';
  return 'Counts are in 0.5 m blocks, about one item each (not documented; from 2024 player tests). Block recipes are 1.0, read from the game files by enshrouded.tools; any marked (pre-1.0) still use the old wiki data, so check those in game.';
}
function shoppingList(P) {
  const perVox = (typeof PER_VOXEL === 'number' && PER_VOXEL > 0) ? PER_VOXEL : 1;
  const { book, parts } = recipeBook();
  const rows = blockCounts(P).map(r => {
    const rec = book[r.name] || null, items = Math.ceil(r.vox * perVox);
    const runs = rec && rec.m ? Math.ceil(items / rec.m) : null;
    return { ...r, items, rec, runs };
  });
  const need = new Map(), crafted = new Map(), raw = new Map();
  const addTo = (m, k, v) => m.set(k, (m.get(k) || 0) + v);
  for (const r of rows) if (r.rec && r.runs) for (const [item, qty] of r.rec.i) addTo(need, item, qty * r.runs);
  // expand crafted parts a level at a time (each part's runs round up)
  for (let depth = 0; depth < 6 && need.size; depth++) {
    const next = new Map();
    for (const [item, qty] of need) {
      const p = parts[item];
      if (!p || !p.m) { addTo(raw, item, qty); continue; }
      addTo(crafted, item, qty);
      const runs = Math.ceil(qty / p.m);
      for (const [sub, q] of p.i) addTo(next, sub, q * runs);
    }
    need.clear(); for (const [k, v] of next) need.set(k, v);
  }
  for (const [k, v] of need) addTo(raw, k, v);
  for (const r of rows) if (r.rec && r.rec.dig) addTo(raw, r.name, r.items);     // dig-only terrain: gather it as is
  const sort = m => [...m.entries()].sort((a, b) => b[1] - a[1]);
  const openings = new Map(openingCounts(P).map(r => [r.name, r.n]));
  for (const it of P.items) if (IN_WALL.has(it.mount)) openings.set(it.label, (openings.get(it.label) || 0) + 1);
  return { rows, raw: sort(raw), crafted: sort(crafted), items: itemCounts(P), openings: [...openings.entries()].sort((a, b) => b[1] - a[1]), ground: groundCounts(P), perVox };
}
const craftText = r => !r.rec ? 'No recipe: not a catalogue block'
  : r.rec.dig ? 'Dig or mine it'
  : `${r.runs.toLocaleString()} × ${r.rec.s || r.rec.c || 'craft'}: ${r.rec.i.map(([k, q]) => `${q} ${k}`).join(' + ')} → ${r.rec.m}${r.rec.flag ? ' ⚠' : ''}${r.rec.v1 ? '' : ' (pre-1.0)'}`;
function shoppingText(P, L) {
  const lines = [`Shopping list: ${P.name}`, '', 'BLOCKS (0.5 m blocks, estimates)'];
  for (const r of L.rows) lines.push(`- ${r.name}: ${r.items} (${craftText(r)})`);
  if (L.crafted.length) { lines.push('', 'CRAFTED PARTS'); for (const [k, v] of L.crafted) lines.push(`- ${k}: ${v}`); }
  if (L.raw.length) { lines.push('', 'RAW RESOURCES'); for (const [k, v] of L.raw) lines.push(`- ${k}: ${v}`); }
  if (L.ground) lines.push('', `GROUND: about ${L.ground.up} blocks of dirt to place for raised ground; digging frees about ${L.ground.down}.`);
  if (L.openings.length) { lines.push('', 'DOORS & WINDOWS'); for (const [k, v] of L.openings) lines.push(`- ${k} × ${v}`); }
  if (L.items.length) { lines.push('', 'STATIONS, CHESTS & FURNITURE'); for (const [k, v] of L.items) lines.push(`- ${k} × ${v}`); }
  lines.push('', recipeNote());
  return lines.join('\n');
}
function openShoppingList() {
  if (!S.plan) return;
  const P = S.plan, L = shoppingList(P), fmtN = n => n.toLocaleString();
  const table = h('table', { class: 'shop' },
    h('thead', null, h('tr', null, h('th', { text: 'Material' }), h('th', { text: 'Blocks', class: 'num' }), h('th', { text: 'Craft' }))),
    h('tbody', null, ...L.rows.map(r => h('tr', null,
      h('td', null, h('span', { class: 'swatch sm', style: `background:${r.color}` }), ' ', r.name),
      h('td', { class: 'num', text: fmtN(r.items) }),
      h('td', { class: 'craft', text: craftText(r), title: r.rec && r.rec.flag ? 'The wiki data for this one looks off or changed in 1.0. Check it in game' : '' })))));
  const list = (title, rows, suffix = '') => rows.length ? h('div', { class: 'section' }, h('h4', { text: title }), h('dl', { class: 'stats' }, ...rows.flatMap(([k, v]) => [h('dt', { text: k }), h('dd', { text: suffix + fmtN(v) })]))) : null;
  const ground = L.ground ? h('p', { class: 'note', text: `Ground: about ${fmtN(L.ground.up)} blocks of dirt to place where it's raised; digging frees about ${fmtN(L.ground.down)}.` }) : null;
  openModal('Shopping list', [
    h('p', { class: 'note', text: recipeNote() }),
    L.rows.length ? h('div', { class: 'shopwrap' }, table) : h('p', { class: 'note', text: 'Nothing built yet.' }),
    h('div', { class: 'grid2 shopsum' }, list('Raw resources to gather', L.raw), list('Crafted parts', L.crafted)),
    ground, list('Doors & windows', L.openings, '× '), list('Stations, chests & furniture', L.items, '× '),
  ], [{ label: 'Copy as text', primary: true, onClick: () => copyText(shoppingText(P, L), 'Shopping list') }, { label: 'Close', onClick: closeModal }]);
  document.querySelector('#modal .modal').classList.add('wide');
}
