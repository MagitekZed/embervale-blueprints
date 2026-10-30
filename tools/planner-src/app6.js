
// ---------------------------------------------------------------------------
// Plan pane
// ---------------------------------------------------------------------------
// Place another plan into this one (see place.js).
function placeSection() {
  const others = sortedPlans().filter(([id]) => id !== S.planId);
  if (!others.length) return null;
  const sel = h('select', { 'aria-label': 'Plan to place' }, ...others.map(([id, d]) => h('option', { value: id, text: `${str(d.name, 80) || 'Untitled plan'}${Number(d.cell) === 0.5 ? ' · 0.5 m' : ''}` })));
  return h('div', { class: 'section' }, h('h4', { text: 'Place another plan' }),
    h('p', { class: 'note', text: `Stamp a building from another plan into this one, simplified to ${fmt(S.plan.cell)} m squares: walls, doors and windows always survive, the rest goes by what covers most of each square, and roof heights are averaged. Levels line up by height. Items and areas come too.` }),
    h('div', { class: 'row' }, sel, h('button', { class: 'btn btn-sm btn-accent', type: 'button', text: 'Place…', disabled: S.readOnly, onclick: () => armPlace(sel.value) })));
}
function renderPlanPane() {
  const pane = $('#pane-plan');
  if (!S.plan) { pane.replaceChildren(); return; }
  const P = S.plan;
  const name = h('input', { type: 'text', value: P.name, maxlength: '80', 'aria-label': 'Plan name' });
  name.addEventListener('input', () => { P.name = name.value.trim().slice(0, 80) || 'Untitled plan'; markDirty(); renderPlanSelect(); });
  const notes = h('textarea', { 'aria-label': 'Design notes', placeholder: 'Goals, materials to gather, ideas… Claude can read and add to these.' });
  notes.value = P.notes;
  notes.addEventListener('input', () => { P.notes = notes.value.slice(0, 20000); markDirty(); });
  const cm = P.cell;
  const w = h('input', { type: 'number', value: fmt(P.w * cm), min: String(4 * cm), max: String(MAX_GRID * cm), step: String(cm), 'aria-label': 'Width in metres' });
  const hh = h('input', { type: 'number', value: fmt(P.h * cm), min: String(4 * cm), max: String(MAX_GRID * cm), step: String(cm), 'aria-label': 'Depth in metres' });
  const res = h('select', { 'aria-label': 'Square size' },
    h('option', { value: '1', text: '1 m squares (1M cubes): layout' }),
    h('option', { value: '0.5', text: '0.5 m squares (single blocks): detail' }));
  res.value = String(cm);
  res.addEventListener('change', async () => { const ok = await setResolution(Number(res.value)); if (!ok) res.value = String(S.plan.cell); });
  const altar = h('select', { 'aria-label': 'Altar build area' }, ...GAME.altarSizes.map((v, i) => h('option', { value: String(v), text: `Altar level ${i + 1} · ${v} × ${v} m` })));
  altar.value = String(P.altar);
  altar.addEventListener('change', () => { begin(); P.altar = Number(altar.value); commit(); });
  const importBox = h('textarea', { class: 'code', 'aria-label': 'Plan JSON to import', placeholder: '{ "name": "…", "levels": [ … ] }' });
  const importErr = h('p', { class: 'err', hidden: true });
  pane.replaceChildren(
    h('div', { class: 'pane-head' }, h('h3', { text: 'Plan' })),
    h('label', { class: 'field' }, h('span', { text: 'Name' }), name),
    h('label', { class: 'field' }, h('span', { text: 'Design notes' }), notes),
    projectSection(),
    h('div', { class: 'section' }, h('h4', { text: 'Summary' }), h('dl', { class: 'stats', id: 'statsBox' }),
      h('div', { class: 'btnrow' },
        h('button', { class: 'btn btn-sm btn-accent', type: 'button', text: 'Shopping list…', title: 'Blocks, crafting runs and raw resources this plan needs', onclick: openShoppingList }),
        h('button', { class: 'btn btn-sm', type: 'button', disabled: S.readOnly, text: 'Painted doors → items', title: 'Turn every painted door and window named after a real one into a placed item in its wall', onclick: convertPaintedOpenings }))),
    limitsSection(),
    h('div', { class: 'section' }, h('h4', { text: 'Grid, canvas & altar' }),
      h('label', { class: 'field' }, h('span', { text: 'Square size' }), res),
      h('p', { class: 'note', text: `Use 1 m for whole-base layouts. Switch to 0.5 m to place single blocks: thin walls, trim, half-metre steps (canvas up to ${MAX_GRID / 2} m, room for the 160 m build area).` }),
      h('div', { class: 'grid3' }, h('label', { class: 'field' }, h('span', { text: 'Width (m)' }), w), h('label', { class: 'field' }, h('span', { text: 'Depth (m)' }), hh),
        h('div', { class: 'field' }, h('span', { text: ' ' }), h('button', { class: 'btn', type: 'button', text: 'Resize', onclick: () => resizePlan(Math.round(Number(w.value) / cm), Math.round(Number(hh.value) / cm)) }))),
      h('label', { class: 'field' }, h('span', { text: 'Altar build area' }), altar),
      h('p', { class: 'note', text: 'Build areas grow with altar upgrades: 40, 80, 120 and 160 m. The dashed square is centred on each Flame Altar you place. Centring is approximate.' })),
    ...[placeSection()].filter(Boolean),                // (none when there's no other plan)
    h('div', { class: 'callout' }, S.mode === 'db'
      ? [h('b', { text: 'Shared with Claude. ' }), 'Plans are stored with this page. In chat, ask Claude to look at or draft a plan by name. Its edits show up here live, and Undo can roll them back.']
      : [h('b', { text: 'Saved in this browser only. ' }), 'Copy plan JSON below to keep a backup or move a plan to another browser, and paste one into Import to open it.']),
    h('div', { class: 'section' }, h('h4', { text: 'Share & export' }),
      h('div', { class: 'btnrow' },
        h('button', { class: 'btn btn-sm', type: 'button', text: 'Copy level as text', title: 'A text grid of this level, handy to paste into chat', onclick: () => copyText(levelText(lv()), 'Level text') }),
        h('button', { class: 'btn btn-sm', type: 'button', text: 'Copy plan JSON', onclick: () => copyText(JSON.stringify(serialize(P, false), null, 1), 'Plan JSON') }),
        h('button', { class: 'btn btn-sm', type: 'button', text: 'Save image', onclick: savePng }),
        h('button', { class: 'btn btn-sm', type: 'button', text: 'Save JSON file', onclick: saveJson }))),
    h('details', null, h('summary', { text: 'Import a plan' }), h('div', { class: 'inner' },
      h('p', { class: 'note', text: 'Paste plan JSON (from “Copy plan JSON”). It opens as a new plan.' }), importBox, importErr,
      h('div', null, h('button', { class: 'btn btn-sm btn-accent', type: 'button', text: 'Import as new plan', onclick: () => importPlan(importBox.value, importErr) })))),
    h('div', { class: 'section' }, h('h4', { text: 'Manage' }),
      h('div', { class: 'btnrow' },
        h('button', { class: 'btn btn-sm', type: 'button', text: 'Duplicate plan', onclick: duplicatePlan }),
        h('button', { class: 'btn btn-sm btn-danger', type: 'button', text: 'Delete plan', onclick: deletePlan }))),
  );
  renderStats();
}
function renderStats() {
  const box = $('#statsBox');
  if (!box || !S.plan) return;
  const P = S.plan, B = boundsOf(P.levels, false), counts = computeCounts();
  const rows = [
    ['Footprint used', B ? `${metres(B.w)} × ${metres(B.h)} m` : '–'],
    ['Canvas', `${metres(P.w)} × ${metres(P.h)} m (${P.cell} m squares)`],
    ['Levels', `${P.levels.length} · ${fmt(topOfLevels())} m tall`],
    ['Items placed', String(P.items.length)],
  ];
  const out = countOutsideAltar(P);
  if (out != null) rows.push(['Outside the altar area', out ? `${out} sq (hatched red)` : 'none']);
  const byName = new Map();                                  // sizes of one material (block layers make several) count together
  for (const [k, e] of Object.entries(P.palette)) if (counts[k]) byName.set(e.name, (byName.get(e.name) || 0) + counts[k]);
  for (const [n, c] of byName) rows.push([n, `${c} sq`]);
  box.replaceChildren(...rows.flatMap(([a, b]) => [h('dt', { text: a }), h('dd', { text: b })]));
  const lim = $('#limitsBox'), fresh = limitsSection();
  if (lim && fresh) lim.replaceWith(fresh);
  updateLimitChip();
}

// ---------------------------------------------------------------------------
// Inspector
// ---------------------------------------------------------------------------
function renderInspector() {
  const box = $('#inspector');
  const sel = S.sel;
  if (!S.plan || !sel) { box.hidden = true; box.replaceChildren(); markPicked(); pickOutline(); return; }
  const P = S.plan;
  const kids = [];
  if (sel.type === 'item') {
    const it = findItem(sel.id);
    if (!it) { box.hidden = true; return; }
    const label = h('input', { type: 'text', id: 'inspName', value: it.label, maxlength: '40', 'aria-label': 'Label' });
    label.addEventListener('input', () => { liveBegin(); it.label = label.value.slice(0, 40) || 'Item'; markDirty(); req2d(); });
    label.addEventListener('change', () => { liveCommit(); renderPlacedList(); });
    const cm = P.cell, st = itemStep(P), mount = mountOf(it), inWall = IN_WALL.has(mount);
    const numIn = (key, lab, min, max, step) => {
      const squares = key !== 'h';
      const inp = h('input', { type: 'number', value: fmt(squares ? it[key] * cm : it[key]), min: String(VOXEL), max: String(squares ? max * cm : max), step: String(VOXEL), 'aria-label': lab + ' in metres' });
      inp.addEventListener('change', () => {
        begin();
        it[key] = squares ? clamp(snapStep(Number(inp.value) / cm, st) || it[key], st, max) : blocksNum(inp.value, it.h, 0.5, 40);
        const R = itemRect(it);
        it.x = clamp(it.x, 0, Math.max(0, P.w - R.w)); it.y = clamp(it.y, 0, Math.max(0, P.h - R.h));
        commit(); renderInspector();
      });
      return h('label', { class: 'field' }, h('span', { text: lab }), inp);
    };
    const color = h('input', { type: 'color', value: it.color, 'aria-label': 'Colour' });
    color.addEventListener('input', () => { liveBegin(); it.color = color.value; req2d(); mark3d(); });
    color.addEventListener('change', liveCommit);
    const lvlSel = h('select', { 'aria-label': 'Level' }, ...P.levels.map(l => h('option', { value: l.id, text: l.name })));
    lvlSel.value = it.level;
    lvlSel.addEventListener('change', () => { begin(); it.level = lvlSel.value; commit(); S.sel = null; renderInspector(); renderPlacedList(); });
    // how it sits, and how high: a window's sill, how high a wall item hangs
    const mSel = h('select', { 'aria-label': 'How it sits' }, ...Object.entries(MOUNTS).map(([v, t]) => h('option', { value: v, text: t })));
    mSel.value = mount;
    mSel.addEventListener('change', () => {
      begin(); const m = mSel.value, L = P.levels.find(l => l.id === it.level);
      if (m === 'floor') delete it.mount; else it.mount = m;
      if (IN_WALL.has(m)) it.d = 1;
      const z = defaultZ(m, it.h, L); if (z > 0) it.z = z; else delete it.z;
      commit(); renderInspector();
    });
    const zLab = mount === 'window' ? 'Sill at' : mount === 'wall' ? 'Hangs at' : mount === 'ceiling' ? 'Bottom at' : 'Raised by';
    const zIn = h('input', { type: 'number', value: fmt(it.z || 0), min: '0', max: '80', step: String(VOXEL), 'aria-label': zLab + ' (metres above the floor)' });
    zIn.addEventListener('change', () => { begin(); const z = blocksNum(zIn.value, 0, 0, 80); if (z > 0) it.z = z; else delete it.z; commit(); renderInspector(); });
    const base = LIB_BY_TYPE[it.type], def = base ? libDef(base) : null;
    let libBox = null;
    if (def && def.src) {
      const cur = { w: num(it.w * cm, 1, 0.5, 64), d: inWall ? def.d : num(it.d * cm, 1, 0.5, 64), h: it.h, ...(mount !== 'floor' ? { mount } : {}), ...(mount === 'window' || mount === 'wall' ? { z: it.z || 0 } : {}) };
      const same = def.measured && cur.w === def.w && cur.d === def.d && cur.h === def.h && (cur.z == null || cur.z === def.z) && mountOf(cur) === mountOf(def);
      const bl = m => Math.round(m / VOXEL);
      libBox = h('div', { class: 'callout section' },
        h('div', null, h('b', { text: def.name }), def.by ? ` · ${def.by}` : '', def.role ? ` · ${def.role}` : ''),
        def.recipe ? h('div', { text: 'Recipe: ' + def.recipe }) : null,
        h('div', null, `New ${def.name}s: ${bl(def.h)} tall × ${bl(def.w)} wide × ${bl(def.d)} deep blocks `, h('span', { class: 'tag ' + (def.measured ? 'ok' : 'est'), text: def.measured ? 'measured' : def.craft ? 'guess' : 'est.' })),
        h('div', { class: 'btnrow' },
          h('button', { class: 'btn btn-sm', type: 'button', disabled: same || S.readOnly, title: 'Save this one’s size, and how it sits, for every new one you place (shared with every plan)', text: 'Use this size for all new', onclick: () => { saveLibSize(it.type, cur); toast(`New ${def.name}s will be ${bl(cur.h)} × ${bl(cur.w)} blocks (tall × wide).`); } }),
          S.libSizes && S.libSizes[it.type] ? h('button', { class: 'btn btn-sm btn-ghost', type: 'button', disabled: S.readOnly, text: def.craft && !base.sized ? 'Forget the size' : 'Back to estimate', onclick: () => saveLibSize(it.type, null) }) : null,
          def.craft ? null : h('a', { class: 'btn btn-sm btn-ghost', href: wikiUrl(def), target: '_blank', rel: 'noopener', text: 'Wiki' })));
    }
    kids.push(
      h('div', { class: 'pane-head' }, h('h3', { text: 'Item' }), h('span', { class: 'note', text: `faces ${FACING[it.rot]}` })),
      h('label', { class: 'field' }, h('span', { text: 'Label' }), label),
      h('div', { class: 'grid3' }, numIn('w', inWall ? 'Wide' : 'Width', 1, 128, 1), inWall ? null : numIn('d', 'Depth', 1, 128, 1), numIn('h', 'Height', 0.1, 40, 0.5)),
      h('div', { class: 'grid2' }, h('label', { class: 'field', title: 'Doors and windows cut their opening in the wall they sit in. Wall and ceiling items hang' }, h('span', { text: 'Sits' }), mSel),
        h('label', { class: 'field', title: 'Its bottom, in metres above the level floor' }, h('span', { text: zLab }), zIn)),
      libBox,
      h('div', { class: 'row' }, color, h('label', { class: 'field', style: 'flex:1' }, h('span', { text: 'Level' }), lvlSel)),
      h('div', { class: 'btnrow' },
        h('button', { class: 'btn btn-sm', type: 'button', text: 'Rotate', title: 'Rotate (R)', onclick: () => { begin(); rotateItem(it); commit(); renderInspector(); } }),
        h('button', { class: 'btn btn-sm', type: 'button', text: 'Duplicate', onclick: () => { begin(); const c = { ...it, id: uid('i'), x: clamp(it.x + 1, 0, P.w - 1), y: clamp(it.y + 1, 0, P.h - 1) }; P.items.push(c); commit(); S.sel = { type: 'item', id: c.id }; renderInspector(); } }),
        h('button', { class: 'btn btn-sm btn-danger', type: 'button', text: 'Delete', onclick: deleteSelection })));
  } else if (sel.type === 'zone') {
    const z = findZone(sel.id);
    if (!z) { box.hidden = true; return; }
    const name = h('input', { type: 'text', id: 'inspName', value: z.name, maxlength: '40', 'aria-label': 'Area name' });
    name.addEventListener('input', () => { liveBegin(); z.name = name.value.slice(0, 40) || 'Area'; markDirty(); req2d(); });
    name.addEventListener('change', liveCommit);
    name.addEventListener('keydown', e => { if (e.key === 'Enter') name.blur(); });
    const color = h('input', { type: 'color', value: z.color, 'aria-label': 'Colour' });
    color.addEventListener('input', () => { liveBegin(); z.color = color.value; req2d(); });
    color.addEventListener('change', liveCommit);
    const cm = P.cell;
    const numIn = (key, lab) => {
      const inp = h('input', { type: 'number', value: fmt(z[key] * cm), min: key === 'w' || key === 'h' ? String(cm) : '0', max: String(MAX_GRID * cm), step: String(cm), 'aria-label': lab + ' in metres' });
      inp.addEventListener('change', () => {
        begin();
        z[key] = clampInt(Number(inp.value) / cm, key === 'w' || key === 'h' ? 1 : 0, MAX_GRID, z[key]);
        z.w = Math.min(z.w, P.w); z.h = Math.min(z.h, P.h);
        z.x = clamp(z.x, 0, P.w - z.w); z.y = clamp(z.y, 0, P.h - z.h);
        commit(); renderInspector();
      });
      return h('label', { class: 'field' }, h('span', { text: lab }), inp);
    };
    kids.push(
      h('div', { class: 'pane-head' }, h('h3', { text: 'Area' }), h('span', { class: 'note', text: `${fmt(z.w * z.h * cm * cm)} m²` })),
      h('div', { class: 'row' }, h('label', { class: 'field', style: 'flex:1' }, h('span', { text: 'Name' }), name), color),
      h('div', { class: 'grid2' }, numIn('x', 'X (m)'), numIn('y', 'Y (m)'), numIn('w', 'Width (m)'), numIn('h', 'Depth (m)')),
      h('div', { class: 'btnrow' }, h('button', { class: 'btn btn-sm btn-danger', type: 'button', text: 'Delete area', onclick: deleteSelection })));
  } else if (sel.type === 'block') {
    const L = P.levels.find(l => l.id === sel.lid), e = P.palette[sel.k];
    if (!e) { box.hidden = true; box.replaceChildren(); markPicked(); pickOutline(); return; }
    const goTo = () => {                                     // the same square in 2D, on its level or its layer
      if (layerOn()) setLayer(Math.floor(sel.z0 / layerSize() + 1e-6));
      else if (L) setLevel(P.levels.indexOf(L));
      S.sel = { type: 'cells', rect: { x: sel.x, y: sel.y, w: 1, h: 1 } };
      if (S.view === '3d') setView('split');
      renderInspector(); req2d();
    };
    const what = sel.gable ? ' · the gable wall carried up under the roof' : sel.around ? ` · the wall round a ${P.palette[sel.around] ? P.palette[sel.around].kind : 'door'}` : '';
    kids.push(
      h('div', { class: 'pane-head' }, h('h3', { text: 'Block' }), h('span', { class: 'note mono', text: `x${metres(sel.x)} y${metres(sel.y)} · ${fmt(sel.z0)} to ${fmt(sel.z1)} m` })),
      materialRows([{ k: sel.k, e, L, note: what }]),
      h('div', { class: 'btnrow' }, h('button', { class: 'btn btn-sm', type: 'button', text: 'Show it in 2D', title: 'Select this square in the 2D view, on its level (or layer)', onclick: goTo })),
      buildCardEl(sel));
  } else if (sel.type === 'cells') {
    const R = sel.rect;
    const others = P.levels.filter(l => l !== lv());
    const lvlSel = h('select', { 'aria-label': 'Target level' }, ...others.map(l => h('option', { value: l.id, text: l.name })));
    const brush = P.palette[S.brush];
    kids.push(
      h('div', { class: 'pane-head' }, h('h3', { text: R.w === 1 && R.h === 1 ? 'Square' : 'Selection' }), h('span', { class: 'note mono', text: `${metres(R.w)} × ${metres(R.h)} m at x${metres(R.x)} y${metres(R.y)}` })),
      materialsHere(R),
      h('p', { class: 'note', text: 'Drag inside the box to move it. Arrow keys nudge it (Shift moves 5).' }),
      h('div', { class: 'btnrow' },
        h('button', { class: 'btn btn-sm', type: 'button', text: 'Copy', onclick: copySelection }),
        brush ? h('button', { class: 'btn btn-sm', type: 'button', text: `Fill with ${brush.name}`, onclick: () => fillSelection(S.brush) }) : null,
        h('button', { class: 'btn btn-sm btn-danger', type: 'button', text: 'Clear', onclick: deleteSelection })),
      others.length ? h('div', { class: 'row' }, h('label', { class: 'field', style: 'flex:1' }, h('span', { text: 'Copy to level' }), lvlSel),
        h('button', { class: 'btn btn-sm', type: 'button', text: 'Copy there', onclick: () => copySelectionToLevel(lvlSel.value) })) : null,
      buildCardEl(sel));
  }
  box.replaceChildren(...kids.filter(Boolean));
  box.hidden = false;
  markPicked(); pickOutline();
}

// ---------------------------------------------------------------------------
// Modal dialogs
// ---------------------------------------------------------------------------
let modalClose = null;
function openModal(title, body, actions) {
  const mb = $('#modal .modal'); if (mb) mb.classList.remove('wide', 'xwide');
  $('#modalTitle').textContent = title;
  $('#modalBody').replaceChildren(...[].concat(body).filter(Boolean));
  $('#modalActions').replaceChildren(...actions.map(a => h('button', { class: 'btn' + (a.primary ? ' btn-accent' : '') + (a.danger ? ' btn-danger' : ''), type: 'button', text: a.label, onclick: a.onClick })));
  $('#modal').hidden = false;
  const first = $('#modalBody input, #modalBody textarea') || $('#modalActions .btn-accent') || $('#modalActions .btn');
  if (first) setTimeout(() => first.focus(), 0);
}
function closeModal() { $('#modal').hidden = true; document.querySelector('#modal .modal').classList.remove('wide', 'xwide'); if (modalClose) { const f = modalClose; modalClose = null; f(); } }
function confirmBox(title, message, okLabel, danger) {
  return new Promise(resolve => {
    let done = false;
    const finish = v => { if (done) return; done = true; modalClose = null; $('#modal').hidden = true; resolve(v); };
    modalClose = () => finish(false);
    openModal(title, h('p', { class: 'note', style: 'font-size:14px', text: message }), [
      { label: 'Cancel', onClick: () => finish(false) },
      { label: okLabel, primary: !danger, danger, onClick: () => finish(true) },
    ]);
  });
}
$('#modal').addEventListener('pointerdown', e => { if (e.target === $('#modal')) closeModal(); });
function newPlanDialog(project) {
  if (!S.store) return;
  const name = h('input', { type: 'text', value: 'New base', maxlength: '80', 'aria-label': 'Plan name' });
  const here = typeof project === 'string' ? project : currentProject() === '*' ? (S.plan ? S.plan.project || '' : '') : currentProject();
  const pf = projectField(here, () => {});
  const presets = [
    ['48:40', 'Altar level 1', '48 × 48 m canvas, room for a 40 m build area'],
    ['88:80', 'Altar level 2', '88 × 88 m canvas, room for an 80 m build area'],
    ['128:120', 'Altar level 3', '128 × 128 m canvas, room for a 120 m build area'],
    ['168:160', 'Altar level 4', '168 × 168 m canvas, room for the full 160 m build area'],
    ['32:40', 'Single building', '32 × 32 m, for one house or tower. Pairs well with 0.5 m squares'],
  ];
  const radios = presets.map(([v, t, d], i) => h('label', { class: 'choice' }, h('input', { type: 'radio', name: 'np-size', value: v, checked: i === 0 }), h('span', null, h('b', { text: t }), h('small', { text: d }))));
  const res = h('select', { 'aria-label': 'Square size' },
    h('option', { value: '1', text: '1 m squares (1M cubes): best for layout' }),
    h('option', { value: '0.5', text: `0.5 m squares (single blocks): detail, up to ${MAX_GRID / 2} m` }));
  const create = () => {
    const [sizeM, altar] = ((document.querySelector('input[name="np-size"]:checked') || {}).value || '48:40').split(':').map(Number);
    const cell = Number(res.value) === 0.5 ? 0.5 : 1;
    const cells = Math.min(MAX_GRID, Math.round(sizeM / cell));
    closeModal();
    if (cells * cell < sizeM) toast(`Half-metre squares cap the canvas at ${MAX_GRID / 2} m, so this plan is ${cells * cell} × ${cells * cell} m.`);
    createPlan(str(name.value, 80) || 'New base', cells, cells, altar, null, cell, pf.value());
  };
  name.addEventListener('keydown', e => { if (e.key === 'Enter') create(); });
  openModal('Start a plan', [h('label', { class: 'field' }, h('span', { text: 'Name' }), name), h('label', { class: 'field' }, h('span', { text: 'Project' }), pf.sel), pf.other,
    h('div', { class: 'section' }, ...radios), h('label', { class: 'field' }, h('span', { text: 'Square size' }), res)],
    [{ label: 'Cancel', onClick: closeModal }, { label: 'Create plan', primary: true, onClick: create }]);
}
async function createPlan(name, w, hh, altar, data, cell, project) {
  if (S.dirty) await flushSave();
  const id = S.store.newId();
  const p = data ? normalizePlan(data) : blankPlan(name, w, hh, cell === 0.5 ? 0.5 : 1);
  if (!data) { p.altar = GAME.altarSizes.includes(altar) ? altar : 40; p.project = (project || '').slice(0, 40); }
  if (S.project !== '*') S.project = p.project || '';
  histPark();
  S.creating = id; S.planId = id; S.plan = p; S.baseRev = null;
  progSubscribe(id);
  S.hist = []; S.fut = []; S.sel = null; S.itemDef = null; S.levelIdx = Math.max(0, p.levels.findIndex(l => l.elev >= 0));
  ensureBrushes(); hideEmpty(); LS.set('last', id);
  S.dirty = true; flushSave();
  fitView(!!data); V3.fit = true; refreshAll();
}
function duplicatePlan() { const d = serialize(S.plan, false); d.name = (S.plan.name + ' copy').slice(0, 80); createPlan(d.name, 0, 0, 0, d).then(() => toast('Plan duplicated.')); }
async function deletePlan() {
  if (!(await confirmBox('Delete this plan?', `“${S.plan.name}” will be deleted for good, for you and for Claude.`, 'Delete plan', true))) return;
  const id = S.planId;
  S.planId = null; S.plan = null; S.dirty = false; clearTimeout(S.saveTimer);
  try { await S.store.remove(id); toast('Plan deleted.'); } catch { toast('Couldn’t delete the plan. Try again.', 'bad'); }
  const next = newestPlanId();
  if (next && next !== id) openPlan(next); else { refreshAll(); showEmpty('none'); }
}
function importPlan(text, errEl) {
  let d;
  try { d = JSON.parse(text); } catch { errEl.textContent = 'That isn’t valid JSON. Paste the whole text from “Copy plan JSON”.'; errEl.hidden = false; return; }
  if (d && d.data && d.data.levels) d = d.data;
  if (!d || typeof d !== 'object' || !Array.isArray(d.levels)) { errEl.textContent = 'No levels found in that JSON.'; errEl.hidden = false; return; }
  errEl.hidden = true;
  createPlan('', 0, 0, 0, d).then(() => toast('Plan imported.'));
}

// ---------------------------------------------------------------------------
// Export
// ---------------------------------------------------------------------------
async function copyText(text, label) {
  try { await navigator.clipboard.writeText(text); toast(`${label} copied.`); }
  catch {
    const ta = h('textarea', { class: 'code', readonly: true, 'aria-label': label }); ta.value = text;
    openModal(`Copy ${label.toLowerCase()}`, [h('p', { class: 'note', text: 'Press Ctrl+C (or ⌘C) to copy.' }), ta], [{ label: 'Done', primary: true, onClick: closeModal }]);
    setTimeout(() => { ta.focus(); ta.select(); }, 30);
  }
}
function levelText(L) {
  const P = S.plan;
  const B = boundsOf([L], false) || { x: 0, y: 0, w: Math.min(P.w, 30), h: Math.min(P.h, 15) };
  const used = new Set();
  for (let y = B.y; y < B.y + B.h; y++) for (const c of L.grid[y].slice(B.x, B.x + B.w)) if (c !== ' ') used.add(c);
  // one character per square, or (when a symbol past the 94 visible characters is used) each square as its
  // three-digit symbol number
  const wide = [...used].some(c => !PRINT.test(c));
  const cellText = c => (wide ? (c === ' ' ? '   ' : code3(symCode(c))) : c), sep = wide ? ' ' : '';
  const rows = [];
  for (let y = B.y; y < B.y + B.h; y++) rows.push(String(y).padStart(4) + ' ' + L.grid[y].slice(B.x, B.x + B.w).map(cellText).join(sep).replace(/ +$/, ''));
  const head = wide
    ? [' '.repeat(5) + Array.from({ length: B.w }, (_, i) => String(B.x + i).padStart(3)).join(' ')]
    : [' '.repeat(5) + Array.from({ length: B.w }, (_, i) => ((B.x + i) % 10 === 0 ? String(Math.floor((B.x + i) / 10) % 10) : ' ')).join(''),
       ' '.repeat(5) + Array.from({ length: B.w }, (_, i) => String((B.x + i) % 10)).join('')];
  const lines = [`Plan “${P.name}”, ${L.name} (base ${fmt(L.elev)} m, height ${fmt(L.height)} m). 1 square = ${P.cell} m; x/y below count squares.`, 'Legend:'];
  for (const c of used) { const e = P.palette[c]; lines.push(`  ${wide ? code3(symCode(c)) : c}  ${e ? `${e.name} (${KINDS[e.kind].label.toLowerCase()}${e.kind === 'roof' ? `, top at ${fmt(roofTop(e, P.cell))} m` : e.height ? `, ${fmt(e.height)} m tall` : ''}${e.base ? `, raised ${fmt(e.base)} m` : ''}${e.under && P.palette[e.under] ? `, over ${wide ? code3(symCode(e.under)) : e.under}` : ''})` : 'unknown symbol'}`); }
  lines.push('```', ...head, ...rows, '```');
  const items = P.items.filter(i => i.level === L.id);
  if (items.length) { lines.push('Items:'); for (const i of items) lines.push(`  - ${i.label} (${i.type}) at x ${i.x}, y ${i.y}, ${metres(i.w)}×${metres(i.d)} m, faces ${FACING[i.rot]}`); }
  const zones = P.zones.filter(z => z.level === L.id);
  if (zones.length) { lines.push('Areas:'); for (const z of zones) lines.push(`  - ${z.name}: x ${z.x}, y ${z.y}, ${metres(z.w)}×${metres(z.h)} m`); }
  return lines.join('\n');
}
async function getDownloads() {
  try { return window.claude && window.claude.use ? await window.claude.use('downloads') : null; } catch { return null; }
}
async function offerFile(filename, data) {
  const dl = await getDownloads();
  if (!dl) { toast('Saving files isn’t available here. Use the copy buttons instead.'); return; }
  try { await dl.save({ filename, data }); }
  catch (e) { if (e && e.code !== 'declined') toast('Couldn’t save the file.', 'bad'); }
}
function savePng() {
  const P = S.plan, L = lv();
  const s = clamp(Math.floor(2400 / Math.max(P.w, P.h)), 8, 32), pad = 28, head = 46;
  const cv = document.createElement('canvas'); cv.width = P.w * s + pad * 2; cv.height = P.h * s + pad * 2 + head;
  const g = cv.getContext('2d');
  renderPlan(g, { ox: pad, oy: pad + head, s }, cv.width, cv.height, { levelIdx: S.levelIdx, ghost: false, zones: S.opt.zones, altar: S.opt.altar });
  g.fillStyle = T.panel; g.fillRect(0, 0, cv.width, head + 10);
  g.fillStyle = T.ink; g.font = `600 20px ${FONT_UI}`; g.textAlign = 'left'; g.textBaseline = 'middle';
  g.fillText(`${P.name} · ${L.name}`, pad, head / 2 + 4);
  g.fillStyle = T.muted; g.font = `500 13px ${FONT_MONO}`; g.textAlign = 'right';
  g.fillText(`${metres(P.w)} × ${metres(P.h)} m · 1 square = ${P.cell} m`, cv.width - pad, head / 2 + 4);
  cv.toBlob(b => { if (b) offerFile(`${slug(P.name)}-${slug(L.name)}.png`, b); }, 'image/png');
}
function saveJson() { offerFile(`${slug(S.plan.name)}.json`, JSON.stringify(serialize(S.plan, false), null, 1)); }

// ---------------------------------------------------------------------------
// Refresh helpers, keyboard, boot
// ---------------------------------------------------------------------------
function refreshPanels() { renderMaterials(); renderItemsPane(); renderLevels(); renderPlanPane(); renderInspector(); renderOptbar(); updateStatus(); updateUndo(); req2d(); mark3d(); }
function refreshAll() { renderPlanSelect(); refreshPanels(); setSync(); }
const typing = el => el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT' || el.isContentEditable);
window.addEventListener('keydown', e => {
  if (!$('#modal').hidden) { if (e.key === 'Escape') closeModal(); return; }
  if (typing(e.target)) { if (e.key === 'Escape') e.target.blur(); return; }
  if (!S.plan) return;
  const k = e.key, lk = k.toLowerCase(), mod = e.ctrlKey || e.metaKey;
  if (mod) {
    if (lk === 'z' && S.tool === 'built' && !e.shiftKey) { e.preventDefault(); progUndo(); }   // (with Mark built, undo takes back a mark)
    else if (lk === 'z') { e.preventDefault(); e.shiftKey ? redo() : undo(); }
    else if (lk === 'y') { e.preventDefault(); redo(); }
    else if (lk === 'k') { e.preventDefault(); openFinder(); }
    else if (lk === 'c' && S.sel) { e.preventDefault(); copySelection(); }
    else if (lk === 'v' && S.clip) { e.preventDefault(); pasteClip(e.shiftKey); }
    return;
  }
  if (k === ' ') { if (!spaceDown) { spaceDown = true; setCursor(); } e.preventDefault(); return; }
  if (S.wallChain && S.tool === 'wall') {
    if (k === 'Enter') { e.preventDefault(); wallFinish(); return; }
    if (k === 'Escape') { e.preventDefault(); wallCancel(); return; }
    if (k === 'Backspace' || k === 'Delete') { e.preventDefault(); wallBack(); return; }
  }
  if (lk === 'f' && S.tool === 'wall') { cycleWallSide(); return; }
  if (k === 'Escape') { if (G) abortGesture(); else if (S.sel) { S.sel = null; renderInspector(); } else if (S.measure) S.measure = null; else if (S.tool !== 'select') setTool('select'); req2d(); return; }
  if (k === 'Delete' || k === 'Backspace') { if (S.sel) { e.preventDefault(); deleteSelection(); } return; }
  // ] and [ step a layer in block-layer mode, a level otherwise; Page Up and Page Down always step a level
  if (layerOn() && (k === ']' || k === '[')) { e.preventDefault(); stepLayer(k === ']' ? 1 : -1); return; }
  if (layerOn() && (k === 'PageUp' || k === 'PageDown')) { e.preventDefault(); stepLayer((k === 'PageUp' ? 1 : -1) * Math.round(GAME.levelH / layerSize())); return; }
  if (k === ']' || k === 'PageUp') { e.preventDefault(); stepLevel(1); return; }       // (trim levels are stepped over)
  if (k === '[' || k === 'PageDown') { e.preventDefault(); stepLevel(-1); return; }
  if (lk === 'k') { toggleLayers(); return; }
  if (k.startsWith('Arrow') && S.sel) {
    e.preventDefault();
    const n = e.shiftKey ? 5 : 1;
    nudgeSelection(...turnVec(k === 'ArrowLeft' ? -n : k === 'ArrowRight' ? n : 0, k === 'ArrowUp' ? -n : k === 'ArrowDown' ? n : 0, -camRot(S.cam)));   // (as on screen)
    return;
  }
  if (lk === 'r') {
    if (S.tool === 'item') { S.itemRot = (S.itemRot + 90) % 360; if (S.hover) S.ghostItem = ghostFor(S.hover[0] + 0.5, S.hover[1] + 0.5); req2d(); }
    else if (S.tool === 'place') rotatePlace();
    else if (S.sel && S.sel.type === 'item') { const it = findItem(S.sel.id); if (it) { begin(); rotateItem(it); commit(); renderInspector(); } }
    return;
  }
  if (/^[1-9]$/.test(k)) { hotbarPick(Number(k)); return; }
  if (k === '/') { e.preventDefault(); openFinder(); return; }
  if (k === '?') { e.preventDefault(); openKeys(); return; }
  if (k === '`') { e.preventDefault(); cycleView(); return; }
  if (k === '.' || k === ',') { e.preventDefault(); goStep(STEPS.at < 0 ? 0 : STEPS.at + (k === '.' ? 1 : -1)); return; }
  if (lk === 'n') { e.preventDefault(); nextUnbuilt(); return; }
  if (k === '+' || k === '=') { zoomAt(W2 / 2, H2 / 2, 1.25); return; }
  if (k === '-' || k === '_') { zoomAt(W2 / 2, H2 / 2, 0.8); return; }
  if (k === '0') { fitView(true); return; }
  if (k === '>' || k === '<') { setViewTurn(camRot(S.cam) + (k === '>' ? 1 : -1)); return; }   // (Shift + . and ,)
  if (lk === 'x' && !e.shiftKey) { cycleMirror(); return; }
  const tool = TOOLS.find(t => t !== 'sep' && t.key.toLowerCase() === lk);
  if (tool) setTool(tool.id);
});
window.addEventListener('keyup', e => { if (e.key === ' ') { spaceDown = false; setCursor(); } });
window.addEventListener('blur', () => { spaceDown = false; });

function bindChrome() {
  $('#viewSeg').addEventListener('click', e => { const b = e.target.closest('button[data-view]'); if (b) setView(b.dataset.view); });
  $('#undoBtn').addEventListener('click', undo);
  $('#redoBtn').addEventListener('click', redo);
  $('#histBtn').addEventListener('click', toggleHistPop);
  $('#newPlanBtn').addEventListener('click', newPlanDialog);
  $('#planSelect').addEventListener('change', e => { if (e.target.value && e.target.value !== S.planId) openPlan(e.target.value); });
  $('#projectSelect').addEventListener('change', e => pickProject(e.target.value));
  if (LS.get('project', null) === '*') S.project = '*';
  $('#tabs').addEventListener('click', e => { const b = e.target.closest('[role="tab"]'); if (b) { openTab(b.dataset.tab); LS.set('tab', b.dataset.tab); } });
  $('#panelBtn').addEventListener('click', () => $('#panel').classList.toggle('open'));
  $('#panelClose').addEventListener('click', () => $('#panel').classList.remove('open'));
  $('#lvlUp').addEventListener('click', () => { if (layerOn()) stepLayer(1); else if (!stepLevel(1)) toggleLevelPop('up'); });
  $('#lvlDown').addEventListener('click', () => { if (layerOn()) stepLayer(-1); else if (!stepLevel(-1)) toggleLevelPop('dig'); });
  bindStrip();
  $('#limitChip').addEventListener('click', () => { openTab('plan'); LS.set('tab', 'plan'); const b = $('#limitsBox'); if (b) { b.scrollIntoView({ block: 'nearest' }); b.classList.remove('flash'); void b.offsetWidth; b.classList.add('flash'); } });
  $('#modeLevels').addEventListener('click', () => setLayerMode(false));
  $('#craftBtn').addEventListener('click', openCrafting);
  $('#findBtn').addEventListener('click', openFinder);
  $('#keysBtn').addEventListener('click', openKeys);
  $('#modeLayers').addEventListener('click', () => setLayerMode(true));
  $('#stLevel').addEventListener('click', () => toggleLevelPop());
  initTips();
  $('#zoomIn').addEventListener('click', () => zoomAt(W2 / 2, H2 / 2, 1.25));
  $('#zoomOut').addEventListener('click', () => zoomAt(W2 / 2, H2 / 2, 0.8));
  $('#fitBtn').addEventListener('click', () => fitView(true));
  $('#turnLeft').addEventListener('click', () => setViewTurn(camRot(S.cam) - 1));
  $('#turnRight').addEventListener('click', () => setViewTurn(camRot(S.cam) + 1));
  $('#turnReset').addEventListener('click', () => setViewTurn(0));
  $('#bannerLoad').addEventListener('click', () => { if (S.remote) adoptRemote(S.remote, 'Loaded the newer version. Undo puts yours back.'); });
  $('#bannerKeep').addEventListener('click', () => { S.remote = null; hideBanner(); markDirty(); });
  const cut = $('#cutBtn'), sh = $('#shadowBtn');
  cut.setAttribute('aria-pressed', String(S.opt.cut)); sh.setAttribute('aria-pressed', String(S.opt.shadows));
  cut.addEventListener('click', () => { S.opt.cut = !S.opt.cut; cut.setAttribute('aria-pressed', String(S.opt.cut)); LS.set('opt', S.opt); mark3d(); });
  sh.addEventListener('click', () => { S.opt.shadows = !S.opt.shadows; sh.setAttribute('aria-pressed', String(S.opt.shadows)); LS.set('opt', S.opt); mark3d(); });
  $('#resetCamBtn').addEventListener('click', () => { if (V3.ok) fit3d(); });
  $('#viewBtn').addEventListener('click', toggleViewPop);
  bindHighlights();
  new ResizeObserver(() => resize2d()).observe($('#view2d'));
  new ResizeObserver(() => resize3d()).observe($('#view3d'));
  const onTheme = () => { readTokens(); req2d(); mark3d(); };
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', onTheme);
  new MutationObserver(onTheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => req2d());
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') flushSave(); });
  window.addEventListener('pagehide', () => flushSave());
}

async function boot() {
  readTokens();
  const opt = LS.get('opt', null);
  if (opt && typeof opt === 'object') Object.assign(S.opt, opt);
  if (MIRROR_MODES.some(m => m[0] === LS.get('mirror', ''))) S.mirror.mode = LS.get('mirror', 'off');
  if (Number(LS.get('roomThick', 0)) > 0) S.roomThick = Number(LS.get('roomThick', 0));
  S.view = ['2d', 'split', '3d'].includes(LS.get('view', '')) ? LS.get('view', 'split') : (window.matchMedia('(max-width: 860px)').matches ? '2d' : 'split');
  renderToolrail(); bindChrome(); renderOptbar(); updateUndo(); setSync();
  openTab(PANEL_TABS.includes(LS.get('tab', '')) ? LS.get('tab', 'materials') : 'materials');
  $('#panel').classList.remove('open');
  setView(S.view, false);
  renderPlanSelect();
  let db = null, user = null;
  if (window.claude && typeof window.claude.use === 'function') {
    try { [db, user] = await Promise.all([window.claude.use('db'), window.claude.use('user')]); } catch { db = null; }
  }
  if (db && user) { try { if ((await user.can('data.write')) === false) S.readOnly = true; } catch { /* keep editable */ } }
  S.mode = db ? 'db' : 'local';
  S.store = packedStore(db ? dbStore(db) : localStore());
  setSync();
  S.store.subscribe(onPlans, onStoreError);
  S.store.subscribeDoc('meta/library', onLibSizes, () => {});
  S.store.subscribeDoc('meta/craft', onCraftDoc, () => {});
  S.store.subscribeDoc('meta/inventory', onInvDoc, () => {});
}
boot();
})();
