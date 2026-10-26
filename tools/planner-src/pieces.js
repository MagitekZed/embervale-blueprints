
// ---------------------------------------------------------------------------
// Ready-made pieces, built from blocks and roof squares: stairs, spiral stairs, arches, battlements and
// roofs. Each piece makes the palette entries it needs (one per step height, arch course or roof height),
// reusing identical ones. Roofs mirror Roof in tools/drafts/mage_common.py.
// ---------------------------------------------------------------------------
const PIECES = [
  { id: 'stairs', label: 'Stairs', group: 'Stairs, arches & walls', shape: 'box', how: 'Drag along the run, from the bottom step to the top' },
  { id: 'spiral', label: 'Spiral stair', group: 'Stairs, arches & walls', shape: 'click', how: 'Click where its centre goes. One full turn climbs this level' },
  { id: 'arch', label: 'Arch', group: 'Stairs, arches & walls', shape: 'line', how: 'Drag across the opening along a wall line. It cuts the opening and sets the arch' },
  { id: 'battlements', label: 'Battlements', group: 'Stairs, arches & walls', shape: 'line', how: 'Drag along the wall, on the level above it' },
  { id: 'gable', label: 'Gable roof', group: 'Roofs', shape: 'box', roof: true, how: 'On the level above the walls, drag over them. The ridge runs the long way' },
  { id: 'hip', label: 'Hipped roof', group: 'Roofs', shape: 'box', roof: true, how: 'On the level above the walls, drag over them. All four sides slope' },
  { id: 'lean', label: 'Lean-to roof', group: 'Roofs', shape: 'box', roof: true, how: 'On the level above the walls, drag from the high side to the low side' },
  { id: 'cone', label: 'Cone roof', group: 'Roofs', shape: 'box', roof: true, how: 'On the level above the walls, drag a box round the tower' },
  { id: 'dome', label: 'Dome', group: 'Roofs', shape: 'box', roof: true, how: 'On the level above the walls, drag a box round them' },
];
const pieceDef = () => PIECES.find(p => p.id === S.piece) || PIECES[0];
const stripHeight = n => n.replace(/\s+[\d.]+ m$/, '').replace(/\s+\((?:step|tread|arch|newel|merlon)[^)]*\)$/, '');
const sameEntry = (a, b) => a.name === b.name && a.kind === b.kind && a.color === b.color && (a.height || 0) === (b.height || 0) &&
  (a.base || 0) === (b.base || 0) && (a.under || '') === (b.under || '');
const half = v => Math.max(0.5, Math.round(v * 2) / 2);           // whole 0.5 m blocks

// Material choices: block pieces use a wall or block from this plan; roofs use a roof material from this
// plan or the block catalogue.
function pieceBlockMat() {
  const P = S.plan;
  let e = P.palette[S.pieceMat];
  if (!e || !(e.kind === 'wall' || e.kind === 'block')) {
    const k = (P.palette[S.brush] && ['wall', 'block'].includes(P.palette[S.brush].kind)) ? S.brush : Object.keys(P.palette).find(c => ['wall', 'block'].includes(P.palette[c].kind));
    S.pieceMat = k || null; e = k ? P.palette[k] : null;
  }
  return e ? { name: stripHeight(e.name), color: e.color } : { name: 'Stone', color: '#84837e' };
}
function roofChoices() {
  const seen = new Map();
  for (const e of Object.values(S.plan.palette)) if (e.kind === 'roof') { const n = stripHeight(e.name); if (!seen.has(n)) seen.set(n, e.color); }
  for (const b of BLOCKS) if (b.g === 'Roofs' && !seen.has(b.n)) seen.set(b.n, b.c);
  return [...seen.entries()].map(([name, color]) => ({ name, color }));
}
function pieceRoofMat() {
  const list = roofChoices();
  return list.find(m => m.name === S.pieceRoof) || list.find(m => m.name === 'Castle Roof Block') || list[0];
}

// --- generators: each returns [{ x, y, e }] in squares, e a palette entry ------------------------
function makePiece(a, b) {
  const P = S.plan, L = lv(), cm = P.cell, H = L.height, def = pieceDef(), out = [];
  const put = (x, y, e) => { if (inB(x, y)) out.push({ x, y, e }); };
  if (def.id === 'stairs') {
    const m = pieceBlockMat(), R = rectFrom(a, b), alongX = R.w >= R.h, len = alongX ? R.w : R.h;
    const dir = alongX ? (b[0] >= a[0] ? 1 : -1) : (b[1] >= a[1] ? 1 : -1), rise = S.pieceRise;
    for (let i = 0; i < len; i++) {
      const hh = Math.min(H, (i + 1) * rise), e = { name: `${m.name} (step ${fmt(hh)} m)`.slice(0, 40), kind: 'block', color: m.color, height: hh };
      const at = dir > 0 ? i : len - 1 - i;
      for (let j = 0; j < (alongX ? R.h : R.w); j++) put(alongX ? R.x + at : R.x + j, alongX ? R.y + j : R.y + at, e);
    }
  } else if (def.id === 'spiral') {
    const m = pieceBlockMat(), rs = S.pieceSpiral / 2 / cm, rise = S.pieceRise, n = Math.max(4, Math.round(H / rise));
    const cx = a[0] + 0.5, cy = a[1] + 0.5;
    for (let y = Math.floor(cy - rs - 1); y <= cy + rs + 1; y++) for (let x = Math.floor(cx - rs - 1); x <= cx + rs + 1; x++) {
      const dx = x + 0.5 - cx, dy = y + 0.5 - cy, d = Math.hypot(dx, dy);
      if (d > rs) continue;
      if (d < 0.5) { put(x, y, { name: `${m.name} (newel)`.slice(0, 40), kind: 'wall', color: m.color }); continue; }
      const ang = (Math.atan2(dx, -dy) + Math.PI * 2) % (Math.PI * 2), k = Math.min(n - 1, Math.floor(ang / (Math.PI * 2 / n)));
      const e = { name: `${m.name} (tread ${fmt(k * rise)} m)`.slice(0, 40), kind: 'block', color: m.color, height: rise };
      if (k) e.base = k * rise;
      put(x, y, e);
    }
  } else if (def.id === 'arch' || def.id === 'battlements') {
    const m = pieceBlockMat(), horiz = Math.abs(b[0] - a[0]) >= Math.abs(b[1] - a[1]);
    const lo = horiz ? Math.min(a[0], b[0]) : Math.min(a[1], b[1]), hi = horiz ? Math.max(a[0], b[0]) : Math.max(a[1], b[1]), n = hi - lo + 1;
    const cell = i => horiz ? [lo + i, a[1]] : [a[0], lo + i];
    if (def.id === 'battlements') {
      for (let i = 0; i < n; i++) if (Math.floor(i * cm) % 2 === 0) put(...cell(i), { name: `${m.name} (merlon)`.slice(0, 40), kind: 'block', color: m.color, height: 1.5 });
    } else {
      // The arch fits the level: a 2 m clear opening at the sides and one course above the crown. Wide
      // spans flatten into an elliptical (or two-centred) arch rather than poking through the ceiling.
      const span = n * cm, r = span / 2, rise = Math.max(0, Math.min(r, H - 2.5)), spring = H - 0.5 - rise;
      const pointed = s => { const Rn = 1.6; return Math.sqrt(Math.max(0, Rn * Rn - (s + Rn - 1) ** 2)) / Math.sqrt(Rn * Rn - (Rn - 1) ** 2); };
      for (let i = 0; i < n; i++) {
        const sx = Math.abs((i + 0.5) * cm - span / 2) / r;      // 0 at the crown, 1 at the springing
        const u = S.pieceArch === 'flat' || rise < 0.5 ? H - 1 : spring + rise * (S.pieceArch === 'pointed' ? pointed(sx) : Math.sqrt(Math.max(0, 1 - sx * sx)));
        const base = clamp(Math.floor(u * 2) / 2, 0.5, H - 0.5);
        put(...cell(i), { name: `${m.name} (arch)`.slice(0, 40), kind: 'block', color: m.color, height: H - base, base });
      }
    }
  } else if (def.roof) {
    const m = pieceRoofMat(), R = rectFrom(a, b), ov = S.pieceOverhang, pitch = S.piecePitch, hc = cm / 2;
    const X0 = R.x * cm - ov, Y0 = R.y * cm - ov, X1 = (R.x + R.w) * cm + ov, Y1 = (R.y + R.h) * cm + ov;
    const ccx = (X0 + X1) / 2, ccy = (Y0 + Y1) / 2, rad = Math.min(X1 - X0, Y1 - Y0) / 2;
    const alongX = R.w >= R.h, fromLow = { x: b[0] >= a[0], y: b[1] >= a[1] };
    for (let y = Math.floor(Y0 / cm); y < Math.ceil(Y1 / cm); y++) for (let x = Math.floor(X0 / cm); x < Math.ceil(X1 / cm); x++) {
      const mx = (x + 0.5) * cm, my = (y + 0.5) * cm;
      let hh = null;
      if (def.id === 'gable') hh = 0.5 + ((alongX ? Math.min(my - Y0, Y1 - my) : Math.min(mx - X0, X1 - mx)) - hc) * pitch;
      else if (def.id === 'hip') hh = 0.5 + (Math.min(my - Y0, Y1 - my, mx - X0, X1 - mx) - hc) * pitch;
      else if (def.id === 'lean') {                            // high where the drag started
        const horizDrag = Math.abs(b[0] - a[0]) >= Math.abs(b[1] - a[1]);
        const dist = horizDrag ? (fromLow.x ? X1 - mx : mx - X0) : (fromLow.y ? Y1 - my : my - Y0);
        hh = 0.5 + (dist - hc) * pitch * 0.6;
      } else {
        const d = Math.hypot(mx - ccx, my - ccy);
        if (d > rad) continue;
        if (def.id === 'cone') hh = 0.5 + (rad - d) * pitch * 2;
        else { const Rr = rad / 0.9, z0 = Math.sqrt(1 - 0.81); hh = 0.5 + rad * (Math.sqrt(Math.max(0, 1 - (d / Rr) ** 2)) - z0) / (1 - z0); }
      }
      const top = half(hh);
      put(x, y, { name: `${m.name} ${fmt(top)} m`.slice(0, 40), kind: 'roof', color: m.color, height: top });
    }
  }
  // mirrored copies share the same entries
  if (!mirrorOn()) return out;
  const all = [], seen = new Set();
  for (const c of out) for (const [x, y] of mirrorPts(c.x, c.y)) { const k = x + ',' + y; if (!seen.has(k) && inB(x, y)) { seen.add(k); all.push({ x, y, e: c.e }); } }
  return all;
}
function pieceGroups(cells) {
  const by = new Map();
  for (const c of cells) { const k = c.e.color + '|' + c.e.kind; if (!by.has(k)) by.set(k, { cells: [], ch: null, color: c.e.color }); by.get(k).cells.push([c.x, c.y]); }
  return [...by.values()];
}
function writePiece(cells) {
  const P = S.plan, key = new Map();
  let full = 0;
  const symbolFor = e => {
    const sig = JSON.stringify(e);
    if (key.has(sig)) return key.get(sig);
    let k = Object.keys(P.palette).find(c => sameEntry(P.palette[c], e)) || null;
    if (!k) { k = nextFreeKey(); if (k) P.palette[k] = { ...e }; else full++; }
    key.set(sig, k);
    return k;
  };
  begin();
  for (const c of cells) { const k = symbolFor(c.e); if (k) setCell(lv(), c.x, c.y, k); }
  commit(); renderMaterials();
  if (full) toast('The palette is full (999 symbols), so some of the piece was left out. Remove unused materials and try again.');
}
function pieceSummary(cells) {
  const def = pieceDef();
  if (!cells.length) return '';
  if (def.id === 'stairs') { const top = Math.max(...cells.map(c => c.e.height)); return `climbs ${fmt(top)} m`; }
  if (def.roof) { const top = Math.max(...cells.map(c => c.e.height)); return `${fmt(top)} m high`; }
  return '';
}

// --- options bar --------------------------------------------------------------
function pieceControls() {
  const def = pieceDef();
  const sel = h('select', { 'aria-label': 'Piece', title: 'Which piece to place' });
  for (const g of [...new Set(PIECES.map(p => p.group))]) sel.append(h('optgroup', { label: g }, ...PIECES.filter(p => p.group === g).map(p => h('option', { value: p.id, text: p.label }))));
  sel.value = def.id;
  sel.addEventListener('change', () => { S.piece = sel.value; S.preview = null; renderOptbar(); req2d(); });
  const kids = [sel];
  if (def.roof) {
    const mats = roofChoices(), ms = h('select', { 'aria-label': 'Roof material', title: 'Roof material: this plan’s roofs first, then the catalogue' }, ...mats.map(m => h('option', { value: m.name, text: m.name })));
    ms.value = pieceRoofMat().name;
    ms.addEventListener('change', () => { S.pieceRoof = ms.value; });
    const pitch = h('select', { 'aria-label': 'Pitch', title: 'How steep: rise per metre' }, ...[[0.58, '30°'], [1, '45°'], [1.73, '60°']].map(([v, t]) => h('option', { value: String(v), text: t })));
    pitch.value = String(S.piecePitch);
    pitch.addEventListener('change', () => { S.piecePitch = Number(pitch.value); });
    const ov = h('select', { 'aria-label': 'Overhang', title: 'How far the eaves reach past the walls' }, ...[[0, 'No overhang'], [0.5, '0.5 m eaves'], [1, '1 m eaves']].map(([v, t]) => h('option', { value: String(v), text: t })));
    ov.value = String(S.pieceOverhang);
    ov.addEventListener('change', () => { S.pieceOverhang = Number(ov.value); });
    kids.push(ms);
    if (def.id !== 'dome') kids.push(pitch);
    kids.push(ov);
  } else {
    kids.push(h('label', { class: 'inline' }, 'Material', paletteSelect(['wall', 'block'], S.pieceMat || S.brush, v => { S.pieceMat = v; })));
    if (def.id === 'stairs' || def.id === 'spiral') {
      const rise = h('select', { 'aria-label': 'Step height', title: 'Height of each step. Half a metre is one block, which you walk up' }, ...[[0.5, '0.5 m steps'], [1, '1 m steps']].map(([v, t]) => h('option', { value: String(v), text: t })));
      rise.value = String(S.pieceRise);
      rise.addEventListener('change', () => { S.pieceRise = Number(rise.value); });
      kids.push(rise);
    }
    if (def.id === 'spiral') {
      const w = h('select', { 'aria-label': 'Width', title: 'Outside width of the stair' }, ...[3, 4, 5, 6].map(v => h('option', { value: String(v), text: `${v} m across` })));
      w.value = String(S.pieceSpiral);
      w.addEventListener('change', () => { S.pieceSpiral = Number(w.value); });
      kids.push(w);
    }
    if (def.id === 'arch') {
      const seg = h('div', { class: 'seg', role: 'group', 'aria-label': 'Arch shape' });
      for (const [v, lab] of [['round', 'Round'], ['pointed', 'Pointed'], ['flat', 'Lintel']]) seg.append(h('button', { type: 'button', 'aria-pressed': String(S.pieceArch === v), text: lab, onclick: () => { S.pieceArch = v; renderOptbar(); } }));
      kids.push(seg);
    }
  }
  kids.push(h('span', { class: 'hint', id: 'pieceOut', text: def.how }));
  return kids;
}
