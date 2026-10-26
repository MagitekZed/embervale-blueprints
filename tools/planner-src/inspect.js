
// ---------------------------------------------------------------------------
// What's in a square: the Select tool shows it. Click a square and the Materials tab highlights its
// material (and the inspector lists it, with the floor under a raised piece and the level it's on); drag a
// selection and it lists every material inside. The status bar names the material under the pointer.
// ---------------------------------------------------------------------------
// A material's size and placement, as the Materials list words it.
function matDetail(e) {
  const P = S.plan;
  return KINDS[e.kind].label + (e.kind === 'roof' ? ` · top ${fmt(roofTop(e, P.cell))} m` : '')
    + ((e.kind === 'door' || e.kind === 'window') && e.opening ? ` · ${fmt(e.opening)} m tall` : '') + (e.kind === 'window' && e.sill != null ? ` · sill ${fmt(e.sill)} m` : '') + ((e.kind === 'door' || e.kind === 'window') && e.height ? ` · in a ${fmt(e.height)} m wall` : '')
    + ((e.kind === 'wall' || e.kind === 'block') ? (e.height ? ` · ${fmt(e.height)} m tall` : '') + (e.base ? ` · raised ${fmt(e.base)} m` : '')
      + (e.under && P.palette[e.under] ? ` · over ${P.palette[e.under].name}` : '') : '');
}
// The level a symbol in square (x, y) belongs to: the one holding it there, or a raised piece over it.
const levelHolding = (x, y, k) => S.plan.levels.find(L => L.grid[y][x] === k || (S.plan.palette[L.grid[y][x]] || {}).under === k) || null;
// On a block layer: the level whose blocks of symbol k fill this square on this layer (two levels can have
// the same floor in a square, a storey apart). A gable wall under a roof, or the wall round a door, falls
// back to the level that holds it.
function layerOwner(x, y, k) {
  const P = S.plan, pal = P.palette, [Z0, Z1] = layerZ(curLayer());
  const on = (L, e, z0, z1) => (e.kind === 'roof' ? hits(roofSpan(L, x, y), z0, z1) : hits(spanOf(e, L), z0, z1));
  for (const L of P.levels) {
    const c = L.grid[y][x], e = pal[c];
    if (!e || L.elev - FLOOR_T >= Z1 - 1e-6) continue;
    const z0 = Z0 - L.elev, z1 = Z1 - L.elev;
    if (c === k && on(L, e, z0, z1)) return L;
    if (e.under === k && pal[k] && on(L, pal[k], z0, z1)) return L;
  }
  return levelHolding(x, y, k);
}
// What's in square (x, y): on a level, its symbol and the floor under a raised piece; on a block layer, what
// shows on that layer, from whichever level holds it. [{ k, e, L, under }]
function squareMaterials(x, y) {
  const P = S.plan, pal = P && P.palette, out = [];
  if (!P || !inB(x, y)) return out;
  if (layerOn()) {
    const k = layerView(curLayer())[y][x];
    if (k !== ' ' && pal[k]) out.push({ k, e: pal[k], L: layerOwner(x, y, k) });
    return out;
  }
  const L = lv(), k = L && L.grid[y][x];
  if (!k || k === ' ' || !pal[k]) return out;
  out.push({ k, e: pal[k], L });
  const u = pal[k].under;
  if (u && pal[u]) out.push({ k: u, e: pal[u], L, under: true });
  for (const t of trimsOf(L)) {                                // pieces stacked over it on its trim levels
    const c = t.grid[y][x];
    if (c !== ' ' && pal[c]) out.push({ k: c, e: pal[c], L: t, stacked: true, note: ' · stacked' });
  }
  return out;
}
// Every material in a selection, with how many squares of it (floors under raised pieces included).
function selectionMaterials(R) {
  const P = S.plan, pal = P.palette, grid = layerOn() ? layerView(curLayer()) : lv().grid, n = new Map();
  const add = k => { if (k && k !== ' ' && pal[k]) n.set(k, (n.get(k) || 0) + 1); };
  for (let y = R.y; y < R.y + R.h; y++) for (let x = R.x; x < R.x + R.w; x++) {
    if (!inB(x, y)) continue;
    const k = grid[y][x];
    add(k);
    if (!layerOn() && pal[k] && pal[k].under) add(pal[k].under);
  }
  return new Map([...n].sort((a, b) => b[1] - a[1]));
}
function pickedSymbols() {
  const s = S.sel;
  if (s && s.type === 'block') return new Set([s.k]);
  return s && s.type === 'cells' && S.plan ? new Set(selectionMaterials(s.rect).keys()) : new Set();
}
// Outline the selection's materials in the Materials list.
function markPicked() {
  const p = pickedSymbols();
  for (const el of document.querySelectorAll('#pane-materials [data-k]')) el.classList.toggle('picked', p.has(el.dataset.k));
  for (const li of document.querySelectorAll('#pane-materials .mat.group')) li.classList.toggle('picked', [...(li.dataset.ks || '')].some(c => p.has(c)));
}
// Open the Materials tab on a material and bring it into view.
function showMaterial(k) {
  if (S.tab !== 'materials') openTab('materials');
  const e = S.plan.palette[k];
  if (!e) return;
  S.matView = 'plan';                                         // its row: unfiltered, its group open
  const sec = MAT_SECTIONS.find(s => s.kinds.includes(e.kind)) || MAT_SECTIONS[0];
  if (S.matFilter && S.matFilter !== 'all' && S.matFilter !== sec.id) S.matFilter = 'all';
  S.matQuery = '';
  S.matOpen = S.matOpen || new Set();
  S.matOpen.add(sec.id + '|' + (e.kind === 'door' || e.kind === 'window' ? e.name : matName(e.name)));
  renderMaterials();
  const el = [...document.querySelectorAll('#pane-materials [data-k]')].find(x => x.dataset.k === k);
  if (!el) return;
  el.scrollIntoView({ block: 'nearest' });
  el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash');
}
// The inspector's list: what's in the clicked square, or every material in a dragged selection.
function materialsHere(R) {
  const one = R.w === 1 && R.h === 1;
  const rows = one ? squareMaterials(R.x, R.y) : [...selectionMaterials(R)].map(([k, n]) => ({ k, e: S.plan.palette[k], n }));
  if (!rows.length) return null;
  return materialRows(rows, one ? 'In this square' : 'Materials in the selection');
}
// [{ k, e, L?, under?, n?, note? }] as inspector rows: the material (click to show it in the Materials tab),
// what it is and where, and "Paint with it".
function materialRows(rows, head) {
  return h('div', { class: 'here' },
    head ? h('div', { class: 'here-head', text: head }) : null,
    h('ul', { class: 'plainlist' }, ...rows.map(r => h('li', { class: 'here-row' },
      h('button', { class: 'here-mat', type: 'button', title: 'Show it in the Materials tab', onclick: () => showMaterial(r.k) },
        h('span', { class: 'swatch', style: `background:${r.e.color};color:${textOn(r.e.color)}`, text: symText(r.k) }),
        h('span', null, h('div', { class: 'mat-name', text: r.e.name }),
          h('div', { class: 'mat-kind', text: matDetail(r.e) + (r.under ? ' · the floor under it' : '') + (r.note || '') + (r.L && (layerOn() || r.L !== lv() || r.note != null) ? ` · on ${r.L.name}` : '') })),
        r.n != null ? h('span', { class: 'mat-count', text: String(r.n) }) : null),
      h('button', { class: 'btn btn-sm', type: 'button', text: 'Paint with it', title: 'Make it the current material', onclick: () => pickBrush(r.k) })))));
}
// The status bar: the material under the pointer.
function hoverMaterial(x, y, inside) {
  const el = $('#stMat');
  if (!el) return;
  const all = inside ? squareMaterials(x, y) : [], m = all.filter(r => !r.stacked), n = all.length - m.length;
  el.textContent = m.length ? m[0].e.name + (m[1] ? ` over ${m[1].e.name}` : '') + (n ? ` · ${n} more stacked` : '') : '';
}
