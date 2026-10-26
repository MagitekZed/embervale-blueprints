
// ---------------------------------------------------------------------------
// Mirror painting: left-right, front-back, both ways, or four turned copies round a centre.
// Applies to the drawing tools and item stamping, not to paste, move or placed plans.
// ---------------------------------------------------------------------------
const MIRROR_MODES = [
  ['off', 'Off', 'No mirroring', 'off'],
  ['x', '↔', 'Mirror left–right, across the upright line', 'left–right'],
  ['y', '↕', 'Mirror front–back, across the level line', 'front–back'],
  ['xy', '✣', 'Mirror both ways: four copies', 'both ways'],
  ['rot', '⟳', 'Four copies turned 90° round the centre: towers, rotundas, cloisters', 'four turned copies'],
];
const MIRROR_TOOLS = new Set(['paint', 'erase', 'line', 'rect', 'room', 'fill', 'item', 'terrain', 'pieces', 'wall', 'replace']);
const mirrorOn = () => S.mirror.mode !== 'off' && MIRROR_TOOLS.has(S.tool);
function mirrorCentre() {
  if (S.mirror.cx == null) { S.mirror.cx = S.plan.w / 2; S.mirror.cy = S.plan.h / 2; }
  return [S.mirror.cx, S.mirror.cy];
}
function setMirror(mode) {
  S.mirror.mode = mode; S.mirrorPick = false; LS.set('mirror', mode);
  renderOptbar(); req2d();
}
function cycleMirror() {
  const i = MIRROR_MODES.findIndex(m => m[0] === S.mirror.mode);
  const next = MIRROR_MODES[(i + 1) % MIRROR_MODES.length];
  setMirror(next[0]);
  toast(`Mirror ${next[3]}${next[0] === 'off' ? '' : ' (X changes it)'}.`);
}
// Every copy of square (x, y), itself first, without repeats.
function mirrorPts(x, y) {
  if (!mirrorOn()) return [[x, y]];
  const [cx, cy] = mirrorCentre(), m = S.mirror.mode;
  const fx = v => Math.round(2 * cx - v - 1), fy = v => Math.round(2 * cy - v - 1);
  let pts;
  if (m === 'x') pts = [[x, y], [fx(x), y]];
  else if (m === 'y') pts = [[x, y], [x, fy(y)]];
  else if (m === 'xy') pts = [[x, y], [fx(x), y], [x, fy(y)], [fx(x), fy(y)]];
  else {
    const dx = x + 0.5 - cx, dy = y + 0.5 - cy;
    pts = [[dx, dy], [-dy, dx], [-dx, -dy], [dy, -dx]].map(([a, b]) => [Math.round(cx + a - 0.5), Math.round(cy + b - 0.5)]);
  }
  const seen = new Set();
  return pts.filter(([a, b]) => { const k = a + ',' + b; if (seen.has(k)) return false; seen.add(k); return true; });
}
function mirrorGroups(groups) {
  if (!mirrorOn()) return groups;
  return groups.map(g => {
    const seen = new Set(), cells = [];
    for (const [x, y] of g.cells) for (const p of mirrorPts(x, y)) { const k = p[0] + ',' + p[1]; if (!seen.has(k)) { seen.add(k); cells.push(p); } }
    return { ...g, cells };
  });
}
function setCellMirrored(L, x, y, ch) { for (const [a, b] of mirrorPts(x, y)) paintSquare(L, a, b, ch); }
function floodMirrored(L, x, y, ch) { let n = 0; for (const [a, b] of mirrorPts(x, y)) n += layerOn() ? layerFlood(a, b, ch) : flood(L, a, b, ch); return n; }
// Copies of a just-placed item: footprint mirrored or turned, facing adjusted to match.
function mirrorItems(it) {
  if (!mirrorOn()) return [];
  const [cx, cy] = mirrorCentre(), m = S.mirror.mode, R = itemRect(it), out = [];
  const flipX = r => ({ 0: 0, 90: 270, 180: 180, 270: 90 })[r], flipY = r => ({ 0: 180, 90: 90, 180: 0, 270: 270 })[r];
  const st = itemStep(), copy = (x, y, rot) => ({ ...it, id: uid('i'), x: snapStep(x, st), y: snapStep(y, st), rot });
  if (m === 'x' || m === 'xy') out.push(copy(2 * cx - R.x - R.w, R.y, flipX(it.rot)));
  if (m === 'y' || m === 'xy') out.push(copy(R.x, 2 * cy - R.y - R.h, flipY(it.rot)));
  if (m === 'xy') out.push(copy(2 * cx - R.x - R.w, 2 * cy - R.y - R.h, flipY(flipX(it.rot))));
  if (m === 'rot') for (let k = 1; k < 4; k++) {
    let x0 = R.x - cx, y0 = R.y - cy, x1 = R.x + R.w - cx, y1 = R.y + R.h - cy;
    for (let n = 0; n < k; n++) [x0, y0, x1, y1] = [-y1, x0, -y0, x1];          // a quarter turn, clockwise on screen
    out.push(copy(cx + Math.min(x0, x1), cy + Math.min(y0, y1), (it.rot + 90 * k) % 360));
  }
  return out.filter(c => !(c.x === it.x && c.y === it.y && c.rot === it.rot))
    .filter(c => { const Q = itemRect(c); return Q.x >= 0 && Q.y >= 0 && Q.x + Q.w <= S.plan.w && Q.y + Q.h <= S.plan.h; });
}
function mirrorControls() {
  const seg = h('div', { class: 'seg', role: 'group', 'aria-label': 'Mirror' });
  for (const [v, lab, tip] of MIRROR_MODES) seg.append(h('button', { type: 'button', 'aria-pressed': String(S.mirror.mode === v), text: lab, title: v === 'off' ? 'Mirror off (X cycles)' : tip, 'aria-label': v === 'off' ? 'Mirror off' : tip, onclick: () => setMirror(v) }));
  const kids = [h('span', { class: 'hint', text: 'Mirror' }), seg];
  if (S.mirror.mode !== 'off') {
    const [cx, cy] = mirrorCentre();
    kids.push(h('button', { class: 'btn btn-sm' + (S.mirrorPick ? ' btn-accent' : ''), type: 'button', text: S.mirrorPick ? 'Click the plan…' : `Centre ${metres(cx)}, ${metres(cy)} m`, title: 'Then click the plan to move the mirror centre. It snaps to the edges and middles of squares', onclick: () => { S.mirrorPick = !S.mirrorPick; renderOptbar(); } }));
  }
  return h('span', { class: 'mirrorbox' }, ...kids);
}
// Mirror lines on the sheet: bold while a mirroring tool is active, faint otherwise.
function drawMirror(g, cam) {
  if (S.mirror.mode === 'off' || !S.plan) return;
  const [cx, cy] = mirrorCentre(), s = cam.s, P = S.plan, m = S.mirror.mode, live = MIRROR_TOOLS.has(S.tool);
  const X = cam.ox + cx * s, Y = cam.oy + cy * s;
  g.save();
  g.strokeStyle = hexA(T.shroud, live ? 0.85 : 0.3); g.lineWidth = live ? 1.5 : 1; g.setLineDash([8, 5]);
  g.beginPath();
  if (m !== 'y') { g.moveTo(X, cam.oy); g.lineTo(X, cam.oy + P.h * s); }
  if (m !== 'x') { g.moveTo(cam.ox, Y); g.lineTo(cam.ox + P.w * s, Y); }
  g.stroke(); g.setLineDash([]);
  g.fillStyle = hexA(T.shroud, live ? 0.9 : 0.4);
  g.beginPath(); g.arc(X, Y, live ? 4 : 3, 0, Math.PI * 2); g.fill();
  if (m === 'rot' && live) { g.beginPath(); g.arc(X, Y, 11, -0.4, 1.2); g.stroke(); }
  g.restore();
}
