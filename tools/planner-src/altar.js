
// ---------------------------------------------------------------------------
// Flame Altar build volume. The wiki sizes the area as a cube (40, 80, 120, 160 m a side); players report
// it's centred on the altar, so it reaches half its size above and below. Keen hasn't said, so the height
// is shown as unconfirmed: in game, the Construction Hammer shows the boundary line.
// ---------------------------------------------------------------------------
function altarVolumes(P) {
  const out = [];
  for (const it of P.items) if (it.type === 'altar') {
    const A = altarRect(it), L = P.levels.find(l => l.id === it.level), z = L ? L.elev : 0, half = P.altar / 2;
    out.push({ x0: A.x, y0: A.y, x1: A.x + A.w, y1: A.y + A.h, z0: z - half, z1: z + half });
  }
  return out;
}
// How high a square's contents reach above its level floor.
function cellTop(P, L, e) {
  if (e.kind === 'wall') return (e.base || 0) + (e.height || L.height);
  if (e.kind === 'block') return (e.base || 0) + (e.height || 1);
  if (e.kind === 'roof') return roofTop(e, P.cell);
  if (e.kind === 'door' || e.kind === 'window') return openingWall(e, L);
  return 0;                                                   // floors and water: their top is the level floor
}
const cellBase = e => (isFloorKind(e) ? -FLOOR_T : e.base || 0);   // and their course is just below it
function insideAltar(vols, x, y, z0, z1) {
  const cx = x + 0.5, cy = y + 0.5;
  return vols.some(v => cx >= v.x0 && cx <= v.x1 && cy >= v.y0 && cy <= v.y1 && z0 >= v.z0 - 0.01 && z1 <= v.z1 + 0.01);
}
// Squares (and items) on every level that stick out of all the altars' volumes.
function countOutsideAltar(P) {
  const vols = altarVolumes(P);
  if (!vols.length) return null;
  let n = 0;
  for (const L of P.levels) for (let y = 0; y < P.h; y++) {
    const row = L.grid[y];
    for (let x = 0; x < P.w; x++) {
      const e = row[x] !== ' ' && P.palette[row[x]];
      if (e && !insideAltar(vols, x, y, L.elev + cellBase(e), L.elev + cellTop(P, L, e))) n++;
    }
  }
  for (const it of P.items) {
    if (it.type === 'altar') continue;
    const L = P.levels.find(l => l.id === it.level), R = itemRect(it), z = (L ? L.elev : 0) + (it.z || 0);
    if (!insideAltar(vols, R.x + R.w / 2 - 0.5, R.y + R.h / 2 - 0.5, z, z + it.h)) n++;
  }
  return n;
}
// 2D: hatch squares on this level that fall outside the build volume, sideways or up and down.
function drawAltarOutside(g, L, cam, x0, x1, y0, y1) {
  const P = S.plan, vols = altarVolumes(P);
  if (!vols.length) return;
  const s = cam.s;
  g.strokeStyle = hexA(T.bad, 0.75); g.lineWidth = Math.max(1, s * 0.08); g.beginPath();
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
    const c = L.grid[y][x], e = c !== ' ' && P.palette[c];
    if (!e || insideAltar(vols, x, y, L.elev + cellBase(e), L.elev + cellTop(P, L, e))) continue;
    const px = cam.ox + x * s, py = cam.oy + y * s;
    g.moveTo(px + s * 0.2, py + s * 0.8); g.lineTo(px + s * 0.8, py + s * 0.2);
    g.moveTo(px + s * 0.2, py + s * 0.2); g.lineTo(px + s * 0.8, py + s * 0.8);
  }
  g.stroke();
}
// 3D: the volume's edges.
function altarBox(v, color) {
  const THREE = window.THREE, p = [];
  const X = [v.x0, v.x1], Z = [v.y0, v.y1], Y = [v.z0, v.z1];
  for (const y of Y) for (const [a, b] of [[[0, 0], [1, 0]], [[1, 0], [1, 1]], [[1, 1], [0, 1]], [[0, 1], [0, 0]]]) p.push(X[a[0]], y, Z[a[1]], X[b[0]], y, Z[b[1]]);
  for (const [i, j] of [[0, 0], [1, 0], [1, 1], [0, 1]]) p.push(X[i], Y[0], Z[j], X[i], Y[1], Z[j]);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(p, 3));
  const l = new THREE.LineSegments(geo, new THREE.LineDashedMaterial({ color, transparent: true, opacity: 0.55, dashSize: 2, gapSize: 1.2 }));
  l.computeLineDistances(); l.userData.ownMat = true;
  return l;
}
