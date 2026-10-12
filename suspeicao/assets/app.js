import * as pdfjsLib from '../vendor/pdf.min.mjs';
import { renderCard, BRAND, setDocs, docOf, sujeito, pesoLongo, pesoItem, pesoResumo, refsTxt } from './card.js';
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL('../vendor/pdf.worker.min.js', import.meta.url).href;

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
const TAGS = { documentado: ['t-doc', 'documentado'], alegado: ['t-all', 'alegado'], 'interpretação': ['t-int', 'interpretação'] };
const tag = l => { const t = TAGS[l] || ['t-int', l]; return `<span class="tag ${t[0]}">${t[1]}</span>`; };

let C = null, CH = {}, TOTAL = 441;
const ARG_KEY = 'suspeicao.arg';
const LABELS = ['documentado', 'alegado', 'interpretação'];
/* só mostra os filtros de etiqueta que têm itens na lista */
const labelsIn = list => LABELS.filter(l => list.some(x => x.label === l));
const V = { doc: 'acordao', page: 1, spread: 1, zoom: 1, steps: null, idx: 0, rects: {}, token: 0, docs: new Map() };
const refDoc = r => (r && r.d) || 'acordao';
/* rótulo de um botão de página: "p. 4" no acórdão, "Fachin, p. 45" nos outros documentos */
const pgLabel = (r, pre = '') => refDoc(r) === 'acordao' ? `${pre}p. ${r.p}` : `${docOf(r.d).chip}, p. ${r.p}`;

async function getJSON(u) { const r = await fetch(u); if (!r.ok) throw new Error(u); return r.json(); }

/* ---------- PDF ---------- */
function chunkOf(p, d = V.doc) { return (CH[d] || []).find(c => p >= c.from && p <= c.to); }
function getDoc(c) {
  if (!V.docs.has(c.file)) V.docs.set(c.file, pdfjsLib.getDocument({ url: c.file, disableAutoFetch: false }).promise);
  return V.docs.get(c.file);
}
async function getPage(p, doc = V.doc) { const c = chunkOf(p, doc); const d = await getDoc(c); return d.getPage(p - c.from + 1); }
/* troca o documento aberto no visualizador */
function setDoc(d) {
  if (!CH[d]) d = 'acordao';
  V.doc = d; TOTAL = CH[d][CH[d].length - 1].to;
  $('#vPage').max = TOTAL; $('.v-of').textContent = 'de ' + TOTAL; $('#vDoc').textContent = docOf(d).label;
}

function visiblePages() {
  const a = [V.page];
  if (V.spread === 2 && V.page < TOTAL) a.push(V.page + 1);
  return a;
}
async function render() {
  const my = ++V.token;
  const stage = $('#vStage'), host = $('#vPages');
  const pages = visiblePages();
  const avail = Math.max(240, stage.clientWidth - 24);
  const w = Math.floor(((avail - (pages.length - 1) * 10) / pages.length) * V.zoom);
  $('#vStatus').textContent = 'Carregando página…';
  host.innerHTML = '';
  const boxes = [];
  for (const p of pages) {
    const box = document.createElement('div'); box.className = 'pgbox'; box.dataset.p = p;
    box.style.width = w + 'px'; box.style.height = Math.round(w * 842 / 596) + 'px';
    box.innerHTML = `<span class="pgno">página ${p}</span>`;
    host.appendChild(box); boxes.push(box);
  }
  for (let i = 0; i < pages.length; i++) {
    const p = pages[i], box = boxes[i];
    try {
      const page = await getPage(p);
      if (my !== V.token) return;
      const vp1 = page.getViewport({ scale: 1 });
      const cssW = w, cssH = Math.round(w * vp1.height / vp1.width);
      box.style.height = cssH + 'px';
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const sc = (cssW * dpr) / vp1.width;
      const vp = page.getViewport({ scale: sc });
      const cv = document.createElement('canvas'); cv.width = Math.floor(vp.width); cv.height = Math.floor(vp.height);
      await page.render({ canvasContext: cv.getContext('2d'), viewport: vp }).promise;
      if (my !== V.token) return;
      box.appendChild(cv);
      drawRects(box, p, cssW / vp1.width);
    } catch (e) { if (my === V.token) $('#vStatus').textContent = 'Não foi possível carregar a página ' + p + '.'; return; }
  }
  if (my === V.token) {
    $('#vStatus').textContent = '';
    const first = $('.hl', host); if (first) first.scrollIntoView({ block: 'center', behavior: 'smooth' }); else stage.scrollTop = 0;
    prefetch(pages[pages.length - 1] + 1);
  }
}
function drawRects(box, p, k) {
  (V.rects[p] || []).forEach(r => {
    const d = document.createElement('div'); d.className = 'hl pulse';
    const pad = 1.5;
    d.style.left = (r[0] - pad) * k + 'px'; d.style.top = (r[1] - pad) * k + 'px';
    d.style.width = (r[2] - r[0] + 2 * pad) * k + 'px'; d.style.height = (r[3] - r[1] + 2 * pad) * k + 'px';
    box.appendChild(d);
  });
}
function prefetch(p) { if (p <= TOTAL) { const c = chunkOf(p); if (c) getDoc(c).catch(() => { }); } }

function openPage(p, opts = {}) {
  if (opts.doc && opts.doc !== V.doc) setDoc(opts.doc);
  p = Math.max(1, Math.min(TOTAL, +p || 1));
  const wasOpen = document.body.classList.contains('viewer-open');
  V.page = V.spread === 2 && p % 2 === 0 && p > 1 ? p - 1 : p;
  if (opts.focus) V.focusPage = opts.focus;
  V.rects = {};
  (opts.refs || []).filter(r => refDoc(r) === V.doc).forEach(r => { (V.rects[r.p] ||= []).push(...(r.r || [])); });
  if (opts.extraRects) Object.entries(opts.extraRects).forEach(([k, v]) => (V.rects[k] ||= []).push(...v));
  document.body.classList.add('viewer-open');
  const vw = $('#viewer'); vw.setAttribute('aria-hidden', 'false');
  $('#vPage').value = V.page;
  $('#vPrev').disabled = V.page <= 1; $('#vNext').disabled = V.page >= TOTAL;
  history.replaceState(null, '', V.doc === 'acordao' ? '#p=' + p : `#d=${V.doc}&p=${p}`);
  render();
  if (!wasOpen) setTimeout(() => $('#vClose').focus({ preventScroll: true }), 50);
}
function closeViewer() {
  document.body.classList.remove('viewer-open'); $('#viewer').setAttribute('aria-hidden', 'true');
  V.steps = null; $('#vGuide').hidden = true; history.replaceState(null, '', V.argHash || location.pathname);
  if (V.opener && document.contains(V.opener)) V.opener.focus();
}
function go(delta) { const step = V.spread; openPage(V.page + delta * step, { refs: [] }); }

/* ---------- passo a passo guiado ---------- */
function startGuide(steps, idx = 0) { V.steps = steps; showStep(idx); }
function showStep(i) {
  const s = V.steps[i]; if (!s) return; V.idx = i;
  const g = $('#vGuide'); g.hidden = false;
  $('#vGuideStep').textContent = `Ponto ${i + 1} de ${V.steps.length}`;
  $('#vGuideTag').innerHTML = tag(s.label);
  $('#vGuideText').innerHTML = `<b>${esc(s.title || '')}</b>${s.title ? '. ' : ''}${esc(s.text || '')}`;
  $('#vRefs').innerHTML = (s.refs || []).map(r => `<button class="chip" data-goto="${r.p}" data-doc="${refDoc(r)}">${pgLabel(r)}</button>`).join('');
  $('#gPrev').disabled = i === 0; $('#gNext').disabled = i === V.steps.length - 1;
  const first = (s.refs || [])[0];
  openPage(first ? first.p : V.page, { doc: first ? refDoc(first) : V.doc, refs: s.refs || [] });
}

/* ---------- busca ---------- */
let SEARCH = null;
async function loadSearch() { if (!SEARCH) SEARCH = await getJSON('data/search.json'); return SEARCH; }
async function doSearch(q) {
  const dlg = $('#searchDlg'); if (!dlg.open) dlg.showModal();
  $('#sInfo').textContent = 'Buscando…'; $('#sList').innerHTML = '';
  const terms = norm(q).split(/\s+/).filter(t => t.length > 1);
  if (!terms.length) { $('#sInfo').textContent = 'Digite ao menos uma palavra.'; return; }
  const S = await loadSearch(); const out = [];
  for (const [d, pages] of Object.entries(S)) for (const [p, txt] of Object.entries(pages)) {
    const n = norm(txt);
    if (terms.every(t => n.includes(t))) {
      const i = n.indexOf(terms[0]); const a = Math.max(0, i - 70), b = Math.min(txt.length, i + 110);
      out.push({ d, p: +p, snip: (a ? '…' : '') + txt.slice(a, b) + (b < txt.length ? '…' : ''), c: terms.reduce((s, t) => s + n.split(t).length - 1, 0) });
    }
  }
  const ord = Object.keys(S);
  out.sort((x, y) => ord.indexOf(x.d) - ord.indexOf(y.d) || x.p - y.p);
  $('#sInfo').textContent = out.length ? `${out.length} página(s) com “${q}”. Toque para abrir e ver a palavra marcada.` : `Nenhuma página com “${q}”. Tente outra grafia ou menos palavras. Algumas páginas são imagens e não têm texto pesquisável.`;
  const re = new RegExp('(' + q.trim().split(/\s+/).filter(t => t.length > 1).map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')', 'gi');
  $('#sList').innerHTML = out.slice(0, 200).map(r => `<li><button data-search-page="${r.p}" data-search-doc="${r.d}" data-q="${esc(q)}"><b class="pg">${esc(pgLabel(r))}</b> ${esc(r.snip).replace(re, '<mark>$1</mark>')}</button></li>`).join('');
}
async function openSearchHit(p, q, doc = 'acordao') {
  let extra = {};
  try {
    const b = await getJSON(`data/boxes/${doc === 'acordao' ? '' : doc + '/'}p${String(p).padStart(3, '0')}.json`);
    const terms = norm(q).split(/\s+/).filter(t => t.length > 1);
    extra[p] = b.words.filter(w => terms.some(t => norm(w[0]).includes(t))).map(w => [w[1], w[2], w[3], w[4]]);
  } catch (e) { }
  $('#searchDlg').close();
  V.steps = null; $('#vGuide').hidden = true;
  openPage(p, { doc, extraRects: extra });
}

/* ---------- render do conteúdo ---------- */
const refChips = refs => (refs || []).map(r => `<button class="chip" data-goto="${r.p}" data-doc="${refDoc(r)}" data-hl="1">${pgLabel(r, 'Ver na ')}</button>`).join('');
function themeColor(id) { const t = C.themes.find(t => t.id === id); return t ? t.color : '#4a5568'; }

function renderPageMap() {
  const m = $('#pagemap'); let h = '';
  for (let p = 1; p <= TOTAL; p++) {
    const s = C.sections.find(s => p >= s.from && p <= s.to);
    h += `<button style="--c:${s ? s.color : '#9aa6b8'}" data-goto="${p}" aria-label="Página ${p}${s ? ': ' + esc(s.name) : ''}" title="p. ${p}${s ? ' · ' + esc(s.name) : ''}"></button>`;
  }
  m.innerHTML = h;
  $('#pagemapLegend').innerHTML = C.legend
    ? C.legend.map(l => `<span style="--c:${l.color}">${esc(l.name)}</span>`).join('')
    : C.sections.map(s => `<span style="--c:${s.color}">pp. ${s.from}–${s.to} ${esc(s.name)}</span>`).join('');
}
function renderStories() {
  $('#stories').innerHTML = C.stories.map(s => `
  <article class="story" id="${s.id}">
    <h3>${esc(s.title)}</h3>
    ${s.paras.map(p => `<p>${p}</p>`).join('')}
    ${s.claims ? `<table class="claims"><thead><tr><th>O que se diz por aí</th><th>O que o documento mostra</th><th></th></tr></thead><tbody>
      ${s.claims.map(c => `<tr><td data-h="O que se diz por aí">${esc(c.say)}</td><td data-h="O que o documento mostra">${esc(c.doc)}</td><td>${tag(c.label)}<div class="refs" style="margin-top:.4rem">${refChips(c.refs)}</div></td></tr>`).join('')}
    </tbody></table>` : ''}
  </article>`).join('');
}
function renderNumbers() {
  $('#numbers').innerHTML = C.numbers.map(n => `<div class="num"><b>${esc(n.value)}</b><span>${esc(n.label)}</span><div class="refs">${refChips(n.refs)}</div></div>`).join('');
}
let tlFilter = 'todos';
function renderTimeline() {
  const f = $('#tlFilters');
  const ls = labelsIn(C.timeline);
  f.innerHTML = ls.length < 2 ? '' : ['todos', ...ls].map(l => `<button class="chip ${tlFilter === l ? 'on' : ''}" data-tl="${l}">${l === 'todos' ? 'Todos' : l}</button>`).join('');
  let y = null, h = '';
  C.timeline.filter(e => tlFilter === 'todos' || e.label === tlFilter).forEach(e => {
    const yr = e.date.slice(-4);
    if (yr !== y) { y = yr; h += `<li class="tl year"><span class="year-n">${yr}</span></li>`; }
    h += `<li class="tl"><div class="tl-date">${esc(e.date)}</div><h3>${esc(e.title)}</h3><p>${esc(e.text)}</p><div class="tl-meta">${tag(e.label)}${refChips(e.refs)}${argBtns(e.id)}</div></li>`;
  });
  $('#timeline').innerHTML = h;
}
function renderOutcome() {
  $('#outcome').innerHTML = C.outcome.map(e => `<li class="tl"><div class="tl-date">${esc(e.date)}</div><h3>${esc(e.title)}</h3><p>${esc(e.text)}</p><div class="tl-meta">${tag(e.label)}${refChips(e.refs)}${(e.sources || []).map(s => `<a href="${esc(s.url)}" rel="noopener noreferrer nofollow" target="_blank">${esc(s.name)}</a>`).join(' ')}</div></li>`).join('');
}
function renderThemes() {
  $('#themes').innerHTML = C.themes.map(t => {
    const n = C.roteiro.filter(r => r.theme === t.id).length;
    return `<article class="theme" style="--c:${t.color}"><h3>${esc(t.title)}</h3><p>${esc(t.lay)}</p><span class="count">${n} pontos</span><div class="refs"><button class="btn" data-theme="${t.id}">Começar este tema</button><button class="btn-s" data-share-tema="${t.id}">Compartilhar tema</button></div></article>`;
  }).join('');
}
let rtLabel = 'todos', rtTheme = 'todos', rtQ = '';
function renderRoteiroFilters() {
  $('#rtFilters').innerHTML = ['todos', ...labelsIn(C.roteiro)].map(l => `<button class="chip ${rtLabel === l ? 'on' : ''}" data-rl="${l}">${l === 'todos' ? 'Todas as etiquetas' : l}</button>`).join('') +
    `<select id="rtTheme" aria-label="Filtrar por tema" class="chip"><option value="todos">Todos os temas</option>${C.themes.map(t => `<option value="${t.id}" ${rtTheme === t.id ? 'selected' : ''}>${esc(t.title)}</option>`).join('')}</select>`;
  $('#rtTheme').onchange = e => { rtTheme = e.target.value; renderRoteiro(); };
}
function filteredRoteiro() {
  const q = norm(rtQ);
  return C.roteiro.filter(r => (rtLabel === 'todos' || r.label === rtLabel) && (rtTheme === 'todos' || r.theme === rtTheme) && (!q || norm(r.title + ' ' + r.text + ' ' + (r.quote || '')).includes(q)));
}
function renderRoteiro() {
  renderRoteiroFilters();
  const list = filteredRoteiro();
  $('#rtCount').textContent = `${list.length} de ${C.roteiro.length} pontos`;
  $('#roteiroList').innerHTML = list.map(r => {
    const t = C.themes.find(t => t.id === r.theme);
    return `<li class="rt" style="--c:${themeColor(r.theme)}"><div class="rt-top">${tag(r.label)}<span>${t ? esc(t.title) : ''}</span></div><h3>${esc(r.title)}</h3><p>${esc(r.text)}</p>${r.quote ? `<p class="quote">“${esc(r.quote)}”</p>` : ''}<div class="refs">${refChips(r.refs)}<button class="chip" data-guide-rt="${r.id}">Seguir daqui, ponto a ponto</button>${argBtns(r.id)}</div></li>`;
  }).join('');
}
function renderExtras() {
  $('#extrasList').innerHTML = C.extras.map(e => `<article class="extra"><div class="tl-meta">${tag(e.label)}<span class="muted">${esc(e.date || '')}</span></div><h3>${esc(e.title)}</h3><p>${esc(e.text)}</p>${e.note ? `<p class="note">${esc(e.note)}</p>` : ''}<div class="src">${e.sources.map(s => `<a href="${esc(s.url)}" rel="noopener noreferrer nofollow" target="_blank">${esc(s.name)}</a>`).join('')}</div></article>`).join('');
}
function renderGlossary() {
  $('#glossary').innerHTML = C.glossary.map(g => `<div><dt>${esc(g.term)}</dt><dd>${esc(g.def)}</dd></div>`).join('');
}
function renderAbout() { $('#about').innerHTML = C.about; }

/* ---------- eventos ---------- */
function refsForClick(btn) {
  // procura o conjunto de refs do item onde o botão está, para marcar o trecho
  const p = +btn.dataset.goto; const card = btn.closest('[data-item]');
  if (!card) return [];
  const item = findItem(card.dataset.item); return item ? (item.refs || []).filter(r => r.p === p) : [];
}
function findItem(id) { return C.roteiro.find(r => r.id === id) || C.timeline.find(r => r.id === id); }

function wire() {
  document.addEventListener('click', e => {
    const t = e.target.closest('button,a'); if (!t) return;
    if (t.dataset.goto && t.closest('#vGuide')) {
      const st = V.steps && V.steps[V.idx]; openPage(+t.dataset.goto, { doc: t.dataset.doc || 'acordao', refs: st ? st.refs : [] });
    } else if (t.dataset.goto) {
      V.opener = t; V.steps = null; $('#vGuide').hidden = true;
      const p = +t.dataset.goto, doc = t.dataset.doc || 'acordao'; const host = t.closest('[data-refs]');
      let refs = [];
      if (host) { try { refs = JSON.parse(host.dataset.refs).filter(r => r.p === p && refDoc(r) === doc); } catch (_) { } }
      openPage(p, { doc, refs });
    } else if (t.dataset.openPage) { V.opener = t; V.steps = null; $('#vGuide').hidden = true; openPage(+t.dataset.openPage, { doc: 'acordao', refs: [] }); }
    else if (t.dataset.openDoc) { V.opener = t; V.steps = null; $('#vGuide').hidden = true; openPage(1, { doc: t.dataset.openDoc, refs: [] }); }
    else if (t.dataset.tl) { tlFilter = t.dataset.tl; renderTimeline(); }
    else if (t.dataset.rl) { rtLabel = t.dataset.rl; renderRoteiro(); }
    else if (t.dataset.theme) {
      V.opener = t;
      const steps = C.roteiro.filter(r => r.theme === t.dataset.theme && r.refs && r.refs.length);
      if (steps.length) startGuide(steps, 0);
    } else if (t.dataset.guideRt) {
      V.opener = t;
      const list = filteredRoteiro().filter(r => r.refs && r.refs.length); const i = list.findIndex(r => r.id === t.dataset.guideRt);
      startGuide(list, Math.max(0, i));
    } else if (t.dataset.searchPage) openSearchHit(+t.dataset.searchPage, t.dataset.q, t.dataset.searchDoc || 'acordao');
    else if (t.dataset.argAdd) toggleArg(t.dataset.argAdd);
    else if (t.dataset.sharePonto) { V.opener = t; openShare(cardPonto(t.dataset.sharePonto)); }
    else if (t.dataset.shareTema) { V.opener = t; openShare(cardTema(t.dataset.shareTema)); }
    else if (t.dataset.argGoto) {
      $('#argDlg').close(); V.opener = t; V.steps = null; $('#vGuide').hidden = true;
      const it = findItem(t.dataset.argItem), p = +t.dataset.argGoto, doc = t.dataset.argDoc || 'acordao';
      openPage(p, { doc, refs: it ? (it.refs || []).filter(r => r.p === p && refDoc(r) === doc) : [] });
    }
  });
  wireArg(); wireShare();
  $('#vClose').onclick = closeViewer;
  $('#vPrev').onclick = () => go(-1); $('#vNext').onclick = () => go(1);
  $('#vPage').onchange = e => openPage(+e.target.value, { refs: [] });
  $('#gPrev').onclick = () => showStep(V.idx - 1); $('#gNext').onclick = () => showStep(V.idx + 1);
  $('#vSpread').onclick = e => {
    V.spread = V.spread === 1 ? 2 : 1; e.currentTarget.textContent = V.spread === 2 ? '2 páginas' : '1 página';
    e.currentTarget.setAttribute('aria-pressed', V.spread === 2); render();
  };
  $('#vZoomIn').onclick = () => { V.zoom = Math.min(2.5, V.zoom + .2); render(); };
  $('#vZoomOut').onclick = () => { V.zoom = Math.max(.6, V.zoom - .2); render(); };
  document.addEventListener('keydown', e => {
    if (!document.body.classList.contains('viewer-open')) return;
    if (e.target.matches('input,select,textarea')) return;
    if (document.querySelector('dialog[open]')) return;
    if (e.key === 'Escape') closeViewer();
    else if (e.key === 'ArrowRight') go(1); else if (e.key === 'ArrowLeft') go(-1);
  });
  $('#searchForm').onsubmit = e => { e.preventDefault(); const q = $('#q').value.trim(); if (q) doSearch(q); };
  $('#rtq').oninput = e => { rtQ = e.target.value; renderRoteiro(); };
  $('#menuBtn').onclick = () => { const m = $('#mobileNav'); m.hidden = !m.hidden; $('#menuBtn').setAttribute('aria-expanded', !m.hidden); };
  $('#mobileNav').onclick = e => { if (e.target.tagName === 'A') { $('#mobileNav').hidden = true; $('#menuBtn').setAttribute('aria-expanded', false); } };
  let rz; window.addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(() => document.body.classList.contains('viewer-open') && render(), 200); });
  if (matchMedia('(max-width:700px)').matches) { V.spread = 1; }
}
/* guarda refs no DOM para marcar o trecho correto ao clicar nos chips */
function stamp() {
  const put = (sel, items, key = 'refs') => $$(sel).forEach((el, i) => { const it = items[i]; if (it && it[key]) el.dataset.refs = JSON.stringify(it[key]); });
  put('#timeline > .tl:not(.year)', C.timeline.filter(e => tlFilter === 'todos' || e.label === tlFilter));
  put('#roteiroList > .rt', filteredRoteiro());
  put('#numbers > .num', C.numbers);
  put('#outcome > li', C.outcome);
  $$('#stories .claims tbody tr').forEach((tr, i) => { });
  let k = 0; C.stories.forEach(s => (s.claims || []).forEach(c => { const tr = $$('#stories .claims tbody tr')[k++]; if (tr) tr.dataset.refs = JSON.stringify(c.refs || []); }));
}
const _rt = renderTimeline, _rr = renderRoteiro;


/* ---------- montar e compartilhar um argumento ---------- */
const AR = { ids: [], title: '', view: false };
const itemTitle = id => { const it = findItem(id); return it ? it.title : ''; };
const itemDoc = it => refDoc((it.refs || [])[0]);
function loadArg() { try { const o = JSON.parse(localStorage.getItem(ARG_KEY) || '{}'); AR.ids = (o.ids || []).filter(findItem); AR.title = o.title || ''; } catch (_) { } }
function saveArg() { try { localStorage.setItem(ARG_KEY, JSON.stringify({ ids: AR.ids, title: AR.title })); } catch (_) { } }
const ROOT = location.origin + location.pathname.replace(/index\.html?$/, '');
function argUrl(ids, title) {
  if (ids.length === 1 && !title) return ROOT + 'ponto/' + ids[0] + '/';
  const q = new URLSearchParams(); q.set('a', ids.join('.')); if (title) q.set('t', title);
  return ROOT + '#' + q.toString();
}
function argBtns(id) {
  return `<button class="btn-s ${AR.ids.includes(id) ? 'on' : ''}" data-arg-add="${id}" aria-pressed="${AR.ids.includes(id)}">${AR.ids.includes(id) ? 'No argumento' : '+ Argumento'}</button><button class="btn-s" data-share-ponto="${id}">Compartilhar</button>`;
}
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('on'); clearTimeout(toast.k); toast.k = setTimeout(() => t.classList.remove('on'), 2200); }
async function copyText(txt, msg) {
  try { await navigator.clipboard.writeText(txt); }
  catch (_) { const a = document.createElement('textarea'); a.value = txt; a.style.position = 'fixed'; a.style.opacity = '0'; document.body.appendChild(a); a.select(); try { document.execCommand('copy'); } catch (e) { } a.remove(); }
  toast(msg || 'Copiado');
}
function refreshArgUI() {
  const tray = $('#argTray'); tray.hidden = AR.ids.length === 0;
  tray.textContent = `Meu argumento (${AR.ids.length})`;
  $$('[data-arg-add]').forEach(b => { const on = AR.ids.includes(b.dataset.argAdd); b.classList.toggle('on', on); b.setAttribute('aria-pressed', on); b.textContent = on ? 'No argumento' : '+ Argumento'; });
}
function toggleArg(id) {
  const i = AR.ids.indexOf(id);
  if (i >= 0) { AR.ids.splice(i, 1); toast('Removido do argumento'); } else { AR.ids.push(id); toast('Adicionado. Veja em “Meu argumento”.'); }
  saveArg(); refreshArgUI(); if ($('#argDlg').open && !AR.view) renderArg();
}
function renderArg() {
  const d = $('#argDlg'); d.classList.toggle('view', AR.view);
  $('#argEdit').hidden = AR.view;
  const single = AR.view && AR.ids.length === 1;
  $('#argHead').textContent = AR.view ? (single ? 'Ponto do ' + BRAND[0].toLowerCase() + BRAND.slice(1) : (AR.title || 'Argumento compartilhado')) : 'Meu argumento';
  $('#argTitle').value = AR.title;
  const items = AR.ids.map(findItem).filter(Boolean);
  const base = items.length ? (single ? pesoLongo(items[0].label, itemDoc(items[0])) : pesoResumo(items)) : '';
  const S = sujeito(items);
  $('#argNote').textContent = AR.view
    ? (single ? `Segundo ${S.t}. Base: ${base}. Toque no número da página para ver o trecho marcado.`
      : `O que ${S.t} ${S.pl ? 'apontam' : 'aponta'}, em ${items.length} passos, na ordem de quem enviou. Base: ${base}. Toque no número da página para ver o trecho marcado.`)
    : (items.length ? `Ordene os pontos na ordem do raciocínio, dê um título e compartilhe. Base até agora: ${base}.` : 'Nenhum ponto ainda. Use “+ Argumento” nos cartões do guia.');
  $('#argList').innerHTML = items.map((it, i) => {
    const pg = (it.refs || []).map(r => `<button class="chip" data-arg-goto="${r.p}" data-arg-doc="${refDoc(r)}" data-arg-item="${it.id}">${pgLabel(r)}</button>`).join('');
    return `<li><div class="arg-row">${tag(it.label)}</div><h3>${esc(it.title)}</h3><p>${esc(it.text)}</p><div class="arg-row">${pg}<button class="mini" data-arg-up="${i}" ${i === 0 ? 'disabled' : ''} aria-label="Subir">↑</button><button class="mini" data-arg-down="${i}" ${i === items.length - 1 ? 'disabled' : ''} aria-label="Descer">↓</button><button class="mini" data-arg-del="${i}">Remover</button></div></li>`;
  }).join('');
  $('#argActions').innerHTML = items.length
    ? `<button class="btn primary" id="argShareBtn">Compartilhar</button><button class="btn" id="argPlay">${single ? 'Ver no documento' : 'Ver passo a passo'}</button>` +
      (AR.view ? (single ? '' : '<button class="btn" id="argMine">Salvar como meu argumento</button>') : '<button class="btn" id="argClear">Limpar tudo</button>')
    : '';
}
function openArg(view) {
  AR.view = !!view; renderArg(); const d = $('#argDlg'); if (!d.open) d.showModal();
}
function wireArg() {
  $('#argTray').onclick = () => { if (AR.view) { loadArg(); } openArg(false); };
  $('#argTitle').oninput = e => { AR.title = e.target.value; saveArg(); };
  $('#argDlg').addEventListener('click', e => {
    const t = e.target.closest('button'); if (!t) return;
    const ds = t.dataset, mv = (i, j) => { [AR.ids[i], AR.ids[j]] = [AR.ids[j], AR.ids[i]]; saveArg(); renderArg(); };
    if (ds.argUp) mv(+ds.argUp, +ds.argUp - 1);
    else if (ds.argDown) mv(+ds.argDown, +ds.argDown + 1);
    else if (ds.argDel !== undefined) { AR.ids.splice(+ds.argDel, 1); saveArg(); refreshArgUI(); renderArg(); }
    else if (t.id === 'argShareBtn') { V.opener = t; openShare(cardArg(AR.ids, AR.title)); }
    else if (t.id === 'argPlay') {
      const steps = AR.ids.map(findItem).filter(x => x && x.refs && x.refs.length);
      $('#argDlg').close(); V.opener = $('#argTray'); if (steps.length) startGuide(steps, 0);
    } else if (t.id === 'argClear') { AR.ids = []; AR.title = ''; saveArg(); refreshArgUI(); $('#argDlg').close(); }
    else if (t.id === 'argMine') { saveArg(); refreshArgUI(); history.replaceState(null, '', location.pathname); V.argHash = ''; AR.view = false; renderArg(); toast('Salvo. Você pode editar e reenviar.'); }
  });
  $('#argDlg').addEventListener('close', () => { if (AR.view) { AR.view = false; loadArg(); refreshArgUI(); } });
  window.addEventListener('hashchange', () => { if (/^#(a|tema)=/.test(location.hash)) openFromHash(); });
  $('#vShare').onclick = e => {
    V.shareOpener = e.currentTarget;
    const st = V.steps && V.steps[V.idx];
    openShare(st && st.id ? cardPonto(st.id) : cardPagina(V.doc, V.page, V.rects[V.page] || []));
  };
}
function openFromHash() {
  const h = location.hash.slice(1); if (!h) return false;
  const q = new URLSearchParams(h);
  let ids = [], title = '';
  if (q.get('tema')) { const th = C.themes.find(t => t.id === q.get('tema')); if (th) { ids = C.roteiro.filter(r => r.theme === th.id).map(r => r.id); title = th.title; } }
  else if (q.get('a')) { ids = q.get('a').split(/[.,]/).filter(findItem); title = (q.get('t') || '').slice(0, 90); }
  else return false;
  if (!ids.length) { toast('Esse link não corresponde a pontos do guia.'); return true; }
  AR.ids = ids; AR.title = title; V.argHash = location.hash; openArg(true); return true;
}

/* ---------- compartilhar: cartões, recorte da página e painel por plataforma ---------- */
const miniItem = it => ({ title: it.title, label: it.label, text: it.text, refs: it.refs || [], doc: itemDoc(it) });
function cardPonto(id) {
  const it = findItem(id); const r0 = (it.refs || [])[0];
  return { kind: 'ponto', id, doc: itemDoc(it), title: it.title, label: it.label, text: it.text, refs: it.refs || [], url: ROOT + 'ponto/' + id + '/',
    excerpt: r0 ? (aspect, px) => excerptCanvas(refDoc(r0), r0.p, r0.r, aspect, px) : null, excerptPage: r0 && r0.p, excerptDoc: r0 && refDoc(r0) };
}
function cardTema(tid) {
  const th = C.themes.find(t => t.id === tid);
  const all = C.roteiro.filter(r => r.theme === tid);
  // temas longos levam só os pontos principais; o link abre o tema inteiro
  const items = th.key && th.key.length ? th.key.map(findItem).filter(Boolean) : all;
  return { kind: 'tema', id: tid, title: th.title, text: th.lay, items: items.map(miniItem), total: all.length, url: ROOT + 'tema/' + tid + '/' };
}
function cardArg(ids, title) {
  if (ids.length === 1) return cardPonto(ids[0]);
  return { kind: 'argumento', title: title || 'Pontos do acórdão do STF', items: ids.map(findItem).filter(Boolean).map(miniItem), url: argUrl(ids, title) };
}
function cardPagina(doc, p, rects) {
  return { kind: 'pagina', doc, title: `Página ${p} ${docOf(doc).de}`, text: '', refs: [doc === 'acordao' ? { p } : { d: doc, p }],
    url: ROOT + (doc === 'acordao' ? '#p=' + p : `#d=${doc}&p=${p}`),
    excerpt: (aspect, px) => excerptCanvas(doc, p, rects, aspect, px), excerptPage: p, excerptDoc: doc };
}
/* recorte da página do PDF em volta do trecho marcado, já com o marca-texto */
async function excerptCanvas(doc, p, rects, aspect, pxW) {
  const page = await getPage(p, doc);
  const vp1 = page.getViewport({ scale: 1 }), PW = vp1.width, PH = vp1.height;
  aspect = Math.max(aspect, PW / PH);
  let x0 = 34, cw = PW - 68, ch = cw / aspect;
  if (ch > PH) { ch = PH; cw = PH * aspect; x0 = (PW - cw) / 2; }
  let cy;
  if (rects && rects.length) {
    let y0 = Math.min(...rects.map(r => r[1])), y1 = Math.max(...rects.map(r => r[3]));
    if (y1 - y0 > ch * 0.8) { y0 = rects[0][1]; y1 = Math.min(y1, y0 + ch * 0.8); }
    cy = (y0 + y1) / 2;
  } else cy = ch / 2;
  const top = Math.max(0, Math.min(PH - ch, cy - ch / 2));
  const s = pxW / cw;
  const cv = document.createElement('canvas'); cv.width = Math.round(cw * s); cv.height = Math.round(ch * s);
  const ctx = cv.getContext('2d'); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, cv.width, cv.height);
  await page.render({ canvasContext: ctx, viewport: page.getViewport({ scale: s, offsetX: -x0 * s, offsetY: -top * s }) }).promise;
  ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = '#ffe14d';
  (rects || []).forEach(r => ctx.fillRect((r[0] - 1.5 - x0) * s, (r[1] - 1.5 - top) * s, (r[2] - r[0] + 3) * s, (r[3] - r[1] + 3) * s));
  ctx.globalCompositeOperation = 'source-over';
  return cv;
}
/* textos de compartilhamento: a voz é sempre a do acórdão, com o peso de cada ponto e a página */
const cap = t => t ? t[0].toUpperCase() + t.slice(1) : t;
const cutText = (t, n) => t.length <= n ? t : t.slice(0, n - 1).replace(/\s+\S*$/, '').replace(/[\s,.;:–—-]+$/, '') + '…';
function msgText(d, wa, withUrl = true) {
  const B = t => (wa ? `*${t}*` : t), L = [];
  if (d.kind === 'ponto') {
    const pg = refsTxt(d.refs, d.doc);
    L.push(B(d.title), docOf(d.doc).voz + ':', '', d.text, '', `Base: ${pesoLongo(d.label, d.doc)}${pg ? ` (${pg})` : ''}.`);
  } else if (d.kind === 'pagina') {
    L.push(B(d.title), docOf(d.doc).sobre);
  } else {
    const n = d.items.length, tot = d.total || n, full = n <= 8, max = full ? n : 8, S = sujeito(d.items), v = S.pl ? 'apontam' : 'aponta';
    L.push(B(d.title));
    if (d.kind === 'tema') L.push(d.text, '', tot > n
      ? `Os ${n} pontos principais deste tema, segundo ${S.t}:`
      : `O que ${S.t} ${v} neste tema, em ${n} pontos:`);
    else L.push(`O que ${S.t} ${v}, em ${n} passos:`);
    d.items.slice(0, max).forEach((it, i) => {
      L.push('', `${i + 1}. ${full ? B(it.title) : it.title}`);
      if (full && it.text) L.push(cutText(it.text, 240));
      const pg = refsTxt(it.refs, it.doc);
      L.push(`${cap(pesoItem(it.label, it.doc))}${pg ? ', ' + pg : ''}.`);
    });
    const rest = tot - max;
    if (rest > 0) L.push('', `E mais ${rest} ${rest === 1 ? 'ponto' : 'pontos'} no link.`);
    L.push('', `${B('Base:')} ${pesoResumo(d.items, true)}.`);
  }
  if (withUrl) L.push('', d.kind === 'ponto' || d.kind === 'pagina' ? 'Veja o trecho marcado no documento original:' : 'Veja cada trecho marcado no documento original:', d.url);
  return L.join('\n');
}
function shortText(d, max) {
  const S = d.items ? sujeito(d.items) : null;
  let t = d.kind === 'ponto' ? `${d.title}. Segundo ${docOf(d.doc).sujeito} (${refsTxt(d.refs, d.doc)}): ${d.text}`
    : d.kind === 'pagina' ? `${d.title}: ${docOf(d.doc).sobre} Com o trecho marcado.`
    : (d.total || d.items.length) > d.items.length
      ? `${d.title}: os ${d.items.length} pontos principais, segundo ${S.t} (${pesoResumo(d.items)}). Veja os ${d.total} pontos com os trechos marcados no documento.`
      : `${d.title}: ${d.items.length} pontos, segundo ${S.t}, com ${pesoResumo(d.items)}. Veja os trechos marcados no documento.`;
  return cutText(t, Math.max(40, max));
}
function platformLinks(d) {
  const e = encodeURIComponent, u = d.url;
  return [
    ['WhatsApp', 'https://wa.me/?text=' + e(msgText(d, true))],
    ['Telegram', 'https://t.me/share/url?url=' + e(u) + '&text=' + e(msgText(d, false, false))],
    ['X (Twitter)', 'https://twitter.com/intent/tweet?text=' + e(shortText(d, 240)) + '&url=' + e(u)],
    ['Facebook', 'https://www.facebook.com/sharer/sharer.php?u=' + e(u)],
    ['Threads', 'https://www.threads.com/intent/post?text=' + e(shortText(d, 440)) + '&url=' + e(u)],
    ['Bluesky', 'https://bsky.app/intent/compose?text=' + e(shortText(d, 295 - u.length) + '\n' + u)],
    ['LinkedIn', 'https://www.linkedin.com/sharing/share-offsite/?url=' + e(u)],
    ['Reddit', 'https://www.reddit.com/submit?url=' + e(u) + '&title=' + e(d.title)],
    ['E-mail', 'mailto:?subject=' + e(d.title) + '&body=' + e(msgText(d, false))],
  ];
}
const SH = { d: null, fmt: 'story', blob: null, file: null, url: null };
function openShare(d) {
  SH.d = d; SH.blob = SH.file = null; if (SH.url) { URL.revokeObjectURL(SH.url); SH.url = null; }
  $('#shWhat').textContent = d.title;
  $('#shLinks').innerHTML = platformLinks(d).map(([n, href]) => `<a class="sh-btn" href="${esc(href)}" target="_blank" rel="noopener noreferrer">${esc(n)}</a>`).join('');
  $('#shNative').hidden = !navigator.share;
  $('#shPrev').hidden = true; $('#shImgActions').hidden = true; $('#shMake').hidden = false; $('#shMake').disabled = false; $('#shMake').textContent = 'Criar imagem';
  $('#shHint').textContent = '';
  $$('#shFmt [data-fmt]').forEach(b => { b.classList.toggle('on', b.dataset.fmt === SH.fmt); b.setAttribute('aria-pressed', b.dataset.fmt === SH.fmt); });
  const dlg = $('#shareDlg'); if (!dlg.open) dlg.showModal();
}
async function makeImage() {
  const d = SH.d, fmt = SH.fmt, btn = $('#shMake');
  btn.disabled = true; btn.textContent = 'Criando imagem…';
  try {
    const cv = await renderCard(d, fmt);
    if (SH.d !== d || SH.fmt !== fmt) return;
    const blob = await new Promise(r => cv.toBlob(r, 'image/png'));
    SH.blob = blob; SH.file = new File([blob], `guia-suspeicao-${d.kind}-${fmt}.png`, { type: 'image/png' });
    if (SH.url) URL.revokeObjectURL(SH.url); SH.url = URL.createObjectURL(blob);
    $('#shImg').src = SH.url; $('#shImg').alt = `Prévia da imagem: ${d.title}`;
    $('#shPrev').hidden = false; $('#shImgActions').hidden = false; btn.hidden = true;
    $('#shSendImg').hidden = !(navigator.canShare && navigator.canShare({ files: [SH.file] }));
    $('#shHint').textContent = fmt === 'story'
      ? 'No Stories, toque no adesivo “Link” e cole o link. Ele é copiado quando você envia ou baixa a imagem.'
      : 'No Feed, links na legenda não ficam clicáveis. Use o QR code da imagem ou escreva “link na bio”. O link é copiado quando você envia ou baixa a imagem.';
  } catch (e) {
    console.error(e); btn.disabled = false; btn.textContent = 'Tentar de novo';
    $('#shHint').textContent = 'Não foi possível criar a imagem agora. Verifique a conexão e tente de novo.';
  }
}
function quietCopy(txt) { try { navigator.clipboard.writeText(txt).catch(() => { }); } catch (_) { } }
function wireShare() {
  const dlg = $('#shareDlg');
  dlg.addEventListener('click', e => {
    const t = e.target.closest('button,a'); if (!t) return;
    const d = SH.d; if (!d) return;
    if (t.dataset.fmt) {
      SH.fmt = t.dataset.fmt;
      $$('#shFmt [data-fmt]').forEach(b => { b.classList.toggle('on', b === t); b.setAttribute('aria-pressed', b === t); });
      if (SH.blob) { SH.blob = null; $('#shImgActions').hidden = true; $('#shPrev').hidden = true; $('#shMake').hidden = false; makeImage(); }
    } else if (t.id === 'shMake') makeImage();
    else if (t.id === 'shCopyLink') copyText(d.url, 'Link copiado');
    else if (t.id === 'shCopyText') copyText(msgText(d, false), 'Texto copiado');
    else if (t.id === 'shNative') navigator.share({ title: d.title, text: shortText(d, 300), url: d.url }).catch(() => { });
    else if (t.id === 'shSendImg' && SH.file) {
      quietCopy(d.url);
      navigator.share({ files: [SH.file] }).then(() => toast('Imagem enviada. O link está copiado.')).catch(() => { });
    } else if (t.id === 'shSave' && SH.url) {
      quietCopy(d.url);
      const a = document.createElement('a'); a.href = SH.url; a.download = SH.file.name; document.body.appendChild(a); a.click(); a.remove();
      toast('Imagem baixada. O link está copiado.');
    }
  });
  dlg.addEventListener('close', () => { const o = V.shareOpener; V.shareOpener = null; if (o && document.contains(o)) o.focus(); });
}
/* usado só pelo script que gera as prévias de link (og:image) */
if (new URLSearchParams(location.search).has('gerar')) {
  window.__guiaCard = async (kind, id, fmt = 'og', q = 0.86, host = location.host) => {
    const d = kind === 'ponto' ? cardPonto(id) : kind === 'tema' ? cardTema(id) : null;
    const card = d || guiaCard();
    card.host = host;
    const cv = await renderCard(card, fmt);
    return cv.toDataURL('image/jpeg', q);
  };
}
function guiaCard() {
  const it = findItem('dec-motivo'), r0 = it.refs[0];
  return { kind: 'guia', doc: 'acordao', kicker: `Acórdão do STF no HC 164.493 (2021), ${CH.acordao[CH.acordao.length - 1].to} páginas`, title: 'Por que o STF declarou Moro parcial, página por página', url: ROOT,
    excerpt: (aspect, px) => excerptCanvas('acordao', r0.p, r0.r, aspect, px), excerptPage: r0.p, excerptDoc: 'acordao' };
}

async function init() {
  [C, CH] = await Promise.all([getJSON('data/content.json'), getJSON('data/chunks.json')]);
  setDocs(Object.fromEntries(C.docs.map(d => [d.id, d])));
  setDoc('acordao');
  $('#mobileNav').innerHTML = $$('.nav a').map(a => `<a href="${a.getAttribute('href')}">${a.textContent}</a>`).join('');
  C.timeline.forEach((e, i) => { e.id = 'cr-' + String(i + 1).padStart(2, '0'); });
  loadArg();
  renderPageMap(); renderStories(); renderNumbers(); renderTimeline(); renderThemes(); renderRoteiro(); renderExtras(); renderOutcome(); renderGlossary(); renderAbout();
  stamp(); wire();
  // re-stamp após filtros
  document.addEventListener('click', e => { if (e.target.closest('[data-tl],[data-rl]')) stamp(); });
  $('#rtq').addEventListener('input', stamp); document.addEventListener('change', e => { if (e.target.id === 'rtTheme') stamp(); });
  refreshArgUI();
  if (!openFromHash()) { const m = location.hash.match(/^#(?:d=(\w+)&)?p=(\d+)/); if (m) openPage(+m[2], { doc: m[1] || 'acordao' }); }
  // tutorial "Como usar": carregado à parte, para que uma falha nele não derrube o guia
  import('./tour.js').then(t => t.initTour()).catch(() => { });
}
init().catch(err => { document.getElementById('conteudo').insertAdjacentHTML('afterbegin', `<p style="padding:1rem;background:#fdebd3;color:#5a2b00">Não foi possível carregar o guia (${esc(err.message)}). Se você abriu o arquivo direto do computador, publique a pasta num servidor web ou rode <code>python3 -m http.server</code> dentro dela.</p>`); console.error(err); });
