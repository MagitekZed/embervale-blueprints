
// ---------------------------------------------------------------------------
// The inventory (planner v68): how many you hold of everything the recipe data knows (gathered resources, crafted
// parts, blocks and every item you can make), shared by all your plans. It's the one place counts are changed:
// the Build tab and the Crafting list only read them, and a count there opens this tab on that item.
// Saved in the database as meta/inventory: { have: { <name>: count }, rev, updatedAt }. Counts used to live in
// meta/craft's `have`; the first load copies them across (`invLegacy()`).
// ---------------------------------------------------------------------------
const INV = { have: {}, ver: 0, loaded: false, doc: undefined, rev: '', legacy: null, migrated: false, saveT: 0 };
const INV_MAX = 999999;
const invUI = { q: '', only: LS.get('invOnly', 'all'), renderT: 0 };
function onInvDoc(d) {
  INV.loaded = true; INV.doc = d;
  if (d && d.rev && d.rev === INV.rev) return;                // (our own save coming back)
  INV.have = { ...(d && d.have && typeof d.have === 'object' ? d.have : {}) };
  invMigrate();
  invChanged(true);
}
// Counts typed before the inventory existed (meta/craft's `have`) become the inventory, once.
function invLegacy(have) { INV.legacy = have && typeof have === 'object' ? have : {}; invMigrate(); }
function invMigrate() {
  if (!INV.loaded || INV.doc || INV.migrated || !INV.legacy || !Object.keys(INV.legacy).length) return;
  INV.migrated = true;
  INV.have = { ...INV.legacy };
  saveInv(); invChanged(true);
  if (!S.readOnly) toast('Your “have” counts moved to the new Inventory tab, where they’re changed from now on.');
}
function saveInv() {
  clearTimeout(INV.saveT);
  INV.saveT = setTimeout(() => {
    if (!S.store || S.readOnly) return;
    INV.rev = Math.random().toString(36).slice(2, 10);
    S.store.saveDoc('meta/inventory', { have: INV.have, rev: INV.rev, updatedAt: Date.now() })
      .catch(() => toast('Couldn’t save the inventory. Try again.', 'bad'));
  }, 400);
}
// Everything that reads counts: the Build tab's caches and colours, the Crafting list, and this tab when the change
// came from elsewhere (another device, or the first load).
function invChanged(external) {
  INV.ver++;
  if (S.plan && typeof progHaveChanged === 'function') progHaveChanged();
  if (typeof craftBox !== 'undefined' && craftBox && craftBox.isConnected) renderCraft();
  if (external && S.tab === 'inventory') renderInventoryPane();
}
function setInv(name, n) {
  n = Math.max(0, Math.min(INV_MAX, Math.round(Number(n)) || 0));
  if ((Number(INV.have[name]) || 0) === n) return;
  if (n) INV.have[name] = n; else delete INV.have[name];
  saveInv(); invChanged(false);
  clearTimeout(invUI.renderT);                               // (badges and filters catch up once typing pauses)
  invUI.renderT = setTimeout(() => { if (S.tab === 'inventory') renderInventoryPane(); }, 700);
}

// "Any wood", "Plant Fiber or Paper Reed" and the like aren't items: a recipe takes any of several. What you hold of
// one is the sum of its options. (Stock shared between such a slot and one of its options can count twice.)
let invAnyCache = null;
function anyOf(name) {
  if (!invAnyCache) {
    invAnyCache = new Map();
    const res = craftData().resources || {}, known = n => !!res[n] || !!craftItem(n);
    for (const [k, r] of Object.entries(res)) {
      const src = r.source || '', m = /^(.+) or (.+)$/.exec(k);
      if (src.startsWith('any of: ')) invAnyCache.set(k, src.slice(8).split(',').map(s => s.trim()).filter(Boolean));
      else if (m && known(m[1]) && known(m[2])) invAnyCache.set(k, [m[1], m[2]]);
    }
  }
  return invAnyCache.get(name) || null;
}
const invCount = name => Math.max(0, Number(INV.have[name]) || 0);
const invHave = name => { const o = anyOf(name); return o ? o.reduce((t, k) => t + invCount(k), 0) : invCount(name); };
function invStock() {                                        // (for resolveNeeds, which uses it up)
  const m = new Map(Object.entries(INV.have).map(([k, v]) => [k, Number(v) || 0]));
  anyOf('');                                                  // (fills the cache)
  for (const k of invAnyCache.keys()) m.set(k, invHave(k));
  return m;
}

// Every item there's a count for: [{ name, top, sub, maker, color }]. Things you make sit under the Crafting
// list's headings and categories; resources that aren't items are gathered (by region) or crafted parts (by station).
let invCat = null;
const INV_TOP_FIRST = ['Gathered resources', 'Crafted parts', 'Building materials'];
function invCatalogue() {
  if (invCat) return invCat;
  const data = craftData(), res = data.resources || {}, out = new Map(), colour = new Map(BLOCKS.map(b => [b.n, b.c]));
  for (const it of data.items) {
    const maker = it.crafter || it.station || ((it.inputs || []).length ? 'by hand' : 'found, not crafted');
    out.set(it.name, { name: it.name, top: craftGroup(it.category), sub: it.category, maker, color: colour.get(it.name) || null });
  }
  for (const [name, r] of Object.entries(res)) {
    if (out.has(name) || r.kind === 'water' || anyOf(name)) continue;
    const crafted = craftKind(name) === 'crafted', g = regionOf(name);
    out.set(name, { name, top: crafted ? 'Crafted parts' : 'Gathered resources', sub: crafted ? g.replace(/^Make at /, '') : g.replace(/^Gather · /, ''),
      maker: craftSource(name), color: colour.get(name) || null });
  }
  invCat = [...out.values()];
  return invCat;
}
const invTopRank = t => { const i = INV_TOP_FIRST.indexOf(t); return i < 0 ? 99 : i; };
const invSubRank = (top, sub) => top === 'Gathered resources' ? (sub === 'Anywhere' ? -1 : REGIONS.indexOf(sub)) : 0;

// What a list of needs takes from the inventory, all the way down the recipes, using what you hold first:
// name -> { need, take (from what you hold), runs (crafts still to make), short (still to gather) }.
function needBreakdown(gross) {
  const depth = new Map();
  const visit = (it, d) => { if (d > 12 || (depth.has(it) && depth.get(it) >= d)) return; depth.set(it, d); const r = recipeFor(it); if (r) for (const i of r.inputs) if (!i.water) visit(i.item, d + 1); };
  for (const it of gross.keys()) visit(it, 0);
  const g = new Map(gross), stock = invStock(), out = new Map();
  for (const it of [...depth.keys()].sort((a, b) => depth.get(a) - depth.get(b))) {
    const q = g.get(it) || 0;
    if (q <= 0) continue;
    const take = Math.min(q, stock.get(it) || 0), rec = { need: q, take, runs: 0, short: 0 };
    stock.set(it, (stock.get(it) || 0) - take);
    const rest = q - take, r = rest > 0 ? recipeFor(it) : null;
    if (rest > 0 && !r) rec.short = rest;
    else if (r) { rec.runs = Math.ceil(rest / r.makes); for (const i of r.inputs) if (!i.water) g.set(i.item, (g.get(i.item) || 0) + i.qty * rec.runs); }
    out.set(it, rec);
  }
  return out;
}
// The needs behind the "This plan" and "Crafting list" filters: blocks and items still to place, or what's still
// to make on the list.
function invNeeds(which) {
  const gross = new Map(), add = (k, n) => { if (n > 0) gross.set(k, (gross.get(k) || 0) + n); };
  if (which === 'plan' && S.plan) {
    for (const m of buildStats().byMat) add(m.name, Math.round(m.n - m.b));
    for (const n of planItemNeeds()) if (n.craft) add(n.name, n.left);
  }
  if (which === 'list') for (const [name, n] of Object.entries(craftDoc.list)) { const it = craftItem(name); if (it) add(name, n * (it.makes || 1)); }
  return needBreakdown(gross);
}

function renderInventoryPane() {
  const pane = $('#pane-inventory');
  if (!pane) return;
  // a redraw keeps the scroll, and the box being typed in with what's typed so far
  const act = document.activeElement, focusName = act && act.dataset ? act.dataset.inv : null;
  const typed = focusName ? [act.value, act.selectionStart, act.selectionEnd] : null, scroll = pane.scrollTop;
  const cat = invCatalogue(), only = ['all', 'held', 'list'].includes(invUI.only) || (invUI.only === 'plan' && S.plan) ? invUI.only : 'all';
  const needs = { plan: S.plan ? invNeeds('plan') : new Map(), list: invNeeds('list') };
  const optionOf = new Map();                                 // (an option counts toward a slot like "Any wood")
  for (const which of ['plan', 'list']) for (const k of [...needs[which].keys()]) { const o = anyOf(k); if (o) for (const x of o) { if (!optionOf.has(x)) optionOf.set(x, k); if (!needs[which].has(x)) needs[which].set(x, { slot: k }); } }
  const held = cat.filter(e => invCount(e.name) > 0).length;
  const inFilter = e => only === 'all' || (only === 'held' ? invCount(e.name) > 0 : needs[only].has(e.name));
  const count = id => id === 'all' ? cat.length : id === 'held' ? held : cat.filter(e => needs[id].has(e.name)).length;
  const chips = h('div', { class: 'chips' }, ...[['all', 'All'], ['held', 'Held'], ['plan', 'This plan'], ['list', 'Crafting list']].filter(([id]) => id !== 'plan' || S.plan).map(([id, lab]) =>
    h('button', { class: 'chip', type: 'button', 'aria-pressed': String(only === id), text: `${lab} ${count(id).toLocaleString()}`,
      title: { all: 'Everything there’s a count for', held: 'What you have any of', plan: 'What this plan still needs, all the way down its recipes', list: 'What the Crafting list still needs, all the way down its recipes' }[id],
      onclick: () => { invUI.only = id; LS.set('invOnly', id); renderInventoryPane(); } })));
  const search = h('input', { type: 'search', placeholder: 'Find an item', 'aria-label': 'Find an item in the inventory', value: invUI.q, autocomplete: 'off' });
  search.addEventListener('input', () => { invUI.q = search.value; drawList(); });
  const listBox = h('div', { class: 'section invlist' });
  const badge = e => {
    if (only !== 'plan' && only !== 'list') return null;
    const r = needs[only].get(e.name);
    if (!r) return null;
    if (r.slot) return h('span', { class: 'inv-need', text: `counts toward ${r.slot}` });
    const bits = [`needs ${Math.ceil(r.need).toLocaleString()}`];
    let cls = 'ok';
    if (r.short) { bits.push(`gather ${Math.ceil(r.short).toLocaleString()}`); cls = 'short'; }
    else if (r.runs) { bits.push(`craft ${r.runs.toLocaleString()}`); cls = 'craft'; }
    else bits.push('covered');
    return h('span', { class: 'inv-need ' + cls, text: bits.join(' · ') });
  };
  const row = e => {
    const n = invCount(e.name);
    const inp = h('input', { type: 'number', min: '0', max: String(INV_MAX), class: 'qty', value: String(n), 'aria-label': `${e.name} you have`, 'data-inv': e.name, disabled: S.readOnly });
    inp.addEventListener('focus', () => inp.select());
    inp.addEventListener('change', () => setInv(e.name, inp.value));
    inp.addEventListener('keydown', ev => {                 // Enter (Shift+Enter back) moves down the list
      if (ev.key !== 'Enter') return;
      ev.preventDefault();
      const all = [...pane.querySelectorAll('[data-inv]')], k = all.indexOf(inp), next = all[k + (ev.shiftKey ? -1 : 1)];
      setInv(e.name, inp.value);
      if (next) { next.focus(); next.scrollIntoView({ block: 'nearest' }); }
    });
    return h('div', { class: 'catrow invrow' + (n ? ' held' : '') },
      e.color ? h('span', { class: 'swatch sm', style: `background:${e.color}` }) : h('span'),
      h('span', { class: 'catname' }, h('span', { class: 'nm', text: e.name }), e.maker ? h('span', { class: 'sub', text: e.maker }) : null, badge(e)),   // (its region or category is the subheading)
      inp);
  };
  function drawList() {
    const q = invUI.q.trim().toLowerCase();
    const hits = cat.filter(e => inFilter(e) && (!q || (e.name + ' ' + e.sub + ' ' + e.top).toLowerCase().includes(q)));
    const tops = new Map();
    for (const e of hits) {
      if (!tops.has(e.top)) tops.set(e.top, new Map());
      const subs = tops.get(e.top);
      if (!subs.has(e.sub)) subs.set(e.sub, []);
      subs.get(e.sub).push(e);
    }
    const flat = !!q || only !== 'all';                       // (a search or filter shows its rows open)
    const cap = 400;
    let shown = 0;
    const parts = [];
    for (const top of [...tops.keys()].sort((a, b) => invTopRank(a) - invTopRank(b) || a.localeCompare(b))) {
      const subs = [...tops.get(top)].sort((a, b) => invSubRank(top, a[0]) - invSubRank(top, b[0]) || a[0].localeCompare(b[0]));
      const n = subs.reduce((t, [, es]) => t + es.length, 0), have = subs.reduce((t, [, es]) => t + es.filter(e => invCount(e.name)).length, 0);
      const d = h('details', { class: 'catgroup' }, h('summary', null, `${top} (${have ? `${have} of ${n}` : n})`));
      const fill = () => {
        if (d.dataset.filled) return;
        d.dataset.filled = '1';
        for (const [name, es] of subs) {
          if (flat && shown >= cap) break;
          const list = es.slice().sort((a, b) => (q && b.name.toLowerCase() === q) - (q && a.name.toLowerCase() === q) || a.name.localeCompare(b.name));
          const take = flat ? list.slice(0, cap - shown) : list;
          shown += take.length;
          d.append(h('div', { class: 'libsub', text: `${name} (${es.length})` }), h('div', { class: 'catlist' }, ...take.map(row)));
        }
      };
      const key = 'inv:' + top;
      if (flat || S.invOpen.has(key) || (focusName && subs.some(([, es]) => es.some(e => e.name === focusName)))) { d.open = true; fill(); }
      d.addEventListener('toggle', () => { if (d.open) { S.invOpen.add(key); fill(); } else S.invOpen.delete(key); });
      parts.push(d);
    }
    if (flat && hits.length > cap) parts.push(h('p', { class: 'note', text: `Showing ${cap} of ${hits.length.toLocaleString()}: search to narrow it down.` }));
    listBox.replaceChildren(...(parts.length ? parts : [h('p', { class: 'note', text: q ? 'Nothing matches that.' : only === 'held' ? 'Nothing held yet. Type how many you have of anything below “All”.' : 'Nothing needed here.' })]));
  }
  S.invOpen = S.invOpen || new Set(LS.get('invOpenTops', []) || []);
  drawList();
  pane.replaceChildren(
    h('div', { class: 'pane-head' }, h('h3', { text: 'Inventory' }), h('span', { class: 'note', text: `${held.toLocaleString()} kinds held` })),
    h('p', { class: 'note' }, 'How many you hold of everything there’s a recipe for, gathered or made. The Build tab and the Crafting list count from here, and this is the one place to change the numbers. Shared by all your plans. Enter moves to the next one.'),
    h('div', { class: 'libsearch' }, search, chips),
    listBox,
    held ? h('div', { class: 'btnrow' }, h('button', { class: 'btn btn-sm btn-danger', type: 'button', disabled: S.readOnly, text: 'Clear every count', onclick: async () => {
      if (!(await confirmBox('Clear the inventory?', `Every count goes back to 0 (${held} kinds held now). The Build tab and the Crafting list will count from nothing.`, 'Clear the inventory', true))) return;
      INV.have = {}; saveInv(); invChanged(false); renderInventoryPane();
    } })) : null);
  LS.set('invOpenTops', [...S.invOpen]);
  pane.scrollTop = scroll;
  if (focusName) {
    const el = pane.querySelector(`[data-inv="${CSS.escape(focusName)}"]`);
    if (el) { el.focus({ preventScroll: true }); if (typed) { el.value = typed[0]; try { el.setSelectionRange(typed[1], typed[2]); } catch { /* number inputs have no selection */ } } }
  }
}
// From a count anywhere else: open this tab on that item, ready to type.
function openInventoryAt(name) {
  if (!$('#modal').hidden) closeModal();
  invUI.q = name; invUI.only = 'all';
  openTab('inventory'); LS.set('tab', 'inventory');
  const el = $('#pane-inventory').querySelector(`[data-inv="${CSS.escape(name)}"]`);
  if (el) { el.scrollIntoView({ block: 'center' }); el.focus(); }
}
// A count shown elsewhere: a button that opens the inventory on it.
function haveBtn(name, extraTip) {
  const n = invHave(name), o = anyOf(name);
  return h('button', { type: 'button', class: 'havebtn mono', text: n.toLocaleString(),
    title: o ? `${o.filter(k => invCount(k)).map(k => `${k} ${invCount(k).toLocaleString()}`).join(', ') || 'none of ' + o.join(', ')} · change them in the Inventory tab` : `You have ${n.toLocaleString()}: change it in the Inventory tab${extraTip || ''}`,
    onclick: () => openInventoryAt(o ? o[0] : name) });
}
