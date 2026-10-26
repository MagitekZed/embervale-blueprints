// ---------------------------------------------------------------------------
// Projects: plans grouped by a `project` name on each plan doc (no separate list: a project exists while a
// plan is in it). The top bar picks a project, then a plan in it; "All plans" lists every plan by project.
// ---------------------------------------------------------------------------
const NO_PROJECT = '';
const projectOf = d => (d && typeof d.project === 'string' ? d.project.trim().slice(0, 40) : NO_PROJECT);
// Every project, with how many plans it holds and when one was last changed. Named ones by name, then "No project".
function projectList() {
  const m = new Map();
  for (const [id, d] of S.plans) {
    const p = id === S.planId && S.plan ? (S.plan.project || NO_PROJECT) : projectOf(d);
    const r = m.get(p) || { name: p, n: 0, latest: 0 };
    r.n++; r.latest = Math.max(r.latest, Number(d.updatedAt) || 0); m.set(p, r);
  }
  if (S.plan && S.planId && !S.plans.has(S.planId)) { const p = S.plan.project || NO_PROJECT; if (!m.has(p)) m.set(p, { name: p, n: 1, latest: Date.now() }); }
  return [...m.values()].sort((a, b) => (a.name === NO_PROJECT) - (b.name === NO_PROJECT) || a.name.localeCompare(b.name));
}
const projectLabel = p => p || 'No project';
// The project the bar is showing: the one picked, else the open plan's.
function currentProject() { return S.project != null ? S.project : (S.plan ? S.plan.project || NO_PROJECT : NO_PROJECT); }

function renderPlanSelect() {
  const psel = $('#projectSelect'), sel = $('#planSelect');
  const list = sortedPlans(), cur = currentProject(), all = cur === '*';
  const nameOf = (id, d) => (id === S.planId && S.plan ? S.plan.name : (str(d.name, 80) || 'Untitled plan'));
  const projOf = (id, d) => (id === S.planId && S.plan ? S.plan.project || NO_PROJECT : projectOf(d));
  // the project picker
  if (psel) {
    const projects = projectList();
    psel.replaceChildren(
      h('option', { value: '*', text: `All plans (${list.length})` }),
      ...projects.map(p => h('option', { value: p.name, text: `${projectLabel(p.name)} (${p.n})` })),
      h('option', { value: '__new__', text: 'New project…' }));
    psel.value = all ? '*' : cur;
    if (psel.value !== (all ? '*' : cur)) { psel.append(h('option', { value: cur, text: projectLabel(cur) })); psel.value = cur; }
    psel.disabled = !S.loaded;
  }
  // the plan picker: this project's plans, or all of them under their projects
  let opts;
  if (all) {
    opts = projectList().map(p => h('optgroup', { label: projectLabel(p.name) },
      ...list.filter(([id, d]) => projOf(id, d) === p.name).map(([id, d]) => h('option', { value: id, text: nameOf(id, d) }))));
  } else {
    opts = list.filter(([id, d]) => projOf(id, d) === cur).map(([id, d]) => h('option', { value: id, text: nameOf(id, d) }));
  }
  if (S.planId && !S.plans.has(S.planId) && S.plan) opts.unshift(h('option', { value: S.planId, text: S.plan.name }));
  if (!opts.length) opts.push(h('option', { value: '', text: S.loaded ? 'No plans yet' : 'Loading…' }));
  sel.replaceChildren(...opts);
  sel.value = S.planId || '';
  sel.disabled = !S.loaded;
}
// Switching project opens its most recently changed plan (unless the open plan is already in it).
function pickProject(v) {
  if (v === '__new__') { newProjectDialog(); renderPlanSelect(); return; }
  S.project = v;
  LS.set('project', v);
  if (v !== '*' && (!S.plan || (S.plan.project || NO_PROJECT) !== v)) {
    const next = sortedPlans().find(([, d]) => projectOf(d) === v);
    if (next) { openPlan(next[0]); return; }
  }
  renderPlanSelect();
}
// A new project needs a plan in it: start one there, or move the open plan in.
function newProjectDialog() {
  const name = h('input', { type: 'text', value: '', maxlength: '40', placeholder: 'Laketown', 'aria-label': 'Project name' });
  const err = h('p', { class: 'err', hidden: true });
  const go = move => {
    const n = name.value.trim().slice(0, 40);
    if (!n) { err.textContent = 'Give the project a name.'; err.hidden = false; return; }
    closeModal();
    S.project = n; LS.set('project', n);
    if (move && S.plan) { setPlanProject(n); toast(`“${S.plan.name}” is in ${n} now.`); }
    else newPlanDialog(n);
  };
  name.addEventListener('input', () => { err.hidden = true; });
  name.addEventListener('keydown', e => { if (e.key === 'Enter') go(false); });
  openModal('New project', [h('p', { class: 'note', style: 'font-size:14px', text: 'A project groups plans: a base and its detail blueprints, say. It exists while a plan is in it.' }),
    h('label', { class: 'field' }, h('span', { text: 'Name' }), name), err],
    [{ label: 'Cancel', onClick: closeModal },
     ...(S.plan && !S.readOnly ? [{ label: 'Move this plan into it', onClick: () => go(true) }] : []),
     { label: 'Start a plan in it', primary: true, onClick: () => go(false) }]);
}
function setPlanProject(n) {
  if (!S.plan || S.readOnly) return;
  S.plan.project = (n || '').trim().slice(0, 40);
  if (S.project !== '*') { S.project = S.plan.project; LS.set('project', S.project); }   // the bar follows the plan
  markDirty(); renderPlanSelect(); renderPlanPane();
}
// A select of the projects there are, "No project", and a new one typed in.
function projectField(value, onChange) {
  const names = [...new Set([...projectList().map(p => p.name), value || NO_PROJECT])].filter(n => n !== NO_PROJECT).sort((a, b) => a.localeCompare(b));
  const sel = h('select', { 'aria-label': 'Project' }, h('option', { value: '', text: 'No project' }), ...names.map(n => h('option', { value: n, text: n })), h('option', { value: '__new__', text: 'New project…' }));
  sel.value = value || '';
  const other = h('input', { type: 'text', maxlength: '40', placeholder: 'New project name', 'aria-label': 'New project name', hidden: true });
  sel.addEventListener('change', () => { if (sel.value === '__new__') { other.hidden = false; other.focus(); } else { other.hidden = true; onChange(sel.value); } });
  other.addEventListener('change', () => { const n = other.value.trim().slice(0, 40); if (n) onChange(n); });
  return { sel, other, value: () => (sel.value === '__new__' ? other.value.trim().slice(0, 40) : sel.value) };
}
// Rename a project: every plan in it, saved (the open one through the usual save).
async function renameProject(from, to) {
  to = (to || '').trim().slice(0, 40);
  if (!to || to === from || S.readOnly) return;
  let n = 0;
  for (const [id, d] of S.plans) {
    if (id === S.planId) continue;
    if (projectOf(d) !== from) continue;
    try { await S.store.save(id, { ...d, project: to }); n++; } catch { toast(`Couldn’t move “${d.name}”. Try again.`, 'bad'); }
  }
  if (S.plan && (S.plan.project || NO_PROJECT) === from) { S.plan.project = to; markDirty(); n++; }
  S.project = to; LS.set('project', to);
  renderPlanSelect(); renderPlanPane();
  toast(`Renamed the project to ${to} (${n} plan${n === 1 ? '' : 's'}).`);
}
function renameProjectDialog() {
  const from = S.plan ? S.plan.project || NO_PROJECT : NO_PROJECT;
  if (!from) return;
  const name = h('input', { type: 'text', value: from, maxlength: '40', 'aria-label': 'Project name' });
  const go = () => { closeModal(); renameProject(from, name.value); };
  name.addEventListener('keydown', e => { if (e.key === 'Enter') go(); });
  openModal(`Rename ${from}`, [h('label', { class: 'field' }, h('span', { text: 'Name' }), name)], [{ label: 'Cancel', onClick: closeModal }, { label: 'Rename', primary: true, onClick: go }]);
}
// The Plan tab's project row.
function projectSection() {
  const P = S.plan, cur = P.project || NO_PROJECT;
  const f = projectField(cur, v => setPlanProject(v));
  f.sel.disabled = S.readOnly;
  return h('div', { class: 'section' },
    h('label', { class: 'field', title: 'Group this plan with others: a base and its detail blueprints, say' }, h('span', { text: 'Project' }), f.sel), f.other,
    cur ? h('div', { class: 'btnrow' }, h('button', { class: 'btn btn-sm', type: 'button', disabled: S.readOnly, text: `Rename ${cur}…`, title: 'Rename the project for every plan in it', onclick: renameProjectDialog })) : null);
}
