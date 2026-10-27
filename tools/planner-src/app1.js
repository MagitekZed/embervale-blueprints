(() => {
'use strict';

// ---------------------------------------------------------------------------
// Game constants. One grid square = 1 m, the size of Enshrouded's "1M" cube
// piece (2 x 2 x 2 voxels; one voxel is a 0.5 m cube).
// ---------------------------------------------------------------------------
const GAME = {
  blockM: 1,        // metres per grid square
  voxelsPer: 2,     // voxels along one edge of a grid square
  levelH: 4,        // default storey height in metres (one 4M wall piece)
  // Openings, measured in game (blocks tall x wide): Crude Wooden and Wooden Door 5 x 4, Round Wooden Door 6 x 6,
  // Wooden Double Door 7 x 8; Wooden Window Frame 3 x 2, Round Wooden Window Frame 2 x 2, Large Round 6 x 6.
  // Widths are painted; an entry's `opening` is its height, `sill` where a window starts.
  doorTop: 2.5,     // a normal door's opening height in metres
  sillTop: 1,       // the sill of a 1.5 m window (the default)
  winTop: 2.5,      // a window's top, level with the top of a normal door, where it fits
  altarSizes: [40, 80, 120, 160], // Flame Altar build area by altar level, in metres
};
const MAX_GRID = 336;                                   // squares a side: 168 m at 0.5 m (the 160 m build area with room round it; 256 before v71)
const MAX_LEVELS = 200;                                      // levels are cheap (cropped, run-encoded); the altar's volume is the real limit
const CELL_SIZES = [1, 0.5]; // metres per grid square: 1M cube, or a single 0.5 m block

const KINDS = {
  wall:   { label: 'Wall',            hint: 'Full height of the level' },
  block:  { label: 'Low wall / block', hint: 'One block tall' },
  roof:   { label: 'Roof',            hint: 'Blocks topped at a set height; steps close up down to lower neighbours' },
  floor:  { label: 'Floor',           hint: 'Flat tile at the level base' },
  water:  { label: 'Water',           hint: 'Flat and see-through' },
  door:   { label: 'Door',            hint: 'Opening in a wall' },
  dig:    { label: 'Dug out (open)',  hint: 'Ground dug away with nothing built there: pits, sunken courts, cave rooms' },
  window: { label: 'Window',          hint: 'Glass set in a wall' },
};
const WALLISH = new Set(['wall', 'block', 'window', 'door']);
const OUTLINED = new Set(['wall', 'block', 'window', 'roof']);
// Top of a roof square above its level floor, in metres (Raise by + Height; one course by default).
const roofTop = (e, cm) => (e.base || 0) + (e.height || cm);
// The wall a door or window sits in runs from the level floor to its own height, if it has one (a 3 m
// outbuilding on a 4 m level, a gable wall rising past a short loft), else to the top of the level.
const openingWall = (e, L) => e.height || L.height;
// The opening itself, [bottom, top] in metres above the level floor: a door from the floor up; a window from
// its sill, which unless set puts its top level with a normal door's (a tall one starts 0.5 m up). Both are
// cut short by a lower wall.
const winSill = e => e.sill != null ? e.sill : Math.max(0.5, GAME.winTop - (e.opening || GAME.winTop - GAME.sillTop));
const openingSpan = (e, L) => {
  const H = openingWall(e, L);
  if (e.kind === 'door') return [0, Math.min(H, e.opening || GAME.doorTop)];
  const s = winSill(e);
  return [Math.min(H, s), Math.min(H, s + (e.opening || GAME.winTop - GAME.sillTop))];
};
// Floors (and water) are one course of blocks, 0.5 m, just below their level's floor height: their top is
// what you walk on, where the level's walls, doors and items start. So an upper storey's floor sits in the
// top course between the walls of the storey below.
const FLOOR_T = 0.5;
const isFloorKind = e => !!e && (e.kind === 'floor' || e.kind === 'water');
// the floor (or water) in a square: the square's own, or the one under a raised piece
function floorUnder(pal, e) { if (!e) return null; if (isFloorKind(e)) return e; const u = e.under && pal[e.under]; return isFloorKind(u) ? u : null; }
// Under a wall, door, window or block on a storey above the ground, the floor course runs on beneath it (it
// stands on the floor) unless a wall of a lower level comes up to meet it. Returns the floor to use, or null.
function floorCourse(P, L, x, y) {
  if (L.elev <= 0.01) return null;                            // on (or in) the ground, the ground holds it
  const pal = P.palette, e = pal[L.grid[y][x]];
  if (!e || !(e.kind === 'wall' || e.kind === 'door' || e.kind === 'window' || (e.kind === 'block' && !(e.base > 0)))) return null;
  if (floorUnder(pal, e)) return null;                        // it has its own floor under it
  let f = null;
  for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
    if (!inB(x + dx, y + dy)) continue;
    const n = floorUnder(pal, pal[L.grid[y + dy][x + dx]]);
    if (n && n.kind === 'floor') { f = n; break; }
  }
  if (!f) return null;
  for (const B of P.levels) {                                 // a lower level's wall reaching up to here holds it
    if (B === L || B.elev >= L.elev - 0.01) continue;
    const w = pal[B.grid[y][x]];
    if (!w) continue;
    const lift = w.base || 0;
    const top = w.kind === 'wall' ? B.elev + lift + (w.height || Math.max(P.cell, B.height - lift))
      : w.kind === 'block' ? B.elev + lift + (w.height || 1)
      : (w.kind === 'door' || w.kind === 'window') ? B.elev + openingWall(w, B) : -Infinity;
    if (top >= L.elev - 0.01 && B.elev + lift <= L.elev - FLOOR_T + 0.01) return null;
  }
  return f;
}

// New plans start with real blocks from the block catalogue (blocks.js); add more from the Materials tab.
const DEFAULT_PALETTE = {
  '#': { name: 'Refined Stone Block',  kind: 'wall',   color: '#84837e' },
  'W': { name: 'Half-Timbered Block',  kind: 'wall',   color: '#71665e' },
  'B': { name: 'Fired Bricks Block',   kind: 'wall',   color: '#aa7657' },
  'I': { name: 'Tarred Wood Block',    kind: 'wall',   color: '#5d5652' },
  '=': { name: 'Rough Stone Block',    kind: 'block',  color: '#7d776a' },
  '.': { name: 'Refined Wood Block',   kind: 'floor',  color: '#75675f' },
  ',': { name: 'Fancy Stone Block',    kind: 'floor',  color: '#92908c' },
  ':': { name: 'Dirt Road Block',      kind: 'floor',  color: '#8c7455' },
  'f': { name: 'Farm Soil',            kind: 'floor',  color: '#90450d' },
  '~': { name: 'Water',                kind: 'water',  color: '#3f8fc1' },
  'D': { name: 'Door',                 kind: 'door',   color: '#7b4a26' },
  'o': { name: 'Window',               kind: 'window', color: '#8fc3df' },
};
const ZONE_COLORS = ['#c4501a', '#2f7fb3', '#3f8a4f', '#8a5cc2', '#b8862b', '#c2416e', '#2f8f8a'];

// Item library. Footprints are in metres (w = width, d = depth, h = height).
// Chests and crafting stations: names, crafters, slots and recipes from the official Enshrouded wiki
// (enshrouded.wiki.gg, checked Oct 2026). Nobody publishes footprints: every crafting station is a
// 2 x 2 m placeholder and chests are estimates until
// the player measures one in game and saves it as the default (stored in the plan database).
const WIKI = 'https://enshrouded.wiki.gg/wiki/';
let LIBRARY = [
  { cat: 'Chests', src: true, items: [
    { type: 'chest-tiny',   name: 'Tiny Chest',   w: 1,   d: 0.5, h: 0.5, color: '#9a6a3c', by: 'Workbench', role: '16 slots', recipe: 'String ×3, Twigs ×6' },
    { type: 'chest-small',  name: 'Small Chest',  w: 1,   d: 1,   h: 1,   color: '#8a5a2b', by: 'Workbench', role: '24 slots', recipe: 'Nails ×6, Wood Logs ×6' },
    { type: 'chest-wooden', name: 'Wooden Chest', w: 1.5, d: 1,   h: 1,   color: '#8a5a2b', by: 'Carpenter', role: '24 slots', recipe: 'Wood Planks ×5, Metal Sheets ×3, Charcoal ×3' },
    { type: 'chest-medium', name: 'Medium Chest', w: 1.5, d: 1,   h: 1,   color: '#7a4f27', by: 'Carpenter', role: '32 slots', recipe: 'Nails ×8, Wood Planks ×10, Metal Sheets ×2' },
    { type: 'chest-large',  name: 'Large Chest',  w: 2,   d: 1,   h: 1,   color: '#7a4f27', by: 'Carpenter', role: '40 slots', recipe: 'Nails ×12, Wood Planks ×16, Bronze Bars ×3' },
    { type: 'chest-silver', name: 'Silver Chest', w: 2,   d: 1,   h: 1,   color: '#8f949a', by: 'Carpenter', role: '40 slots', recipe: 'Silver Bars ×3, Charcoal ×6' },
    { type: 'chest-huge',   name: 'Huge Chest',   w: 2.5, d: 1.5, h: 1.5, color: '#6b4422', by: 'Carpenter', role: '56 slots', recipe: 'Nails ×16, Wood Planks ×20, Iron Bars ×2' },
  ]},
  { cat: 'Magic chests', src: true, note: 'Stations use their contents directly within about 100 m.', items: [
    { type: 'mchest-small',    name: 'Small Magic Chest',    w: 1,   d: 1,   h: 1,   color: '#7b68b5', by: 'Workbench', role: '24 slots', recipe: 'Small Chest, Shroud Spores ×15, Active Mycelium ×15' },
    { type: 'mchest-medium',   name: 'Medium Magic Chest',   w: 1.5, d: 1,   h: 1,   color: '#6b5aa8', by: 'Carpenter', role: '32 slots', recipe: 'Medium Chest, Shroud Core, Goo ×2' },
    { type: 'mchest-large',    name: 'Large Magic Chest',    w: 2,   d: 1,   h: 1,   color: '#5e4f9a', by: 'Carpenter', role: '40 slots', recipe: 'Large Chest, Shroud Particles ×10, Alchemical Base' },
    { type: 'mchest-huge',     name: 'Huge Magic Chest',     w: 2.5, d: 1.5, h: 1.5, color: '#52458c', by: 'Carpenter', role: '56 slots', recipe: 'Huge Chest, Shroud Nexus, Enshrouded Oil ×3' },
    { type: 'mchest-enormous', name: 'Enormous Magic Chest', w: 3,   d: 1.5, h: 1.5, color: '#463b7e', by: 'Carpenter', role: '72 slots', recipe: 'Wood Planks ×24, Shroud Radiance, Shroud Slime ×15, Gold Bars ×2' },
    { type: 'quickstack',      name: 'Quick Stack Station',  w: 1,   d: 1,   h: 2,   color: '#4f7f8f', by: 'Forging the Path', role: 'Sends stackables to nearby magic chests', recipe: '', page: 'Storage' },
  ]},
  { cat: 'Your workbench', src: true, items: [
    { type: 'workbench', name: 'Workbench', w: 2, d: 2, h: 1, color: '#9a7b52', by: 'Hand crafting', role: 'Building blocks, basic furniture; repairs gear', recipe: 'String ×3, Wood Logs ×8' },
  ]},
  { cat: 'Blacksmith · Oswald Anders', src: true, items: [
    { type: 'forge',          name: 'Forge',          w: 2, d: 2,   h: 2,   color: '#6f6a66', by: 'Blacksmith', role: 'Bars, weapons and armour', recipe: 'Stone ×30, Metal Scraps ×10, Charcoal ×10, Wood Logs ×12' },
    { type: 'charcoal-kiln',  name: 'Charcoal Kiln',  w: 2, d: 2,   h: 2.5, color: '#5f5550', by: 'Blacksmith', role: 'Charcoal', recipe: 'Stone ×20' },
    { type: 'smelter',        name: 'Smelter',        w: 2, d: 2,   h: 3,   color: '#7b5a4a', by: 'Blacksmith', role: 'Melts and alloys metal', recipe: 'Fired Brick ×50, Crucible (quest)' },
    { type: 'blast-furnace',  name: 'Blast Furnace',  w: 2, d: 2,   h: 4,   color: '#6a4a3c', by: 'Blacksmith', role: 'More bars, faster, burns Coal', recipe: 'Sand ×30, Fired Brick ×20, Bellows, Lump of Clay ×10, Iron Bars ×10' },
    { type: 'smithing-tools', name: 'Smithing Tools', w: 2, d: 2,   h: 1,   color: '#5a6066', by: 'Blacksmith quest', role: 'Unlocks bronze tools and more', recipe: '' },
  ]},
  { cat: 'Alchemist · Balthazar', src: true, items: [
    { type: 'alchemy',         name: 'Alchemy Station', w: 2, d: 2, h: 1.5, color: '#5f7d6e', by: 'Alchemist', role: 'Potions, black powder and more', recipe: 'Fired Brick ×20, Wood Planks ×6, Nails ×10, Wood Logs ×3, Copper Bars ×5, Cauldron (quest)' },
    { type: 'grinding-stones', name: 'Grinding Stones', w: 2, d: 2,   h: 1,   color: '#7d8a80', by: 'Alchemist', role: 'Grinds ingredients', recipe: '' },
    { type: 'mortar',          name: 'Mortar',          w: 2, d: 2,   h: 1,   color: '#6f8a7a', by: "Quest: The Alchemist's Mortar", role: 'Spells such as Chain Heal and Chain Lightning', recipe: '' },
    { type: 'laboratory',      name: 'Laboratory',      w: 2, d: 2,   h: 1.5, color: '#4f7a6a', by: 'Quest: Scientific Instruments', role: 'Advanced alchemical reagents', recipe: '' },
  ]},
  { cat: 'Carpenter · Cade Hawthorn', src: true, items: [
    { type: 'kiln',          name: 'Kiln',          w: 2, d: 2, h: 2, color: '#a0613f', by: 'Carpenter', role: 'Carpenter workstation', recipe: '' },
    { type: 'table-saw',     name: 'Table Saw',     w: 2, d: 2, h: 1, color: '#a5824f', by: 'Quest: Table Saw For The Carpenter', role: 'Boreal Wood furniture, more lighting', recipe: 'Circular Sawblades (Thornhold)' },
    { type: 'masonry-tools', name: 'Masonry Tools', w: 2, d: 2, h: 1, color: '#8a8f87', by: 'Carpenter quest', role: 'Needed for many furniture recipes', recipe: '' },
  ]},
  { cat: 'Hunter · Athalan Skree', src: true, items: [
    { type: 'tannery',          name: 'Tanning Station',  w: 2, d: 2, h: 1.5, color: '#8b6a4a', by: 'Hunter', role: 'Leather', recipe: '' },
    { type: 'drying-rack',      name: 'Drying Rack',      w: 2, d: 2,   h: 2,   color: '#9a7d55', by: 'Hunter', role: 'Hunter workstation', recipe: '' },
    { type: 'hand-spindle',     name: 'Hand Spindle',     w: 2, d: 2,   h: 1,   color: '#a68a62', by: "Quest: The Hunter's Hand Spindle", role: 'Better armour', recipe: '' },
    { type: 'loom',             name: 'Loom',             w: 2, d: 2, h: 2,   color: '#a7896a', by: 'Hunter', role: 'Cloth', recipe: '' },
    { type: 'spinning',         name: 'Spinning Wheel',   w: 2, d: 2,   h: 1.5, color: '#b49770', by: 'Hunter', role: 'Thread and yarn', recipe: '' },
    { type: 'spinning-machine', name: 'Spinning Machine', w: 2, d: 2, h: 2,   color: '#9c8160', by: 'Hunter', role: 'Hunter workstation', recipe: '' },
  ]},
  { cat: 'Farmer · Emily Fray', src: true, items: [
    { type: 'seedbed',         name: 'Seedbed',         w: 2, d: 2,   h: 0.5, color: '#6f8a43', by: 'Farmer', role: 'Farming supplies', recipe: '' },
    { type: 'cooking-station', name: 'Cooking Station', w: 2, d: 2, h: 1.5, color: '#c46a2a', by: 'Farmer', role: 'Meals (needs the Kettle)', recipe: '' },
    { type: 'oven',            name: 'Oven',            w: 2, d: 2, h: 2,   color: '#b0643a', by: 'Farmer', role: 'Baking', recipe: '' },
    { type: 'kitchen',         name: 'Kitchen',         w: 2, d: 2,   h: 1.5, color: '#9a6a48', by: 'Farmer', role: 'Needed by many recipes', recipe: '' },
  ]},
  { cat: 'Base essentials', items: [
    { type: 'altar',     name: 'Flame Altar',        w: 4, d: 4, h: 3,   color: '#d9541e' },   // 4 x 4 m, measured in game (height a guess)
    { type: 'bed',       name: 'Bed',                w: 2, d: 3, h: 1,   color: '#8c6b4f' },
    { type: 'bed2',      name: 'Double bed',         w: 3, d: 3, h: 1,   color: '#7d5d43' },
    { type: 'mattress',  name: 'Crude mattress',     w: 1, d: 2, h: 1,   color: '#a08466' },
    { type: 'campfire',  name: 'Campfire',           w: 2, d: 2, h: 1,   color: '#c46a2a' },
    { type: 'bathtub',   name: 'Bathtub',            w: 2, d: 3, h: 1,   color: '#6f8fa3' },
  ]},
  { cat: 'Craftspeople (stand + work area)', items: [
    { type: 'npc-blacksmith', name: 'Blacksmith',    w: 3, d: 3, h: 2,   color: '#5f6770' },
    { type: 'npc-alchemist',  name: 'Alchemist',     w: 3, d: 3, h: 2,   color: '#56806c' },
    { type: 'npc-carpenter',  name: 'Carpenter',     w: 3, d: 3, h: 2,   color: '#9a7344' },
    { type: 'npc-hunter',     name: 'Hunter',        w: 3, d: 3, h: 2,   color: '#6d7a45' },
    { type: 'npc-farmer',     name: 'Farmer',        w: 3, d: 3, h: 2,   color: '#7c9a3d' },
    { type: 'npc-collector',  name: 'Collector',     w: 3, d: 3, h: 2,   color: '#8a6aa8' },
    { type: 'npc-bard',       name: 'Bard',          w: 3, d: 3, h: 2,   color: '#b0596f' },
    { type: 'npc-barber',     name: 'Barber',        w: 3, d: 3, h: 2,   color: '#9c6b8e' },
    { type: 'npc-fisher',     name: 'Fisher',        w: 3, d: 3, h: 2,   color: '#3f7f9e' },
  ]},
  { cat: 'Farm & animals', items: [
    { type: 'pen',        name: 'Animal pen',        w: 6, d: 6, h: 1,   color: '#a0905a' },
    { type: 'trough',     name: 'Trough',            w: 2, d: 1, h: 1,   color: '#8a7550' },
    { type: 'fishing',    name: 'Fishing spot',      w: 2, d: 2, h: 1,   color: '#3f8fc1' },
  ]},
  { cat: 'Sparkworks & structure', items: [
    { type: 'stairs',     name: 'Staircase',         w: 2, d: 4, h: 4,   color: '#a98a62' },
    { type: 'ladder',     name: 'Ladder',            w: 1, d: 1, h: 4,   color: '#8f7350' },
    { type: 'lever',      name: 'Lever / switch',    w: 1, d: 1, h: 1,   color: '#c9a227' },
    { type: 'plate',      name: 'Pressure plate',    w: 1, d: 1, h: 1,   color: '#b8862b' },
    { type: 'light',      name: 'Light / lantern',   w: 1, d: 1, h: 1,   color: '#e3b341' },
    { type: 'table',      name: 'Table',             w: 2, d: 1, h: 1,   color: '#9a7b52' },
  ]},
  { cat: 'Plants', note: 'Grown from the Farmer’s seedlings (trees are in his seed list; unconfirmed for 1.0). The footprint is the trunk; the canopy is drawn round it, and you can walk under it. Sizes are estimates.', items: [
    { type: 'tree-broadleaf', name: 'Broadleaf Tree', w: 1, d: 1, h: 8,   color: '#5a8a3c' },
    { type: 'tree-evergreen', name: 'Evergreen Tree', w: 1, d: 1, h: 10,  color: '#3f6b4a' },
    { type: 'shrub',          name: 'Shrub',          w: 1, d: 1, h: 1,   color: '#6a9a4a' },
  ]},
  { cat: 'Walk mode', note: 'Where you start when you walk the build (Walk, in the 3D view). It faces the way you’ll look. Not part of the build.', items: [
    { type: 'spawn',      name: 'Spawn point',       w: 1, d: 1, h: 0.5, color: '#2fa36b' },
  ]},
];
for (const c of LIBRARY) for (const it of c.items) if (c.src) it.src = true;
let LIB_BY_TYPE = {};
function indexLibrary() { LIB_BY_TYPE = {}; for (const c of LIBRARY) for (const it of c.items) LIB_BY_TYPE[it.type] = it; }
indexLibrary();
// Measured sizes saved by the player override the estimates (metres; synced through the database).
// Saved ones can also set how it sits (mount) and how high (z, metres above the floor).
function libDef(def) {
  const m = S.libSizes && S.libSizes[def.type];
  if (m) return { ...def, w: m.w, d: m.d, h: m.h, ...(m.z != null ? { z: m.z } : {}), ...(m.mount ? { mount: m.mount } : {}), measured: true, sized: true };
  return { ...def, measured: !!def.sized };
}
function wikiUrl(def) { return WIKI + encodeURIComponent((def.page || def.name).replace(/ /g, '_')); }

const TOOLS = [
  { id: 'select',  key: 'V', label: 'Select and move', tip: 'Drag to select an area, or grab an item or area label to move it', icon: '<path d="M6 3.5 18 11l-5.2 1.3 3.1 5.7-2.4 1.3-3.1-5.7L6.5 17Z"/>' },
  { id: 'paint',   key: 'B', label: 'Paint blocks', tip: 'Drag to paint the current material. Right-drag erases', icon: '<path d="M4 20l1.2-4.6L15.6 5l3.4 3.4L8.6 18.8Z"/><path d="m13.6 7 3.4 3.4"/>' },
  { id: 'line',    key: 'L', label: 'Line', tip: 'Drag a straight run of the current material. Shift snaps to 45°', icon: '<path d="M6.5 17.5 17.5 6.5"/><rect x="3" y="17" width="4" height="4" rx=".6"/><rect x="17" y="3" width="4" height="4" rx=".6"/>' },
  { id: 'rect',    key: 'U', label: 'Rectangle', tip: 'Drag a box, circle or oval, outlined or filled', icon: '<rect x="4.5" y="5.5" width="15" height="13" rx="1"/>' },
  { id: 'room',    key: 'O', label: 'Room: walls with a floor inside', tip: 'Drag out a square or round room in one go', icon: '<rect x="3.5" y="3.5" width="17" height="17" rx="1"/><path d="M8 8h8v8H8z" stroke-dasharray="2 2"/>' },
  { id: 'wall',    key: 'W', label: 'Wall', tip: 'Drag a thick wall, or click corner to corner. Thickness, height and raise in the bar above', icon: '<path d="M3 9h18v6H3z"/><path d="M9 9v6M15 9v6" opacity=".55"/>' },
  { id: 'pieces',  key: 'P', label: 'Ready-made pieces', tip: 'Stairs, spiral stairs, arches, battlements and roofs, built from blocks', icon: '<path d="M4 20h4v-4h4v-4h4V8h4"/><path d="M4 20V9l8-5 8 5" opacity=".55"/>' },
  { id: 'fill',    key: 'G', label: 'Fill an enclosed area', tip: 'Click inside walls to fill the space. Right-click clears it', icon: '<path d="m5 11 6.5-6.5 7 7L12 18Z"/><path d="M11.5 4.5 9.5 2.5"/><path d="M19.5 15.5c1 1.4 1.5 2.4 1.5 3.1a1.5 1.5 0 0 1-3 0c0-.7.5-1.7 1.5-3.1Z"/>' },
  { id: 'replace', key: 'Q', label: 'Replace a block\'s material', tip: 'Click blocks to make them the current material, keeping their size. Chunk swaps a whole continuous run', icon: '<path d="M4 8h12l-3-3M20 16H8l3 3"/><rect x="17" y="5" width="4" height="4" rx=".6"/><rect x="3" y="15" width="4" height="4" rx=".6"/>' },
  { id: 'terrain', key: 'T', label: 'Shape the ground', tip: 'Raise or lower the ground a block at a time, or level it. Right-drag does the opposite', icon: '<path d="M2.5 18.5 8 10l3.5 4.5L15 8l6.5 10.5Z"/><path d="M2.5 21h19"/>' },
  { id: 'erase',   key: 'E', label: 'Erase', tip: 'Drag to clear squares on this level', icon: '<path d="M8.5 20H20"/><path d="m5 15.5 9-9 4.5 4.5-9 9H8.5Z"/><path d="m10 10.5 4.5 4.5"/>' },
  'sep',
  { id: 'built',   key: 'J', label: 'Mark built', tip: 'Click to mark a chunk built (Shift one block, Alt everything connected); right-click unmarks. In 2D and 3D', icon: '<rect x="3.5" y="3.5" width="17" height="17" rx="2"/><path d="m8 12.5 3 3 5.5-6"/>' },
  { id: 'item',    key: 'I', label: 'Place items and stations', tip: 'Stamp chests, crafting stations and furniture from the Items tab. R turns them', icon: '<path d="m4 8 8-4 8 4v8l-8 4-8-4Z"/><path d="m4 8 8 4 8-4M12 12v8"/>' },
  { id: 'zone',    key: 'Z', label: 'Mark a room or area', tip: 'Drag to outline a room or area, then name it', icon: '<path d="M4 8V4h4M16 4h4v4M20 16v4h-4M8 20H4v-4"/><path d="M9 12h6"/>' },
  { id: 'measure', key: 'M', label: 'Measure', tip: 'Drag to measure a distance in metres', icon: '<path d="M3.5 16.5 16.5 3.5l4 4-13 13Z"/><path d="m7.5 12.5 2 2M10.5 9.5l2 2M13.5 6.5l2 2"/>' },
  { id: 'pan',     key: 'H', label: 'Pan', tip: 'Drag to move the view. Holding Space does the same with any tool', icon: '<path d="M12 3v18M3 12h18"/><path d="m9 6 3-3 3 3M9 18l3 3 3-3M6 9l-3 3 3 3M18 9l3 3-3 3"/>' },
];
const PAINT_TOOLS = new Set(['paint', 'line', 'rect', 'room', 'fill', 'wall', 'replace']);
const FONT_UI = '"Instrument Sans", "Segoe UI", system-ui, sans-serif';
const FONT_MONO = '"JetBrains Mono", ui-monospace, Consolas, monospace';
const FACING = { 0: 'south', 90: 'west', 180: 'north', 270: 'east' };
const SOIL = '#7a6249';                 // earth around anything built below 0 m
const isUnder = L => !!L && L.elev < -0.01;

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const S = {
  store: null, mode: 'connecting', readOnly: false, loaded: false,
  plans: new Map(), planId: null, plan: null,
  baseRev: null, myRevs: new Set(), dirty: false, saving: false, again: false, saveTimer: 0, saveErr: null, creating: null,
  levelIdx: 0, layer: null, layerMem: 0, tool: 'paint', brush: '#', roomWall: '#', roomFloor: '.', rectFilled: false, round: false,
  itemDef: null, itemRot: 0, sel: null, clip: null, float: null, project: null,
  preview: null, hover: null, hoverIn: false, measure: null, ghostItem: null, placing: null,
  mirror: { mode: 'off', cx: null, cy: null }, mirrorPick: false,
  terrainMode: 'raise', terrainSize: 3, terrainRound: false, terrainSet: 1,
  piece: 'stairs', pieceMat: null, pieceRoof: 'Castle Roof Block', piecePitch: 1, pieceOverhang: 0.5, pieceRise: 0.5, pieceSpiral: 4, pieceArch: 'round',
  view: 'split', tab: 'materials', needFit: false,
  cam: { ox: 40, oy: 40, s: 16 },
  opt: { ghost: true, zones: true, altar: true, cut: true, shadows: true },
  hist: [], fut: [], editMat: null, remote: null, libFilter: '', libSizes: {}, catFilter: '', catOpen: new Set(),
};

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
const $ = (s, r = document) => r.querySelector(s);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const uid = (p = '') => p + Math.random().toString(36).slice(2, 8) + Date.now().toString(36).slice(-3);
const isHex = s => typeof s === 'string' && /^#[0-9a-fA-F]{6}$/.test(s);
const PRINT = /^[\x21-\x7e]$/;
// Palette symbols. In memory each square holds one character, a palette key: keys 1 to 94 are the visible
// ASCII characters ! to ~ (so plans saved before numbered symbols keep theirs), keys 95 to 999 are the
// characters from U+0100 on, which only live in memory and show as their number. Saved plans (fmt 2) write
// every key as its number, 001 to 999, and every row as runs of numbers: "045x12,000x3,007" is twelve squares
// of symbol 45, three empty squares, then one of symbol 7. (mage_common.py writes and reads the same.)
const MAX_SYMBOLS = 999;
const symCode = k => { const c = k.charCodeAt(0); return c <= 126 ? c - 32 : c - 0x100 + 95; };
const symChar = n => String.fromCharCode(n <= 94 ? n + 32 : 0x100 + n - 95);
const isSym = k => typeof k === 'string' && k.length === 1 && (PRINT.test(k) || (k.charCodeAt(0) >= 0x100 && k.charCodeAt(0) <= 0x100 + MAX_SYMBOLS - 95));
const symText = k => (PRINT.test(k) ? k : String(symCode(k)));     // how a symbol shows in the interface
const code3 = n => String(n).padStart(3, '0');
function encodeRow(cells) {
  const out = [];
  for (let i = 0; i < cells.length;) {
    let j = i + 1;
    while (j < cells.length && cells[j] === cells[i]) j++;
    out.push(code3(cells[i] === ' ' ? 0 : symCode(cells[i])) + (j - i > 1 ? 'x' + (j - i) : ''));
    i = j;
  }
  return out.join(',');
}
// A saved row's palette keys (' ' for empty). Anything it can't read counts in bad.n and reads as empty.
function decodeRow(s, w, bad) {
  const out = [];
  if (typeof s !== 'string' || !s) return out;
  for (const tok of s.split(',')) {
    const m = /^(\d{3})(?:x(\d{1,4}))?$/.exec(tok);
    if (!m || Number(m[1]) > MAX_SYMBOLS) { if (bad) bad.n++; out.push(' '); continue; }
    const c = Number(m[1]), k = c ? symChar(c) : ' ';
    for (let n = m[2] ? Number(m[2]) : 1; n > 0 && out.length < w; n--) out.push(k);
  }
  return out;
}
const clone = o => JSON.parse(JSON.stringify(o));
const fmt = n => (Math.round(n * 10) / 10).toString();
const CM = () => (S.plan && S.plan.cell) || 1;
const metres = n => fmt(n * CM());
function str(v, max) { return typeof v === 'string' ? v.trim().slice(0, max).trimEnd() : ''; }
function int(v, d) { const n = Math.round(Number(v)); return Number.isFinite(n) ? n : d; }
function clampInt(v, a, b, d) { const n = Math.round(Number(v)); return Number.isFinite(n) ? clamp(n, a, b) : d; }
function num(v, d, a, b) { const n = Number(v); return Number.isFinite(n) ? clamp(Math.round(n * 100) / 100, a, b) : d; }
// Heights in a plan are whole 0.5 m blocks (one voxel), so what's drawn is what you'd build.
const VOXEL = 0.5;
const toBlocks = v => Math.round(v / VOXEL) * VOXEL;
function blocksNum(v, d, a, b) { const n = Number(v); return Number.isFinite(n) ? clamp(toBlocks(n), a, b) : d; }
function hexA(hex, a) {
  if (!isHex(hex)) return hex;
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}
function lum(hex) {
  if (!isHex(hex)) return 0.5;
  const n = parseInt(hex.slice(1), 16);
  return (0.299 * ((n >> 16) & 255) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255;
}
const textOn = hex => lum(hex) > 0.58 ? '#1a272e' : '#ffffff';
// Lighten (t > 0, towards white) or darken (t < 0, towards black) a #rrggbb colour.
function tint(hex, t) {
  if (!isHex(hex) || !t) return hex;
  const n = parseInt(hex.slice(1), 16), to = t > 0 ? 255 : 0, a = Math.min(1, Math.abs(t));
  const ch = v => Math.round(v + (to - v) * a);
  return '#' + [(n >> 16) & 255, (n >> 8) & 255, n & 255].map(v => ch(v).toString(16).padStart(2, '0')).join('');
}
function slug(s) { return (s || 'plan').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40) || 'plan'; }
function abbreviate(t) {
  const words = t.split(/\s+/).filter(Boolean);
  return words.length > 1 ? words.map(w => w[0]).join('').slice(0, 3).toUpperCase() : t.slice(0, 3);
}
const LS = {
  get(k, d) { try { const v = localStorage.getItem('ebp:' + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem('ebp:' + k, JSON.stringify(v)); } catch { /* storage unavailable */ } },
};
function h(tag, props, ...kids) {
  const n = document.createElement(tag);
  if (props) for (const [k, v] of Object.entries(props)) {
    if (v == null || v === false) continue;
    if (k === 'class') n.className = v;
    else if (k === 'text') n.textContent = v;
    else if (k === 'html') n.innerHTML = v; // only used for trusted static icon markup
    else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
    else if (k === 'value' || k === 'checked') n[k] = v;
    else n.setAttribute(k, v === true ? '' : String(v));
  }
  for (const kid of kids.flat()) if (kid != null && kid !== false) n.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  return n;
}
const svg = (paths, cls) => `<svg viewBox="0 0 24 24" aria-hidden="true"${cls ? ` class="${cls}"` : ''}>${paths}</svg>`;

// ---------------------------------------------------------------------------
// Plan model
// ---------------------------------------------------------------------------
function blankGrid(w, h) { const g = new Array(h); for (let y = 0; y < h; y++) g[y] = new Array(w).fill(' '); return g; }
// Rows may be stored cropped: row 0 sits at y = oy and each row starts at x = ox.
function rowsToGrid(rows, w, h, ox = 0, oy = 0) {
  const g = new Array(h);
  for (let y = 0; y < h; y++) {
    const r = (Array.isArray(rows) && y >= oy && typeof rows[y - oy] === 'string') ? rows[y - oy] : '';
    const a = new Array(w);
    for (let x = 0; x < w; x++) { const c = x >= ox ? r.charAt(x - ox) : ''; a[x] = (c && PRINT.test(c)) ? c : ' '; }
    g[y] = a;
  }
  return g;
}
// A level saved in numbered symbols and runs (fmt 2), cropped like rowsToGrid's.
function codeRowsToGrid(rows, w, h, ox = 0, oy = 0, bad) {
  const g = blankGrid(w, h);
  if (!Array.isArray(rows)) return g;
  for (let j = 0; j < rows.length && oy + j < h; j++) {
    const cells = decodeRow(rows[j], w - ox, bad);
    for (let i = 0; i < cells.length; i++) g[oy + j][ox + i] = cells[i];
  }
  return g;
}
// Crop a level to the box around its content so sparse upper levels stay small: the rows as arrays of
// squares (trailing empty ones dropped), and where they start.
function cropCells(grid) {
  let x0 = Infinity, y0 = -1, y1 = -1;
  for (let y = 0; y < grid.length; y++) {
    const r = grid[y];
    for (let x = 0; x < r.length; x++) if (r[x] !== ' ') { if (y0 < 0) y0 = y; y1 = y; if (x < x0) x0 = x; break; }
  }
  if (y0 < 0) return { ox: 0, oy: 0, rows: [] };
  const rows = [];
  for (let y = y0; y <= y1; y++) { const r = grid[y].slice(x0); let n = r.length; while (n && r[n - 1] === ' ') n--; rows.push(r.slice(0, n)); }
  return { ox: x0, oy: y0, rows };
}
// The same as strings of characters (the terrain, and plans saved before fmt 2).
function normalizePlan(d) {
  d = (d && typeof d === 'object') ? d : {};
  const p = { name: '', notes: '', project: '', w: 48, h: 48, altar: 40, cell: 1, palette: {}, levels: [], items: [], zones: [] };
  p.project = typeof d.project === 'string' ? d.project.trim().slice(0, 40) : '';     // the project it's grouped in
  p.name = str(d.name, 80) || 'Untitled plan';
  p.notes = typeof d.notes === 'string' ? d.notes.slice(0, 20000) : '';
  p.w = clampInt(d.w, 4, MAX_GRID, 48);
  p.h = clampInt(d.h, 4, MAX_GRID, 48);
  p.altar = GAME.altarSizes.includes(Number(d.altar)) ? Number(d.altar) : 40;
  p.cell = Number(d.cell) === 0.5 ? 0.5 : 1;
  const pal = (d.palette && typeof d.palette === 'object') ? d.palette : DEFAULT_PALETTE;
  const fmt2 = d.fmt === 2, palNums = fmt2 && d.palette === pal;   // numbered symbols and runs (the default palette is in characters)
  const keyOf = s => (typeof s !== 'string' ? null : palNums ? (/^\d{3}$/.test(s) && +s >= 1 && +s <= MAX_SYMBOLS ? symChar(+s) : null) : (PRINT.test(s) ? s : null));
  const bad = { n: 0 };
  for (const [k0, v] of Object.entries(pal)) {
    const k = keyOf(k0);
    if (!k || !v || typeof v !== 'object') { bad.n += palNums ? 1 : 0; continue; }
    if (Object.keys(p.palette).length >= MAX_SYMBOLS) break;
    p.palette[k] = { name: str(v.name, 40) || ('Symbol ' + k), kind: KINDS[v.kind] ? v.kind : 'wall', color: isHex(v.color) ? v.color.toLowerCase() : '#8a8f96' };
    const ph = blocksNum(v.height, 0, 0, 40);
    if (ph > 0) p.palette[k].height = ph;
    const pb = blocksNum(v.base, 0, 0, 40);
    if (pb > 0) p.palette[k].base = pb;
    const u = keyOf(v.under);
    if (u && u !== k) p.palette[k].under = u;
    const po = blocksNum(v.opening, 0, 0, 40);                  // a large square door's 3 m, a small window's 1 m
    if (po > 0 && (p.palette[k].kind === 'door' || p.palette[k].kind === 'window')) p.palette[k].opening = po;
    if (v.sill != null && p.palette[k].kind === 'window') { const sl = blocksNum(v.sill, -1, 0, 40); if (sl >= 0) p.palette[k].sill = sl; }
  }
  if (!Object.keys(p.palette).length) p.palette = clone(DEFAULT_PALETTE);
  const seen = new Set();
  (Array.isArray(d.levels) ? d.levels : []).slice(0, MAX_LEVELS).forEach((L, i) => {
    if (!L || typeof L !== 'object') return;
    let id = str(L.id, 24).replace(/[^\w-]/g, '') || ('L' + (i + 1));
    while (seen.has(id)) id += 'x';
    seen.add(id);
    p.levels.push({ id, name: str(L.name, 80) || ('Level ' + (i + 1)), elev: blocksNum(L.elev, i * GAME.levelH, -60, 400), height: blocksNum(L.height, GAME.levelH, 0.5, 40), hidden: !!L.hidden, ...(str(L.group, 40).trim() ? { group: str(L.group, 40).trim() } : {}), grid: (fmt2 ? codeRowsToGrid : rowsToGrid)(L.rows, p.w, p.h, clampInt(L.ox, 0, p.w, 0), clampInt(L.oy, 0, p.h, 0), bad) });
  });
  if (bad.n) p.readProblems = bad.n;                        // (not saved: openPlan warns about it)
  if (Array.isArray(d.levels) && d.levels.length > MAX_LEVELS) p.droppedLevels = d.levels.length - MAX_LEVELS;
  if (!p.levels.length) p.levels.push({ id: 'ground', name: 'Ground floor', elev: 0, height: GAME.levelH, hidden: false, grid: blankGrid(p.w, p.h) });
  p.levels.sort((a, b) => a.elev - b.elev);
  const lids = new Set(p.levels.map(l => l.id));
  const first = p.levels.find(l => l.elev >= 0) || p.levels[0];
  const used = new Set();
  for (const it of (Array.isArray(d.items) ? d.items : []).slice(0, 3000)) {
    if (!it || typeof it !== 'object') continue;
    let id = str(it.id, 24) || uid('i');
    while (used.has(id)) id = uid('i');
    used.add(id);
    const type = str(it.type, 64) || 'custom';
    const def = LIB_BY_TYPE[type], st = VOXEL / p.cell;           // positions and sizes on the 0.5 m block grid
    const sq = (v, d, lo, hi) => { const n = Number(v); return Number.isFinite(n) ? clamp(Math.round(n / st) * st, lo, hi) : d; };
    const n = {
      id, level: lids.has(it.level) ? it.level : first.id, type,
      label: str(it.label, 40) || (def ? def.name : 'Item'),
      x: sq(it.x, 0, -4096, 4096), y: sq(it.y, 0, -4096, 4096),
      w: sq(it.w, def ? Math.max(st, Math.round(def.w / p.cell / st) * st) : 1, st, 128), d: sq(it.d, def ? Math.max(st, Math.round(def.d / p.cell / st) * st) : 1, st, 128),
      h: num(it.h, def ? def.h : 1, 0.1, 40),
      rot: [0, 90, 180, 270].includes(Number(it.rot)) ? Number(it.rot) : 0,
      color: isHex(it.color) ? it.color.toLowerCase() : (def ? def.color : '#8a8f96'),
    };
    if (typeof it.mount === 'string' && it.mount !== 'floor' && ['door', 'window', 'wall', 'ceiling'].includes(it.mount)) n.mount = it.mount;
    if (it.z != null) { const z = blocksNum(it.z, 0, 0, 80); if (z > 0) n.z = z; }
    p.items.push(n);
  }
  for (const z of (Array.isArray(d.zones) ? d.zones : []).slice(0, 500)) {
    if (!z || typeof z !== 'object') continue;
    let id = str(z.id, 24) || uid('z');
    while (used.has(id)) id = uid('z');
    used.add(id);
    p.zones.push({
      id, level: lids.has(z.level) ? z.level : first.id, name: str(z.name, 40) || 'Area',
      x: int(z.x, 0), y: int(z.y, 0), w: clampInt(z.w, 1, MAX_GRID, 4), h: clampInt(z.h, 1, MAX_GRID, 4),
      color: isHex(z.color) ? z.color.toLowerCase() : ZONE_COLORS[0],
    });
  }
  p.terrain = terrainFromDoc(d.terrain, p);
  return p;
}
function serialize(p, forHistory) {
  const o = { v: 1, fmt: 2 };
  if (!forHistory) { o.name = p.name; o.notes = p.notes; if (p.project) o.project = p.project; }
  o.w = p.w; o.h = p.h; o.cell = p.cell; o.altar = p.altar;
  o.palette = {};
  for (const [k, e] of Object.entries(p.palette)) {
    const c = clone(e);
    if (c.under) c.under = code3(symCode(c.under));
    o.palette[code3(symCode(k))] = c;
  }
  o.levels = p.levels.map(L => { const c = cropCells(L.grid); return { id: L.id, name: L.name, elev: L.elev, height: L.height, hidden: !!L.hidden, ...(L.group ? { group: L.group } : {}), ox: c.ox, oy: c.oy, rows: c.rows.map(encodeRow) }; });
  o.items = p.items.map(i => ({ id: i.id, level: i.level, type: i.type, label: i.label, x: i.x, y: i.y, w: i.w, d: i.d, h: i.h, rot: i.rot, color: i.color, ...(i.mount ? { mount: i.mount } : {}), ...(i.z ? { z: i.z } : {}) }));
  o.zones = p.zones.map(z => ({ id: z.id, level: z.level, name: z.name, x: z.x, y: z.y, w: z.w, h: z.h, color: z.color }));
  const t = p.terrain && terrainToDoc(p);
  if (t) o.terrain = t;
  return o;
}
function blankPlan(name, w, hgt, cell) {
  return normalizePlan({ name, w, h: hgt, cell, palette: DEFAULT_PALETTE, levels: [{ id: 'ground', name: 'Ground floor', elev: 0, height: GAME.levelH, rows: [] }], items: [], zones: [], notes: '' });
}
const lv = () => (S.plan ? S.plan.levels[S.levelIdx] : null);
const levelIndex = id => { const i = S.plan.levels.findIndex(l => l.id === id); return i < 0 ? clamp(S.levelIdx, 0, S.plan.levels.length - 1) : i; };
function itemRect(it) { const r = it.rot === 90 || it.rot === 270; return { x: it.x, y: it.y, w: r ? it.d : it.w, h: r ? it.w : it.d }; }
const inB = (x, y) => S.plan && x >= 0 && y >= 0 && x < S.plan.w && y < S.plan.h;
let planVer = 0;                                             // bumped by every change to the plan (layer views cache on it)
function setCell(L, x, y, ch) { if (!inB(x, y)) return false; const row = L.grid[y]; if (row[x] === ch) return false; row[x] = ch; planVer++; return true; }
const findItem = id => S.plan.items.find(i => i.id === id);
const findZone = id => S.plan.zones.find(z => z.id === id);
function rectFrom(a, b) {
  const P = S.plan;
  const ax = clamp(a[0], 0, P.w - 1), ay = clamp(a[1], 0, P.h - 1), bx = clamp(b[0], 0, P.w - 1), by = clamp(b[1], 0, P.h - 1);
  const x = Math.min(ax, bx), y = Math.min(ay, by);
  return { x, y, w: Math.abs(bx - ax) + 1, h: Math.abs(by - ay) + 1 };
}
const rectInside = (r, R) => r.x >= R.x && r.y >= R.y && r.x + r.w <= R.x + R.w && r.y + r.h <= R.y + R.h;
function lineCells(x0, y0, x1, y1) {
  const pts = [];
  let dx = Math.abs(x1 - x0), sx = x0 < x1 ? 1 : -1, dy = -Math.abs(y1 - y0), sy = y0 < y1 ? 1 : -1, err = dx + dy;
  for (let guard = 0; guard < 2000; guard++) {
    pts.push([x0, y0]);
    if (x0 === x1 && y0 === y1) break;
    const e2 = 2 * err;
    if (e2 >= dy) { err += dy; x0 += sx; }
    if (e2 <= dx) { err += dx; y0 += sy; }
  }
  return pts;
}
function constrainLine(a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1], ax = Math.abs(dx), ay = Math.abs(dy);
  if (ax > 2 * ay) return [b[0], a[1]];
  if (ay > 2 * ax) return [a[0], b[1]];
  const m = Math.max(ax, ay);
  return [a[0] + Math.sign(dx) * m, a[1] + Math.sign(dy) * m];
}
// Box or round (ellipse fitted to the dragged box). `filled` false gives just the edge.
function shapeTest(a, b, round) {
  const x0 = Math.min(a[0], b[0]), x1 = Math.max(a[0], b[0]), y0 = Math.min(a[1], b[1]), y1 = Math.max(a[1], b[1]);
  const rx = (x1 - x0 + 1) / 2, ry = (y1 - y0 + 1) / 2, cx = x0 + rx, cy = y0 + ry;
  const inside = (x, y) => x >= x0 && x <= x1 && y >= y0 && y <= y1 && (!round || ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0001);
  return { x0, x1, y0, y1, inside };
}
function rectCells(a, b, filled, round) {
  const t = shapeTest(a, b, round), out = [];
  for (let y = t.y0; y <= t.y1; y++) for (let x = t.x0; x <= t.x1; x++) {
    if (!t.inside(x, y)) continue;
    const edge = !t.inside(x - 1, y) || !t.inside(x + 1, y) || !t.inside(x, y - 1) || !t.inside(x, y + 1);
    if (filled || edge) out.push([x, y]);
  }
  return out;
}
function roomGroups(a, b) {
  const t = shapeTest(a, b, S.round), walls = [], inner = [];
  const W = t.x1 - t.x0 + 3, H = t.y1 - t.y0 + 3, at = (x, y) => (y - t.y0 + 1) * W + (x - t.x0 + 1);
  let core = new Uint8Array(W * H);                          // inside the shape, with a border of outside round it
  for (let y = t.y0; y <= t.y1; y++) for (let x = t.x0; x <= t.x1; x++) if (t.inside(x, y)) core[at(x, y)] = 1;
  const T = Math.max(1, Math.round((S.roomThick || CM()) / CM()));
  for (let n = 0; n < T; n++) {                               // peel the walls off, a square at a time
    const next = core.slice();
    for (let i = W + 1; i < W * H - W - 1; i++) if (core[i] && !(core[i - 1] && core[i + 1] && core[i - W] && core[i + W])) next[i] = 0;
    core = next;
  }
  for (let y = t.y0; y <= t.y1; y++) for (let x = t.x0; x <= t.x1; x++) {
    if (!t.inside(x, y)) continue;
    if (!core[at(x, y)]) walls.push([x, y]); else if (S.roomFloor) inner.push([x, y]);
  }
  return [{ cells: inner, ch: S.roomFloor || ' ' }, { cells: walls, ch: S.roomWall }];
}
function flood(L, sx, sy, ch) {
  if (!inB(sx, sy)) return 0;
  const target = L.grid[sy][sx];
  if (target === ch) return 0;
  const stack = [sx, sy];
  let n = 0;
  while (stack.length) {
    const y = stack.pop(), x = stack.pop();
    if (!inB(x, y) || L.grid[y][x] !== target) continue;
    L.grid[y][x] = ch; n++; planVer++;
    stack.push(x + 1, y, x - 1, y, x, y + 1, x, y - 1);
  }
  return n;
}
function computeCounts() {
  const c = {};
  if (!S.plan) return c;
  for (const L of S.plan.levels) for (const row of L.grid) for (const ch of row) if (ch !== ' ') c[ch] = (c[ch] || 0) + 1;
  return c;
}
function boundsOf(levels, withItems = true) {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  const ext = (ax, ay, bx, by) => { x0 = Math.min(x0, ax); y0 = Math.min(y0, ay); x1 = Math.max(x1, bx); y1 = Math.max(y1, by); };
  const ids = new Set(levels.map(l => l.id));
  for (const L of levels) for (let y = 0; y < L.grid.length; y++) { const r = L.grid[y]; for (let x = 0; x < r.length; x++) if (r[x] !== ' ') ext(x, y, x, y); }
  if (withItems) {
    for (const it of S.plan.items) if (ids.has(it.level)) { const R = itemRect(it); ext(Math.floor(R.x), Math.floor(R.y), Math.ceil(R.x + R.w) - 1, Math.ceil(R.y + R.h) - 1); }
    for (const z of S.plan.zones) if (ids.has(z.level)) ext(z.x, z.y, z.x + z.w - 1, z.y + z.h - 1);
  }
  return x0 === Infinity ? null : { x: x0, y: y0, w: x1 - x0 + 1, h: y1 - y0 + 1 };
}
const topOfLevels = () => S.plan.levels.reduce((m, L) => Math.max(m, L.elev + L.height), 0);
function altarRect(it) {
  const size = ((S.plan && S.plan.altar) || 40) / CM(), R = itemRect(it), half = size / 2;
  return { x: R.x + R.w / 2 - half, y: R.y + R.h / 2 - half, w: size, h: size };
}
