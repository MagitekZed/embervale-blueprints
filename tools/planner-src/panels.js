// ---------------------------------------------------------------------------
// Side panels. The Materials tab shows this plan's materials grouped by material (sizes and pieces fold
// into one row, under Walls, Floors, Roofs…), with search, filters and the 1–9 hotbar, or the whole block
// catalogue. The Items tab: search, filter chips, recent items, the placed list, size status. Plus the
// quick finder (/) and the panel's width (drag its left edge).
// ---------------------------------------------------------------------------
const MAT_SECTIONS = [
  { id: 'walls', label: 'Walls and blocks', kinds: ['wall', 'block'] },
  { id: 'floors', label: 'Floors and water', kinds: ['floor', 'water'] },
  { id: 'roofs', label: 'Roofs', kinds: ['roof'] },
  { id: 'openings', label: 'Painted doors and windows', kinds: ['door', 'window'] },
  { id: 'dig', label: 'Digging', kinds: ['dig'] },
];
const MAT_FILTERS = [['all', 'All'], ['walls', 'Walls'], ['floors', 'Floors'], ['roofs', 'Roofs'], ['openings', 'Openings'], ['level', 'On this level']];
const ICON = {
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
  pin: '<path d="M9 4h6l-1 5 3 3H7l3-3Z"/><path d="M12 12v8"/>',
  floor: '<rect x="5" y="8" width="14" height="10" rx="1.5"/><path d="M5 18h14"/>',
  door: '<path d="M7 20V4h10v16"/><path d="M4 20h16"/><circle cx="14" cy="12" r=".9"/>',
  window: '<rect x="5" y="5" width="14" height="14" rx="1"/><path d="M12 5v14M5 12h14"/>',
  wall: '<path d="M5 4v16"/><rect x="8" y="9" width="9" height="6" rx="1"/><path d="M5 12h3"/>',
  ceiling: '<path d="M4 4h16"/><path d="M12 4v5"/><path d="M8 14a4 4 0 0 1 8 0Z"/>',
};

// ---- materials: groups of one material's variants
// A variant's short label: a roof's top height, the piece in brackets ("tread 1 m"), or its height.
function variantLabel(e) {
  if (e.kind === 'roof') return `${fmt(roofTop(e, S.plan.cell))} m`;
  const tag = /\(([^()]*)\)\s*$/.exec(e.name);
  let t = tag ? tag[1] : (/\s([\d.]+ m)$/.exec(e.name) || [])[1];
  if (!t) t = e.kind === 'wall' ? (e.height ? `${fmt(e.height)} m` : 'full height') : e.kind === 'block' ? `${fmt(e.height || 1)} m` : KINDS[e.kind].label.toLowerCase();
  if (e.base && !/up\b/.test(t)) t += ` · ${fmt(e.base)} m up`;
  return t;
}
const variantSort = e => (e.kind === 'roof' ? roofTop(e, S.plan.cell) : (e.base || 0) * 100 + (e.height || 0));
function materialGroups(P, counts) {
  const secs = MAT_SECTIONS.map(s => ({ ...s, groups: new Map() }));
  for (const [k, e] of Object.entries(P.palette)) {
    const sec = secs.find(s => s.kinds.includes(e.kind)) || secs[0];
    const base = e.kind === 'door' || e.kind === 'window' ? e.name : matName(e.name);
    if (!sec.groups.has(base)) sec.groups.set(base, { base, sec: sec.id, key: sec.id + '|' + base, items: [], n: 0 });
    const g = sec.groups.get(base);
    g.items.push(k); g.n += counts[k] || 0;
  }
  for (const s of secs) {
    for (const g of s.groups.values()) g.items.sort((a, b) => variantSort(P.palette[a]) - variantSort(P.palette[b]) || P.palette[a].name.localeCompare(P.palette[b].name));
    s.list = [...s.groups.values()].sort((a, b) => a.base.localeCompare(b.base));
  }
  return secs;
}
function levelSymbols(L) { const s = new Set(); if (L) for (const r of L.grid) for (const c of r) if (c !== ' ') s.add(c); return s; }

function renderMaterials() {
  const pane = $('#pane-materials');
  if (!S.plan) { pane.replaceChildren(); return; }
  const P = S.plan, counts = computeCounts();
  S.matOpen = S.matOpen || new Set();
  const view = S.matView || 'plan';
  const secs = materialGroups(P, counts), nGroups = secs.reduce((t, s) => t + s.list.length, 0), hb = getHotbar();
  const seg = h('div', { class: 'seg wide', role: 'group', 'aria-label': 'Show' },
    h('button', { type: 'button', 'aria-pressed': String(view === 'plan'), text: `This plan · ${nGroups}`, title: 'The materials this plan uses, grouped by material', onclick: () => { S.matView = 'plan'; renderMaterials(); } }),
    h('button', { type: 'button', 'aria-pressed': String(view === 'blocks'), text: `All blocks · ${BLOCKS.length}`, title: 'Every block, roof and terrain material in the game, to add to this plan', onclick: () => { S.matView = 'blocks'; renderMaterials(); } }));
  const head = h('div', { class: 'pane-head' }, h('h3', { text: 'Materials' }),
    h('span', { class: 'btnrow' },
      h('button', { class: 'iconbtn sm btn-ghost', type: 'button', title: 'How materials work', 'data-tip-desc': 'Pick one, then paint. Each symbol is how the plan is stored, and what Claude reads. Counts are squares across all levels', 'aria-expanded': String(!!S.matHelp), html: svg(ICON.info), onclick: () => { S.matHelp = !S.matHelp; renderMaterials(); } }),
      h('button', { class: 'btn btn-sm', type: 'button', text: 'Add material', onclick: addMaterial })));
  const help = S.matHelp ? h('p', { class: 'note', text: `Pick a material, then paint. Materials of the same block fold into one row: open it to pick a size or piece. Each symbol is how the plan is stored, and what Claude reads. Counts are squares (${metres(1)} m each) across all levels. The hotbar's 1–9 keys pick a material; Shift+click a slot to put the current one there.` }) : null;
  if (view === 'blocks') { pane.replaceChildren(head, help, seg, catalogueSection()); return; }

  // filters and search
  const q = (S.matQuery || '').trim().toLowerCase(), f = S.matFilter || 'all';
  const search = h('input', { type: 'text', placeholder: 'Find a material', 'aria-label': 'Find a material', value: S.matQuery || '' });
  search.addEventListener('input', () => { S.matQuery = search.value; drawList(); });
  const chips = h('div', { class: 'chips' }, ...MAT_FILTERS.map(([id, lab]) => h('button', { class: 'chip', type: 'button', 'aria-pressed': String(f === id), text: lab, onclick: () => { S.matFilter = f === id && id !== 'all' ? 'all' : id; renderMaterials(); } })));
  const listBox = h('div', { class: 'section' });
  const drawList = () => {
    const qq = (S.matQuery || '').trim().toLowerCase(), onLevel = f === 'level' ? levelSymbols(lv()) : null;
    const out = [];
    for (const s of secs) {
      if (f !== 'all' && f !== 'level' && f !== s.id) continue;
      const rows = s.list.filter(g => (!qq || g.base.toLowerCase().includes(qq) || g.items.some(k => P.palette[k].name.toLowerCase().includes(qq) || k === qq))
        && (!onLevel || g.items.some(k => onLevel.has(k))));
      if (!rows.length) continue;
      out.push(h('div', { class: 'matsec' }, h('div', { class: 'secthead' }, h('span', { text: s.label }), h('span', { text: String(rows.length) })),
        h('ul', { class: 'matlist' }, ...rows.map(g => matRow(g, P, counts, !!qq, hb)))));
    }
    listBox.replaceChildren(...(out.length ? out : [h('p', { class: 'note', text: qq ? 'No materials match that.' : 'Nothing here yet.' })]));
    markPicked();
  };
  drawList();
  const unknown = Object.keys(counts).filter(k => !P.palette[k]);
  const unused = unusedMaterials(P, counts);
  pane.replaceChildren(...[
    head, help, seg,
    h('div', { class: 'libsearch' }, search, chips),
    h('div', { class: 'section' }, h('div', { class: 'secthead' }, h('span', { text: 'Hotbar' }), h('span', { text: 'keys 1–9' })), hotbarStrip(false)),
    listBox,
    unknown.length ? h('div', { class: 'callout' }, h('b', { text: 'Symbols without a material: ' }), unknown.join(' '), ' ',
      ...unknown.map(k => h('button', { class: 'btn btn-sm', type: 'button', text: `Add “${k}”`, onclick: () => addUnknownSymbol(k) }))) : null,
    unused.length ? h('div', { class: 'secthead tidy' }, h('span', { text: `${unused.length} unused material${unused.length === 1 ? '' : 's'}`, title: unused.map(k => `${k}  ${P.palette[k].name}`).join('\n') }),
      h('button', { class: 'linkbtn', type: 'button', disabled: S.readOnly, text: 'Tidy away', onclick: () => tidyMaterials(unused) })) : null,
  ].filter(Boolean));
}
function matRow(g, P, counts, searching, hb) {
  const ks = g.items, one = ks.length === 1, cur = ks.includes(S.brush);
  const top = ks.reduce((a, b) => ((counts[b] || 0) > (counts[a] || 0) ? b : a));
  const k0 = cur ? S.brush : top, e0 = P.palette[k0];
  const open = !one && (S.matOpen.has(g.key) || searching);
  const slot = hb.findIndex(k => ks.includes(k));
  const words = g.sec === 'roofs' ? 'heights' : 'pieces';
  const li = h('li', { class: 'mat' + (one ? '' : ' group') + (open ? ' open' : ''), 'aria-current': String(cur), 'data-k': one ? k0 : null, 'data-group': g.key, 'data-ks': ks.join('') });
  li.append(h('div', { class: 'mat-row' },
    h('button', { class: 'mat-pick', type: 'button', title: one ? `Paint with ${e0.name}` : `${g.base}: ${ks.length} ${words}`, 'data-tip-desc': one ? matDetail(e0) : 'Open to pick one. Clicking also picks the one you use most', 'aria-expanded': one ? null : String(open),
      onclick: () => { if (one) { pickBrush(k0); return; } if (open) { S.matOpen.delete(g.key); renderMaterials(); } else { S.matOpen.add(g.key); if (!cur) pickBrush(top); else renderMaterials(); } } },
      h('span', { class: 'swatch sm', style: `background:${e0.color};color:${textOn(e0.color)}`, text: symText(k0) }),
      h('span', { class: 'mat-name', text: one ? e0.name : g.base }),
      one ? null : h('span', { class: 'mat-more', text: `${ks.length} ${open ? '▾' : '▸'}`, title: `${ks.length} ${words}` }),
      slot >= 0 ? h('span', { class: 'hotno', text: String(slot + 1), title: `On the hotbar, key ${slot + 1}` }) : null,
      h('span', { class: 'mat-count', text: g.n ? g.n.toLocaleString() : '–', title: 'Squares painted, all levels' })),
    h('button', { class: 'iconbtn sm btn-ghost', type: 'button', title: 'Edit material', 'aria-label': `Edit ${e0.name}`, 'aria-expanded': String(ks.includes(S.editMat)),
      onclick: () => { S.editMat = ks.includes(S.editMat) ? null : k0; if (!one) S.matOpen.add(g.key); renderMaterials(); }, html: svg('<path d="M4 20l1-4.5L15.5 5 19 8.5 8.5 19Z"/>') })));
  if (open) li.append(h('div', { class: 'variants' }, ...ks.map(k => {
    const e = P.palette[k];
    return h('button', { class: 'variant', type: 'button', 'data-k': k, 'aria-pressed': String(k === S.brush), title: e.name, 'data-tip-desc': `${matDetail(e)} · ${counts[k] || 0} squares · double-click to edit`,
      onclick: () => pickBrush(k), ondblclick: () => { S.editMat = k; renderMaterials(); } },
      h('span', { class: 'vsw', style: `background:${e.color};color:${textOn(e.color)}`, text: k }), variantLabel(e));
  })));
  if (ks.includes(S.editMat)) li.append(materialEditor(S.editMat, P.palette[S.editMat]));
  return li;
}
// Materials nothing is painted with, nothing stands on, and nobody is holding.
function unusedMaterials(P, counts) {
  const under = new Set(Object.values(P.palette).map(e => e.under).filter(Boolean));
  return Object.keys(P.palette).filter(k => !counts[k] && !under.has(k) && k !== S.brush && k !== S.roomWall && k !== S.roomFloor);
}
function tidyMaterials(keys) {
  const P = S.plan;
  if (keys.length >= Object.keys(P.palette).length) return;
  begin();
  for (const k of keys) delete P.palette[k];
  commit();
  if (keys.includes(S.editMat)) S.editMat = null;
  renderMaterials(); renderOptbar();
  toast(`Removed ${keys.length} unused material${keys.length === 1 ? '' : 's'}. Undo with Ctrl+Z.`);
}

// ---- the hotbar: nine materials on the 1–9 keys, per plan (kept in this browser)
const hotbarKey = () => 'hotbar:' + (S.planId || 'local');
function getHotbar() {
  const P = S.plan;
  if (!P) return [];
  let hb = LS.get(hotbarKey(), null);
  if (!Array.isArray(hb)) {                                 // to start with: the nine you use most
    const c = computeCounts();
    hb = Object.keys(P.palette).filter(k => P.palette[k].kind !== 'dig').sort((a, b) => (c[b] || 0) - (c[a] || 0)).slice(0, 9);
    LS.set(hotbarKey(), hb);
  }
  hb = hb.slice(0, 9).map(k => (k && P.palette[k] ? k : null));
  while (hb.length < 9) hb.push(null);
  return hb;
}
function setHotbar(hb) { LS.set(hotbarKey(), hb); renderMaterials(); renderOptbar(); }
function pinToHotbar(k, slot) {
  if (!k || !S.plan.palette[k]) return;
  const hb = getHotbar(), was = hb.indexOf(k);
  if (slot == null) { slot = was >= 0 ? was : hb.indexOf(null); if (slot < 0) slot = 8; }
  if (was >= 0) hb[was] = null;
  hb[slot] = k;
  setHotbar(hb);
}
function unpinFromHotbar(k) { const hb = getHotbar(), i = hb.indexOf(k); if (i >= 0) { hb[i] = null; setHotbar(hb); } }
function hotbarStrip(compact) {
  const hb = getHotbar();
  return h('div', { class: 'hotbar' + (compact ? ' compact' : ''), role: 'group', 'aria-label': 'Hotbar' }, ...hb.map((k, i) => {
    const e = k && S.plan.palette[k];
    return h('button', { class: 'hot', type: 'button', 'aria-pressed': String(!!k && k === S.brush),
      style: e ? `background:${e.color};color:${textOn(e.color)}` : null,
      title: e ? `${e.name} (${i + 1})` : `Empty slot (${i + 1})`, 'data-tip-desc': e ? 'Shift+click puts the current material here · right-click empties the slot' : 'Click puts the current material here',
      onclick: ev => { if (ev.shiftKey || !k) pinToHotbar(S.brush, i); else pickBrush(k); },
      oncontextmenu: ev => { ev.preventDefault(); if (k) { const h2 = getHotbar(); h2[i] = null; setHotbar(h2); } } },
      h('span', { class: 'n', text: String(i + 1) }), e && !compact ? h('span', { class: 'k', text: k }) : null);
  }));
}
const hotbarPick = n => { const k = getHotbar()[n - 1]; if (k) pickBrush(k); };

// ---- items: filters, recents, placed list
const ITEM_FILTERS = [['all', 'All'], ['stations', 'Stations'], ['storage', 'Storage'], ['openings', 'Doors and windows'], ['structural', 'Fences, stairs and more'], ['lights', 'Lights'], ['displays', 'Displays'], ['furniture', 'Furniture'],
  ['decor', 'Decor'], ['survivors', 'Survivors'], ['structure', 'Base and farm'], ['placeholders', 'Placeholders'], ['measure', 'Needs measuring']];
function itemFilterOf(cat) {
  const c = cat.cat;
  if (c === 'Chests' || c === 'Magic chests' || c.startsWith('Storage ·')) return 'storage';
  if (c === 'Doors' || c === 'Windows') return 'openings';
  if (c.startsWith('Structure ·')) return 'structural';
  if (c.startsWith('Lights ·')) return 'lights';
  if (c.startsWith('Displays ·')) return 'displays';
  if (c.startsWith('Furniture ·')) return 'furniture';
  if (c.startsWith('Decor')) return 'decor';
  if (c.startsWith('Craftspeople')) return 'survivors';
  if (c === 'Farm & animals' || c.startsWith('Base ·') || c.startsWith('Farm ·') || c.startsWith('Sparkworks') || c === 'Base essentials' || c === 'Walk mode' || c === 'Plants') return 'structure';
  return 'stations';
}
// A library entry that stands in for a kind of thing (Bed, Table, Light): the crafting data has real items of
// its type, none with its name. It still counts as the basic real one in the Crafting list.
function isPlaceholder(it) {
  if (it.craft || typeof CRAFT !== 'object' || !CRAFT) return false;
  const real = CRAFT.items.filter(c => c.libraryType === it.type);
  return real.length > 0 && !real.some(c => c.name === it.name || c.catalogueName === it.name);
}
const placeholderFor = it => { const c = CRAFT.items.find(x => x.libraryType === it.type && x.primary); return c ? c.name : null; };
const needsMeasuring = it => !!it.src && !libDef(it).measured;
// "Makeable by": hide catalogue items you can't make until a later region (planner v52). Items with no region
// (the library's own, the Springlands decorations) always show; found-only pieces with no known region only
// with "Every region".
const itemRegionCap = () => { const r = LS.get('itemRegion', '') || ''; return GAME_REGIONS.indexOf(r); };
// What sets an item's region, as a chain: "Silver Bars (Blast Furnace (Bellows (…)))" reads "Silver Bars → Blast
// Furnace → Bellows from the Forge of Obsidia → Blacksmith's quest" (a step that only names the next one is dropped).
const regionChain = s => {
  const out = [];
  for (const p of String(s).replace(/\)+$/, '').split(' (')) { if (out.length && p.startsWith(out[out.length - 1])) out[out.length - 1] = p; else out.push(p); }
  return out.join(' → ');
};
const withinRegion = it => { const cap = itemRegionCap(); return cap < 0 || (it.region ? GAME_REGIONS.indexOf(it.region) <= cap : !it.found); };
function itemGroups() {
  const groups = [], ph = { cat: 'Placeholders', note: 'Generic stand-ins. Each counts as its basic real item in the Crafting list; swap in a real one when you can.', items: [], filter: 'placeholders' };
  for (const c of LIBRARY) {
    const items = c.items.filter(it => !isPlaceholder(it));
    ph.items.push(...c.items.filter(isPlaceholder));
    if (items.length) groups.push({ cat: c.cat, note: c.note, items, filter: itemFilterOf(c), craft: !!c.craft });
  }
  if (ph.items.length) groups.push(ph);
  return groups;
}
// ---- grouping (planner v61): by category, under headings like the Crafting list's, or by who or what makes it
const ITEM_TAIL = ['By hand', 'Found, not crafted', 'Not crafted', 'Planner', 'Placeholders'];   // these list last
const BATCH_PREFIX = /^(Structure|Lights|Storage|Displays|Furniture|Base|Farm|Stations|Decor) · /;
const LIB_TOP = { 'Chests': 'Storage', 'Magic chests': 'Storage', 'Your workbench': 'Base and stations', 'Base essentials': 'Base and stations',
  'Craftspeople (stand + work area)': 'Survivors', 'Farm & animals': 'Farming and animals', 'Sparkworks & structure': 'Base and stations',
  'Sparkworks': 'Base and stations', 'Plants': 'Decor · Plants and garden', 'Walk mode': 'Planner', 'Placeholders': 'Placeholders', 'Doors': 'Structure', 'Windows': 'Structure' };
const NPC_NAME = { Blacksmith: 'Oswald Anders', Alchemist: 'Balthazar', Carpenter: 'Cade Hawthorn', Hunter: 'Athalan Skree', Farmer: 'Emily Fray',
  Collector: 'Alden Crowley', Bard: 'Valory', Fisher: 'Captain Melville Fontane', Barber: 'Elio Ricci', 'Ancient Researcher': 'Loraine Crim' };
const libStationGroup = cat => cat === 'Your workbench' || (/ · /.test(cat) && !BATCH_PREFIX.test(cat));   // the library's stations by crafter
const subCatOf = cat => (libStationGroup(cat) ? 'Crafting stations' : cat.replace(BATCH_PREFIX, ''));
function topCatOf(cat) {
  if (LIB_TOP[cat]) return LIB_TOP[cat];
  if (libStationGroup(cat)) return 'Base and stations';
  return craftGroup(subCatOf(cat));
}
let CRAFT_NAMES = null;
const craftNamed = n => { if (!CRAFT_NAMES) CRAFT_NAMES = new Map((CRAFT.items || []).map(c => [c.name, c])); return CRAFT_NAMES.get(n) || null; };
// Who or what makes an item: its crafter ("Carpenter · Cade Hawthorn"), else its station, else by hand, found, or
// a planner stand-in. Catalogue entries carry their recipe's crafter; library items are looked up by name.
function makerOf(it, cat) {
  if (cat === 'Placeholders') return 'Placeholders';
  const c = it.craft ? it : (typeof CRAFT === 'object' && CRAFT ? craftNamed(it.name) : null);
  if (!c) return 'Planner';
  const hasRecipe = it.craft ? it.hasRecipe : (c.inputs || []).length > 0;
  if (c.crafter) return NPC_NAME[c.crafter] ? `${c.crafter} · ${NPC_NAME[c.crafter]}` : c.crafter;
  if (c.station) return c.station;
  return hasRecipe ? 'By hand' : c.found ? 'Found, not crafted' : 'Not crafted';
}
const noteRecent = type => { const r = [type, ...(LS.get('recentItems', []) || []).filter(t => t !== type)].slice(0, 8); LS.set('recentItems', r); };
const mountIcon = it => { const m = mountOf(it); return h('span', { class: 'mnt', title: MOUNTS[m], html: svg(ICON[m === 'door' || m === 'window' ? m : m === 'wall' ? 'wall' : m === 'ceiling' ? 'ceiling' : 'floor']) }); };
function sizeText(it) {
  const bl = m => Math.round(m / VOXEL);
  if (it.craft && !it.measured) return '';
  return IN_WALL.has(mountOf(it)) ? `${bl(it.h)}×${bl(it.w)}` : `${fmt(it.w)}×${fmt(it.d)} m`;
}
function itemRow(base) {
  const it = libDef(base), sub = [it.by, it.region, isPlaceholder(base) ? `counts as ${placeholderFor(base) || 'a real one'}` : null].filter(Boolean).join(' · ');
  const st = it.measured ? ['ok', 'measured'] : it.craft ? ['est', 'size?'] : it.src ? ['est', 'est.'] : null;
  const reals = isPlaceholder(base) ? CRAFT.items.filter(c => c.libraryType === base.type).map(c => c.name) : [];
  const tip = [reals.length ? `Real ones: ${reals.join(', ')}` : '', it.recipe ? 'Recipe: ' + it.recipe : '',
    it.region ? `Makeable from the ${it.region}${it.regionBy ? `: ${regionChain(it.regionBy)}` : ''}` : '',
    it.comfort ? `Comfort: ${it.comfort.type} ${it.comfort.value}` : '', it.resist ? Object.entries(it.resist).map(([k, v]) => `${k[0].toUpperCase() + k.slice(1)} resistance ${v}`).join(', ') : '',
    it.holdsNothing ? 'Decorative only: it holds nothing' : '',
    it.unlock ? `Unlocks once you ${it.unlock}` : '', st ? (it.measured ? 'Size measured in game' : it.craft ? 'No size yet: you’ll be asked for one, in blocks' : 'Size is an estimate') : '',
    IN_WALL.has(mountOf(it)) ? 'Size is tall × wide, in blocks' : ''].filter(Boolean).join(' · ');
  return h('button', { class: 'librow', type: 'button', title: it.name, 'data-tip-desc': tip || null, 'aria-pressed': String(!!S.itemDef && S.itemDef.lib === base), onclick: () => armItem(base) },
    mountIcon(it),
    h('span', null, h('span', { class: 'nm', text: it.name }), sub ? h('span', { class: 'sub', text: sub }) : null),
    h('span', { class: 'fp' }, sizeText(it), st ? h('span', { class: 'tag ' + st[0], text: st[1] }) : null));
}
function renderItemsPane() {
  const pane = $('#pane-items');
  S.libOpen = S.libOpen || new Set();
  const f = S.itemFilter || 'all';
  const search = h('input', { type: 'text', placeholder: 'Find an item', 'aria-label': 'Find an item', value: S.libFilter });
  const chips = h('div', { class: 'chips' }, ...ITEM_FILTERS.map(([id, lab]) => h('button', { class: 'chip', type: 'button', 'aria-pressed': String(f === id), text: lab,
    onclick: () => { S.itemFilter = f === id && id !== 'all' ? 'all' : id; renderItemsPane(); } })));
  const libBox = h('div', { class: 'section' });
  const regionSel = h('select', { 'aria-label': 'Show items makeable up to a region', title: 'Hide items you can’t make until a later region',
    onchange: () => { LS.set('itemRegion', regionSel.value); renderItemsPane(); } },
    h('option', { value: '', text: 'Every region' }), ...GAME_REGIONS.map(r => h('option', { value: r, text: `Up to ${r.includes('’') || r.includes("'") ? '' : 'the '}${r}` })));
  regionSel.value = LS.get('itemRegion', '') || '';
  const mode = LS.get('itemGroupBy', 'category') === 'crafter' ? 'crafter' : 'category';
  const groupSeg = h('span', { class: 'seg seg-sm', role: 'group', 'aria-label': 'Group items by' },
    ...[['category', 'Category', 'Group by the kind of thing it is'], ['crafter', 'Crafter', 'Group by who or what makes it']].map(([v, t, tip]) =>
      h('button', { type: 'button', 'aria-pressed': String(mode === v), text: t, title: tip, onclick: () => { LS.set('itemGroupBy', v); renderItemsPane(); } })));
  const groups = itemGroups().map(g => ({ ...g, items: g.items.filter(withinRegion) })).filter(g => g.items.length);
  const drawLib = () => {
    const q = S.libFilter.trim().toLowerCase();
    const parts = [];
    if (f === 'measure') {                                  // everything still waiting for a size
      const placed = new Set((S.plan ? S.plan.items : []).map(i => i.type));
      const rows = groups.flatMap(g => g.items.filter(needsMeasuring)).filter(it => !q || it.name.toLowerCase().includes(q));
      rows.sort((a, b) => (placed.has(b.type) - placed.has(a.type)) || a.name.localeCompare(b.name));
      parts.push(h('div', { class: 'secthead' }, h('span', { text: `${rows.length} without a measured size` }),
        h('button', { class: 'linkbtn', type: 'button', text: 'Copy checklist', title: 'A list to take into the game: the ones in this plan first', onclick: () => copyText(measureChecklist(rows, placed), 'Measuring checklist') })),
      h('div', { class: 'liblist' }, ...rows.map(itemRow)));
      libBox.replaceChildren(...parts);
      return;
    }
    // headings (by category or by maker), each with its categories as subheadings
    const tops = new Map();
    for (const g of groups) {
      if (f !== 'all' && g.filter !== f) continue;
      for (const it of g.items) {
        const sub = subCatOf(g.cat), top = mode === 'crafter' ? makerOf(it, g.cat) : topCatOf(g.cat);
        if (q && !(it.name.toLowerCase().includes(q) || sub.toLowerCase().includes(q) || top.toLowerCase().includes(q))) continue;
        if (!tops.has(top)) tops.set(top, new Map());
        const subs = tops.get(top);
        if (!subs.has(sub)) subs.set(sub, { items: [], note: mode === 'category' ? g.note : null, kind: topCatOf(g.cat) });
        subs.get(sub).items.push(it);
      }
    }
    const tail = n => ITEM_TAIL.indexOf(n);
    for (const top of [...tops.keys()].sort((a, b) => (tail(a) - tail(b)) || a.localeCompare(b))) {
      // (by maker, a maker's categories sit with their kind: its lights together, then its structure, and so on)
      const subs = [...tops.get(top)].sort((a, b) => (mode === 'crafter' ? a[1].kind.localeCompare(b[1].kind) : 0) || a[0].localeCompare(b[0]));
      const n = subs.reduce((t, [, x]) => t + x.items.length, 0);
      const d = h('details', { class: 'catgroup' }, h('summary', null, `${top} (${n})`));
      const fill = () => {
        if (d.dataset.filled) return;
        d.dataset.filled = '1';
        for (const [name, x] of subs) d.append(...[subs.length > 1 || name !== top ? h('div', { class: 'libsub', text: `${name} (${x.items.length})` }) : null,
          x.note ? h('p', { class: 'note', text: x.note }) : null, h('div', { class: 'liblist' }, ...x.items.map(itemRow))].filter(Boolean));
      };
      const key = mode + ':' + top;
      if (q || (f !== 'all' && tops.size <= 3) || S.libOpen.has(key)) { d.open = true; fill(); }
      d.addEventListener('toggle', () => { if (d.open) { S.libOpen.add(key); fill(); } else S.libOpen.delete(key); });
      parts.push(d);
    }
    libBox.replaceChildren(...(parts.length ? parts : [h('p', { class: 'note', text: 'Nothing matches that.' })]));
  };
  search.addEventListener('input', () => { S.libFilter = search.value; drawLib(); });
  drawLib();
  // recently placed, one click to pick up again
  const recent = (LS.get('recentItems', []) || []).map(t => LIB_BY_TYPE[t]).filter(Boolean);
  const recentBox = recent.length ? h('div', { class: 'section' }, h('div', { class: 'secthead' }, h('span', { text: 'Recent' })),
    h('div', { class: 'chips' }, ...recent.map(it => h('button', { class: 'chip', type: 'button', 'aria-pressed': String(!!S.itemDef && S.itemDef.lib === it), text: it.name, onclick: () => armItem(it) })))) : null;
  const cName = h('input', { type: 'text', value: 'Custom item', maxlength: '40', 'aria-label': 'Name' });
  const cW = h('input', { type: 'number', value: '2', min: '0.5', max: '64', step: '0.5', 'aria-label': 'Width in metres' });
  const cD = h('input', { type: 'number', value: '2', min: '0.5', max: '64', step: '0.5', 'aria-label': 'Depth in metres' });
  const cH = h('input', { type: 'number', value: '1', min: '0.5', max: '40', step: '0.5', 'aria-label': 'Height in metres' });
  const cC = h('input', { type: 'color', value: '#8a7a6a', 'aria-label': 'Colour' });
  const custom = h('details', null, h('summary', { text: 'Custom item' }), h('div', { class: 'inner' },
    h('label', { class: 'field' }, h('span', { text: 'Name' }), cName),
    h('div', { class: 'grid3' }, h('label', { class: 'field' }, h('span', { text: 'Width' }), cW), h('label', { class: 'field' }, h('span', { text: 'Depth' }), cD), h('label', { class: 'field' }, h('span', { text: 'Height' }), cH)),
    h('div', { class: 'row' }, cC, h('button', { class: 'btn btn-accent btn-sm', type: 'button', text: 'Place it', onclick: () => armItem({ type: 'custom', name: str(cName.value, 40) || 'Custom item', w: num(cW.value, 2, 0.5, 64), d: num(cD.value, 2, 0.5, 64), h: num(cH.value, 1, 0.1, 40), color: cC.value }) }))));
  pane.replaceChildren(...[
    h('div', { class: 'pane-head' }, h('h3', { text: 'Items' }),
      h('button', { class: 'iconbtn sm btn-ghost', type: 'button', title: 'Where items and sizes come from', 'aria-expanded': String(!!S.itemsHelp), html: svg(ICON.info), onclick: () => { S.itemsHelp = !S.itemsHelp; renderItemsPane(); } })),
    S.itemsHelp ? h('p', { class: 'note srcnote' }, 'Chest and station names, crafters, slots and recipes come from the ', h('a', { href: WIKI + 'Storage', target: '_blank', rel: 'noopener', text: 'Enshrouded wiki' }),
      '; everything else is every building item in 1.0 (crafting data from enshrouded.tools). Each shows the first region where you could make it; “Show” hides later ones, and “Group by” lists them by kind or by who makes them. Nobody publishes sizes: “est.” is a guess, “size?” asks you in blocks the first time, and “measured” is from the game. Click to stamp, R turns it (a door or window flips), and the thick edge is the front. Doors and windows snap into the wall under the cursor; wall items hang on the nearest wall.') : null,
    h('div', { class: 'libsearch' }, search, h('div', { class: 'libopts' }, h('label', { class: 'regionpick' }, h('span', { text: 'Show' }), regionSel),
      h('span', { class: 'groupby' }, h('span', { text: 'Group by' }), groupSeg)), chips),
    S.plan ? placedSummary() : null,
    f === 'all' && !S.libFilter.trim() ? recentBox : null,
    libBox, custom,
  ].filter(Boolean));
}
function measureChecklist(rows, placed) {
  const line = it => `- [ ] ${it.name}${it.by ? ` (${it.by})` : ''}: ${IN_WALL.has(mountOf(it)) ? 'tall × wide' : 'wide × deep × tall'} in blocks`;
  const a = rows.filter(it => placed.has(it.type)), b = rows.filter(it => !placed.has(it.type));
  return ['Enshrouded items to measure', '', ...(a.length ? ['In this plan:', ...a.map(line), ''] : []), 'Everything else:', ...b.map(line)].join('\n');
}
// "Placed in this plan": every item, grouped by name, each one a click away on the plan.
function placedSummary() {
  const P = S.plan, n = P.items.length;
  const box = h('div', { class: 'section placedbox' });
  const head = h('div', { class: 'secthead' }, h('span', { id: 'placedCount', text: `Placed in this plan · ${n}` }),
    n ? h('button', { class: 'linkbtn', type: 'button', 'aria-expanded': String(!!S.showPlaced), text: S.showPlaced ? 'Hide list' : 'Show list', onclick: () => { S.showPlaced = !S.showPlaced; renderItemsPane(); } }) : null);
  box.append(head);
  if (S.showPlaced && n) {
    const by = new Map();
    for (const it of P.items) { if (!by.has(it.label)) by.set(it.label, []); by.get(it.label).push(it); }
    S.placedOpen = S.placedOpen || new Set();
    const L = lv();
    box.append(h('ul', { class: 'plainlist' }, ...[...by.entries()].sort((a, b) => b[1].length - a[1].length || a[0].localeCompare(b[0])).map(([label, its]) => {
      const open = S.placedOpen.has(label), here = its.filter(i => L && i.level === L.id).length;
      return h('li', null,
        h('button', { class: 'placed', type: 'button', 'data-items': its.map(i => i.id).join(','), 'aria-expanded': String(open), onclick: () => { if (open) S.placedOpen.delete(label); else S.placedOpen.add(label); renderItemsPane(); } },
          h('span', { text: label }), h('span', { text: `×${its.length}${here && here < its.length ? ` · ${here} here` : ''}` })),
        open ? h('ul', { class: 'plainlist sub' }, ...its.map(it => {
          const Lv = P.levels.find(l => l.id === it.level);
          return h('li', null, h('button', { class: 'placed small', type: 'button', 'data-items': it.id, title: 'Select it on the plan', onclick: () => selectItemOnPlan(it) },
            h('span', { text: Lv ? Lv.name : '?' }), h('span', { text: `x ${metres(it.x)} · y ${metres(it.y)} m` })));
        })) : null);
    })));
  }
  return box;
}
function selectItemOnPlan(it) {
  const i = S.plan.levels.findIndex(l => l.id === it.level);
  if (i >= 0 && i !== S.levelIdx) { if (layerOn()) setLayerMode(false); setLevel(i); }
  S.sel = { type: 'item', id: it.id }; setTool('select'); renderInspector();
  const R = itemRect(it), s = S.cam.s;
  if (W2 && H2) { S.cam.ox = W2 / 2 - (R.x + R.w / 2) * s; S.cam.oy = H2 / 2 - (R.y + R.h / 2) * s; }
  req2d();
}
// After edits: keep the placed count (and the open list) up to date.
function renderPlacedList() {
  const el = $('#placedCount');
  if (el && S.plan) el.textContent = `Placed in this plan · ${S.plan.items.length}`;
  if (S.showPlaced && !$('#pane-items').hidden) renderItemsPane();
}

// ---- the quick finder: / then type, Enter to paint or place with it. Results come under headings (planner v64):
// commands, levels and areas, this plan's materials, items, blocks to add. The heading with the best match comes
// first; each shows its top few and a "Show all" row. Chips (or Tab) narrow it to one kind.
const FIND_SECS = [['cmd', 'Commands'], ['place', 'Levels and areas'], ['mat', 'Materials in this plan'], ['item', 'Items'], ['block', 'Blocks to add']];
const FIND_CHIPS = [['all', 'All'], ['cmd', 'Commands'], ['place', 'Places'], ['mat', 'Materials'], ['item', 'Items'], ['block', 'Blocks']];
function openFinder() {
  if (!S.plan) return;
  const P = S.plan, inPlan = new Set(Object.values(P.palette).map(e => e.name + '|' + e.kind));
  const all = [];
  for (const [k, e] of Object.entries(P.palette)) all.push({ sec: 'mat', label: e.name, sub: KINDS[e.kind].label, color: e.color, sym: k, go: () => { openTab('materials'); pickBrush(k); } });
  for (const b of BLOCKS) {
    const kind = b.g === 'Roofs' ? 'roof' : b.k === 'floor' ? 'floor' : 'wall';
    if (!inPlan.has(b.n + '|' + kind)) all.push({ sec: 'block', label: b.n, sub: [b.g, blockRegion(b), `add as a ${kind}`].filter(Boolean).join(' · '), color: b.c, go: () => { addCatalogueBlock(b, kind); openTab('materials'); } });
  }
  for (const g of itemGroups()) for (const it of g.items) {
    const d = libDef(it);
    all.push({ sec: 'item', label: it.name, sub: [subCatOf(g.cat), d.by, d.region].filter(Boolean).join(' · '), color: it.color, go: () => { openTab('items'); armItem(it); } });
  }
  // commands (with their keys), levels and areas by name
  for (const c of paletteCommands()) all.push({ sec: 'cmd', label: c.label, sub: 'Command', key: c.key, cmd: true, go: () => { noteCommand(c.label); c.run(); } });
  P.levels.forEach((L, i) => { if (!trimParent(L)) all.push({ sec: 'place', label: L.name, sub: `Level · ${fmt(L.elev)} to ${fmt(L.elev + L.height)} m · ${levelGroup(L)}`, color: T.muted, go: () => { if (layerOn()) setLayerMode(false); setLevel(i); } }); });
  for (const z of P.zones) {
    const L = P.levels.find(l => l.id === z.level);
    all.push({ sec: 'place', label: z.name, sub: `Area · ${L ? L.name : ''}`, color: z.color, go: () => { if (layerOn()) setLayerMode(false); if (L) setLevel(P.levels.indexOf(L)); S.sel = { type: 'zone', id: z.id }; centreOn(z.x, z.y, z.w, z.h); renderInspector(); } });
  }
  const recent = (LS.get(RECENT_CMDS, []) || []).map(l => all.find(r => r.cmd && r.label === l)).filter(Boolean);
  const input = h('input', { type: 'text', placeholder: 'Type a command, level, area, material, block or item', 'aria-label': 'Find or do anything', autocomplete: 'off' });
  const chipBox = h('div', { class: 'chips finder-chips', role: 'tablist', 'aria-label': 'Show' });
  const list = h('ul', { class: 'finder', role: 'listbox' });
  let hits = [], at = 0, only = 'all', counts = {};
  const score = (q, s) => { const l = s.toLowerCase(); if (l.startsWith(q)) return 0; if (l.includes(' ' + q)) return 1; if (l.includes(q)) return 2; const words = q.split(/\s+/).filter(Boolean); return words.length > 1 && words.every(w => l.includes(w)) ? 3 : -1; };
  const best = (q, r) => { const a = score(q, r.label), b = r.cmd ? score(q, r.label.replace(/^[^:]+:\s*/, '')) : -1; return a < 0 ? b : b < 0 ? a : Math.min(a, b); };   // (a command matches with or without its "Camera:" part)
  const row = (r, i) => h('li', { role: 'option', 'aria-selected': String(i === at) },
    h('button', { type: 'button', class: 'finder-row' + (r.more ? ' more' : ''), onclick: () => pick(r), onmousemove: () => { if (at !== i) { at = i; mark(); } } },
      r.more ? h('span', { class: 'cmdmark', 'aria-hidden': 'true', text: '…' }) : r.cmd ? h('span', { class: 'cmdmark', 'aria-hidden': 'true', text: '›' })
        : h('span', { class: 'swatch sm', style: `background:${r.color};color:${textOn(r.color)}`, text: r.sym ? symText(r.sym) : '' }),
      h('span', null, h('span', { class: 'nm', text: r.label }), r.sub ? h('span', { class: 'sub', text: r.sub }) : null),
      r.key ? h('kbd', { text: r.key }) : null));
  const draw = () => {
    const q = input.value.trim().toLowerCase();
    const bySec = new Map(FIND_SECS.map(([id]) => [id, []]));
    if (q) for (const r of all) { const s = best(q, r); if (s >= 0) bySec.get(r.sec).push([s, r]); }
    else { bySec.set('cmd', recent.map(r => [0, r])); bySec.set('mat', all.filter(r => r.sec === 'mat').slice(0, 12).map(r => [0, r])); }
    for (const v of bySec.values()) v.sort((a, b) => a[0] - b[0] || a[1].label.localeCompare(b[1].label));
    chipBox.replaceChildren(...FIND_CHIPS.map(([id, lab]) => {
      const n = id === 'all' ? [...bySec.values()].reduce((t, v) => t + v.length, 0) : bySec.get(id).length;
      counts[id] = n;
      return h('button', { class: 'chip', type: 'button', role: 'tab', 'aria-pressed': String(only === id), 'aria-selected': String(only === id), text: q && id !== 'all' ? `${lab} ${n}` : lab,
        onclick: () => { only = id; at = 0; draw(); input.focus(); } });
    }));
    // the heading with the best match first (an empty box keeps the fixed order)
    const secs = FIND_SECS.filter(([id]) => (only === 'all' || only === id) && bySec.get(id).length)
      .sort((a, b) => (q ? bySec.get(a[0])[0][0] - bySec.get(b[0])[0][0] : 0) || FIND_SECS.indexOf(a) - FIND_SECS.indexOf(b));
    const per = only === 'all' ? (q ? 5 : 12) : 200, out = [];
    hits = [];
    for (const [id, label] of secs) {
      const v = bySec.get(id);
      out.push(h('li', { class: 'finder-head', role: 'presentation', text: `${q ? '' : id === 'cmd' ? 'Recent ' : ''}${q || id !== 'cmd' ? label : 'commands'}${q ? ` · ${v.length}` : ''}` }));
      for (const [, r] of v.slice(0, per)) { out.push(row(r, hits.length)); hits.push(r); }
      if (v.length > per && only === 'all') { const m = { more: true, label: `Show all ${v.length} ${label.toLowerCase()}`, go: () => { only = id; at = 0; draw(); } }; out.push(row(m, hits.length)); hits.push(m); }
      else if (v.length > per) out.push(h('li', { class: 'note', text: `The first ${per} of ${v.length}: type more to narrow it down.` }));
    }
    at = Math.min(at, Math.max(0, hits.length - 1));
    list.replaceChildren(...(out.length ? out : [h('li', { class: 'note', text: 'Nothing matches that.' })]));
  };
  const mark = () => list.querySelectorAll('[role="option"]').forEach((li, i) => li.setAttribute('aria-selected', String(i === at)));
  const pick = r => { if (r.more) { r.go(); input.focus(); return; } closeModal(); r.go(); };
  input.addEventListener('input', () => { at = 0; draw(); });
  input.addEventListener('keydown', e => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); at = clamp(at + (e.key === 'ArrowDown' ? 1 : -1), 0, Math.max(0, hits.length - 1)); mark(); const li = list.querySelectorAll('[role="option"]')[at]; if (li) li.scrollIntoView({ block: 'nearest' }); }
    else if (e.key === 'Enter' && hits[at]) { e.preventDefault(); pick(hits[at]); }
    else if (e.key === 'Tab') {                               // Tab and Shift+Tab step through the chips with matches
      e.preventDefault();
      let k = FIND_CHIPS.findIndex(([id]) => id === only);
      for (let n = 0; n < FIND_CHIPS.length; n++) {
        k = (k + (e.shiftKey ? FIND_CHIPS.length - 1 : 1)) % FIND_CHIPS.length;
        if (FIND_CHIPS[k][0] === 'all' || counts[FIND_CHIPS[k][0]]) break;
      }
      only = FIND_CHIPS[k][0]; at = 0; draw();
    }
  });
  draw();
  openModal('Find or do anything', [input, chipBox, h('p', { class: 'note', text: 'Commands (with their keys), levels and areas, materials in this plan, items, and every block in the game. ↑ ↓ to move, Enter to pick, Tab to show one kind. ? lists every shortcut.' }), list], [{ label: 'Close', onClick: closeModal }]);
}

// ---- the panel's size: drag its edge (double-click resets), kept in this browser. Beside the sheet it's the left edge
// and the width; in a tall window (TALL_MQ, where the panel runs along the bottom) it's the top edge and the height.
const TALL_MQ = '(max-aspect-ratio: 3/4) and (min-width: 861px)';
(function panelSize() {
  const grip = $('#panelGrip'), root = document.documentElement, tall = window.matchMedia(TALL_MQ);
  const applyW = w => { root.style.setProperty('--panel-w', Math.round(w) + 'px'); };
  const applyH = v => { root.style.setProperty('--panel-h', Math.round(v) + 'px'); };
  const savedW = Number(LS.get('panelW', 0)), savedH = Number(LS.get('panelH', 0));
  if (savedW) applyW(savedW);
  if (savedH) applyH(savedH);
  if (!grip) return;
  const tip = () => { grip.removeAttribute('title'); grip.dataset.tip = tall.matches ? 'Drag to make the panel taller' : 'Drag to widen the panel'; };
  tip(); tall.addEventListener('change', tip);
  let drag = null;
  const relayout = () => { resize2d(); if (S.view !== '2d' && typeof resize3d === 'function' && V3.ok) resize3d(); req2d(); };
  grip.addEventListener('pointerdown', e => {
    const r = $('#panel').getBoundingClientRect();
    drag = { tall: tall.matches, x: e.clientX, y: e.clientY, size: tall.matches ? r.height : r.width };
    try { grip.setPointerCapture(e.pointerId); } catch { /* not a live pointer */ } e.preventDefault();
  });
  grip.addEventListener('pointermove', e => {
    if (!drag) return;
    if (drag.tall) applyH(clamp(drag.size + (drag.y - e.clientY), 180, Math.max(240, window.innerHeight * 0.7)));
    else applyW(clamp(drag.size + (drag.x - e.clientX), 280, Math.max(320, Math.min(720, window.innerWidth * 0.55))));
    relayout();
  });
  const end = () => {
    if (!drag) return;
    const r = $('#panel').getBoundingClientRect();
    LS.set(drag.tall ? 'panelH' : 'panelW', Math.round(drag.tall ? r.height : r.width)); drag = null;
  };
  grip.addEventListener('pointerup', end); grip.addEventListener('pointercancel', end);
  grip.addEventListener('dblclick', () => {
    if (tall.matches) { root.style.removeProperty('--panel-h'); LS.set('panelH', 0); }
    else { root.style.removeProperty('--panel-w'); LS.set('panelW', 0); }
    relayout();
  });
})();
