// ---------------------------------------------------------------------------
// The history (planner v46): every undo step has a name and a time, each plan keeps its last HIST_MAX steps
// while the page is open (switching plans no longer loses them), and the History pop-up beside Undo and Redo
// jumps straight to any of them. A step is { s, label, t }: s the plan as it was before (undo stack) or after
// (redo stack) the step, label what it did.
// ---------------------------------------------------------------------------
const HIST_MAX = 20;
const HIST_BY_PLAN = new Map();                                // plan id -> { hist, fut }, for the plans not open
function histPark() { if (S.planId) HIST_BY_PLAN.set(S.planId, { hist: S.hist, fut: S.fut }); }
function histLoad(id) { const h0 = HIST_BY_PLAN.get(id); S.hist = h0 ? h0.hist : []; S.fut = h0 ? h0.fut : []; }
function histTrim() { while (S.hist.length > HIST_MAX) S.hist.shift(); while (S.fut.length > HIST_MAX) S.fut.shift(); }

// What changed between two snapshots (serialize(p, true) as JSON), in a few words: what was painted, placed,
// moved or changed, how much, and where.
function describeChange(beforeJson, afterJson) {
  let A, B;
  try { A = JSON.parse(beforeJson); B = JSON.parse(afterJson); } catch { return 'Edit'; }
  const out = [], palName = (o, ch) => { const e = o.palette[code3(symCode(ch))]; return e ? e.name : 'a material'; };
  const short = n => String(n || '').replace(/^[^:]{1,30}:\s+/, '');   // "Isle: the crown (+28 m)" -> "the crown (+28 m)"
  const byId = list => new Map((list || []).map(x => [x.id, x]));
  // levels added, removed, changed
  const la = byId(A.levels), lb = byId(B.levels);
  const added = B.levels.filter(l => !la.has(l.id)), removed = A.levels.filter(l => !lb.has(l.id));
  if (added.length) out.push(added.length === 1 ? `Add level ${short(added[0].name)}` : `Add ${added.length} levels`);
  if (removed.length) out.push(removed.length === 1 ? `Delete level ${short(removed[0].name)}` : `Delete ${removed.length} levels`);
  // squares: only the levels whose rows changed are decoded
  const cellsOf = L => { const m = new Map(); (L.rows || []).forEach((r, j) => decodeRow(r, 4096).forEach((c, i) => { if (c !== ' ') m.set(((L.oy || 0) + j) * 4096 + (L.ox || 0) + i, c); })); return m; };
  let painted = 0, erased = 0;
  const newMat = new Map(), where = [];
  for (const L of B.levels) {
    const o = la.get(L.id);
    if (!o || (o.ox === L.ox && o.oy === L.oy && JSON.stringify(o.rows) === JSON.stringify(L.rows))) continue;
    const ca = cellsOf(o), cb = cellsOf(L);
    let n = 0;
    for (const [k, c] of cb) if (ca.get(k) !== c) { painted++; n++; newMat.set(c, (newMat.get(c) || 0) + 1); }
    for (const k of ca.keys()) if (!cb.has(k)) { erased++; n++; }
    if (n) where.push(L);
  }
  if (painted || erased) {
    const top = [...newMat].sort((a, b) => b[1] - a[1])[0], at = where.length === 1 ? ` · ${short(where[0].name)}` : where.length > 1 ? ` · ${where.length} levels` : '';
    const sq = n => `${n.toLocaleString()} square${n === 1 ? '' : 's'}`;
    if (painted && !erased) out.push((newMat.size === 1 ? `Paint ${palName(B, top[0])}` : `Paint ${newMat.size} materials`) + ` · ${sq(painted)}${at}`);
    else if (erased && !painted) out.push(`Erase ${sq(erased)}${at}`);
    else out.push(`Edit ${sq(painted + erased)}${at}`);
  }
  // items and areas
  const things = (a, b, noun, nameOf) => {
    const ma = byId(a), mb = byId(b);
    const add = (b || []).filter(x => !ma.has(x.id)), del = (a || []).filter(x => !mb.has(x.id));
    const moved = [], changed = [];
    for (const x of b || []) {
      const y = ma.get(x.id);
      if (!y || JSON.stringify(x) === JSON.stringify(y)) continue;
      if (x.x !== y.x || x.y !== y.y || x.level !== y.level) moved.push(x); else changed.push([y, x]);
    }
    const one = (list, verb, many) => list.length === 1 ? `${verb} ${nameOf(list[0])}` : `${verb} ${list.length} ${many}`;
    if (add.length) out.push(one(add, noun === 'item' ? 'Place' : 'Mark', noun === 'item' ? 'items' : 'areas'));
    if (del.length) out.push(one(del, 'Remove', `${noun}s`));
    if (moved.length) out.push(one(moved, 'Move', `${noun}s`));
    if (changed.length) {
      const [y, x] = changed[0];
      const verb = noun === 'item' && changed.length === 1 && x.rot !== y.rot ? 'Turn' : x.name !== y.name && noun === 'area' ? 'Rename' : 'Edit';
      out.push(changed.length === 1 ? `${verb} ${nameOf(x)}` : `Edit ${changed.length} ${noun}s`);
    }
  };
  things(A.items, B.items, 'item', it => it.label || it.type);
  things(A.zones, B.zones, 'area', z => z.name);
  // level settings: shown or hidden, renamed, grouped, raised
  const hid = [], shown = [], renamed = [], grouped = [], moved = [];
  for (const L of B.levels) {
    const o = la.get(L.id);
    if (!o) continue;
    if (!!o.hidden !== !!L.hidden) (L.hidden ? hid : shown).push(L);
    if (o.name !== L.name) renamed.push(L);
    if ((o.group || '') !== (L.group || '')) grouped.push(L);
    if (o.elev !== L.elev || o.height !== L.height) moved.push(L);
  }
  const lv1 = (list, verb, many) => list.length === 1 ? `${verb} ${short(list[0].name)}` : `${verb} ${list.length} ${many}`;
  if (hid.length) out.push(lv1(hid, 'Hide', 'levels'));
  if (shown.length) out.push(lv1(shown, 'Show', 'levels'));
  if (renamed.length) out.push(lv1(renamed, 'Rename', 'levels'));
  if (grouped.length) { const g = grouped[0].group; out.push(grouped.every(l => l.group === g) && g ? `Group ${grouped.length === 1 ? short(grouped[0].name) : grouped.length + ' levels'} as ${g}` : lv1(grouped, 'Regroup', 'levels')); }
  if (moved.length) out.push(lv1(moved, 'Change the height of', 'levels'));
  // materials
  const pa = A.palette || {}, pb = B.palette || {};
  const pAdd = Object.keys(pb).filter(k => !pa[k]), pDel = Object.keys(pa).filter(k => !pb[k]);
  const pChg = Object.keys(pb).filter(k => pa[k] && JSON.stringify(pa[k]) !== JSON.stringify(pb[k]));
  if (pChg.length) out.push(pChg.length === 1 ? `Edit material ${pb[pChg[0]].name}` : `Edit ${pChg.length} materials`);
  if (pAdd.length && !painted) out.push(pAdd.length === 1 ? `Add material ${pb[pAdd[0]].name}` : `Add ${pAdd.length} materials`);
  if (pDel.length) out.push(pDel.length === 1 ? `Remove material ${pa[pDel[0]].name}` : `Tidy away ${pDel.length} materials`);
  if (JSON.stringify(A.terrain || null) !== JSON.stringify(B.terrain || null)) out.push('Shape the ground');
  if (A.altar !== B.altar || A.cell !== B.cell || A.w !== B.w || A.h !== B.h) out.push('Change the plan’s settings');
  if (!out.length) return 'Edit';
  return out[0] + (out.length > 1 ? ` + ${out.length - 1} more` : '');
}

function agoText(t) {
  const s = Math.max(0, (Date.now() - t) / 1000);
  if (s < 45) return 'just now';
  if (s < 3600) return `${Math.round(s / 60)} min ago`;
  return `${Math.round(s / 3600)} h ago`;
}
// Undo or redo several steps at once, then redraw once.
function jumpHistory(back, fwd) {
  if (!S.plan || G) return;
  if (liveBase != null) liveCommit();
  if (!back && !fwd) return;
  let cur = snap();
  for (let n = 0; n < back && S.hist.length; n++) { const e = S.hist.pop(); S.fut.push({ s: cur, label: e.label, t: e.t }); cur = e.s; }
  for (let n = 0; n < fwd && S.fut.length; n++) { const e = S.fut.pop(); S.hist.push({ s: cur, label: e.label, t: e.t }); cur = e.s; }
  histTrim();
  restoreSnap(cur); afterEdit(); refreshPanels(); updateUndo();
}
let histPop = null;
function closeHistPop() { if (!histPop) return; histPop.remove(); histPop = null; document.removeEventListener('pointerdown', histPopOutside, true); $('#histBtn').setAttribute('aria-expanded', 'false'); }
function histPopOutside(e) { if (histPop && !histPop.contains(e.target) && !e.target.closest('#histBtn')) closeHistPop(); }
function toggleHistPop() {
  if (histPop) { closeHistPop(); return; }
  if (!S.plan) return;
  hideTip(true);
  const rows = [];
  const row = (label, t, state, onclick) => h('button', { class: 'hp-row ' + state, type: 'button', role: 'option', 'aria-selected': String(state === 'cur'), onclick: () => { closeHistPop(); onclick(); } },
    h('span', { class: 'hp-label', text: label }), h('span', { class: 'hp-t', text: state === 'undone' ? `undone · ${agoText(t)}` : agoText(t) }));
  S.fut.forEach((e, j) => rows.push(row(e.label, e.t, 'undone', () => jumpHistory(0, S.fut.length - j))));
  for (let i = S.hist.length - 1; i >= 0; i--) {
    const e = S.hist[i], back = S.hist.length - 1 - i;
    rows.push(row(e.label, e.t, back === 0 ? 'cur' : 'done', () => jumpHistory(back, 0)));
  }
  const start = h('button', { class: 'hp-row start' + (S.hist.length ? '' : ' cur'), type: 'button', role: 'option', 'aria-selected': String(!S.hist.length),
    onclick: () => { closeHistPop(); jumpHistory(S.hist.length, 0); } }, h('span', { class: 'hp-label', text: S.hist.length >= HIST_MAX ? 'Earlier (older steps aren’t kept)' : 'Where you started' }), h('span', { class: 'hp-t', text: '' }));
  histPop = h('div', { class: 'histpop', role: 'listbox', 'aria-label': 'History' },
    h('div', { class: 'hp-head' }, h('b', { text: 'History' }), h('span', { text: `last ${HIST_MAX} steps of this plan` })),
    ...(rows.length ? rows : [h('p', { class: 'hp-empty', text: 'Nothing to undo yet.' })]), start);
  document.body.append(histPop);
  const r = $('#histBtn').getBoundingClientRect();
  histPop.style.top = (r.bottom + 6) + 'px';
  histPop.style.left = clamp(r.right - histPop.offsetWidth, 8, innerWidth - histPop.offsetWidth - 8) + 'px';
  $('#histBtn').setAttribute('aria-expanded', 'true');
  histPop.addEventListener('keydown', e => {
    const list = [...histPop.querySelectorAll('.hp-row')], at = list.indexOf(document.activeElement);
    if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); closeHistPop(); $('#histBtn').focus(); }
    else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); e.stopPropagation(); const n = list[clamp(at + (e.key === 'ArrowDown' ? 1 : -1), 0, list.length - 1)]; if (n) n.focus(); }
    else e.stopPropagation();
  });
  setTimeout(() => document.addEventListener('pointerdown', histPopOutside, true), 0);
  const f = histPop.querySelector('.hp-row.cur') || histPop.querySelector('.hp-row');
  if (f) f.focus();
}
