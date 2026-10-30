// ---------------------------------------------------------------------------
// Keyboard help and the command palette (planner v50). SHORTCUTS is the one table of keys: the ? overlay lists
// it (the tools straight from TOOLS), and the palette's commands show their keys from it.
// ---------------------------------------------------------------------------
const SHORTCUTS = [
  ['Levels and layers', [
    ['[  ]', 'Level down / up (trim levels are stepped over); a layer in Layers mode'],
    ['Page Up  Page Down', 'Level up / down; 4 m at a time in Layers mode'],
    ['K', 'Whole levels / block layers'],
  ]],
  ['Editing', [
    ['Ctrl+Z', 'Undo (with Mark built: take back the last mark)'],
    ['Ctrl+Shift+Z  Ctrl+Y', 'Redo'],
    ['Ctrl+C  Ctrl+V', 'Copy and paste the selection'],
    ['Delete', 'Delete the selection'],
    ['Arrows', 'Nudge the selection (Shift: 5 squares)'],
    ['R', 'Turn the item'],
    ['X', 'Mirror painting: off, ↔, ↕, ✣, ⟳'],
    ['1–9', 'Pick from the hotbar (Shift-click a slot to put the current material there)'],
    ['Space (hold)', 'Pan with any tool'],
    ['Esc', 'Cancel, deselect, then back to Select'],
  ]],
  ['Finding and views', [
    ['/  Ctrl+K', 'Find or do anything: commands, levels, areas, materials, blocks, items'],
    ['?', 'These shortcuts'],
    ['`', 'Views: 2D, Split, 3D'],
    ['+  −', 'Zoom the plan'],
    ['0', 'Fit the plan'],
  ]],
  ['Steps (Build tab)', [
    [',  .', 'Previous / next step'],
    ['N', 'Next step that isn’t built'],
  ]],
  ['Tool by tool', [
    ['Line: Shift', 'Lock to 0°, 45°, 90°'],
    ['Paint: right-drag', 'Erase'],
    ['Wall: Enter  double-click  right-click', 'Finish the chain of corners'],
    ['Wall: Backspace', 'Take back a corner'],
    ['Wall: F', 'Thickness centred, left or right of the line'],
    ['Replace: right-click', 'Pick up a block’s material'],
    ['Mark built: Shift-click', 'One block'],
    ['Mark built: Alt-click', 'Everything connected, shown or not'],
    ['Mark built: right-click', 'Unmark'],
  ]],
  ['3D view', [
    ['Drag', 'Orbit'],
    ['Right-drag  Shift-drag', 'Pan'],
    ['Scroll', 'Zoom'],
    ['Paint: click', 'Put a block against the face'],
    ['Paint: right-click', 'Take a block away (Erase: click)'],
    ['Paint: Ctrl+drag', 'A row along the surface'],
    ['Select: click', 'Inspect a block or item'],
  ]],
  ['Walk mode', [
    ['W A S D', 'Move'], ['Shift', 'Run on / off'], ['Drag', 'Look'], ['Space', 'Jump (hold: higher; swims up in water)'],
    ['E', 'Open the door in reach'], ['F', 'Full screen'], ['Enter', 'Back to the spawn point'], ['Esc', 'Stop walking'],
  ]],
];
function shortcutGroups() {
  const tools = TOOLS.filter(t => t !== 'sep').map(t => [t.key, t.label]);
  return [['Tools', tools], ...SHORTCUTS];
}
const kbdEls = keys => keys.split(/\s{2,}/).flatMap((k, i) => [i ? ' ' : null, h('kbd', { text: k })]).filter(x => x !== null);
function openKeys() {
  const filter = h('input', { type: 'text', placeholder: 'Filter: “layer”, “wall”, “3D”…', 'aria-label': 'Filter the shortcuts', autocomplete: 'off' });
  const box = h('div', { class: 'keysbox' });
  const draw = () => {
    const q = filter.value.trim().toLowerCase();
    const groups = shortcutGroups().map(([g, rows]) => [g, rows.filter(([k, d]) => !q || g.toLowerCase().includes(q) || k.toLowerCase().includes(q) || d.toLowerCase().includes(q))]).filter(([, rows]) => rows.length);
    box.replaceChildren(...(groups.length ? groups.map(([g, rows]) => h('section', { class: 'keysgroup' }, h('h4', { text: g }),
      h('dl', null, ...rows.flatMap(([k, d]) => [h('dt', null, ...kbdEls(k)), h('dd', { text: d })])))) : [h('p', { class: 'note', text: 'No shortcut matches that.' })]));
  };
  filter.addEventListener('input', draw);
  draw();
  openModal('Keyboard shortcuts', [filter, box], [{ label: 'Close', onClick: closeModal }]);
  const m = $('#modal .modal'); if (m) m.classList.add('wide');
}

// ---------------------------------------------------------------------------
// Commands for the palette: { label, key?, run }. Ones that only make sense now say so with `when`.
// ---------------------------------------------------------------------------
function cycleView() { const order = ['2d', 'split', '3d'], i = order.indexOf(S.view); setView(order[(i + 1) % order.length]); }
const need3d = () => { if (S.view === '2d') setView('split'); };
function centreOn(x, y, w, hgt) { S.cam.ox = W2 / 2 - (x + w / 2) * S.cam.s; S.cam.oy = H2 / 2 - (y + hgt / 2) * S.cam.s; updateZoom(); req2d(); }
function paletteCommands() {
  const tool = t => ({ label: `Tool: ${t.label}`, key: t.key, run: () => setTool(t.id) });
  const toggle = (label, on, flip, key) => ({ label: `${label}: ${on ? 'turn off' : 'turn on'}`, key, run: flip });
  const cmds = [
    ...TOOLS.filter(t => t !== 'sep').map(tool),
    { label: 'View: 2D', key: '`', run: () => setView('2d') }, { label: 'View: Split', key: '`', run: () => setView('split') }, { label: 'View: 3D', key: '`', run: () => setView('3d') },
    ...VIEWS.map(([id, label]) => ({ label: `Camera: ${label}`, run: () => { need3d(); setTimeout(() => viewPreset(id), 60); } })),
    { label: 'Camera: frame the selection', run: () => { need3d(); setTimeout(frameSelection, 60); } },
    { label: S.section ? '3D: show everything again' : '3D: show only the selection', run: () => { need3d(); setTimeout(toggleSection, 60); } },
    { label: 'Camera: reset the 3D view', run: () => { need3d(); setTimeout(() => V3.ok && fit3d(), 60); } },
    toggle('Cutaway', S.opt.cut, () => $('#cutBtn').click()),
    toggle('Shadows', S.opt.shadows, () => $('#shadowBtn').click()),
    toggle('Block layers', layerOn(), () => toggleLayers(), 'K'),
    toggle('Layers: outline the layer below', S.opt.olBelow, () => { S.opt.olBelow = !S.opt.olBelow; LS.set('opt', S.opt); renderOptbar(); req2d(); }),
    toggle('Layers: outline the layer above', S.opt.olAbove, () => { S.opt.olAbove = !S.opt.olAbove; LS.set('opt', S.opt); renderOptbar(); req2d(); }),
    toggle('Show progress', S.opt.progress, () => { S.opt.progress = !S.opt.progress; LS.set('opt', S.opt); progDrawCache.key = ''; req2d(); mark3d(); if (S.tab === 'build') renderBuildPane(); }),
    toggle('What I can afford', S.opt.afford, () => { S.opt.afford = !S.opt.afford; LS.set('opt', S.opt); progDrawCache.key = ''; req2d(); mark3d(); if (S.tab === 'build') renderBuildPane(); }),
    ...MIRROR_MODES.map(m => ({ label: `Mirror: ${m[3]}`, key: 'X', run: () => setMirror(m[0]) })),
    ...PANEL_TABS.map(t => ({ label: `Panel: ${t[0].toUpperCase() + t.slice(1)} tab`, run: () => { openTab(t); LS.set('tab', t); } })),
    { label: 'Undo', key: 'Ctrl+Z', run: undo }, { label: 'Redo', key: 'Ctrl+Shift+Z', run: redo },
    { label: 'History: every step you can undo', run: toggleHistPop },
    { label: 'Fit the plan', key: '0', run: () => fitView(true) },
    { label: 'Walk around the build', run: () => { need3d(); setTimeout(() => $('#walkBtn').click(), 80); } },
    { label: 'Crafting list', run: openCrafting },
    { label: 'Keyboard shortcuts', key: '?', run: openKeys },
    { label: 'New plan', run: newPlanDialog },
    { label: 'Levels: add a level on top', run: () => addLevel('top') }, { label: 'Levels: dig a level below', run: () => addLevel('below') },
    { label: 'Steps: next step that isn’t built', key: 'N', run: () => { openTab('build'); nextUnbuilt(); } },
    { label: 'Steps: next step', key: '.', run: () => { openTab('build'); goStep(STEPS.at + 1); } },
    { label: 'Steps: previous step', key: ',', run: () => { openTab('build'); goStep(Math.max(0, STEPS.at - 1)); } },
    { label: 'Steps: stop following', run: stopSteps, when: () => STEPS.at >= 0 },
  ];
  return cmds.filter(c => !c.when || c.when());
}
const RECENT_CMDS = 'recentCmds';
function noteCommand(label) { const r = (LS.get(RECENT_CMDS, []) || []).filter(x => x !== label); r.unshift(label); LS.set(RECENT_CMDS, r.slice(0, 8)); }
