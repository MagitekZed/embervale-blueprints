// ---------------------------------------------------------------------------
// Build guidance (planner v49): where things are measured from the Flame Altar, a build card for what's
// selected, and the step-by-step build order (a prototype).
// Distances are from the altar's edges to the near edge of the thing, in metres and blocks, so a block right
// beside the altar is 0 away; heights are from the altar's base (what it stands on) and from 0 m.
// ---------------------------------------------------------------------------
function altars() {
  const P = S.plan;
  return P ? P.items.filter(i => i.type === 'altar').map(it => { const L = P.levels.find(l => l.id === it.level); return { R: itemRect(it), base: (L ? L.elev : 0) + (it.z || 0) }; }) : [];
}
const blk = m => `${fmt(m)} m (${Math.round(m / BLOCK_H).toLocaleString()} block${Math.round(m / BLOCK_H) === 1 ? '' : 's'})`;
// A box of squares [x0, x1) x [y0, y1) whose bottom is at z0 metres, relative to the nearest altar.
function altarRel(x0, x1, y0, y1, z0) {
  const as = altars();
  if (!as.length) return null;
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  const A = as.reduce((a, b) => (Math.hypot(b.R.x + b.R.w / 2 - cx, b.R.y + b.R.h / 2 - cy) < Math.hypot(a.R.x + a.R.w / 2 - cx, a.R.y + a.R.h / 2 - cy) ? b : a));
  const cm = CM(), R = A.R;
  const axis = (a0, a1, r0, r1, pos, neg) => a0 >= r1 ? { dir: pos, m: (a0 - r1) * cm } : a1 <= r0 ? { dir: neg, m: (r0 - a1) * cm } : null;
  return { ew: axis(x0, x1, R.x, R.x + R.w, 'E', 'W'), ns: axis(y0, y1, R.y, R.y + R.h, 'S', 'N'), dz: z0 == null ? null : z0 - A.base, z0, base: A.base };
}
function altarText(rel, short) {
  if (!rel) return '';
  const parts = [];
  for (const a of [rel.ew, rel.ns]) if (a) parts.push(`${short ? `${fmt(a.m)} m (${Math.round(a.m / BLOCK_H)})` : blk(a.m)} ${a.dir}`);
  let s = parts.length ? `${parts.join(' · ')} of the altar’s edges` : (rel.ew || rel.ns ? '' : 'over the altar');
  if (rel.dz != null) {
    const d = Math.abs(rel.dz), h0 = `${rel.z0 >= 0 ? '+' : ''}${fmt(rel.z0)} m`;
    s += (s ? ' · ' : '') + (d < 1e-6 ? `level with its base (${h0})` : `${short ? `${fmt(d)} m (${Math.round(d / BLOCK_H)})` : blk(d)} ${rel.dz > 0 ? 'above' : 'below'} its base (${h0})`);
  }
  return s;
}
// The two lines of the altar card: across (east-west, north-south) and up or down.
function altarLines(rel) {
  const m = d => `${fmt(d)} m (${Math.round(d / BLOCK_H)})`;
  const parts = [rel.ew, rel.ns].filter(Boolean).map(a => `${m(a.m)} ${a.dir}`);
  const across = parts.length ? `${parts.join(' · ')} of the altar` : 'Over the altar';
  if (rel.dz == null) return [across, ''];
  const d = Math.abs(rel.dz), at = `at ${rel.z0 >= 0 ? '+' : ''}${fmt(rel.z0)} m`;
  return [across, d < 1e-6 ? `Level with its base · ${at}` : `${m(d)} ${rel.dz > 0 ? 'above' : 'below'} its base · ${at}`];
}
// The altar card (planner v53), at the top left of the map: where the square or block under the pointer is from
// the altar. It replaced a status-bar readout that wrapped the bar onto a second line in narrow windows.
function altarReadout(x, y, z0) {
  const el = $('#altarCard');
  if (!el) return;
  const rel = x == null || !S.plan || !inB(x, y) ? null : altarRel(x, x + 1, y, y + 1, z0);
  if (!rel) { el.hidden = true; return; }
  const [a, b] = altarLines(rel);
  el.firstElementChild.textContent = a; el.lastElementChild.textContent = b;
  el.lastElementChild.hidden = !b;
  el.hidden = false;
}
// Fade the card while the pointer is over or near it, so it never hides what you're working on.
(function altarCardFade() {
  const views = $('#views'), el = $('#altarCard');
  if (!views || !el) return;
  views.addEventListener('pointermove', ev => {
    if (el.hidden) return;
    const r = el.getBoundingClientRect(), pad = 24;
    el.classList.toggle('near', ev.clientX < r.right + pad && ev.clientY < r.bottom + pad && ev.clientX > r.left - pad && ev.clientY > r.top - pad);
  });
  views.addEventListener('pointerleave', () => el.classList.remove('near'));
})();
// What 2D hovering means for height: the layer's bottom, or the current level's floor.
const hoverZ = () => (layerOn() ? layerZ(curLayer())[0] : (lv() ? lv().elev : 0));
let altar3dRaf = 0;
function altar3dHover(cx, cy) {
  if (altar3dRaf) return;
  altar3dRaf = requestAnimationFrame(() => {
    altar3dRaf = 0;
    const hit = bmHit(cx, cy);
    if (!hit || hit.k < -1) { altarReadout(null); return; }
    altarReadout(hit.x, hit.z, hit.k * CM());
  });
}

// ---------------------------------------------------------------------------
// The build card: what a selection holds (materials and blocks), its size in blocks, and where it starts from
// the altar, with a Copy button for a phone or a second screen.
// ---------------------------------------------------------------------------
function cardParts(sel) {
  if (!S.plan || !sel) return null;
  const I = pgIndex();
  if (sel.type === 'cells') {
    const V = pgView('2d', false), R = sel.rect, out = [];
    for (let y = R.y; y < R.y + R.h; y++) for (let x = R.x; x < R.x + R.w; x++) for (const s of I.cols.get(y * S.plan.w + x) || []) if (inView(V, s)) { const [a, b] = clipSeg(V, s); out.push({ s, z0: a, z1: b }); }
    return out;
  }
  if (sel.type === 'block' && sel.box) {
    const V = pgView('3d', false), seg = pgSegAt(sel.x, sel.y, V, sel.z0 + 1e-3);
    return seg ? pgChunk(seg, V) : null;
  }
  return null;
}
function buildCardText(parts, title) {
  if (!parts || !parts.length) return null;
  const P = S.plan, bpS = CM() / BLOCK_H;
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity, z0 = Infinity, z1 = -Infinity;
  const mats = new Map(), lids = new Set();
  for (const p of parts) {
    x0 = Math.min(x0, p.s.x); x1 = Math.max(x1, p.s.x + 1); y0 = Math.min(y0, p.s.y); y1 = Math.max(y1, p.s.y + 1);
    z0 = Math.min(z0, p.z0); z1 = Math.max(z1, p.z1);
    const n = partBlocks(p), m = mats.get(p.s.name) || { n: 0, b: 0 };
    m.n += n; m.b += partBuilt(p); mats.set(p.s.name, m); lids.add(p.s.lid);
  }
  const W = Math.round((x1 - x0) * bpS), D = Math.round((y1 - y0) * bpS), Hh = Math.round((z1 - z0) / BLOCK_H);
  const rel = altarRel(x0, x1, y0, y1, z0), lvNames = P.levels.filter(l => lids.has(l.id)).map(l => (trimParent(l) ? trimLabel(l) : l.name));
  const tot = [...mats.values()].reduce((t, m) => t + m.n, 0), built = [...mats.values()].reduce((t, m) => t + m.b, 0);
  const lines = [
    title,
    `Size: ${W} × ${D} × ${Hh} blocks (${fmt((x1 - x0) * CM())} × ${fmt((y1 - y0) * CM())} × ${fmt(z1 - z0)} m)`,
    `Blocks: ${[...mats].sort((a, b) => b[1].n - a[1].n).map(([n, m]) => `${n} ${Math.round(m.n).toLocaleString()}`).join(' · ')}${built ? ` (${Math.round(built).toLocaleString()} of ${Math.round(tot).toLocaleString()} built)` : ''}`,
    rel ? `Starts: ${altarText(rel, false)}` : 'No Flame Altar in this plan to measure from.',
    `Levels: ${lvNames.slice(0, 4).join(', ')}${lvNames.length > 4 ? ` and ${lvNames.length - 4} more` : ''}`,
  ];
  return lines;
}
function buildCardEl(sel) {
  const parts = cardParts(sel);
  if (!parts || !parts.length) return null;
  const lines = buildCardText(parts, sel.type === 'block' ? `Build card · the connected ${parts[0].s.name}` : 'Build card · the selection');
  return h('div', { class: 'section buildcard' },
    h('div', { class: 'pane-head' }, h('h4', { text: 'Build card' }),
      h('button', { class: 'btn btn-sm', type: 'button', text: 'Copy', title: 'Copy the card as text, for a phone or a second screen', onclick: () => copyText(lines.join('\n'), 'Build card') })),
    ...lines.slice(1).map(t => h('p', { class: 'note', text: t })));
}

// ---------------------------------------------------------------------------
// Steps (a prototype): the build in order, a group of levels at a time (lowest first), each labelled area in it
// (the largest area round a square; squares in none are the rest of the group), one course at a time from the
// bottom. Each step lists its blocks; the views follow it (Layers mode at its course, its blocks highlighted,
// the rest faded); "Mark this step built" marks them.
// ---------------------------------------------------------------------------
const STEPS = { key: '', list: [], at: -1 };
function buildSteps() {
  const P = S.plan, key = [S.planId, planVer].join('#');
  if (STEPS.key === key) return STEPS.list;
  const I = pgIndex(), groups = levelGroups(P).slice().sort((a, b) => a.lo - b.lo || a.top - b.top), cm = CM(), list = [];
  for (const G of groups) {
    const levs = G.items.flatMap(it => [it.L, ...it.trims.map(t => t.L)]), lids = new Set(levs.map(l => l.id));
    const zones = P.zones.filter(z => lids.has(z.level)).sort((a, b) => b.w * b.h - a.w * a.h);
    const areaOf = (x, y) => zones.findIndex(z => x >= z.x && x < z.x + z.w && y >= z.y && y < z.y + z.h);
    const byArea = new Map();
    for (const s of I.segs) {
      if (!lids.has(s.lid)) continue;
      const a = areaOf(s.x, s.y);
      if (!byArea.has(a)) byArea.set(a, []);
      byArea.get(a).push(s);
    }
    const order = [...byArea.keys()].sort((a, b) => (a < 0) - (b < 0) || (a >= 0 && b >= 0 ? (zones[a].y - zones[b].y) || (zones[a].x - zones[b].x) : 0));
    for (const a of order) {
      const segs = byArea.get(a), name = a >= 0 ? zones[a].name : (zones.length ? `The rest of ${G.name}` : G.name);
      const k0 = Math.floor(Math.min(...segs.map(s => s.z0)) / cm + 1e-6), k1 = Math.ceil(Math.max(...segs.map(s => s.z1)) / cm - 1e-6);
      const courses = [];
      for (let k = k0; k < k1; k++) {
        const z0 = k * cm, z1 = z0 + cm, parts = [];
        for (const s of segs) if (s.z0 < z1 - 1e-6 && s.z1 > z0 + 1e-6) parts.push({ s, z0: Math.max(z0, s.z0), z1: Math.min(z1, s.z1) });
        if (parts.length) courses.push({ k, z0, z1, parts });
      }
      courses.forEach((c, i) => list.push({ group: G.name, area: name, course: i + 1, of: courses.length, k: c.k, z0: c.z0, z1: c.z1, parts: c.parts, lids }));
    }
  }
  STEPS.key = key; STEPS.list = list;
  if (STEPS.at >= list.length) STEPS.at = -1;
  return list;
}
const stepBlocks = st => st.parts.reduce((t, p) => t + partBlocks(p), 0);
const stepBuilt = st => st.parts.reduce((t, p) => t + partBuilt(p), 0);
const stepDone = st => stepBuilt(st) >= stepBlocks(st) - 1e-6;
// Follow a step: Layers mode at its course, its blocks highlighted.
function goStep(i) {
  const list = buildSteps();
  if (!list.length) return;
  STEPS.at = clamp(i, 0, list.length - 1);
  const st = list[STEPS.at];
  if (!layerOn()) setLayerMode(true);
  setLayer(st.k);
  const cells = new Set(st.parts.map(p => p.s.c));
  S.stepHl = { type: 'step', lids: st.lids, cells, z0: st.z0, z1: st.z1 };
  hlSet(S.stepHl, true);
  if (S.tab === 'build') renderBuildPane();
}
function stopSteps() { STEPS.at = -1; S.stepHl = null; hlSet(null, true); if (S.tab === 'build') renderBuildPane(); }
function nextUnbuilt() {
  const list = buildSteps();
  for (let n = 1; n <= list.length; n++) { const i = (Math.max(-1, STEPS.at) + n) % list.length; if (!stepDone(list[i])) { goStep(i); return; } }
  toast('Every step is built.');
}
function stepsSection() {
  const list = buildSteps();
  if (!list.length) return null;
  const at = STEPS.at, st = list[at];
  const done = list.filter(stepDone).length;
  const head = h('div', { class: 'pane-head' }, h('h4', { text: `Steps · ${done} of ${list.length} built` }),
    h('span', { class: 'btnrow' }, h('button', { class: 'btn btn-sm btn-accent', type: 'button', text: at < 0 ? 'Start' : 'Next unbuilt', title: 'Go to the first step that isn’t built yet', onclick: nextUnbuilt })));
  if (!st) return h('div', { class: 'section steps' }, head, h('p', { class: 'note', text: 'The build in order: a group of levels at a time (lowest first), each labelled area in it, one course at a time from the bottom. The views follow the step you’re on.' }));
  const mats = new Map();
  for (const p of st.parts) { const m = mats.get(p.s.name) || { n: 0, b: 0, color: p.s.color }; m.n += partBlocks(p); m.b += partBuilt(p); mats.set(p.s.name, m); }
  const lastOfArea = st.course === st.of;
  const areaItems = lastOfArea ? S.plan.items.filter(it => st.lids.has(it.level) && it.type !== 'spawn' && !it.type.startsWith('npc-')) : [];
  const card = buildCardText(st.parts, '');
  return h('div', { class: 'section steps' }, head,
    h('div', { class: 'stepcard' + (stepDone(st) ? ' done' : '') },
      h('div', { class: 'note', text: `Step ${at + 1} of ${list.length} · ${st.group}` }),
      h('b', { text: `${st.area} · course ${st.course} of ${st.of}` }),
      h('div', { class: 'note', text: `${fmt(st.z0)} to ${fmt(st.z1)} m` + (card && card[3] ? ` · ${card[3].replace(/^Starts: /, '')}` : '') }),
      h('ul', { class: 'plainlist stepmats' }, ...[...mats].sort((a, b) => b[1].n - a[1].n).map(([n, m]) => h('li', null,
        h('span', { class: 'swatch sm', style: `background:${m.color}` }), h('span', { text: n }), h('span', { class: 'mono', text: m.b >= m.n - 1e-6 ? '✓' : `${Math.round(m.n - m.b).toLocaleString()}` })))),
      lastOfArea && areaItems.length ? h('p', { class: 'note', text: `Then the items on these levels (${areaItems.length}): mark them placed with the tool.` }) : null),
    h('div', { class: 'btnrow' },
      h('button', { class: 'btn btn-sm', type: 'button', text: '‹ Previous', disabled: at <= 0, onclick: () => goStep(at - 1) }),
      h('button', { class: 'btn btn-sm', type: 'button', text: 'Next ›', disabled: at >= list.length - 1, onclick: () => goStep(at + 1) }),
      h('button', { class: 'btn btn-sm btn-accent', type: 'button', disabled: S.readOnly || stepDone(st), text: 'Mark this step built', onclick: () => { progMark(st.parts, true, `${st.area}, course ${st.course}`); goStep(at); } }),
      h('button', { class: 'btn btn-sm btn-ghost', type: 'button', text: 'Stop', title: 'Stop following the steps', onclick: stopSteps })),
    stepOutline(list));
}
// The steps by group and area, with how far each area's got; click one to go to its first unbuilt course.
function stepOutline(list) {
  const areas = [];
  list.forEach((st, i) => { const a = areas[areas.length - 1]; if (a && a.group === st.group && a.area === st.area) { a.last = i; a.steps.push(st); } else areas.push({ group: st.group, area: st.area, first: i, last: i, steps: [st] }); });
  let g = null;
  const rows = [];
  for (const a of areas) {
    if (a.group !== g) { g = a.group; rows.push(h('li', { class: 'so-group', text: g })); }
    const done = a.steps.filter(stepDone).length, here = STEPS.at >= a.first && STEPS.at <= a.last;
    rows.push(h('li', null, h('button', { class: 'so-row' + (here ? ' cur' : ''), type: 'button', onclick: () => { const j = a.steps.findIndex(s => !stepDone(s)); goStep(a.first + (j < 0 ? 0 : j)); } },
      h('span', { text: a.area }), h('span', { class: 'mono', text: done === a.steps.length ? '✓' : `${done}/${a.steps.length}` }))));
  }
  return h('details', { class: 'stepoutline' }, h('summary', { text: `All areas (${areas.length})` }), h('ul', { class: 'plainlist' }, ...rows));
}
