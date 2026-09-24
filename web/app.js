'use strict';

const DOWNLOAD_URL = 'https://github.com/ShiduLab/ComboCode/releases/latest';
const MINE_KEY = 'combocode.web.userGoals.v1';
const FAVORITES_KEY = 'combocode.web.favorites.v1';

const state = {
  standardGoals: [],
  userGoals: [],
  goals: [],
  favorites: new Set(),
  currentGoal: null,
  currentRoute: null,
  currentArchive: null,
  currentMine: null,
  activeTab: 'search',
  searchSort: {col: null, desc: false},
  archiveSort: {col: 'goal', desc: false},
  editingMineId: null,
  version: 'ComboCode Web'
};

const $ = id => document.getElementById(id);
const els = {};

function normalize(text='') {
  return String(text).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()
    .replace(/[^a-z0-9+#.:/_-]+/g,' ').trim().replace(/\s+/g,' ');
}

function domains(goal) {
  const vals = [goal.category || 'Altro', ...(Array.isArray(goal.domains) ? goal.domains : goal.domains ? [goal.domains] : [])];
  return [...new Set(vals.filter(Boolean))];
}

function indexGoal(goal) {
  const fields = [
    goal.name, ...(goal.aliases||[]), ...(goal.keywords||[]), goal.description, goal.category,
    ...(Array.isArray(goal.domains)?goal.domains:[]), goal.context, goal.origin,
    ...(goal.routes||[]).flatMap(r=>[r.value,r.kind,r.note])
  ];
  return normalize(fields.filter(Boolean).join(' '));
}

function scoreGoal(goal, query) {
  const q = normalize(query);
  if (!q) return 1;
  const tokens = q.split(' ');
  const name = normalize(goal.name);
  const aliases = (goal.aliases||[]).map(normalize);
  const keywords = (goal.keywords||[]).map(normalize);
  const blob = goal._index || indexGoal(goal);
  let score = 0;
  if (q === name) score += 120;
  if (aliases.includes(q)) score += 112;
  if (keywords.includes(q)) score += 104;
  if (name.startsWith(q)) score += 80;
  if (aliases.some(a=>a.startsWith(q))) score += 72;
  if (keywords.some(k=>k.startsWith(q))) score += 68;
  if (name.includes(q)) score += 62;
  if (aliases.some(a=>a.includes(q))) score += 54;
  if (keywords.some(k=>k.includes(q))) score += 50;
  if (blob.includes(q)) score += 40;
  for (const t of tokens) {
    if (name.includes(t)) score += 16;
    else if (aliases.some(a=>a.includes(t))) score += 13;
    else if (keywords.some(k=>k.includes(t))) score += 11;
    else if (blob.includes(t)) score += 8;
    else return 0;
  }
  return score;
}

function parseStorage(key, fallback) {
  try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : fallback; }
  catch { return fallback; }
}

function saveMine() { localStorage.setItem(MINE_KEY, JSON.stringify(state.userGoals)); }
function saveFavorites() { localStorage.setItem(FAVORITES_KEY, JSON.stringify([...state.favorites])); }

function refreshCombinedGoals() {
  const map = new Map();
  for (const g of [...state.standardGoals, ...state.userGoals]) {
    if (!g || !g.id) continue;
    const copy = structuredClone(g);
    copy._index = indexGoal(copy);
    map.set(copy.id, copy);
  }
  state.goals = [...map.values()];
  populateFilters();
}

async function loadCatalog() {
  const [versionResp, indexResp] = await Promise.all([fetch('VERSION'), fetch('packs-index.json')]);
  if (versionResp.ok) state.version = (await versionResp.text()).trim();
  if (!indexResp.ok) throw new Error('Indice pack non disponibile.');
  const packNames = await indexResp.json();
  const packs = await Promise.all(packNames.map(name => fetch(`data/packs/${name}`).then(r => {
    if (!r.ok) throw new Error(`Pack non disponibile: ${name}`);
    return r.json();
  })));
  const goals = [];
  for (const p of packs) goals.push(...(p.goals || []));
  state.standardGoals = goals;
  state.userGoals = parseStorage(MINE_KEY, []);
  state.favorites = new Set(parseStorage(FAVORITES_KEY, []));
  refreshCombinedGoals();
}

function populateFilters() {
  const categories = ['Tutte', ...[...new Set(state.goals.flatMap(domains))].sort((a,b)=>a.localeCompare(b,'it',{sensitivity:'base'}))];
  const kinds = ['TUTTI', ...[...new Set(state.goals.flatMap(g=>(g.routes||[]).map(r=>r.kind||'ROUTE')))].sort((a,b)=>a.localeCompare(b))];
  setOptions(els.globalCategory, categories, els.globalCategory.value || 'Tutte');
  setOptions(els.archiveCategory, categories, els.archiveCategory.value || 'Tutte');
  setOptions(els.archiveKind, kinds, els.archiveKind.value || 'TUTTI');
}

function setOptions(select, values, keep) {
  select.innerHTML = '';
  for (const v of values) {
    const o = document.createElement('option'); o.value=v; o.textContent=v; select.appendChild(o);
  }
  if (values.includes(keep)) select.value = keep;
}

function setTab(name) {
  state.activeTab = name;
  document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));
  document.querySelectorAll('.tabpage').forEach(p=>p.classList.toggle('active',p.id===`tab-${name}`));
  if (name==='search') refreshSearch();
  if (name==='all') refreshArchive();
  if (name==='mine') refreshMine();
}

function searchGoals(query, category='Tutte') {
  let rows = state.goals.filter(g => category==='Tutte' || domains(g).includes(category))
    .map(g=>({goal:g,score:scoreGoal(g,query)})).filter(x=>x.score>0);
  rows.sort((a,b)=>b.score-a.score || a.goal.name.localeCompare(b.goal.name,'it',{sensitivity:'base'}));
  return rows.slice(0,80);
}

function td(text, cls='') { const x=document.createElement('td'); x.textContent=text ?? ''; if(cls)x.className=cls; return x; }

function prepareRow(tr) {
  tr.tabIndex = -1;
  return tr;
}

function selectRow(tbody, tr) {
  tbody.querySelectorAll('tr').forEach(r => {
    r.classList.remove('selected');
    r.tabIndex = -1;
  });
  if (tr) {
    tr.classList.add('selected');
    tr.tabIndex = 0;
  }
}

function bindRowNavigation(table) {
  table.addEventListener('keydown', e => {
    if (!['ArrowUp','ArrowDown','Home','End'].includes(e.key)) return;

    const body = table.tBodies[0];
    const rows = [...body.rows];
    if (!rows.length) return;

    const selected = body.querySelector('tr.selected');
    let index = selected ? rows.indexOf(selected) : 0;

    if (e.key === 'ArrowUp') index = Math.max(0, index - 1);
    if (e.key === 'ArrowDown') index = Math.min(rows.length - 1, index + 1);
    if (e.key === 'Home') index = 0;
    if (e.key === 'End') index = rows.length - 1;

    e.preventDefault();
    const next = rows[index];
    next.click();
    next.focus({preventScroll:true});
    next.scrollIntoView({block:'nearest'});
  });
}

function refreshSearch() {
  const rows = searchGoals(els.globalSearch.value, els.globalCategory.value);
  if (state.searchSort.col) {
    const {col,desc}=state.searchSort;
    rows.sort((a,b)=>{
      const av=normalize(col==='goal'?a.goal.name:a.goal.category), bv=normalize(col==='goal'?b.goal.name:b.goal.category);
      return (av<bv?-1:av>bv?1:0)*(desc?-1:1);
    });
  }
  const body=els.goalTable.tBodies[0]; body.innerHTML='';
  for (const {goal} of rows) {
    const tr=prepareRow(document.createElement('tr')); tr.dataset.id=goal.id;
    tr.append(td(`${state.favorites.has(goal.id)?'★ ':''}${goal.name}`)); tr.append(td(goal.category||''));
    tr.addEventListener('click',()=>{showGoal(goal,tr);tr.focus({preventScroll:true});}); body.append(tr);
  }
  if (rows.length) showGoal(rows[0].goal, body.rows[0]); else clearGoal();
  setStatus(`${rows.length} obiettivi trovati · ${state.goals.length} nell’archivio · ${state.version}`);
}

function showGoal(goal,tr) {
  state.currentGoal=goal; state.currentRoute=null; selectRow(els.goalTable.tBodies[0],tr);
  els.goalTitle.textContent=goal.name||'ComboCode'; els.goalDescription.textContent=goal.description||'Un obiettivo, più route.';
  const body=els.routeTable.tBodies[0]; body.innerHTML='';
  (goal.routes||[]).forEach((route,i)=>{
    const row=prepareRow(document.createElement('tr')); row.dataset.index=i;
    row.append(td(`${route.kind||'ROUTE'}  ·  ${route.value||''}`)); row.append(td(route.safety||'SAFE','center'));
    row.addEventListener('click',()=>{showSearchRoute(goal,route,row);row.focus({preventScroll:true});}); body.append(row);
  });
  els.searchFavorite.textContent = state.favorites.has(goal.id)?'★ Preferito':'☆ Preferito';
  if ((goal.routes||[]).length) showSearchRoute(goal,goal.routes[0],body.rows[0]); else updateSearchButtons(null);
}

function clearGoal() {
  state.currentGoal=null; state.currentRoute=null; els.goalTitle.textContent='ComboCode'; els.goalDescription.textContent='Nessun risultato.';
  els.routeTable.tBodies[0].innerHTML=''; els.routeDetail.textContent=''; updateSearchButtons(null);
}

function showSearchRoute(goal,route,tr) {
  state.currentGoal=goal; state.currentRoute=route; selectRow(els.routeTable.tBodies[0],tr);
  els.routeDetail.textContent = routeDescription(goal,route); updateSearchButtons(route);
}

function canWebExecute(route) {
  if (!route) return false;
  const v=String(route.value||'').trim();
  return /^(https?:|mailto:|tel:)/i.test(v);
}

function routeInstruction(route) {
  if (!route) return '';
  const k=String(route.kind||'').toUpperCase();
  if (canWebExecute(route)) return 'Puoi aprire questa route direttamente dal sito oppure cliccare COPIA.';
  if (k==='HOTKEY') return 'Usa direttamente la combinazione di tasti indicata sul PC.';
  if (k==='RUN') return 'Clicca COPIA, premi Win + R, incolla il comando e premi Invio.';
  if (k==='CMD') return 'Clicca COPIA, apri il Prompt dei comandi, incolla il comando e premi Invio.';
  if (k==='POWERSHELL') return 'Clicca COPIA, apri PowerShell, incolla il comando e premi Invio.';
  if (k==='URI' || k==='APP') return 'Clicca COPIA, premi Win + R, incolla la stringa e premi Invio.';
  if (k==='MOUSE' || k==='KEY+MOUSE' || k==='TASTIERA+MOUSE') return 'Esegui sul PC il gesto o la combinazione indicata.';
  return 'Clicca COPIA e usa il codice nel contesto indicato sul tuo PC.';
}

function routeDescription(goal,route) {
  const bits=[];
  if (route.note) bits.push(route.note);
  if (route.verified) bits.push(`Verifica: ${route.verified}.`);
  bits.push(routeInstruction(route));
  return bits.join(' ');
}

function executionHint(route) {
  if (!route || canWebExecute(route)) return '';
  return 'Per usare questo comando scarica ComboCode';
}

function hintHTML(route) {
  const txt=executionHint(route); return txt ? `${txt} · <a href="${DOWNLOAD_URL}" target="_blank" rel="noopener">Download</a>` : '';
}

function updateSearchButtons(route) {
  const ok=canWebExecute(route); els.searchExecute.disabled=!ok; els.searchCopy.disabled=!route;
  els.searchSource.disabled=!(route && route.source && /^https?:/i.test(route.source));
  els.searchExecuteHint.innerHTML=hintHTML(route);
}

function currentArchiveRoute(){ return state.currentArchive?.route || null; }
function currentMineRoute(){ return state.currentMine?.route || null; }

function archiveRows() {
  const q=els.archiveSearch.value, cat=els.archiveCategory.value, kind=els.archiveKind.value;
  const rows=[];
  for (const g of state.goals) {
    if (cat!=='Tutte' && !domains(g).includes(cat)) continue;
    if (q && scoreGoal(g,q)<=0) continue;
    (g.routes||[]).forEach((route,index)=>{ if(kind==='TUTTI'||route.kind===kind) rows.push({goal:g,route,index}); });
  }
  const {col,desc}=state.archiveSort;
  const getter=r=>({goal:r.goal.name,kind:r.route.kind,value:r.route.value,cat:r.goal.category,safety:r.route.safety,verified:r.route.verified}[col]||'');
  rows.sort((a,b)=>normalize(getter(a)).localeCompare(normalize(getter(b)))*(desc?-1:1));
  return rows;
}

function refreshArchive() {
  const rows=archiveRows(); const body=els.archiveTable.tBodies[0]; body.innerHTML=''; state.currentArchive=null;
  rows.forEach((x,i)=>{
    const tr=prepareRow(document.createElement('tr')); tr.dataset.index=i;
    tr.append(td(x.goal.name));tr.append(td(x.route.kind||'','center'));tr.append(td(x.route.value||''));tr.append(td(x.goal.category||''));tr.append(td(x.route.safety||'SAFE','center'));tr.append(td(x.route.verified||'non verificato'));
    tr.addEventListener('click',()=>{showArchiveRow(x,tr);tr.focus({preventScroll:true});});body.append(tr);
  });
  const routeCount=state.goals.reduce((n,g)=>n+(g.routes||[]).length,0);
  els.archiveSummary.textContent=`${rows.length} route visualizzate · archivio: ${state.goals.length} obiettivi / ${routeCount} route · ordine ${state.archiveSort.col} ${state.archiveSort.desc?'↓':'↑'}`;
  els.archiveDetail.textContent=''; els.archiveExecute.disabled=true; els.archiveCopy.disabled=true; els.archiveSource.disabled=true; els.archiveExecuteHint.innerHTML='';
  if(rows.length) showArchiveRow(rows[0],body.rows[0]); setStatus(els.archiveSummary.textContent);
}

function showArchiveRow(x,tr) {
  state.currentArchive=x; selectRow(els.archiveTable.tBodies[0],tr);
  els.archiveDetail.textContent=`${x.goal.name} · ${routeDescription(x.goal,x.route)}`;
  els.archiveExecute.disabled=!canWebExecute(x.route); els.archiveCopy.disabled=false;
  els.archiveSource.disabled=!(x.route.source && /^https?:/i.test(x.route.source)); els.archiveExecuteHint.innerHTML=hintHTML(x.route);
}

function refreshMine(selectId=null) {
  const q=normalize(els.mineSearch.value); let rows=[];
  for (const g of state.userGoals) {
    const route=(g.routes||[{}])[0]; const blob=normalize([g.name,g.context,g.description,...(g.aliases||[]),route.kind,route.value,route.note].join(' '));
    if(q && !blob.includes(q)) continue; rows.push({goal:g,route});
  }
  rows.sort((a,b)=>normalize(a.goal.context).localeCompare(normalize(b.goal.context)) || normalize(a.goal.name).localeCompare(normalize(b.goal.name)));
  const body=els.mineTable.tBodies[0]; body.innerHTML=''; state.currentMine=null;
  rows.forEach(x=>{
    const tr=prepareRow(document.createElement('tr')); tr.dataset.id=x.goal.id;
    tr.append(td(x.goal.name));tr.append(td(x.route.kind||'','center'));tr.append(td(x.route.value||''));tr.append(td(x.goal.context||''));tr.append(td(x.route.safety||'SAFE','center'));
    tr.addEventListener('click',()=>{showMineRow(x,tr);tr.focus({preventScroll:true});});body.append(tr);
  });
  els.mineSummary.textContent=`${rows.length} shortcut personali · archivio locale del browser`;
  els.mineDetail.textContent=''; [els.mineExecute,els.mineCopy,els.mineEdit,els.mineDelete].forEach(b=>b.disabled=true); els.mineExecuteHint.innerHTML='';
  const chosen=rows.findIndex(x=>x.goal.id===selectId); if(rows.length) showMineRow(rows[chosen>=0?chosen:0],body.rows[chosen>=0?chosen:0]);
  setStatus(els.mineSummary.textContent);
}

function showMineRow(x,tr) {
  state.currentMine=x; selectRow(els.mineTable.tBodies[0],tr);
  els.mineDetail.textContent=`${x.goal.name} · ${routeDescription(x.goal,x.route)}`;
  els.mineExecute.disabled=!canWebExecute(x.route); els.mineCopy.disabled=false; els.mineEdit.disabled=false; els.mineDelete.disabled=false; els.mineExecuteHint.innerHTML=hintHTML(x.route);
}

async function copyText(text) {
  if (!text) return;
  try { await navigator.clipboard.writeText(text); toast('Copiato negli appunti.'); }
  catch {
    const ta=document.createElement('textarea'); ta.value=text; ta.style.position='fixed';ta.style.opacity='0';document.body.append(ta);ta.select();document.execCommand('copy');ta.remove();toast('Copiato negli appunti.');
  }
}

function executeWeb(route) { if (canWebExecute(route)) window.open(route.value,'_blank','noopener'); }
function openSource(route) { if(route?.source && /^https?:/i.test(route.source)) window.open(route.source,'_blank','noopener'); }

function toggleFavorite() {
  const g=state.currentGoal;if(!g)return;
  if(state.favorites.has(g.id))state.favorites.delete(g.id);else state.favorites.add(g.id);saveFavorites();refreshSearch();
}

function exportMarkdown(goal,route) {
  if(!goal||!route)return;
  const md=`---\ntype: ComboCode\nplatform: ${goal.platform||'Windows'}\ncategory: ${goal.category||'Altro'}\n---\n\n# ${goal.name}\n\n${goal.description||''}\n\n## ${route.kind||'ROUTE'}\n\n\`${route.value||''}\`\n\n${routeInstruction(route)}\n`;
  downloadBlob(`${safeName(goal.name)}.md`,md,'text/markdown;charset=utf-8');
}
function safeName(s){return String(s||'ComboCode').replace(/[\\/:*?"<>|]+/g,'-').trim()}
function downloadBlob(name,content,type){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([content],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500)}

function cloneToMine(goal,route) {
  if(!goal||!route)return;
  const copy={id:`user.web.${crypto.randomUUID?.()||Date.now()}`,name:goal.name,category:'MIE',context:goal.context||'Generale',origin:'user',description:`Shortcut personale · ${goal.context||'Generale'}`,aliases:[...(goal.aliases||[])],keywords:['personale','mia','shortcut',route.kind||''],platform:'Personalizzata',routes:[structuredClone(route)]};
  copy.routes[0].verified='PERSONALE';copy.routes[0].source_label='Creata dall’utente';state.userGoals.push(copy);saveMine();refreshCombinedGoals();toast('Salvata nelle MIE.');
}

function openMineDialog(goal=null) {
  state.editingMineId=goal?.id||null; const r=(goal?.routes||[{}])[0];
  els.mineDialogTitle.textContent=goal?'ComboCode — Modifica shortcut':'ComboCode — Aggiungi shortcut';
  els.fName.value=goal?.name||''; els.fKind.value=r.kind||'HOTKEY'; els.fValue.value=r.value||''; els.fContext.value=goal?.context||''; els.fAliases.value=(goal?.aliases||[]).join(', '); els.fSafety.value=r.safety||'SAFE'; els.fNote.value=r.note||'';
  els.mineDialog.showModal(); setTimeout(()=>els.fName.focus(),0);
}

function saveMineForm(e) {
  e.preventDefault();
  const name=els.fName.value.trim(), value=els.fValue.value.trim(); if(!name||!value)return;
  const kind=els.fKind.value, context=els.fContext.value.trim()||'Generale', aliases=els.fAliases.value.split(',').map(x=>x.trim()).filter(Boolean);
  const id=state.editingMineId||`user.web.${crypto.randomUUID?.()||Date.now()}`;
  const goal={id,name,category:'MIE',context,origin:'user',description:`Shortcut personale · ${context}`,aliases,keywords:['personale','mia','shortcut',context,kind,...aliases],platform:'Personalizzata',routes:[{kind,value,handler:'manual',executable:false,safety:els.fSafety.value,verified:'PERSONALE',source_label:'Creata dall’utente',note:els.fNote.value.trim()}]};
  const idx=state.userGoals.findIndex(g=>g.id===id); if(idx>=0)state.userGoals[idx]=goal;else state.userGoals.push(goal);
  saveMine();refreshCombinedGoals();els.mineDialog.close();refreshMine(id);toast('Shortcut salvata.');
}

function deleteMine() {
  if(!state.currentMine)return; const id=state.currentMine.goal.id;
  if(!confirm(`Eliminare “${state.currentMine.goal.name}”?`))return;
  state.userGoals=state.userGoals.filter(g=>g.id!==id);saveMine();refreshCombinedGoals();refreshMine();toast('Shortcut eliminata.');
}

function exportMine() { downloadBlob('ComboCode-MIE.json',JSON.stringify({goals:state.userGoals},null,2),'application/json;charset=utf-8'); }
async function importMine(file) {
  try { const data=JSON.parse(await file.text()); const goals=Array.isArray(data)?data:(data.goals||[]); if(!Array.isArray(goals))throw new Error();
    const map=new Map(state.userGoals.map(g=>[g.id,g])); for(const g of goals){if(g?.id&&g?.name)map.set(g.id,g)} state.userGoals=[...map.values()];saveMine();refreshCombinedGoals();refreshMine();toast('Import completato.');
  } catch { alert('File JSON non valido per ComboCode.'); }
}

function setStatus(text){els.statusText.textContent=text}
let toastTimer; function toast(text){els.toast.textContent=text;els.toast.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>els.toast.classList.remove('show'),1600)}

function bindUI() {
  [els.goalTable, els.routeTable, els.archiveTable, els.mineTable].forEach(bindRowNavigation);
  document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>setTab(b.dataset.tab)));
  els.globalSearch.addEventListener('input',refreshSearch); els.globalCategory.addEventListener('change',refreshSearch); els.clearGlobal.addEventListener('click',()=>{els.globalSearch.value='';refreshSearch();els.globalSearch.focus()});
  els.goalTable.querySelectorAll('th[data-sort]').forEach(th=>th.addEventListener('click',()=>{const c=th.dataset.sort;if(state.searchSort.col===c)state.searchSort.desc=!state.searchSort.desc;else state.searchSort={col:c,desc:false};refreshSearch()}));
  els.searchExecute.addEventListener('click',()=>executeWeb(state.currentRoute)); els.searchCopy.addEventListener('click',()=>copyText(state.currentRoute?.value)); els.searchFavorite.addEventListener('click',toggleFavorite); els.searchExport.addEventListener('click',()=>exportMarkdown(state.currentGoal,state.currentRoute)); els.searchSaveMine.addEventListener('click',()=>cloneToMine(state.currentGoal,state.currentRoute)); els.searchSource.addEventListener('click',()=>openSource(state.currentRoute));

  [els.archiveSearch,els.archiveKind,els.archiveCategory].forEach(x=>x.addEventListener(x.tagName==='INPUT'?'input':'change',refreshArchive)); els.archiveReset.addEventListener('click',()=>{els.archiveSearch.value='';els.archiveKind.value='TUTTI';els.archiveCategory.value='Tutte';refreshArchive()});
  els.archiveTable.querySelectorAll('th[data-sort]').forEach(th=>th.addEventListener('click',()=>{const c=th.dataset.sort;if(state.archiveSort.col===c)state.archiveSort.desc=!state.archiveSort.desc;else state.archiveSort={col:c,desc:false};refreshArchive()}));
  els.archiveExecute.addEventListener('click',()=>executeWeb(currentArchiveRoute())); els.archiveCopy.addEventListener('click',()=>copyText(currentArchiveRoute()?.value)); els.archiveSaveMine.addEventListener('click',()=>state.currentArchive&&cloneToMine(state.currentArchive.goal,state.currentArchive.route)); els.archiveSource.addEventListener('click',()=>openSource(currentArchiveRoute()));

  els.mineSearch.addEventListener('input',()=>refreshMine()); els.mineClear.addEventListener('click',()=>{els.mineSearch.value='';refreshMine();els.mineSearch.focus()}); els.mineAdd.addEventListener('click',()=>openMineDialog()); els.mineEdit.addEventListener('click',()=>state.currentMine&&openMineDialog(state.currentMine.goal)); els.mineDelete.addEventListener('click',deleteMine); els.mineExecute.addEventListener('click',()=>executeWeb(currentMineRoute())); els.mineCopy.addEventListener('click',()=>copyText(currentMineRoute()?.value));
  els.mineExport.addEventListener('click',exportMine); els.mineImport.addEventListener('click',()=>els.mineImportFile.click()); els.mineImportFile.addEventListener('change',()=>{const f=els.mineImportFile.files[0];if(f)importMine(f);els.mineImportFile.value='' });
  els.mineForm.addEventListener('submit',saveMineForm);
  els.mineForm.querySelector('button[value="cancel"]').addEventListener('click',()=>els.mineDialog.close());

  document.addEventListener('keydown',e=>{
    if(e.key==='Escape' && els.mineDialog.open){els.mineDialog.close();return}
    if(e.ctrlKey && (e.key.toLowerCase()==='k'||e.key.toLowerCase()==='l')){e.preventDefault();els.globalSearch.focus();els.globalSearch.select()}
    if(e.ctrlKey&&e.key==='1'){e.preventDefault();setTab('search')} if(e.ctrlKey&&e.key==='2'){e.preventDefault();setTab('all')} if(e.ctrlKey&&e.key==='3'){e.preventDefault();setTab('mine')}
  });
}

function mapElements() {
  const ids=['globalSearch','clearGlobal','globalCategory','goalTable','routeTable','goalTitle','goalDescription','routeDetail','searchExecute','searchCopy','searchFavorite','searchExport','searchSaveMine','searchSource','searchExecuteHint','archiveSearch','archiveKind','archiveCategory','archiveReset','archiveTable','archiveSummary','archiveDetail','archiveExecute','archiveCopy','archiveSaveMine','archiveSource','archiveExecuteHint','mineSearch','mineClear','mineAdd','mineImport','mineExport','mineImportFile','mineTable','mineDetail','mineExecute','mineCopy','mineEdit','mineDelete','mineExecuteHint','mineSummary','statusText','mineDialog','mineForm','mineDialogTitle','fName','fKind','fValue','fContext','fAliases','fSafety','fNote','toast'];
  for(const id of ids)els[id]=$(id);
}

async function start() {
  mapElements(); bindUI(); setStatus('Caricamento archivio ComboCode…');
  try { await loadCatalog(); refreshSearch(); refreshArchive(); refreshMine(); setTab('search'); if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js').catch(()=>{}); }
  catch(err){console.error(err);setStatus(`Errore caricamento: ${err.message}`);els.goalDescription.textContent='Impossibile caricare l’archivio ComboCode.';}
}

document.addEventListener('DOMContentLoaded',start);
