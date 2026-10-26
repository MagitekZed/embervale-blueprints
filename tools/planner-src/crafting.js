
// ---------------------------------------------------------------------------
// Crafting list: pick what to craft and how many, and get a shopping list of the resources with where each
// comes from (the station that makes it, or the region it's gathered in), and the stations and crafters
// you'll need. A quantity is a number of crafts, so a stack of ammo counts once. Recipes come from craft.js
// (generated from tools/craft-src). The list is saved in the database (meta/craft), so it's the same on every
// device. What you already have comes from the Inventory tab (inventory.js, planner v68), which is the only place
// counts change; here they're shown, and resources count only what's still to make.
// ---------------------------------------------------------------------------
let craftDoc = { list: {} }, craftLegacyHave = null;
const craftUI = { q: '', cat: 'all', open: null, raw: false, openRow: null };
let craftBox = null, craftSaveT = 0;
const craftData = () => (typeof CRAFT === 'object' && CRAFT ? CRAFT : { items: [], resources: {} });
const craftItem = name => craftData().items.find(i => i.name === name);
function onCraftDoc(d) {
  const ok = o => (o && typeof o === 'object' ? o : {});
  craftDoc = { list: { ...ok(d && d.list) } };
  craftLegacyHave = d && d.have && typeof d.have === 'object' ? d.have : null;   // (counts from before the inventory)
  invLegacy(craftLegacyHave);
  if (craftBox && craftBox.isConnected) renderCraft();
}
function saveCraft() {
  clearTimeout(craftSaveT);
  craftSaveT = setTimeout(() => {
    if (!S.store || S.readOnly) return;
    // (the old `have` is written back untouched, so nothing is lost if the inventory hasn't taken it over yet)
    S.store.saveDoc('meta/craft', { list: craftDoc.list, ...(craftLegacyHave ? { have: craftLegacyHave } : {}), updatedAt: Date.now() })
      .catch(() => toast('Couldn’t save the crafting list. Try again.', 'bad'));
  }, 400);
}
const clampQty = n => Math.max(0, Math.min(9999, Math.round(Number(n)) || 0));
function setCraftQty(name, n) { n = clampQty(n); if (n) craftDoc.list[name] = n; else delete craftDoc.list[name]; saveCraft(); renderCraft(); }
// What's still to make of something on the list: the units the crafts on the list make, less what you have.
function craftLeft(name) {
  const it = craftItem(name), makes = it && it.makes > 1 ? it.makes : 1, crafts = craftDoc.list[name] || 0;
  const need = crafts * makes, have = invHave(name), left = Math.max(0, need - have);
  return { name, it, makes, crafts, need, have, left, leftCrafts: Math.ceil(left / makes) };
}

// Everything the list still needs: resources totalled for the crafts still to make (what you already have of an
// item isn't made again), the stations (with their crafters and what they need), and, with "break down" on,
// crafted parts swapped for what they're made from (rounded up to whole crafts).
function craftTotals(breakDown) {
  const data = craftData(), res = data.resources || {}, need = new Map(), stations = new Map(), parts = new Map();
  const add = (item, qty) => need.set(item, (need.get(item) || 0) + qty);
  const station = (name, crafter, requires, forWhat) => {
    if (!name && crafter) name = `${crafter}’s own menu`;      // (no station: the crafter makes it)
    if (!name) return;
    const s = stations.get(name) || { name, crafter, requires: new Set(), for: new Set() };
    for (const r of requires || []) s.requires.add(r);
    s.for.add(forWhat); stations.set(name, s);
  };
  for (const name of Object.keys(craftDoc.list)) {
    const L = craftLeft(name), it = L.it;
    if (!it || !L.leftCrafts) continue;
    station(it.station, it.crafter, it.requires, name);
    for (const i of it.inputs || []) add(i.item, i.qty * L.leftCrafts);
  }
  // With "break down" on, crafted parts are made from what they're made of, each part's whole need at once
  // (parts nearer the top first, so every use of a part is counted before it's broken down), using the parts
  // you already hold first: those show as needed and covered, and only the rest is broken down.
  if (breakDown) {
    const isPart = it => !!(res[it] && res[it].recipe && (res[it].recipe.inputs || []).length), depth = new Map();
    const visit = (it, d) => { if (!isPart(it) || d > 12 || (depth.has(it) && depth.get(it) >= d)) return; depth.set(it, d); for (const i of res[it].recipe.inputs) visit(i.item, d + 1); };
    for (const it of [...need.keys()]) visit(it, 0);
    for (const it of [...depth.keys()].sort((a, b) => depth.get(a) - depth.get(b))) {
      const qty = need.get(it) || 0;
      if (!qty) continue;
      const r = res[it].recipe, take = Math.min(qty, invHave(it));
      if (take) need.set(it, take); else need.delete(it);
      const rest = qty - take;
      if (rest <= 0) continue;
      const runs = Math.ceil(rest / (r.makes || 1));
      parts.set(it, runs);
      station(r.station, r.crafter, r.requires, it);
      for (const i of r.inputs) add(i.item, i.qty * runs);
    }
  }
  return { need, stations, parts };
}

// ---------------------------------------------------------------------------
// The smart count (planner v51): for something the plan needs, what's in your inventory, how much more you could
// craft right now from what you have (following the whole chain through parts, in whole crafts), and what's
// still to gather to finish. Every count is against everything you have, so two blocks made of the same
// Stone both show what they could make; when you craft one and update the counts, the rest follow.
// ---------------------------------------------------------------------------
function recipeFor(name) {
  const it = craftItem(name);
  if (it && (it.inputs || []).length) return { inputs: it.inputs, makes: it.makes || 1 };
  const r = (craftData().resources || {})[name];
  return r && r.recipe && (r.recipe.inputs || []).length ? { inputs: r.recipe.inputs, makes: r.recipe.makes || 1 } : null;
}
const haveStock = () => invStock();
// What making the things in `gross` (Map: name -> how many) takes from `stock` (a Map, used up), crafting what's
// missing: { short: raw materials still short, runs: crafts per thing made (the targets and the parts on the
// way) }. Each part's whole need is worked out before it's crafted, nearest the top first; `skip` names things
// whose own stock doesn't count (a target's finished ones). Water charges never run short.
function resolveNeeds(gross, stock, skip) {
  const depth = new Map();
  const visit = (it, d) => { if (d > 12 || (depth.has(it) && depth.get(it) >= d)) return; depth.set(it, d); const r = recipeFor(it); if (r) for (const i of r.inputs) if (!i.water) visit(i.item, d + 1); };
  for (const it of gross.keys()) visit(it, 0);
  const g = new Map(gross), short = new Map(), runs = new Map();
  for (const it of [...depth.keys()].sort((a, b) => depth.get(a) - depth.get(b))) {
    let q = g.get(it) || 0;
    if (q <= 0) continue;
    if (!skip || !skip.has(it)) { const take = Math.min(q, stock.get(it) || 0); if (take) { stock.set(it, stock.get(it) - take); q -= take; } }
    if (q <= 0) continue;
    const r = recipeFor(it);
    if (!r) { short.set(it, q); continue; }
    const n = Math.ceil(q / r.makes);
    runs.set(it, n);
    for (const i of r.inputs) if (!i.water) g.set(i.item, (g.get(i.item) || 0) + i.qty * n);
  }
  return { short, runs };
}
function smartCount(name, left) {
  const inv = invHave(name), rest = Math.max(0, left - inv), r = recipeFor(name);
  const res = { name, left, inv, rest, recipe: !!r, makes: r ? r.makes : 1, runs: 0, craftable: 0, finishes: rest === 0, gather: new Map(), parts: new Map() };
  if (!rest) return res;
  if (!r) { res.gather.set(name, rest); return res; }
  const base = haveStock();
  base.delete(name);                                          // (finished ones are the inventory, counted above)
  const need = Math.ceil(rest / r.makes);
  const skip = new Set([name]);
  const tryRuns = n => { const out = resolveNeeds(new Map([[name, n * r.makes]]), new Map(base), skip); out.runs.delete(name); return out; };
  const all = tryRuns(need);
  res.parts = all.runs;
  if (!all.short.size) { res.runs = need; res.finishes = true; }
  else {
    let lo = 0, hi = need - 1;                                 // the most whole crafts you can make now
    while (lo < hi) { const mid = Math.ceil((lo + hi) / 2); if (!tryRuns(mid).short.size) lo = mid; else hi = mid - 1; }
    res.runs = lo; res.gather = all.short;
  }
  res.craftable = res.runs * r.makes;
  return res;
}
// The ingredients a thing's chain uses, with how much one craft takes: [{ item, qty, depth }].
function chainOf(name, depth = 0, mult = 1, out = [], seen = new Set()) {
  const r = depth < 6 ? recipeFor(name) : null;
  if (!r) return out;
  for (const i of r.inputs) {
    if (i.water) continue;
    out.push({ item: i.item, qty: i.qty * mult, depth });
    const sub = recipeFor(i.item);
    if (sub && !seen.has(i.item)) { seen.add(i.item); chainOf(i.item, depth + 1, i.qty * mult / sub.makes, out, seen); }
  }
  return out;
}
// The items the open plan still needs placed (the Build tab's items), by the crafting list's names.
function planItemNeeds() {
  const P = S.plan, byName = new Map(), byType = new Map(), out = new Map();
  for (const it of craftData().items) { byName.set(it.name, it); if (it.catalogueName) byName.set(it.catalogueName, it); if (it.libraryType && it.primary) byType.set(it.libraryType, it); }
  for (const it of P.items) {
    if (it.type === 'spawn' || it.type.startsWith('npc-')) continue;
    const d = LIB_BY_TYPE[it.type], c = byType.get(it.type) || (d && d.craft ? byName.get(d.name) : null) || byName.get(it.label);
    const name = c ? c.name : (d ? d.name : it.label), placed = typeof PROG === 'object' && PROG.items.has(itemKey(it));
    const n = out.get(name) || { name, total: 0, left: 0, craft: !!c };
    n.total++; if (!placed) n.left++;
    out.set(name, n);
  }
  return [...out.values()].sort((a, b) => b.left - a.left || a.name.localeCompare(b.name));
}
const craftSource = item => {
  const r = craftData().resources[item];
  if (!r) return '';
  const alt = r.alt && (r.alt.station || r.alt.crafter);        // gathered, but also craftable somewhere
  return (r.source || (r.note ? 'see note' : '')) + (alt ? ` (or craft at the ${alt})` : '');
};
const craftNote = item => { const r = craftData().resources[item]; return r && r.note ? r.note : ''; };
// Where to go for a resource: the region its source names first (Springlands to Cinder's Cradle, the Blackmire,
// the Hollow Halls), "Anywhere" for things found all over; a crafted one goes by its station.
const REGIONS = ['Springlands', 'Revelwood', 'Blackmire', 'Nomad Highlands', 'Kindlewastes', 'Albaneve Summits', 'Veilwater Basin', "Cinder's Cradle", 'Hollow Halls'];
function regionOf(item) {
  const src = craftSource(item) || '';
  if (craftKind(item) === 'crafted') return 'Make at ' + (src || 'a station');
  let best = null, at = Infinity;
  for (const r of REGIONS) { const i = src.indexOf(r); if (i >= 0 && i < at) { at = i; best = r; } }
  return 'Gather · ' + (best || 'Anywhere');
}
const regionRank = g => (g.startsWith('Make') ? 100 : g.endsWith('Anywhere') ? 0 : 1 + REGIONS.findIndex(r => g.endsWith(r)));
const craftKind = item => { const r = craftData().resources[item]; return r ? r.kind || '' : ''; };

function openCrafting() {
  craftBox = h('div', { class: 'craft' });
  openModal('Crafting list', [craftBox], [
    { label: 'Copy as text', primary: true, onClick: () => copyText(craftListText(), 'Crafting list') },
    { label: 'Clear the list', onClick: () => { if (!Object.keys(craftDoc.list).length) return; craftDoc.list = {}; saveCraft(); renderCraft(); } },
    { label: 'Close', onClick: closeModal },
  ]);
  document.querySelector('#modal .modal').classList.add('wide', 'xwide');
  renderCraft();
  // (after openModal's own focus, which lands on "Copy as text" and scrolled the dialog to the bottom)
  setTimeout(() => { const q = craftBox.querySelector('.craft-search'); if (q) q.focus({ preventScroll: true }); craftBox.parentElement.scrollTop = 0; }, 0);
}
// The category picker groups the categories under headings (planner v55): groups and the categories in them run
// alphabetically, and each group with more than one category can be picked whole ("g:<group>"). Categories of new
// catalogue batches land in a decoration heading unless named here or in one of the batch sets. Storage is only
// what holds items; Displays what shows them. Decorations split into five headings (planner v60).
const CRAFT_GROUP_OF = { 'Chests': 'Storage', 'Magic chests': 'Storage',
  'Crafting stations': 'Base and stations', 'Base & furniture': 'Base and stations', 'Sparkworks': 'Base and stations', 'Water': 'Base and stations',
  'Kitchen stations': 'Base and stations', 'Station parts': 'Base and stations', 'Buff shrines': 'Base and stations',
  'Building tools': 'Tools and bundles', 'Reward bundles': 'Tools and bundles', 'Survivors': 'Survivors',
  'Eternal spells': 'Eternal spells and arrows', 'Eternal arrows': 'Eternal spells and arrows', 'Doors': 'Structure', 'Windows': 'Structure' };
const DECOR_GROUP_OF = Object.fromEntries([
  ['Decor · Containers', ['Barrels and crates', 'Baskets', 'Cabinets and cupboards', 'Shelves', 'Vases, pots and urns']],
  ['Decor · Kitchen and table', ['Tableware', 'Kitchenware']],
  ['Decor · Plants and garden', ['Plants', 'Plant pots', 'Farm decor', 'Wall flowers and wreaths']],
  ['Decor · Wall art and textiles', ['Banners and flags', 'Paintings', 'Tapestries', 'Rugs and mats', 'Emblems', 'Signs']],
].flatMap(([g, cs]) => cs.map(c => [c, g])));
function craftGroup(cat) {
  if (CRAFT_GROUP_OF[cat]) return CRAFT_GROUP_OF[cat];
  if (BUILD_CATS.has(cat)) return 'Building materials';
  if (LIGHT_CATS.has(cat)) return 'Lights';
  if (STORAGE_CATS.has(cat)) return 'Storage';
  if (DISPLAY_CATS.has(cat)) return 'Displays';
  if (FURNITURE_CATS.has(cat)) return 'Furniture';
  if (FARM_CATS.has(cat)) return 'Farming and animals';
  if (STATION_CATS.has(cat)) return 'Base and stations';
  if (STRUCTURE_CATS.has(cat)) return 'Structure';
  return DECOR_GROUP_OF[cat] || 'Decor · Other';
}
const alphaCmp = (a, b) => a.localeCompare(b);
function renderCraft() {
  if (!craftBox) return;
  const ticked = document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.got : null;
  const stepFocus = document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.crafts : null;
  // Redrawing replaces everything, which would throw each scroll box back to the top (ticking items off one
  // by one meant scrolling back down every time). Note where the resources table, the recipe list, the dialog and
  // the to-craft table are, and put them back after; a list that changed (a new search, category or breakdown)
  // starts at the top.
  const scrollers = () => [craftBox.querySelector('.res-wrap'), craftBox.querySelector('.craft-items'), craftBox.parentElement, craftBox.querySelector('.todo-wrap')];
  const was = scrollers().map(el => el ? [el.scrollTop, el.scrollLeft] : null);
  const listKey = `${craftUI.q}|${craftUI.cat}`, tableKey = String(craftUI.raw);
  if (craftUI.listKey !== listKey) was[1] = null;
  if (craftUI.tableKey !== tableKey) was[0] = null;
  craftUI.listKey = listKey; craftUI.tableKey = tableKey;
  const data = craftData(), cats = [...new Set(data.items.map(i => i.category))];
  const groups = new Map();                                   // group -> Map(category -> how many)
  for (const i of data.items) {
    const g = craftGroup(i.category);
    if (!groups.has(g)) groups.set(g, new Map());
    groups.get(g).set(i.category, (groups.get(g).get(i.category) || 0) + 1);
  }
  const gNames = [...groups.keys()].sort(alphaCmp);
  const qn = craftUI.q.trim().toLowerCase();
  const inCat = i => craftUI.cat === 'all' || i.category === craftUI.cat || craftUI.cat === 'g:' + craftGroup(i.category);
  const shown = data.items.filter(i => inCat(i) && (!qn || (i.name + ' ' + (i.school || '')).toLowerCase().includes(qn)))
    .sort((a, b) => gNames.indexOf(craftGroup(a.category)) - gNames.indexOf(craftGroup(b.category)) || alphaCmp(a.category, b.category));
  // ---- the picker
  const search = h('input', { class: 'craft-search', type: 'search', placeholder: 'Find something to craft', 'aria-label': 'Find a recipe', value: craftUI.q });
  search.addEventListener('input', () => { craftUI.q = search.value; renderCraft(); const s = craftBox.querySelector('.craft-search'); s.focus(); s.setSelectionRange(s.value.length, s.value.length); });
  let catSeg = null;
  if (cats.length > 1) {
    catSeg = h('select', { 'aria-label': 'Category', title: 'Show one kind of thing' }, h('option', { value: 'all', text: `Everything (${data.items.length})` }),
      ...gNames.map(g => {
        const cs = [...groups.get(g)].sort((a, b) => alphaCmp(a[0], b[0])), total = cs.reduce((t, c) => t + c[1], 0);
        return h('optgroup', { label: g },
          ...(cs.length > 1 ? [h('option', { value: 'g:' + g, text: `All ${g.toLowerCase()} (${total})` })] : []),
          ...cs.map(([c, n]) => h('option', { value: c, text: `${c} (${n})` })));
      }));
    catSeg.value = craftUI.cat;
    if (catSeg.value !== craftUI.cat) { craftUI.cat = 'all'; catSeg.value = 'all'; }
    catSeg.addEventListener('change', () => { craftUI.cat = catSeg.value; renderCraft(); });
  }
  const stepper = (it, where) => {
    const n = craftDoc.list[it.name] || 0;
    const inp = h('input', { type: 'number', min: '0', max: '9999', value: String(n), 'aria-label': `How many ${it.name}`, class: 'qty', 'data-crafts': where ? `${where}:${it.name}` : null });
    inp.addEventListener('change', () => setCraftQty(it.name, inp.value));
    return h('span', { class: 'stepper' },
      h('button', { class: 'iconbtn sm', type: 'button', 'aria-label': `One less ${it.name}`, title: 'One less', disabled: !n, onclick: () => setCraftQty(it.name, n - 1), text: '−' }),
      inp,
      h('button', { class: 'iconbtn sm', type: 'button', 'aria-label': `One more ${it.name}`, title: it.makes > 1 ? `One more craft (${it.makes} per craft)` : 'One more', onclick: () => setCraftQty(it.name, n + 1), text: '+' }));
  };
  const unsure = it => !!(it.check || (it.confidence && !['confirmed-1.0', 'likely-1.0'].includes(it.confidence)));
  const pickRows = [];
  let lastCat = null;
  for (const it of shown) {
    if (it.category !== lastCat && (craftUI.cat === 'all' || craftUI.cat.startsWith('g:')))
      pickRows.push(h('li', { class: 'craft-cat', text: craftUI.cat === 'all' ? `${craftGroup(it.category)} · ${it.category}` : it.category }));
    lastCat = it.category;
    pickRows.push(pickRow(it));
  }
  function pickRow(it) {
    const open = craftUI.open === it.name;
    const craftable = (it.inputs || []).length > 0;
    const sub = [it.level ? `level ${it.level}` : null, it.rarity, it.school, it.slots ? (/^\d+$/.test(String(it.slots)) ? `${it.slots} slots` : String(it.slots)) : null,
      !craftable ? 'no recipe in 1.0' : it.station ? `${it.station}${it.crafter ? ` (${it.crafter})` : ''}` : it.crafter ? `${it.crafter}’s menu` : 'by hand',
      it.makes > 1 ? `makes ${it.makes}` : null, it.newIn1_0 ? 'new in 1.0' : null,
      it.renamedFrom && it.renamedFrom !== it.name ? `was ${it.renamedFrom}` : null].filter(Boolean).join(' · ');
    return h('li', { class: 'craft-item' + (craftDoc.list[it.name] ? ' on' : '') },
      h('button', { class: 'craft-name', type: 'button', 'aria-expanded': String(open), title: 'Show the recipe', onclick: () => { craftUI.open = open ? null : it.name; renderCraft(); } },
        h('span', { class: 'nm', text: it.name + (unsure(it) ? ' ⚠' : '') }), h('span', { class: 'sub', text: sub })),
      craftable ? stepper(it) : h('span', { class: 'sub', text: '–' }),
      open ? h('div', { class: 'craft-recipe' },
        h('ul', { class: 'plainlist' }, ...(it.inputs || []).map(i => h('li', { title: craftNote(i.item) }, h('span', { class: 'num', text: `${i.qty} ×` }), ' ', i.water ? 'Water (charges)' : i.item, h('span', { class: 'sub', text: craftSource(i.item) ? ` · ${craftSource(i.item)}` : '' })))),
        (it.requires || []).length ? h('p', { class: 'note', text: `Needs: ${it.requires.join(', ')}` }) : null,
        it.placeholder ? h('p', { class: 'note', text: `One of the real items behind the planner’s “${it.placeholder}”.` }) : null,
        it.quest ? h('p', { class: 'note', text: `Also from a quest: ${it.quest}` }) : null,
        it.foundAt ? h('p', { class: 'note', text: `Also found at: ${[].concat(it.foundAt).join(', ')}` }) : null,
        it.note ? h('p', { class: 'note', text: it.note }) : null,
        ...(it.check || []).map(t => h('p', { class: 'note warn', text: '⚠ ' + t })),
        it.confidence === 'unknown' ? h('p', { class: 'note warn', text: 'Recipe not found yet: check it in game.' }) : it.confidence === 'pre-1.0' ? h('p', { class: 'note warn', text: 'This recipe may be from before 1.0: check it in game.' }) : null,
        (it.sources || []).length ? h('p', { class: 'note' }, 'Source: ', ...it.sources.slice(0, 2).flatMap((u, i) => [i ? ', ' : '', h('a', { href: u, target: '_blank', rel: 'noopener', text: new URL(u).hostname })])) : null) : null);
  }
  const fromPlan = S.plan ? h('span', { class: 'btnrow' },
    h('button', { class: 'btn btn-sm', type: 'button', text: 'Add from this plan', title: `Put everything “${S.plan.name}” needs on the list: its blocks (as crafts) and its chests, stations and furniture`, onclick: () => addFromPlan() }),
    h('button', { class: 'btn btn-sm', type: 'button', text: 'Materials only', title: `Put only “${S.plan.name}”’s blocks, roofs and soils on the list (as crafts)`, onclick: () => addFromPlan('materials') }),
    h('button', { class: 'btn btn-sm', type: 'button', text: 'Everything else', title: `Put only “${S.plan.name}”’s chests, stations, furniture, doors and windows on the list`, onclick: () => addFromPlan('objects') }),
    h('button', { class: 'btn btn-sm btn-accent', type: 'button', text: 'What I’m short', title: `The blocks “${S.plan.name}” still needs beyond what you have (Build tab), as crafts: with “Break down crafted parts” on, the list below is what to gather, by region`, onclick: addShortFromBuild })) : null;
  const picker = h('div', { class: 'craft-pick' },
    h('div', { class: 'craft-tools' }, search, catSeg, fromPlan),
    pickRows.length ? h('ul', { class: 'plainlist craft-items' }, ...pickRows) : h('p', { class: 'note', text: data.items.length ? 'Nothing matches that.' : 'No recipes loaded yet.' }));
  // ---- the list: what's to craft, tracked (crafts, need, what you have, what's still to make), then the
  // resources for what's still to make, by where they come from (gathered ones by region, crafted by station)
  const T = craftTotals(craftUI.raw), names = Object.keys(craftDoc.list).filter(craftItem);
  craftUI.got = craftUI.got || new Set();
  const tickBox = (key, label, tip) => {
    const t = h('input', { type: 'checkbox', checked: craftUI.got.has(key), 'aria-label': label, title: tip, 'data-got': key });
    t.addEventListener('change', () => { if (t.checked) craftUI.got.add(key); else craftUI.got.delete(key); renderCraft(); });
    return t;
  };
  const num = v => Math.ceil(v).toLocaleString(), closes = ' (this closes the list)';
  const todo = names.map(craftLeft).sort((a, b) => gNames.indexOf(craftGroup(a.it.category)) - gNames.indexOf(craftGroup(b.it.category)) || alphaCmp(a.it.category, b.it.category) || alphaCmp(a.name, b.name));
  const stillToMake = todo.filter(t => t.left).length;
  let lastTodoCat = null;
  const todoTable = todo.length ? h('table', { class: 'shop craft-table todo-table' },
    h('thead', null, h('tr', null, h('th', { text: '' }), h('th', { text: 'Item' }), h('th', { class: 'num', text: 'Crafts' }), h('th', { class: 'num', text: 'Need' }), h('th', { class: 'num', text: 'Have' }), h('th', { class: 'num', text: 'To make' }), h('th', { text: '' }))),
    h('tbody', null, ...todo.flatMap(t => {
      const out = [], it = t.it, cat = `${craftGroup(it.category)} · ${it.category}`, key = 'item:' + t.name, got = craftUI.got.has(key), open = craftUI.openRow === t.name;
      if (cat !== lastTodoCat) { lastTodoCat = cat; out.push(h('tr', { class: 'craft-src' }, h('th', { colSpan: 7, text: cat }))); }
      const maker = it.station ? `${it.station}${it.crafter ? ` (${it.crafter})` : ''}` : it.crafter ? `${it.crafter}’s menu` : (it.inputs || []).length ? 'by hand' : 'no recipe in 1.0';
      out.push(h('tr', { class: (t.left ? '' : 'done') + (got ? ' got' : '') },
        h('td', { class: 'got' }, tickBox(key, `Made the ${t.name}`, 'Tick it off as you make it')),
        h('td', null, h('button', { class: 'todo-name', type: 'button', 'aria-expanded': String(open), title: open ? 'Hide what it takes' : 'What the ones still to make take',
          onclick: () => { craftUI.openRow = open ? null : t.name; renderCraft(); } },
          h('span', { class: 'nm', text: t.name }), h('span', { class: 'sub', text: maker + (t.makes > 1 ? ` · makes ${t.makes} a craft` : '') }))),
        h('td', { class: 'num' }, stepper(it, 'todo')),
        h('td', { class: 'num', text: num(t.need) }),
        h('td', { class: 'num' }, haveBtn(t.name, closes)),
        h('td', { class: 'num', text: t.left ? num(t.left) + (t.makes > 1 ? ` (${t.leftCrafts} craft${t.leftCrafts === 1 ? '' : 's'})` : '') : '✓' }),
        h('td', null, h('button', { class: 'iconbtn sm', type: 'button', 'aria-label': `Remove ${t.name}`, title: 'Take it off the list', onclick: () => setCraftQty(t.name, 0), text: '×' }))));
      if (open) {                                            // what the ones still to make take, one level down
        const ins = (it.inputs || []).filter(i => !i.water);
        out.push(h('tr', { class: 'todo-ins' }, h('td', { colSpan: 7 },
          !ins.length ? h('p', { class: 'note', text: 'There’s no recipe for it in the 1.0 data.' })
            : t.leftCrafts ? h('table', { class: 'shop' },
              h('thead', null, h('tr', null, h('th', { text: `For the ${num(t.leftCrafts)} craft${t.leftCrafts === 1 ? '' : 's'} still to make` }), h('th', { class: 'num', text: 'Need' }), h('th', { class: 'num', text: 'Have' }), h('th', { class: 'num', text: 'Short' }))),
              h('tbody', null, ...ins.map(i => {
                const need = i.qty * t.leftCrafts, short = Math.max(0, need - invHave(i.item));
                return h('tr', { class: short ? '' : 'done' }, h('td', { text: i.item }), h('td', { class: 'num', text: num(need) }), h('td', { class: 'num' }, haveBtn(i.item, closes)), h('td', { class: 'num', text: short ? num(short) : '✓' }));
              })))
            : h('p', { class: 'note', text: 'You have them all, so nothing’s needed for it.' }))));
      }
      return out;
    }))) : null;
  const rows = [...T.need].sort((a, b) => regionRank(regionOf(a[0])) - regionRank(regionOf(b[0])) || regionOf(a[0]).localeCompare(regionOf(b[0])) || a[0].localeCompare(b[0]));   // (by where to go)
  let lastSrc = null;
  const table = rows.length ? h('table', { class: 'shop craft-table' },
    h('thead', null, h('tr', null, h('th', { text: '' }), h('th', { text: 'Resource' }), h('th', { class: 'num', text: 'Need' }), h('th', { class: 'num', text: 'Have' }), h('th', { class: 'num', text: 'Short' }), h('th', { text: 'From' }))),
    h('tbody', null, ...rows.flatMap(([item, qty]) => {
      const short = Math.max(0, qty - invHave(item)), grp = regionOf(item), got = craftUI.got.has(item);
      const out = [];
      if (grp !== lastSrc) { lastSrc = grp; out.push(h('tr', { class: 'craft-src' }, h('th', { colSpan: 6, text: grp }))); }
      out.push(h('tr', { class: (short ? '' : 'done') + (got ? ' got' : '') },
        h('td', { class: 'got' }, tickBox(item, `Got the ${item}`, 'Tick it off as you gather it')), h('td', { text: item }), h('td', { class: 'num', text: num(qty) }), h('td', { class: 'num' }, haveBtn(item, closes)),
        h('td', { class: 'num', text: short ? num(short) : '✓' }),
        h('td', { class: 'craft', text: craftSource(item) || '?', title: craftNote(item) })));
      return out;
    }))) : null;
  const stations = [...T.stations.values()];
  const toInv = h('button', { class: 'btn btn-sm', type: 'button', text: 'Update counts in the Inventory', title: 'Close the list and open the Inventory tab on everything it still needs',
    onclick: () => { closeModal(); invUI.q = ''; invUI.only = 'list'; LS.set('invOnly', 'list'); openTab('inventory'); LS.set('tab', 'inventory'); } });
  const list = h('div', { class: 'craft-list' },
    h('div', { class: 'craft-head' }, h('h4', { text: todo.length ? `To craft · ${stillToMake ? `${stillToMake} of ${todo.length} still to make` : 'all made'}` : 'To craft' }), todo.length ? toInv : null),
    todoTable ? h('div', { class: 'shopwrap todo-wrap' }, todoTable) : h('p', { class: 'note', text: 'Nothing yet. Pick recipes on the left.' }),
    todo.length ? h('p', { class: 'note', text: 'Have counts come from the Inventory tab: click one to change it there (this closes the list). What you already have isn’t made again, so the resources below are for what’s still to make.' }) : null,
    rows.length ? h('div', { class: 'craft-head' }, h('h4', { text: 'Resources' }),
      h('label', { class: 'check', title: 'Swap crafted parts (bars, charcoal…) for what they’re made from, where the recipe is known' },
        h('input', { type: 'checkbox', checked: craftUI.raw, onchange: e => { craftUI.raw = e.target.checked; renderCraft(); } }), ' Break down crafted parts')) : null,
    table ? h('div', { class: 'shopwrap res-wrap' }, table) : null,
    T.parts.size ? h('p', { class: 'note', text: 'Crafts along the way: ' + [...T.parts].map(([k, n]) => `${k} × ${n} craft${n > 1 ? 's' : ''}`).join(', ') }) : null,
    stations.length ? h('h4', { text: 'Stations' }) : null,
    stations.length ? h('ul', { class: 'plainlist craft-stations' }, ...stations.map(s => h('li', null,
      h('b', { text: s.name }), s.crafter ? ` · ${s.crafter}` : '', s.requires.size ? h('span', { class: 'sub', text: ` · needs ${[...s.requires].join(', ')}` }) : null))) : null);
  craftBox.replaceChildren(
    h('p', { class: 'note', text: data.note || '' }),
    h('div', { class: 'craft-cols' }, picker, list));
  scrollers().forEach((el, k) => { if (el && was[k]) { el.scrollTop = was[k][0]; el.scrollLeft = was[k][1]; } });
  if (ticked) { const el = craftBox.querySelector(`[data-got="${CSS.escape(ticked)}"]`); if (el) el.focus({ preventScroll: true }); }   // (so Tab and Space carry on down the list)
  if (stepFocus) { const el = craftBox.querySelector(`[data-crafts="${CSS.escape(stepFocus)}"]`); if (el) el.focus({ preventScroll: true }); }
}
// Put what the open plan needs on the list: each block material as whole crafts (at one item per 0.5 m
// block), and its chests, stations and furniture. A quantity already higher on the list stays. `only` is
// 'materials' (just the blocks) or 'objects' (just the rest: furniture, stations, doors and windows).
function addFromPlan(only) {
  const doMats = only !== 'objects', doObjs = only !== 'materials';
  if (!S.plan) return;
  const items = craftData().items, byName = new Map(), byType = new Map();
  for (const it of items) {
    byName.set(it.name, it); if (it.catalogueName) byName.set(it.catalogueName, it);
    if (it.libraryType && it.primary) byType.set(it.libraryType, it);       // the basic one of each kind
  }
  const perVox = typeof PER_VOXEL === 'number' && PER_VOXEL > 0 ? PER_VOXEL : 1, set = (it, n) => { craftDoc.list[it.name] = Math.max(craftDoc.list[it.name] || 0, n); };
  let blocks = 0, objects = 0;
  const gathered = [];
  for (const r of doMats ? blockCounts(S.plan) : []) {
    const it = byName.get(r.name);
    if (!it) { gathered.push(r.name); continue; }
    set(it, Math.ceil(Math.ceil(r.vox * perVox) / (it.makes || 1))); blocks++;
  }
  const counts = new Map();
  for (const it of doObjs ? S.plan.items : []) counts.set(it.type, (counts.get(it.type) || 0) + 1);
  for (const [type, n] of counts) {
    const d = LIB_BY_TYPE[type], it = byType.get(type) || (d && d.craft ? byName.get(d.name) : null);   // a real door, window or decoration by name
    if (it) { set(it, Math.ceil(n / (it.makes || 1))); objects++; }
  }
  // doors and windows: one per opening, for materials named after a real door or window (pick it in the
  // material's Item list); the rest are left for you to choose
  let unpicked = 0;
  for (const r of doObjs ? openingCounts(S.plan) : []) {
    const it = byName.get(r.name);
    if (it && it.opening) { set(it, r.n); objects++; } else unpicked += r.n;
  }
  saveCraft(); renderCraft();
  const mats = `${blocks} block material${blocks === 1 ? '' : 's'}`, objs = `${objects} kind${objects === 1 ? '' : 's'} of object`;
  toast(`Added ${doMats && doObjs ? `${mats} and ${objs}` : doMats ? mats : objs} from “${S.plan.name}”.`
    + (gathered.length ? ` Gathered, not crafted: ${gathered.slice(0, 4).join(', ')}${gathered.length > 4 ? '…' : ''}.` : '')
    + (unpicked ? ` ${unpicked} door and window opening${unpicked === 1 ? '' : 's'} not counted: choose the Item for each door and window material (Materials tab).` : ''));
}
// The blocks the open plan still needs beyond what you have (the Build tab's counts), as crafts on the list.
// Blocks with no recipe (gathered ones, like granite) are named instead.
function addShortFromBuild() {
  if (!S.plan) return;
  const st = buildStats(), byName = new Map(), raw = [];
  for (const it of craftData().items) { byName.set(it.name, it); if (it.catalogueName) byName.set(it.catalogueName, it); }
  let n = 0;
  for (const m of st.byMat) {
    const short = Math.max(0, Math.round(m.n - m.b) - haveOf(m.name));
    if (!short) continue;
    const it = byName.get(m.name);
    if (!it || !(it.inputs || []).length) { raw.push(`${m.name} ${short.toLocaleString()}`); continue; }
    craftDoc.list[it.name] = Math.max(craftDoc.list[it.name] || 0, Math.ceil(short / (it.makes || 1)));
    n++;
  }
  let ni = 0;
  for (const m of planItemNeeds()) {                         // items not placed yet, beyond what you hold
    const short = Math.max(0, m.left - invHave(m.name)), it = byName.get(m.name);
    if (!short || !it || !(it.inputs || []).length) continue;
    craftDoc.list[it.name] = Math.max(craftDoc.list[it.name] || 0, Math.ceil(short / (it.makes || 1)));
    ni++;
  }
  craftUI.raw = true;                                        // (broken down to what to gather)
  saveCraft(); renderCraft();
  toast(n || ni || raw.length ? `Added ${n} block${n === 1 ? '' : 's'}${ni ? ` and ${ni} item${ni === 1 ? '' : 's'}` : ''} you’re short of, as crafts${raw.length ? `. Gather as they are: ${raw.slice(0, 3).join(', ')}${raw.length > 3 ? '…' : ''}` : ''}.` : 'You have enough of every block for this plan.');
}
function craftListText() {
  const T = craftTotals(craftUI.raw), names = Object.keys(craftDoc.list).filter(craftItem);
  if (!names.length) return 'Crafting list: nothing on it yet.';
  const lines = ['Crafting list', '', 'To craft (crafts: what you have, what’s still to make):', ...names.map(n => {
    const t = craftLeft(n);
    return `  [${craftUI.got && craftUI.got.has('item:' + n) ? 'x' : ' '}] ${n} × ${t.crafts}${t.makes > 1 ? ` (${t.need})` : ''}: have ${t.have.toLocaleString()}, ${t.left ? `make ${t.left.toLocaleString()}` : 'done'}`;
  }), '', 'Resources for what’s still to make (need / short), by where they come from:'];
  const by = new Map();                                      // gathered ones by region, crafted by station
  for (const [item, qty] of T.need) { const k = regionOf(item); if (!by.has(k)) by.set(k, []); by.get(k).push([item, qty]); }
  for (const [k, list] of [...by].sort((a, b) => regionRank(a[0]) - regionRank(b[0]) || a[0].localeCompare(b[0]))) {
    lines.push(k + ':');
    for (const [item, qty] of list) { const short = Math.max(0, qty - invHave(item)); lines.push(`  [${craftUI.got && craftUI.got.has(item) ? 'x' : ' '}] ${item}: ${qty}${short !== qty ? ` (short ${short})` : ''}`); }
  }
  const st = [...T.stations.values()];
  if (st.length) lines.push('', 'Stations:', ...st.map(s => `  ${s.name}${s.crafter ? ` (${s.crafter})` : ''}${s.requires.size ? `, needs ${[...s.requires].join(', ')}` : ''}`));
  return lines.join('\n');
}
