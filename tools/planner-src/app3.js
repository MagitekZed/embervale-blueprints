
// ---------------------------------------------------------------------------
// Theme tokens for canvas drawing
// ---------------------------------------------------------------------------
let T = {};
function readTokens() {
  const cs = getComputedStyle(document.documentElement);
  for (const k of ['bg', 'panel', 'raised', 'sheet', 'off', 'glass', 'ink', 'muted', 'faint', 'line', 'grid', 'grid-major', 'accent', 'accent-soft', 'shroud', 'bad'])
    T[k] = cs.getPropertyValue('--' + k).trim() || '#888888';
}

// ---------------------------------------------------------------------------
// 2D rendering
// ---------------------------------------------------------------------------
const c2d = $('#c2d'), ctx = c2d.getContext('2d');
const RUL = { top: 20, left: 30 };
let W2 = 0, H2 = 0, DPR = 1, raf2 = 0;
const zoneLabelBoxes = new Map();
function resize2d() {
  const r = $('#view2d').getBoundingClientRect();
  DPR = Math.min(window.devicePixelRatio || 1, 2);
  W2 = Math.max(1, Math.floor(r.width)); H2 = Math.max(1, Math.floor(r.height));
  c2d.width = W2 * DPR; c2d.height = H2 * DPR;
  if (S.needFit && W2 > 50) { S.needFit = false; fitView(true); }
  draw2d();
}
function req2d() { if (!raf2) raf2 = requestAnimationFrame(() => { raf2 = 0; draw2d(); }); }
const toGridPt = p => [(p.x - S.cam.ox) / S.cam.s, (p.y - S.cam.oy) / S.cam.s];
// The 2D view turns a quarter at a time (cam.r: clockwise quarter turns, 0–3) about the view's middle. Drawing and the
// pointer work in the unturned view and the canvas is turned as a whole; these convert to and from the screen.
const camRot = cam => (cam && cam.r) || 0;
const viewMid = () => [Math.round(W2 / 2), Math.round(H2 / 2)];      // (whole pixels, so crisp lines stay crisp turned)
function turnVec(dx, dy, r) { r = ((r % 4) + 4) % 4; for (let i = 0; i < r; i++) [dx, dy] = [-dy, dx]; return [dx, dy]; }
function toScreen(cam, x, y) { const [cx, cy] = viewMid(), [dx, dy] = turnVec(x - cx, y - cy, camRot(cam)); return [cx + dx, cy + dy]; }
function fromScreen(cam, x, y) { const [cx, cy] = viewMid(), [dx, dy] = turnVec(x - cx, y - cy, -camRot(cam)); return [cx + dx, cy + dy]; }
function screenBox(cam, x, y, w, hh) {
  const [ax, ay] = toScreen(cam, x, y), [bx, by] = toScreen(cam, x + w, y + hh);
  return { x: Math.min(ax, bx), y: Math.min(ay, by), w: Math.abs(bx - ax), h: Math.abs(by - ay) };
}
// The screen as a rectangle of the unturned view.
function viewRect(cam, W, H) {
  if (!camRot(cam)) return { x: 0, y: 0, w: W, h: H };
  const [ax, ay] = fromScreen(cam, 0, 0), [bx, by] = fromScreen(cam, W, H);
  return { x: Math.min(ax, bx), y: Math.min(ay, by), w: Math.abs(bx - ax), h: Math.abs(by - ay) };
}
// Labels stay upright: fn(x, y, w, h) draws in the box as it shows on screen, with the canvas turned back to match.
function upright(g, cam, x, y, w, hh, fn) {
  const r = camRot(cam);
  if (!r) return fn(x, y, w, hh);
  const bw = r % 2 ? hh : w, bh = r % 2 ? w : hh;
  g.save(); g.translate(x + w / 2, y + hh / 2); g.rotate(-r * Math.PI / 2);
  const out = fn(-bw / 2, -bh / 2, bw, bh);
  g.restore();
  return out;
}
function setViewTurn(r) {
  if (!S.plan) return;
  S.cam.r = ((r % 4) + 4) % 4;
  LS.set('turn:' + S.planId, S.cam.r);
  updateZoom(); req2d();
}

function roundRectPath(g, x, y, w, hh, r) {
  r = Math.max(0, Math.min(r, w / 2, hh / 2));
  g.beginPath();
  g.moveTo(x + r, y); g.lineTo(x + w - r, y); g.arcTo(x + w, y, x + w, y + r, r);
  g.lineTo(x + w, y + hh - r); g.arcTo(x + w, y + hh, x + w - r, y + hh, r);
  g.lineTo(x + r, y + hh); g.arcTo(x, y + hh, x, y + hh - r, r);
  g.lineTo(x, y + r); g.arcTo(x, y, x + r, y, r);
  g.closePath();
}
function kindAt(L, x, y) { if (!inB(x, y)) return null; const e = S.plan.palette[L.grid[y][x]]; return e ? e.kind : null; }
function wallRunsHorizontally(L, x, y) {
  const l = kindAt(L, x - 1, y), r = kindAt(L, x + 1, y), u = kindAt(L, x, y - 1), d = kindAt(L, x, y + 1);
  const hz = (WALLISH.has(l) ? 1 : 0) + (WALLISH.has(r) ? 1 : 0), vt = (WALLISH.has(u) ? 1 : 0) + (WALLISH.has(d) ? 1 : 0);
  return hz >= vt;
}

function renderPlan(g, cam, W, H, o) {
  const P = S.plan, s = cam.s, L = P.levels[o.levelIdx], V = viewRect(cam, W, H);
  g.fillStyle = T.off; g.fillRect(V.x, V.y, V.w, V.h);
  g.fillStyle = T.sheet; g.fillRect(cam.ox, cam.oy, P.w * s, P.h * s);
  const x0 = clamp(Math.floor((V.x - cam.ox) / s), 0, P.w), x1 = clamp(Math.ceil((V.x + V.w - cam.ox) / s), 0, P.w);
  const y0 = clamp(Math.floor((V.y - cam.oy) / s), 0, P.h), y1 = clamp(Math.ceil((V.y + V.h - cam.oy) / s), 0, P.h);
  // in block-layer mode the view is the layer, whichever levels hold it, over the layer below it
  const lay = !!o.layer && layerOn(), k = lay ? curLayer() : 0;
  const VL = lay ? { ...L, id: null, ids: new Set(layerLevels(k).map(l => l.id)), elev: layerZ(k)[0], height: layerSize(), grid: layerView(k) } : L;
  drawGround(g, cam, VL, x0, x1, y0, y1);
  if (S.tool === 'terrain' && terrainOn(P) && cam === S.cam) drawTerrainMap(g, cam, x0, x1, y0, y1);
  // guide level (Levels mode): the level below; underground, the level above (the building you're digging under)
  const gi = isUnder(L) ? o.levelIdx + 1 : o.levelIdx - 1;
  if (o.ghost && !lay && gi >= 0 && gi < P.levels.length) drawGhost(g, P.levels[gi], cam, x0, x1, y0, y1);
  drawCells(g, VL, cam, x0, x1, y0, y1);
  if (!lay) drawTrimDots(g, L, cam, x0, x1, y0, y1);
  if (cam === S.cam) { drawProgress2d(g, cam, x0, x1, y0, y1); drawHighlight2d(g, cam, x0, x1, y0, y1, VL.grid); }
  if (o.zones) drawZoneFills(g, VL, cam);
  drawGrid(g, cam, x0, x1, y0, y1);
  if (o.zones) drawZoneBorders(g, VL, cam);
  // block layers: the layers just below (red) and above (blue, dashed) outlined over this one, filled squares too
  if (lay && o.olBelow) drawLayerOutline(g, layerView(k - 1), cam, x0, x1, y0, y1, OUTLINE_BELOW, false);
  if (lay && o.olAbove) drawLayerOutline(g, layerView(k + 1), cam, x0, x1, y0, y1, OUTLINE_ABOVE, true);
  if (lay) drawLayerItems(g, cam, k); else drawItems(g, L, cam);
  if (o.altar) { drawAltarOutside(g, L, cam, x0, x1, y0, y1); drawAltars(g, cam); }
}
// Squares with more pieces stacked on the level's trim levels get a dot in the corner (the inspector lists them).
function drawTrimDots(g, L, cam, x0, x1, y0, y1) {
  const s = cam.s;
  if (s < 9 || !L) return;
  const trims = trimsOf(L);
  if (!trims.length) return;
  const r = Math.max(1.5, s * 0.09), off = s - r * 2.2;
  g.fillStyle = hexA(T.ink, 0.6);
  g.beginPath();
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
    if (!trims.some(t => t.grid[y][x] !== ' ')) continue;
    const px = cam.ox + x * s + off, py = cam.oy + y * s + off;
    g.moveTo(px + r, py); g.arc(px, py, r, 0, Math.PI * 2);
  }
  g.fill();
}
// Below ground, every empty square is earth: a soil wash with a scatter of grit.
function drawSoil(g, cam, x0, x1, y0, y1) {
  const s = cam.s;
  g.fillStyle = hexA(SOIL, 0.34); g.fillRect(cam.ox + x0 * s, cam.oy + y0 * s, (x1 - x0) * s, (y1 - y0) * s);
  if (s < 6) return;
  g.fillStyle = hexA(SOIL, 0.55);
  const r = Math.max(1, s * 0.07);
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
    const hsh = (x * 73856093) ^ (y * 19349663);
    if ((hsh & 7) === 0) g.fillRect(cam.ox + (x + 0.2 + ((hsh >> 4) & 7) / 12) * s, cam.oy + (y + 0.2 + ((hsh >> 8) & 7) / 12) * s, r, r);
  }
}
function drawGhost(g, B, cam, x0, x1, y0, y1) {
  const s = cam.s, pal = S.plan.palette;
  g.fillStyle = hexA(T.ink, 0.13);
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
    const e = pal[B.grid[y][x]];
    if (e && WALLISH.has(e.kind)) g.fillRect(cam.ox + x * s, cam.oy + y * s, s, s);
  }
  g.fillStyle = hexA(T.ink, 0.05);
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
    const e = pal[B.grid[y][x]];
    if (e && !WALLISH.has(e.kind)) g.fillRect(cam.ox + x * s, cam.oy + y * s, s, s);
  }
}
// The edge of everything on another layer, drawn as a line round it (so it shows over this layer's filled squares).
const OUTLINE_BELOW = '#e0533d', OUTLINE_ABOVE = '#3b82f6';
function drawLayerOutline(g, grid, cam, x0, x1, y0, y1, color, dashed) {
  const s = cam.s, pal = S.plan.palette, P = S.plan;
  if (s < 1.5) return;
  const on = (x, y) => { if (x < 0 || y < 0 || x >= P.w || y >= P.h) return false; const e = pal[grid[y][x]]; return !!e && e.kind !== 'dig'; };
  g.save();
  g.strokeStyle = color; g.lineWidth = Math.max(1.5, Math.min(3, s * 0.14)); g.lineCap = 'butt';
  if (dashed) g.setLineDash([Math.max(3, s * 0.3), Math.max(2, s * 0.2)]);
  g.beginPath();
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
    if (!on(x, y)) continue;
    const px = cam.ox + x * s, py = cam.oy + y * s;
    if (!on(x, y - 1)) { g.moveTo(px, py); g.lineTo(px + s, py); }
    if (!on(x, y + 1)) { g.moveTo(px, py + s); g.lineTo(px + s, py + s); }
    if (!on(x - 1, y)) { g.moveTo(px, py); g.lineTo(px, py + s); }
    if (!on(x + 1, y)) { g.moveTo(px + s, py); g.lineTo(px + s, py + s); }
  }
  g.stroke();
  g.restore();
}
function drawCells(g, L, cam, x0, x1, y0, y1) {
  const s = cam.s, pal = S.plan.palette, grid = L.grid, ox = cam.ox, oy = cam.oy;
  const symbols = [];
  // roofs are shaded by height, higher is lighter, so slopes read at a glance
  let rLo = Infinity, rHi = -Infinity;
  for (const e of Object.values(pal)) if (e.kind === 'roof') { const t = roofTop(e, CM()); rLo = Math.min(rLo, t); rHi = Math.max(rHi, t); }
  const roofShade = e => rHi > rLo ? tint(e.color, -0.14 + 0.36 * (roofTop(e, CM()) - rLo) / (rHi - rLo)) : e.color;
  for (let y = y0; y < y1; y++) {
    const row = grid[y];
    for (let x = x0; x < x1; x++) {
      const ch = row[x];
      if (ch === ' ') continue;
      const e = pal[ch], px = ox + x * s, py = oy + y * s;
      if (!e) { g.fillStyle = '#d0368a'; g.fillRect(px, py, s + 0.5, s + 0.5); if (s >= 12) symbols.push(['?', px, py, ch]); continue; }
      if (e.kind === 'dig') {                                    // dug away: clear the soil, dashed edge
        g.fillStyle = T.sheet; g.fillRect(px, py, s + 0.5, s + 0.5);
        if (s >= 8) { g.fillStyle = hexA(e.color, 0.18); g.fillRect(px + s * 0.15, py + s * 0.15, s * 0.7, s * 0.7); }
        continue;
      }
      if (e.kind === 'door') { g.fillStyle = hexA(e.color, 0.22); g.fillRect(px, py, s + 0.5, s + 0.5); symbols.push(['door', px, py, x, y, e.color]); continue; }
      const uf = e.under && pal[e.under];
      if (uf && (uf.kind === 'floor' || uf.kind === 'water' || uf.kind === 'roof')) {     // raised piece over a floor or roof: that, then an inset
        g.fillStyle = uf.kind === 'roof' ? roofShade(uf) : uf.color; g.fillRect(px, py, s + 0.5, s + 0.5);
        const ins = s * 0.18; g.fillStyle = e.color; g.fillRect(px + ins, py + ins, s - 2 * ins, s - 2 * ins);
      } else { g.fillStyle = e.kind === 'roof' ? roofShade(e) : e.color; g.fillRect(px, py, s + 0.5, s + 0.5); }
      if (e.kind === 'window' || (e.kind === 'block' && s >= 9) || (e.kind === 'water' && s >= 14)) symbols.push([e.kind, px, py, x, y, e.color]);
    }
  }
  if (s >= 5) {
    g.beginPath();
    const solid = (x, y) => { if (!inB(x, y)) return false; const e = pal[grid[y][x]]; return !!e && OUTLINED.has(e.kind); };
    for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
      if (!solid(x, y)) continue;
      const px = ox + x * s, py = oy + y * s;
      if (!solid(x, y - 1)) { g.moveTo(px, py); g.lineTo(px + s, py); }
      if (!solid(x, y + 1)) { g.moveTo(px, py + s); g.lineTo(px + s, py + s); }
      if (!solid(x - 1, y)) { g.moveTo(px, py); g.lineTo(px, py + s); }
      if (!solid(x + 1, y)) { g.moveTo(px + s, py); g.lineTo(px + s, py + s); }
    }
    g.strokeStyle = hexA(T.ink, 0.75); g.lineWidth = s >= 16 ? 1.5 : 1; g.stroke();
    // contour lines between roof squares of different heights
    const rt = (x, y) => { if (!inB(x, y)) return NaN; let e = pal[grid[y][x]]; if (e && e.kind !== 'roof' && e.under && pal[e.under]) e = pal[e.under]; return e && e.kind === 'roof' ? roofTop(e, CM()) : NaN; };
    g.beginPath();
    for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
      const t = rt(x, y);
      if (t !== t) continue;
      const px = ox + x * s, py = oy + y * s, r = rt(x + 1, y), d = rt(x, y + 1);
      if (r === r && Math.abs(r - t) > 0.01) { g.moveTo(px + s, py); g.lineTo(px + s, py + s); }
      if (d === d && Math.abs(d - t) > 0.01) { g.moveTo(px, py + s); g.lineTo(px + s, py + s); }
    }
    g.strokeStyle = hexA(T.ink, 0.32); g.lineWidth = 1; g.stroke();
  }
  for (const sy of symbols) {
    const [kind, px, py] = sy;
    if (kind === '?') { g.fillStyle = '#ffffff'; g.font = `700 ${Math.round(s * 0.55)}px ${FONT_MONO}`; g.textAlign = 'center'; g.textBaseline = 'middle'; upright(g, cam, px, py, s, s, (bx, by) => g.fillText(sy[3], bx + s / 2, by + s / 2 + 1)); continue; }
    const horiz = wallRunsHorizontally(L, sy[3], sy[4]);
    g.lineWidth = Math.max(1, s * 0.07);
    if (kind === 'door') {
      g.strokeStyle = sy[5];
      g.beginPath();
      if (horiz) { g.moveTo(px, py + s); g.lineTo(px, py); g.arc(px, py + s, s, -Math.PI / 2, 0); }
      else { g.moveTo(px, py); g.lineTo(px + s, py); g.arc(px, py, s, 0, Math.PI / 2); }
      g.stroke();
    } else if (kind === 'window') {
      g.strokeStyle = hexA(T.ink, 0.7);
      g.beginPath();
      if (horiz) { g.moveTo(px, py + s * 0.4); g.lineTo(px + s, py + s * 0.4); g.moveTo(px, py + s * 0.6); g.lineTo(px + s, py + s * 0.6); }
      else { g.moveTo(px + s * 0.4, py); g.lineTo(px + s * 0.4, py + s); g.moveTo(px + s * 0.6, py); g.lineTo(px + s * 0.6, py + s); }
      g.stroke();
    } else if (kind === 'block') {
      g.strokeStyle = hexA(T.ink, 0.35);
      g.beginPath(); g.moveTo(px + s * 0.2, py + s * 0.8); g.lineTo(px + s * 0.8, py + s * 0.2); g.stroke();
    } else if (kind === 'water') {
      g.strokeStyle = 'rgba(255,255,255,0.55)';
      g.beginPath();
      for (const f of [0.38, 0.68]) { g.moveTo(px + s * 0.18, py + s * f); g.quadraticCurveTo(px + s * 0.34, py + s * (f - 0.12), px + s * 0.5, py + s * f); g.quadraticCurveTo(px + s * 0.66, py + s * (f + 0.12), px + s * 0.82, py + s * f); }
      g.stroke();
    }
  }
}
function drawGrid(g, cam, x0, x1, y0, y1) {
  const s = cam.s, P = S.plan, ox = cam.ox, oy = cam.oy;
  const five = Math.round(5 / CM()), metre = Math.round(1 / CM());
  const vline = x => { const px = Math.round(ox + x * s) + 0.5; g.moveTo(px, oy + y0 * s); g.lineTo(px, oy + y1 * s); };
  const hline = y => { const py = Math.round(oy + y * s) + 0.5; g.moveTo(ox + x0 * s, py); g.lineTo(ox + x1 * s, py); };
  g.lineWidth = 1;
  if (s >= 6) {
    g.strokeStyle = T.grid; g.beginPath();
    for (let x = x0; x <= x1; x++) if (x % five) vline(x);
    for (let y = y0; y <= y1; y++) if (y % five) hline(y);
    g.stroke();
    if (metre > 1) {
      g.beginPath();
      for (let x = x0; x <= x1; x++) if (x % five && x % metre === 0) vline(x);
      for (let y = y0; y <= y1; y++) if (y % five && y % metre === 0) hline(y);
      g.stroke();
    }
  }
  g.strokeStyle = T['grid-major']; g.beginPath();
  const step = s * five >= 16 ? five : five * 2;
  for (let x = Math.ceil(x0 / step) * step; x <= x1; x += step) vline(x);
  for (let y = Math.ceil(y0 / step) * step; y <= y1; y += step) hline(y);
  g.stroke();
  g.strokeStyle = hexA(T.ink, 0.45);
  g.strokeRect(Math.round(ox) + 0.5, Math.round(oy) + 0.5, Math.round(P.w * s), Math.round(P.h * s));
}
const onLevel = (L, id) => (L.ids ? L.ids.has(id) : id === L.id);   // L.ids: a block layer's levels
function drawZoneFills(g, L, cam) {
  const s = cam.s;
  for (const z of S.plan.zones) if (onLevel(L, z.level)) { g.fillStyle = hexA(z.color, 0.11); g.fillRect(cam.ox + z.x * s, cam.oy + z.y * s, z.w * s, z.h * s); }
}
function drawZoneBorders(g, L, cam) {
  const s = cam.s;
  if (g === ctx) zoneLabelBoxes.clear();
  for (const z of S.plan.zones) {
    if (!onLevel(L, z.level)) continue;
    const px = cam.ox + z.x * s, py = cam.oy + z.y * s, w = z.w * s, hh = z.h * s;
    const sel = S.sel && S.sel.type === 'zone' && S.sel.id === z.id;
    g.setLineDash(sel ? [] : [6, 4]); g.lineWidth = sel ? 2.5 : 1.5; g.strokeStyle = sel ? T.accent : z.color;
    g.strokeRect(px + 1, py + 1, w - 2, hh - 2); g.setLineDash([]);
    g.font = `700 11px ${FONT_UI}`;
    const label = z.name.toUpperCase();
    upright(g, cam, px, py, w, hh, (zx, zy, zw, zh) => {          // the label in the zone's top-left corner on screen
      if (zw <= 30 || zh <= 18) return;
      const tw = Math.min(g.measureText(label).width, Math.max(0, zw - 22));
      const bx = zx + 4, by = zy + 4, bw = tw + 12, bh = 17;
      roundRectPath(g, bx, by, bw, bh, 4); g.fillStyle = z.color; g.fill();
      g.save(); g.beginPath(); g.rect(bx, by, bw - 4, bh); g.clip();
      g.fillStyle = textOn(z.color); g.textAlign = 'left'; g.textBaseline = 'middle'; g.fillText(label, bx + 6, by + bh / 2 + 0.5);
      g.restore();
      if (g === ctx) { const sb = screenBox(cam, px, py, w, hh); zoneLabelBoxes.set(z.id, { x: sb.x + 4, y: sb.y + 4, w: bw, h: bh }); }   // (on screen)
    });
  }
}
function drawItems(g, L, cam) {
  for (const it of S.plan.items) if (it.level === L.id) drawItem(g, it, cam, 1, S.sel && S.sel.type === 'item' && S.sel.id === it.id);
}
// On a block layer: the items on any level that stand in it (from their level's floor up to their height).
function drawLayerItems(g, cam, k) {
  const [Z0, Z1] = layerZ(k);
  for (const it of S.plan.items) {
    const L = S.plan.levels.find(l => l.id === it.level), z = L ? L.elev + (it.z || 0) : 0;
    if (L && z < Z1 - 1e-6 && z + (it.h || 1) > Z0 + 1e-6) drawItem(g, it, cam, 1, S.sel && S.sel.type === 'item' && S.sel.id === it.id);
  }
}
function drawItem(g, it, cam, alpha, selected) {
  const s = cam.s, R = itemRect(it), mount = mountOf(it);
  const px = cam.ox + R.x * s, py = cam.oy + R.y * s, w = R.w * s, hh = R.h * s, ins = Math.min(2.5, s * 0.08);
  g.globalAlpha = alpha;
  roundRectPath(g, px + ins, py + ins, w - 2 * ins, hh - 2 * ins, Math.min(6, s * 0.22));
  g.fillStyle = mount === 'wall' || mount === 'ceiling' ? hexA(it.color, 0.55) : it.color; g.fill();
  if (mount === 'wall' || mount === 'ceiling') g.setLineDash(mount === 'ceiling' ? [2, 3] : [5, 3]);   // hung up, not standing
  g.lineWidth = selected ? 2.5 : 1.2; g.strokeStyle = it.bad ? T.bad || '#c0392b' : selected ? T.accent : hexA(T.ink, 0.85); g.stroke();
  g.setLineDash([]);
  if (mount === 'window') {                                  // a pane down the middle of the wall
    g.strokeStyle = 'rgba(255,255,255,0.85)'; g.lineWidth = Math.max(1, s * 0.06); g.beginPath();
    if (R.w >= R.h) { g.moveTo(px + ins + 1, py + hh / 2); g.lineTo(px + w - ins - 1, py + hh / 2); } else { g.moveTo(px + w / 2, py + ins + 1); g.lineTo(px + w / 2, py + hh - ins - 1); }
    g.stroke();
  }
  const fw = Math.max(2, s * 0.13), ink = textOn(it.color) === '#ffffff' ? 'rgba(255,255,255,0.8)' : 'rgba(26,39,46,0.7)';
  g.strokeStyle = ink; g.lineWidth = fw; g.beginPath();
  const e = ins + fw / 2 + 1;
  if (it.rot === 0) { g.moveTo(px + e, py + hh - e); g.lineTo(px + w - e, py + hh - e); }
  else if (it.rot === 90) { g.moveTo(px + e, py + e); g.lineTo(px + e, py + hh - e); }
  else if (it.rot === 180) { g.moveTo(px + e, py + e); g.lineTo(px + w - e, py + e); }
  else { g.moveTo(px + w - e, py + e); g.lineTo(px + w - e, py + hh - e); }
  g.stroke();
  if (it.type === 'stairs' && s >= 8) {
    const along = (it.rot === 0 || it.rot === 180) ? 'y' : 'x';
    const len = along === 'y' ? hh : w, n = Math.max(3, Math.round(len / Math.max(6, s * 0.34)));
    g.strokeStyle = ink; g.lineWidth = 1; g.beginPath();
    for (let i = 1; i < n; i++) {
      if (along === 'y') { const yy = py + (hh * i) / n; g.moveTo(px + ins + 2, yy); g.lineTo(px + w - ins - 2, yy); }
      else { const xx = px + (w * i) / n; g.moveTo(xx, py + ins + 2); g.lineTo(xx, py + hh - ins - 2); }
    }
    g.stroke();
    const dir = { 0: [0, -1], 90: [1, 0], 180: [0, 1], 270: [-1, 0] }[it.rot];
    const cx = px + w / 2, cy = py + hh / 2, half = (along === 'y' ? hh : w) * 0.32;
    const tx = cx + dir[0] * half, ty = cy + dir[1] * half;
    g.lineWidth = Math.max(1.5, s * 0.08); g.beginPath();
    g.moveTo(cx - dir[0] * half, cy - dir[1] * half); g.lineTo(tx, ty);
    const a = Math.atan2(dir[1], dir[0]), hl = Math.max(4, s * 0.25);
    g.moveTo(tx, ty); g.lineTo(tx - hl * Math.cos(a - 0.6), ty - hl * Math.sin(a - 0.6));
    g.moveTo(tx, ty); g.lineTo(tx - hl * Math.cos(a + 0.6), ty - hl * Math.sin(a + 0.6));
    g.stroke();
  } else if (Math.min(w, hh) >= 14) upright(g, cam, px, py, w, hh, (bx, by, bw, bh) => {
    const lines = fitLabel(g, it.label, bw - 6, bh - 4, clamp(Math.round(s * 0.36), 9, 13));
    if (lines) {
      g.fillStyle = textOn(it.color); g.textAlign = 'center'; g.textBaseline = 'middle';
      const lh = lines.fs + 2, y0 = by + bh / 2 - (lines.text.length - 1) * lh / 2 + 0.5;
      lines.text.forEach((t, i) => g.fillText(t, bx + bw / 2, y0 + i * lh));
    }
  });
  g.globalAlpha = 1;
}
// Fit a label into a box: shrink, then try two lines, then truncate with an ellipsis.
function fitLabel(g, label, maxW, maxH, fs0) {
  const fits = (t) => g.measureText(t).width <= maxW;
  for (let fs = fs0; fs >= 8; fs--) {
    g.font = `600 ${fs}px ${FONT_UI}`;
    if (fits(label) && maxH >= fs) return { fs, text: [label] };
    const words = label.split(/\s+/);
    if (words.length > 1 && maxH >= fs * 2 + 2) {
      for (let k = 1; k < words.length; k++) {
        const a = words.slice(0, k).join(' '), b = words.slice(k).join(' ');
        if (fits(a) && fits(b)) return { fs, text: [a, b] };
      }
    }
  }
  const fs = 8;
  g.font = `600 ${fs}px ${FONT_UI}`;
  if (maxH < fs) return null;
  let t = label;
  while (t.length > 1 && !fits(t + '…')) t = t.slice(0, -1);
  if (t.length < 2) { t = abbreviate(label); return fits(t) ? { fs, text: [t] } : null; }
  return { fs, text: [t + '…'] };
}
function drawAltars(g, cam) {
  const s = cam.s;
  for (const it of S.plan.items) {
    if (it.type !== 'altar') continue;
    const A = altarRect(it), px = cam.ox + A.x * s, py = cam.oy + A.y * s;
    g.fillStyle = hexA(T.shroud, 0.035); g.fillRect(px, py, A.w * s, A.h * s);
    g.setLineDash([9, 5]); g.lineWidth = 1.6; g.strokeStyle = T.shroud;
    g.strokeRect(px, py, A.w * s, A.h * s); g.setLineDash([]);
    g.font = `700 10.5px ${FONT_UI}`; g.fillStyle = T.shroud; g.textAlign = 'left'; g.textBaseline = 'bottom';
    upright(g, cam, px, py, A.w * s, A.h * s, (bx, by) => g.fillText(`ALTAR BUILD AREA · ${S.plan.altar} × ${S.plan.altar} M · ±${S.plan.altar / 2} M UP AND DOWN (UNCONFIRMED)`, bx + 2, by - 3));
  }
}
function drawOverlays(g, cam) {
  const s = cam.s, P = S.plan, ox = cam.ox, oy = cam.oy;
  if (S.preview) {
    for (const grp of S.preview) {
      const e = P.palette[grp.ch];
      g.fillStyle = grp.ch === ' ' ? hexA(T.bad, 0.25) : hexA(grp.color || (e ? e.color : T.accent), 0.62);
      for (const [x, y] of grp.cells) if (inB(x, y)) g.fillRect(ox + x * s, oy + y * s, s, s);
    }
  }
  const F = S.float;
  if (F) {
    for (const [cx, cy, ch] of F.cells) {
      const e = P.palette[ch];
      g.fillStyle = e ? e.color : '#d0368a';
      g.fillRect(ox + (F.R.x + F.dx + cx) * s, oy + (F.R.y + F.dy + cy) * s, s + 0.5, s + 0.5);
    }
  }
  let R = null;
  if (F) R = { x: F.R.x + F.dx, y: F.R.y + F.dy, w: F.R.w, h: F.R.h };
  else if (G && G.type === 'marquee') R = rectFrom(G.a, G.b);
  else if (S.sel && S.sel.type === 'cells') R = S.sel.rect;
  if (R) {
    g.fillStyle = T['accent-soft']; g.fillRect(ox + R.x * s, oy + R.y * s, R.w * s, R.h * s);
    g.setLineDash([5, 4]); g.lineWidth = 1.5; g.strokeStyle = T.accent;
    g.strokeRect(ox + R.x * s + 0.5, oy + R.y * s + 0.5, R.w * s, R.h * s); g.setLineDash([]);
    sizeTag(g, `${metres(R.w)} × ${metres(R.h)} m`, ox + R.x * s, oy + R.y * s, R.w * s, R.h * s);
  }
  if (G && G.type === 'zone') {
    const Z = rectFrom(G.a, G.b), c = ZONE_COLORS[P.zones.length % ZONE_COLORS.length];
    g.fillStyle = hexA(c, 0.12); g.fillRect(ox + Z.x * s, oy + Z.y * s, Z.w * s, Z.h * s);
    g.setLineDash([6, 4]); g.lineWidth = 1.5; g.strokeStyle = c; g.strokeRect(ox + Z.x * s, oy + Z.y * s, Z.w * s, Z.h * s); g.setLineDash([]);
    sizeTag(g, `${metres(Z.w)} × ${metres(Z.h)} m`, ox + Z.x * s, oy + Z.y * s, Z.w * s, Z.h * s);
  }
  if (S.tool === 'wall' && S.wallChain) {                    // the run being drawn, and the whole chain so far
    const c = S.wallChain, last = c.pts[c.pts.length - 1], run = Math.max(Math.abs(c.hover[0] - last[0]), Math.abs(c.hover[1] - last[1]));
    const diag = c.hover[0] !== last[0] && c.hover[1] !== last[1];
    let len = 0;
    const pts = [...c.pts, c.hover];
    for (let i = 0; i + 1 < pts.length; i++) len += Math.max(Math.abs(pts[i + 1][0] - pts[i][0]), Math.abs(pts[i + 1][1] - pts[i][1])) * (pts[i + 1][0] !== pts[i][0] && pts[i + 1][1] !== pts[i][1] ? Math.SQRT2 : 1);
    sizeTag(g, `${fmt(run * (diag ? Math.SQRT2 : 1) * CM())} m${c.pts.length > 1 ? ` · ${fmt(len * CM())} m in all` : ''}`, ox + c.hover[0] * s, oy + c.hover[1] * s, s, s);
  }
  if (G && (G.type === 'line' || G.type === 'rect' || G.type === 'room')) {
    const Z = G.type === 'line' ? null : rectFrom(G.a, G.b);
    if (Z) sizeTag(g, `${metres(Z.w)} × ${metres(Z.h)} m`, ox + Z.x * s, oy + Z.y * s, Z.w * s, Z.h * s);
    else sizeTag(g, `${metres(Math.max(Math.abs(G.b[0] - G.a[0]), Math.abs(G.b[1] - G.a[1])) + 1)} m`, ox + G.b[0] * s, oy + G.b[1] * s, s, s);
  }
  drawMirror(g, cam);
  drawTerrainBrush(g, cam);
  if (S.tool === 'place' && !G) drawPlaceGhost(g, cam);
  if (S.tool === 'item' && S.ghostItem && S.itemDef && S.hoverIn && !G) {
    const gh = S.ghostItem, def = S.itemDef;
    const gi = { ...def, label: def.name, x: gh.x, y: gh.y, rot: gh.rot != null ? gh.rot : S.itemRot, ...(IN_WALL.has(mountOf(def)) ? { d: 1 } : {}), bad: gh.bad };
    drawItem(g, gi, cam, 0.55, true);
    for (const c of mirrorItems(gi)) drawItem(g, c, cam, 0.35, true);
    if (def.type === 'altar' && S.opt.altar) {
      const A = altarRect({ x: gh.x, y: gh.y, w: def.w, d: def.d, rot: S.itemRot });
      g.setLineDash([9, 5]); g.lineWidth = 1.2; g.strokeStyle = hexA(T.shroud, 0.6);
      g.strokeRect(ox + A.x * s, oy + A.y * s, A.w * s, A.h * s); g.setLineDash([]);
    }
  }
  drawHoverGhost(g, cam);
  if (S.hover && S.hoverIn && !G && (PAINT_TOOLS.has(S.tool) || S.tool === 'erase') && inB(S.hover[0], S.hover[1])) {
    g.lineWidth = 1.5; g.strokeStyle = T.accent;
    g.strokeRect(ox + S.hover[0] * s + 0.75, oy + S.hover[1] * s + 0.75, s - 1.5, s - 1.5);
  }
  if (S.measure) {
    const [ax, ay] = S.measure.a, [bx, by] = S.measure.b;
    const pax = ox + ax * s, pay = oy + ay * s, pbx = ox + bx * s, pby = oy + by * s;
    g.strokeStyle = T.accent; g.lineWidth = 2; g.setLineDash([]);
    g.beginPath(); g.moveTo(pax, pay); g.lineTo(pbx, pby); g.stroke();
    g.fillStyle = T.accent;
    for (const [qx, qy] of [[pax, pay], [pbx, pby]]) { g.beginPath(); g.arc(qx, qy, 3.5, 0, Math.PI * 2); g.fill(); }
    sizeTag(g, measureText(), Math.min(pax, pbx), Math.min(pay, pby), Math.abs(pbx - pax), Math.abs(pby - pay), true);
  }
}
function measureText() {
  const [ax, ay] = S.measure.a, [bx, by] = S.measure.b;
  const dx = Math.abs(bx - ax), dy = Math.abs(by - ay), d = Math.hypot(dx, dy);
  return `${metres(dx)} × ${metres(dy)} m · ${metres(d)} m straight`;
}
// A tag over the top-right corner of a box of the unturned view, as the box shows on screen (beside: just right of it).
function sizeTag(g, text, x0, y0, bw, bh, beside) {
  const b = screenBox(S.cam, x0, y0, bw, bh), x = beside ? b.x + b.w + 6 : b.x + b.w, y = beside ? b.y - 4 : b.y;
  g.save(); g.setTransform(DPR, 0, 0, DPR, 0, 0);
  g.font = `600 11px ${FONT_MONO}`;
  const w = g.measureText(text).width + 12, hh = 19;
  let bx = beside ? x : x - w, by = y - hh - 4;
  bx = clamp(bx, RUL.left + 2, W2 - w - 2); by = clamp(by, RUL.top + 2, H2 - hh - 2);
  roundRectPath(g, bx, by, w, hh, 5); g.fillStyle = T.ink; g.fill();
  g.fillStyle = T.panel; g.textAlign = 'left'; g.textBaseline = 'middle'; g.fillText(text, bx + 6, by + hh / 2 + 0.5);
  g.restore();
}
// The rulers read whichever plan axis runs across or down the screen (x and y swap when the view is turned).
function drawRulers(g, cam, W, H) {
  const s = cam.s, P = S.plan, top = RUL.top, left = RUL.left, r = camRot(cam);
  g.fillStyle = T.panel; g.fillRect(0, 0, W, top); g.fillRect(0, 0, left, H);
  if (S.hover && S.hoverIn) {
    const b = screenBox(cam, cam.ox + S.hover[0] * s, cam.oy + S.hover[1] * s, s, s);
    g.fillStyle = T['accent-soft'];
    g.fillRect(b.x, 0, b.w, top); g.fillRect(0, b.y, left, b.h);
  }
  const cm = CM(), stepM = [1, 2, 5, 10, 20, 50, 100].find(v => (v / cm) * s >= 28) || 100, step = Math.round(stepM / cm);
  const across = r % 2 ? 'y' : 'x', down = r % 2 ? 'x' : 'y';
  const at = (axis, v) => toScreen(cam, cam.ox + (axis === 'x' ? v : 0) * s, cam.oy + (axis === 'y' ? v : 0) * s);
  g.font = `500 10px ${FONT_MONO}`; g.fillStyle = T.muted; g.textBaseline = 'middle';
  g.beginPath();
  g.textAlign = 'center';
  for (let v = 0; v <= (across === 'x' ? P.w : P.h); v += step) {
    const px = Math.round(at(across, v)[0]) + 0.5;
    if (px < left + 8 || px > W) continue;
    g.moveTo(px, top - 5); g.lineTo(px, top); g.fillText(fmt(v * cm), px, 9);
  }
  g.textAlign = 'right';
  for (let v = 0; v <= (down === 'x' ? P.w : P.h); v += step) {
    const py = Math.round(at(down, v)[1]) + 0.5;
    if (py < top + 6 || py > H) continue;
    g.moveTo(left - 5, py); g.lineTo(left, py); g.fillText(fmt(v * cm), left - 7, py);
  }
  g.strokeStyle = T.faint; g.lineWidth = 1; g.stroke();
  g.strokeStyle = T.line; g.beginPath(); g.moveTo(0, top + 0.5); g.lineTo(W, top + 0.5); g.moveTo(left + 0.5, 0); g.lineTo(left + 0.5, H); g.stroke();
  g.fillStyle = T.panel; g.fillRect(0, 0, left, top);
  g.fillStyle = T.faint; g.textAlign = 'center'; g.font = `600 9px ${FONT_MONO}`; g.fillText('M', left / 2, top / 2 + 1);
}
const COMPASS = { dx: 22, dy: 24, r: 13 };                       // (from the view's top-right corner)
function drawScaleAndCompass(g, cam, W, H) {
  const s = cam.s;
  const cm = CM(), seg = s / cm, metresLen = [1, 2, 5, 10, 20, 50].find(v => v * seg >= 56) || 50, len = metresLen * seg;
  const x = RUL.left + 12, y = H - 14;
  const label = `${metresLen} m`;
  g.font = `600 10.5px ${FONT_MONO}`;
  const tw = g.measureText(label).width;
  roundRectPath(g, x - 6, y - 17, Math.max(len, tw) + 12, 25, 6); g.fillStyle = T.glass; g.fill();
  g.fillStyle = T.ink; g.fillRect(x, y, len, 3);
  g.fillStyle = T.sheet; for (let i = 1; i < metresLen && metresLen <= 10; i += 2) g.fillRect(x + i * seg, y + 0.75, seg, 1.5);
  g.fillStyle = T.ink; g.textAlign = 'left'; g.textBaseline = 'bottom'; g.fillText(label, x, y - 3);
  const cx = W - COMPASS.dx, cy = RUL.top + COMPASS.dy, r = camRot(cam);
  g.beginPath(); g.arc(cx, cy, COMPASS.r, 0, Math.PI * 2); g.fillStyle = T.glass; g.fill();
  g.strokeStyle = r ? T.accent : T.line; g.lineWidth = r ? 1.5 : 1; g.stroke();   // (turned: click it for north up)
  g.save(); g.translate(cx, cy); g.rotate(r * Math.PI / 2);
  g.beginPath(); g.moveTo(0, -9); g.lineTo(4.5, 3); g.lineTo(0, 0.5); g.lineTo(-4.5, 3); g.closePath();
  g.fillStyle = T.accent; g.fill();
  g.restore();
  const [nx, ny] = turnVec(0, 8, r);
  g.fillStyle = T.ink; g.font = `700 9px ${FONT_UI}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('N', cx + nx, cy + ny);
}
const onCompass = p => Math.hypot(p.sx - (W2 - COMPASS.dx), p.sy - (RUL.top + COMPASS.dy)) <= COMPASS.r + 2;
function draw2d() {
  const g = ctx;
  g.setTransform(DPR, 0, 0, DPR, 0, 0);
  if (!S.plan) { g.fillStyle = T.panel || '#eee'; g.fillRect(0, 0, W2, H2); return; }
  const r = camRot(S.cam), [cx, cy] = viewMid();
  if (r) { g.translate(cx, cy); g.rotate(r * Math.PI / 2); g.translate(-cx, -cy); }
  renderPlan(g, S.cam, W2, H2, { levelIdx: S.levelIdx, layer: true, ghost: S.opt.ghost, olBelow: S.opt.olBelow, olAbove: S.opt.olAbove, zones: S.opt.zones, altar: S.opt.altar });
  drawOverlays(g, S.cam);
  g.setTransform(DPR, 0, 0, DPR, 0, 0);
  drawRulers(g, S.cam, W2, H2);
  drawScaleAndCompass(g, S.cam, W2, H2);
}
function fitView(toContent) {
  if (!S.plan) return;
  if (W2 < 50 || H2 < 50) { S.needFit = true; return; }
  const P = S.plan;
  let B = toContent ? boundsOf(P.levels) : null;
  if (B) { const pad = 3; B = { x: B.x - pad, y: B.y - pad, w: B.w + pad * 2, h: B.h + pad * 2 }; }
  else B = { x: 0, y: 0, w: P.w, h: P.h };
  const aw = Math.max(50, W2 - RUL.left - 24), ah = Math.max(50, H2 - RUL.top - 24), odd = camRot(S.cam) % 2;
  const s = clamp(odd ? Math.min(aw / B.h, ah / B.w) : Math.min(aw / B.w, ah / B.h), 3, 48);
  const [mx, my] = fromScreen(S.cam, RUL.left + 12 + aw / 2, RUL.top + 12 + ah / 2);   // (the middle of the free area)
  S.cam.s = s;
  S.cam.ox = mx - (B.x + B.w / 2) * s;
  S.cam.oy = my - (B.y + B.h / 2) * s;
  updateZoom(); req2d();
}
function zoomAt(px, py, f) {
  const s0 = S.cam.s, s1 = clamp(s0 * f, 3, 96), k = s1 / s0;
  S.cam.ox = px - (px - S.cam.ox) * k; S.cam.oy = py - (py - S.cam.oy) * k; S.cam.s = s1;
  updateZoom(); req2d();
}
function updateZoom() {
  $('#stZoom').textContent = Math.round(S.cam.s / 16 * 100) + '%';
  const r = camRot(S.cam), b = $('#turnReset');
  if (b) { b.disabled = !r; b.textContent = r ? `${r * 90}°` : 'N'; b.title = r ? `Turned ${r * 90}° clockwise: back to north up` : 'North is up'; }
}

// ---------------------------------------------------------------------------
// 2D input
// ---------------------------------------------------------------------------
let G = null;            // active gesture
let spaceDown = false;
const P2 = new Map();
function loc2(e) {
  const r = c2d.getBoundingClientRect(), sx = e.clientX - r.left, sy = e.clientY - r.top, [x, y] = fromScreen(S.cam, sx, sy);
  return { x, y, sx, sy };
}
function setCursor() {
  let c = 'crosshair';
  if (spaceDown || S.tool === 'pan') c = G && G.type === 'pan' ? 'grabbing' : 'grab';
  else if (S.tool === 'select') c = G && G.type && G.type.startsWith('move') ? 'grabbing' : 'default';
  c2d.style.cursor = c;
}
function updateHover(p) {
  if (!S.plan) return;
  const [gx, gy] = toGridPt(p), cx = Math.floor(gx), cy = Math.floor(gy);
  S.hoverIn = p.sx > RUL.left && p.sy > RUL.top && p.sx < W2 && p.sy < H2;
  S.hover = [cx, cy];
  if (S.tool === 'item' && S.itemDef) S.ghostItem = ghostFor(gx, gy);
  updateGroundOut(cx, cy);
  if (S.tool === 'pieces' && !G && pieceDef().shape === 'click') S.preview = S.hoverIn && inB(cx, cy) ? pieceGroups(makePiece([cx, cy], [cx, cy])) : null;
  const st = $('#stCursor');
  if (S.hoverIn && inB(cx, cy)) st.textContent = `x ${metres(cx)} m · y ${metres(cy)} m`;
  else st.textContent = 'x – · y –';
  hoverMaterial(cx, cy, S.hoverIn && inB(cx, cy));
  if (S.hoverIn && inB(cx, cy)) altarReadout(cx, cy, hoverZ()); else altarReadout(null);
  if (S.tool === 'select' && !G) {
    const over = hitItem(gx, gy) || (S.sel && S.sel.type === 'cells' && pointInRect(cx, cy, S.sel.rect));
    c2d.style.cursor = spaceDown ? 'grab' : (over ? 'move' : 'default');
  }
}
const pointInRect = (x, y, R) => x >= R.x && y >= R.y && x < R.x + R.w && y < R.y + R.h;
function hitItem(gx, gy) {
  const L = lv();
  if (!L) return null;
  for (let i = S.plan.items.length - 1; i >= 0; i--) {
    const it = S.plan.items[i];
    if (it.level !== L.id) continue;
    const R = itemRect(it);
    if (gx >= R.x && gx < R.x + R.w && gy >= R.y && gy < R.y + R.h) return it;
  }
  return null;
}
function hitZone(p, gx, gy) {
  const L = lv();
  for (let i = S.plan.zones.length - 1; i >= 0; i--) {
    const z = S.plan.zones[i];
    if (z.level !== L.id) continue;
    const b = zoneLabelBoxes.get(z.id);
    if (b && p.sx >= b.x && p.sx <= b.x + b.w && p.sy >= b.y && p.sy <= b.y + b.h) return z;
    const band = Math.max(0.3, 5 / S.cam.s);
    const inside = gx >= z.x - band && gx <= z.x + z.w + band && gy >= z.y - band && gy <= z.y + z.h + band;
    const deep = gx > z.x + band && gx < z.x + z.w - band && gy > z.y + band && gy < z.y + z.h - band;
    if (inside && !deep) return z;
  }
  return null;
}
function pinchStart() {
  const [a, b] = [...P2.values()];
  return { type: 'pinch', d0: Math.hypot(a.x - b.x, a.y - b.y) || 1, m0: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }, s0: S.cam.s, ox0: S.cam.ox, oy0: S.cam.oy };
}
function pinchMove() {
  const [a, b] = [...P2.values()];
  const d = Math.hypot(a.x - b.x, a.y - b.y) || 1, m = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
  const s1 = clamp(G.s0 * d / G.d0, 3, 96), k = s1 / G.s0;
  S.cam.s = s1; S.cam.ox = m.x - (G.m0.x - G.ox0) * k; S.cam.oy = m.y - (G.m0.y - G.oy0) * k;
  updateZoom(); req2d();
}
function abortGesture() {
  if (!G) return;
  if (['paint', 'moveItem', 'moveZone', 'moveCells', 'replace'].includes(G.type)) { S.float = null; cancelAction(); }
  S.preview = null; G = null;
  req2d(); mark3d();
}
function toolDown(p, e) {
  const [gx, gy] = toGridPt(p), cx = Math.floor(gx), cy = Math.floor(gy);
  const erase = e.button === 2, t = S.tool;
  if (S.readOnly && !['select', 'measure', 'pan'].includes(t)) { toast('This plan is view-only.'); return; }
  if (liveBase != null) liveCommit();
  if (document.activeElement && document.activeElement !== document.body && document.activeElement.blur) document.activeElement.blur();
  if (S.mirrorPick) {                                        // placing the mirror centre: snap to edges and middles
    S.mirror.cx = clamp(Math.round(gx * 2) / 2, 0, S.plan.w); S.mirror.cy = clamp(Math.round(gy * 2) / 2, 0, S.plan.h);
    S.mirrorPick = false; renderOptbar(); req2d(); return;
  }
  switch (t) {
    case 'paint': case 'erase': {
      const ch = (t === 'erase' || erase) ? ' ' : S.brush;
      begin(); setCellMirrored(lv(), cx, cy, ch);
      G = { type: 'paint', ch, last: [cx, cy] }; mark3d(); break;
    }
    case 'line': G = { type: 'line', a: [cx, cy], b: [cx, cy], ch: erase ? ' ' : S.brush }; S.preview = mirrorGroups([{ cells: [[cx, cy]], ch: G.ch }]); break;
    case 'rect': G = { type: 'rect', a: [cx, cy], b: [cx, cy], ch: erase ? ' ' : S.brush }; S.preview = mirrorGroups([{ cells: [[cx, cy]], ch: G.ch }]); break;
    case 'room': G = { type: 'room', a: [cx, cy], b: [cx, cy], erase }; S.preview = mirrorGroups(erase ? [{ cells: [[cx, cy]], ch: ' ' }] : roomGroups(G.a, G.b)); break;
    case 'fill': {
      if (!inB(cx, cy)) break;
      begin(); const n = floodMirrored(lv(), cx, cy, erase ? ' ' : S.brush); commit();
      if (n > 400) toast(`Filled ${n} squares. Undo with Ctrl+Z if that spilled out.`);
      break;
    }
    case 'item': {
      if (!S.itemDef) { toast('Pick an item in the Items tab first.'); openTab('items'); break; }
      if (erase) { const hit = hitItem(gx, gy); if (hit) { begin(); S.plan.items = S.plan.items.filter(i => i !== hit); commit(); } break; }
      S.ghostItem = ghostFor(gx, gy); placeItem(); break;
    }
    case 'zone': if (inB(cx, cy)) G = { type: 'zone', a: [cx, cy], b: [cx, cy] }; break;
    case 'terrain': G = terrainDown(cx, cy, erase); break;
    case 'pieces': {
      if (pieceDef().shape === 'click') { if (inB(cx, cy)) { writePiece(makePiece([cx, cy], [cx, cy])); S.preview = null; } break; }
      G = { type: 'piece', a: [cx, cy], b: [cx, cy] }; G.cells = makePiece(G.a, G.b); S.preview = pieceGroups(G.cells); break;
    }
    case 'place': if (erase) setTool('select'); else placeHere(cx, cy); break;
    case 'wall': wallDown(cx, cy, erase); break;
    case 'built': builtDown(gx, gy, cx, cy, e); break;
    case 'replace': replaceDown(cx, cy, erase); break;
    case 'measure': { const a = [Math.round(gx), Math.round(gy)]; S.measure = { a, b: a.slice() }; G = { type: 'measure' }; break; }
    case 'select': selectDown(p, gx, gy, cx, cy); break;
  }
}
function selectDown(p, gx, gy, cx, cy) {
  const it = hitItem(gx, gy);
  if (it) {
    S.sel = { type: 'item', id: it.id }; renderInspector();
    if (!S.readOnly) { begin(); G = { type: 'moveItem', id: it.id, grab: [gx - it.x, gy - it.y] }; }
    return;
  }
  if (S.sel && S.sel.type === 'cells' && pointInRect(cx, cy, S.sel.rect) && !S.readOnly) {
    begin(); liftSelection(); G = { type: 'moveCells', start: [cx, cy] }; return;
  }
  const z = hitZone(p, gx, gy);
  if (z) {
    S.sel = { type: 'zone', id: z.id }; renderInspector();
    if (!S.readOnly) { begin(); G = { type: 'moveZone', id: z.id, grab: [gx - z.x, gy - z.y] }; }
    return;
  }
  S.sel = null; renderInspector();
  G = { type: 'marquee', a: [cx, cy], b: [cx, cy] };
}
function toolMove(p, e) {
  const [gx, gy] = toGridPt(p), cx = Math.floor(gx), cy = Math.floor(gy), P = S.plan;
  switch (G.type) {
    case 'paint':
      if (cx !== G.last[0] || cy !== G.last[1]) { for (const [x, y] of lineCells(G.last[0], G.last[1], cx, cy)) setCellMirrored(lv(), x, y, G.ch); G.last = [cx, cy]; mark3d(); }
      break;
    case 'line': G.b = e.shiftKey ? constrainLine(G.a, [cx, cy]) : [cx, cy]; S.preview = mirrorGroups([{ cells: lineCells(G.a[0], G.a[1], G.b[0], G.b[1]), ch: G.ch }]); break;
    case 'rect': G.b = [cx, cy]; S.preview = mirrorGroups([{ cells: rectCells(G.a, G.b, S.rectFilled, S.round), ch: G.ch }]); break;
    case 'room': G.b = [cx, cy]; S.preview = mirrorGroups(G.erase ? [{ cells: rectCells(G.a, G.b, true, S.round), ch: ' ' }] : roomGroups(G.a, G.b)); break;
    case 'zone': case 'marquee': G.b = [clamp(cx, 0, P.w - 1), clamp(cy, 0, P.h - 1)]; break;
    case 'terrain': terrainMove(G, cx, cy); break;
    case 'piece': { G.b = [cx, cy]; G.cells = makePiece(G.a, G.b); S.preview = pieceGroups(G.cells); const o = $('#pieceOut'); if (o) o.textContent = pieceSummary(G.cells) || pieceDef().how; break; }
    case 'measure': S.measure.b = [Math.round(gx), Math.round(gy)]; updateOptReadout(); break;
    case 'wall': wallMove(cx, cy); break;
    case 'built': builtMove(cx, cy); break;
    case 'replace': replaceMove(cx, cy); break;
    case 'moveItem': {
      const it = findItem(G.id); if (!it) break;
      const R = itemRect(it), st = itemStep(P);
      if (IN_WALL.has(it.mount)) {                           // a door or window slides along walls, hopping to the one under the cursor
        const IL = S.plan.levels.find(l => l.id === it.level) || lv();   // (along its own level's walls)
        const slot = wallSlot(layerOn() ? { ...IL, anyBase: true } : IL, gx, gy, it.w, it.rot);
        if (slot) { it.x = slot.x; it.y = slot.y; it.rot = slot.rot; mark3d(); break; }
      }
      it.x = clamp(snapStep(gx - G.grab[0], st), 0, Math.max(0, P.w - R.w)); it.y = clamp(snapStep(gy - G.grab[1], st), 0, Math.max(0, P.h - R.h));
      mark3d(); break;
    }
    case 'moveZone': {
      const z = findZone(G.id); if (!z) break;
      z.x = clamp(Math.round(gx - G.grab[0]), 0, Math.max(0, P.w - z.w)); z.y = clamp(Math.round(gy - G.grab[1]), 0, Math.max(0, P.h - z.h));
      break;
    }
    case 'moveCells': moveFloat(cx - G.start[0], cy - G.start[1]); break;
  }
}
function toolUp() {
  const L = lv();
  switch (G.type) {
    case 'paint': case 'terrain': commit(); break;
    case 'piece': if (G.cells && G.cells.length) writePiece(G.cells); break;
    case 'line': case 'rect': case 'room': {
      const groups = S.preview || [], Z = rectFrom(G.a, G.b), pal = S.plan.palette;
      const mat = ch => (pal[ch] ? matName(pal[ch].name) : 'erase');
      const label = G.type === 'room' ? (G.erase ? `Clear ${metres(Z.w)} × ${metres(Z.h)} m` : `Room · ${metres(Z.w)} × ${metres(Z.h)} m${S.roomThick > CM() ? `, ${fmt(S.roomThick)} m walls` : ''}`)
        : G.ch === ' ' ? `Erase a ${G.type === 'line' ? 'line' : 'box'}` : G.type === 'line' ? `Line · ${mat(G.ch)} · ${metres(Math.max(Math.abs(G.b[0] - G.a[0]), Math.abs(G.b[1] - G.a[1])) + 1)} m`
        : `${S.round ? 'Circle' : 'Rectangle'} · ${mat(G.ch)} · ${metres(Z.w)} × ${metres(Z.h)} m`;
      begin(label + (L ? ` · ${L.name.replace(/^[^:]{1,30}:\s+/, '')}` : '')); for (const grp of groups) for (const [x, y] of grp.cells) paintSquare(L, x, y, grp.ch, G.type === 'room'); commit();
      break;
    }
    case 'zone': addZone(G.a, G.b); break;
    case 'wall': wallUp(); return;                             // (a chain of corners keeps its preview)
    case 'replace': replaceUp(); break;
    case 'marquee': {
      const R = rectFrom(G.a, G.b), one = R.w === 1 && R.h === 1;
      const here = one ? squareMaterials(R.x, R.y) : [];
      S.sel = (one && !here.length) ? null : { type: 'cells', rect: R };
      renderInspector();
      if (here.length) showMaterial(here[0].k);                // a click on a square: its material in the Materials tab
      break;
    }
    case 'moveItem': case 'moveZone': commit(); renderInspector(); break;
    case 'moveCells': dropFloat(); commit(); renderInspector(); break;
  }
  S.preview = null;
}
c2d.addEventListener('pointerdown', e => {
  if (!S.plan) return;
  const p = loc2(e);
  P2.set(e.pointerId, p);
  try { c2d.setPointerCapture(e.pointerId); } catch { /* ignore */ }
  if (P2.size === 2) { abortGesture(); G = pinchStart(); return; }
  if (P2.size > 2 || G) return;
  if (e.button === 0 && camRot(S.cam) && onCompass(p)) { P2.delete(e.pointerId); setViewTurn(0); return; }   // (the compass: north up)
  if (e.button === 1 || spaceDown || S.tool === 'pan' || p.sx < RUL.left || p.sy < RUL.top) {
    G = { type: 'pan', sx: p.x, sy: p.y, ox: S.cam.ox, oy: S.cam.oy }; setCursor(); e.preventDefault(); return;
  }
  if (e.button !== 0 && e.button !== 2) return;
  updateHover(p);
  toolDown(p, e);
  setCursor(); req2d();
});
c2d.addEventListener('pointermove', e => {
  if (!S.plan) return;
  const p = loc2(e);
  if (P2.has(e.pointerId)) P2.set(e.pointerId, p);
  if (G && G.type === 'pinch') { if (P2.size >= 2) pinchMove(); return; }
  updateHover(p);
  if (G && G.type === 'pan') { S.cam.ox = G.ox + p.x - G.sx; S.cam.oy = G.oy + p.y - G.sy; }
  else if (G) toolMove(p, e);
  else if (S.tool === 'wall' && S.wallChain) { const [gx, gy] = toGridPt(p); wallMove(Math.floor(gx), Math.floor(gy)); }
  req2d();
});
c2d.addEventListener('dblclick', () => { if (S.tool === 'wall' && S.wallChain) wallFinish(); });
function endPointer(e) {
  if (!P2.has(e.pointerId)) return;
  P2.delete(e.pointerId);
  if (G && G.type === 'pinch') { if (P2.size === 0) G = null; return; }
  if (G && G.type !== 'pan') toolUp();
  G = null;
  setCursor(); req2d();
}
c2d.addEventListener('pointerup', endPointer);
c2d.addEventListener('pointercancel', e => { P2.delete(e.pointerId); abortGesture(); });
c2d.addEventListener('pointerleave', () => { if (!G) { S.hoverIn = false; if (S.tool === 'pieces') S.preview = null; $('#stCursor').textContent = 'x – · y –'; hoverMaterial(0, 0, false); req2d(); } });
c2d.addEventListener('contextmenu', e => e.preventDefault());
c2d.addEventListener('wheel', e => {
  if (!S.plan) return;
  e.preventDefault();
  const p = loc2(e);
  zoomAt(p.x, p.y, Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0015)));
}, { passive: false });
