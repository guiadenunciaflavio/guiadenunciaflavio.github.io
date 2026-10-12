/* Tutorial "Como usar": destaca cada parte do guia, uma por vez, e explica para que serve.
   Abre sozinho na primeira visita. Quem chega por um link de ponto, tema ou página vê só um convite,
   para não tapar o que veio ver. Também abre pelo "Como usar" (botões com data-tour) e pelo endereço #como-usar.
   O mesmo arquivo serve aos três guias; o texto muda conforme <body data-guia>. */

const $ = (s, r = document) => r.querySelector(s);
const GUIA = ['suspeicao', 'cargo'].includes(document.body.dataset.guia) ? document.body.dataset.guia : 'denuncia';
const KEY = 'guia.tour.' + GUIA;
const HASH = '#como-usar';
const reduce = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const narrow = () => innerWidth < 700;
const frame = () => new Promise(r => requestAnimationFrame(() => r()));
const sleep = ms => new Promise(r => setTimeout(r, ms));
/* sem acesso ao armazenamento, não dá para lembrar: melhor não abrir sozinho a cada visita */
const seen = () => { try { return localStorage.getItem(KEY) === '1'; } catch (_) { return true; } };
const markSeen = () => { try { localStorage.setItem(KEY, '1'); } catch (_) { } };

const TXT = {
  denuncia: {
    busca: 'Digite um nome ou uma palavra, como “Queiroz” ou “chocolate”. A busca lista as páginas onde ela aparece, e cada resultado abre a página com a palavra marcada.',
    mapa: 'Cada quadradinho é uma das 290 páginas da denúncia, na cor da parte do documento (a legenda fica logo abaixo). Toque em um deles para abrir a página.',
    etiquetas: 'Cada ponto do guia leva uma destas etiquetas. Ela diz o peso do que se afirma: um fato escrito no documento, uma acusação do Ministério Público ou uma leitura que liga fatos.',
    entenda: 'O caso em poucos parágrafos, com uma tabela que compara o que se diz por aí com o que o documento mostra. Cada linha tem o botão para ver a página.',
    documento: 'O documento abre na página certa, com o trecho marcado em amarelo. A barra do ponto mostra o resumo e leva ao <b>Próximo ponto</b> do tema.',
    menu: 'No menu ficam a Cronologia, os Fatos extras (de fora da denúncia, sempre com fonte), o Desfecho do caso e o Glossário. <b>Todos os guias</b> volta à página inicial.',
    ponto: 'Etiqueta, tema, resumo e as páginas. <b>Ver na p.</b> abre o trecho marcado, e <b>Seguir daqui, ponto a ponto</b> começa um passo a passo a partir dele.',
  },
  suspeicao: {
    busca: 'Digite um nome ou uma palavra, como “Palocci” ou “grampo”. A busca procura nos três documentos (o acórdão do STF, a decisão de Fachin e a do Comitê da ONU), e cada resultado abre a página com a palavra marcada.',
    mapa: 'Cada quadradinho é uma das 441 páginas do acórdão, na cor do voto ou da parte (a legenda fica logo abaixo). Toque em um deles para abrir a página.',
    etiquetas: 'Cada ponto do guia leva uma destas etiquetas. Ela diz o peso do que se afirma: uma decisão ou um ato registrado, uma afirmação de alguém ou uma leitura nossa que liga fatos.',
    entenda: 'O que o STF decidiu, em poucos parágrafos, e uma tabela que compara o que se diz por aí com o que os documentos mostram. Cada linha tem o botão para ver a página.',
    documento: 'O documento abre na página certa, com o trecho marcado em amarelo. No topo aparece qual dos três documentos está aberto, e a barra do ponto leva ao <b>Próximo ponto</b> do tema.',
    menu: 'No menu ficam a Cronologia, os Fatos extras (de fora do acórdão, sempre com fonte), o Desfecho e o Glossário. <b>Todos os guias</b> volta à página inicial.',
    ponto: 'Etiqueta, tema, resumo e as páginas. <b>Ver na p.</b> abre o trecho marcado, e <b>Seguir daqui, ponto a ponto</b> começa um passo a passo a partir dele.',
  },
  cargo: {
    busca: 'Digite um nome ou uma palavra, como “Defensoria” ou “PPB”. A busca procura nos sete documentos, e cada resultado abre a página com a palavra marcada.',
    mapa: 'Cada linha é um dos sete documentos, e cada quadradinho, uma página. Os de cor cheia têm trecho marcado no guia. Toque em um deles para abrir a página.',
    etiquetas: 'Cada ponto do guia leva uma destas etiquetas. Ela diz o peso do que se afirma: um fato registrado nos documentos, uma informação de reportagem ou uma leitura nossa que liga os fatos.',
    entenda: 'O caso em poucos parágrafos, com uma tabela que compara o que se diz por aí com o que os documentos mostram. Cada linha tem o botão para ver a página.',
    documento: 'O documento abre na página certa, com o trecho marcado em amarelo. No topo aparece qual dos sete documentos está aberto, e a barra do ponto leva ao <b>Próximo ponto</b> do tema.',
    menu: 'No menu ficam a Cronologia, os Fatos extras (de reportagens, sempre com link), o que veio Depois do cargo e o Glossário. <b>Todos os guias</b> volta à página inicial.',
    ponto: 'Etiqueta, tema, resumo e os documentos. O botão com o documento e a página, como <b>Boletim 2000, p. 3384</b>, abre o trecho marcado, e <b>Seguir daqui, ponto a ponto</b> começa um passo a passo a partir dele.',
  },
}[GUIA];

/* cada passo: alvo (seletor, lista de seletores ou função), título e texto. compact: alvo menor, para quando o
   principal não cabe na tela junto com o cartão (celulares pequenos). viewer: o passo precisa do documento aberto */
const STEPS = [
  { title: 'Como usar este guia', text: 'Em um minuto, veja onde fica cada coisa e para que serve. Você pode sair quando quiser e rever o tutorial em <b>Como usar</b>.', primary: 'Começar', secondary: 'Agora não' },
  { target: '#searchForm', title: 'Busque qualquer palavra', text: TXT.busca },
  { target: ['.pagemap-wrap figcaption', '#pagemap'], title: 'O mapa das páginas', text: TXT.mapa },
  { target: '.how .labels', title: 'Três etiquetas', text: TXT.etiquetas },
  { target: ['#stories .claims thead', '#stories .claims tbody tr'], compact: ['#entenda > h2', '#stories .story h3'], title: 'Entenda em 2 minutos', text: TXT.entenda },
  { target: '#themes .theme', title: 'Temas, ponto a ponto', text: 'Escolha um tema e toque em <b>Começar este tema</b>. O guia abre o documento e leva você pelos pontos, um a um, marcando cada trecho. No próximo passo, este tema abre como exemplo.' },
  { viewer: true, target: () => (innerWidth <= 1000 ? '#vGuide' : '#viewer'), compact: ['#vDoc', '#vGuide .v-guide-top'], title: 'O documento, com o trecho marcado', text: TXT.documento },
  { viewer: true, target: '.v-head', title: 'Mudar de página e compartilhar', text: '<b>‹</b> e <b>›</b> mudam de página, <b>+</b> e <b>−</b> mudam o tamanho e <b>Compartilhar</b> envia o ponto aberto. No computador, <b>1 página</b> passa a mostrar duas lado a lado. <b>Fechar</b> volta ao guia.' },
  { target: ['#rtFilters', '.rt-search'], title: 'Roteiro de Tudo', text: 'Todos os pontos que encontramos, inclusive os menores. Filtre por etiqueta ou por tema, ou digite uma palavra para filtrar a lista.' },
  { target: '#roteiroList > .rt', compact: '#roteiroList > .rt .refs', title: 'Em cada ponto', text: TXT.ponto },
  { target: '#roteiroList > .rt [data-arg-add]', title: 'Monte o seu argumento', text: 'Toque em <b>+ Argumento</b> nos pontos que quiser juntar. Eles vão para <b>Meu argumento</b>, um botão que aparece no canto da tela, onde você põe na ordem, dá um título e envia tudo junto.' },
  { target: '#roteiroList > .rt [data-share-ponto]', title: 'Compartilhe', text: 'Envie pelo WhatsApp, Telegram, X e outras redes, sempre com o link para o trecho marcado. Para Instagram e TikTok, o guia cria uma imagem com o trecho e um QR code. Temas inteiros também podem ser enviados.' },
  { target: () => (innerWidth > 1240 ? '.nav' : '#menuBtn'), title: 'As outras seções', text: TXT.menu },
  { title: 'Pronto', text: 'Comece por <b>Entender em 2 minutos</b> ou escolha um tema. Para ver este tutorial de novo, use <b>Como usar</b>, no início da página ou no menu.', primary: 'Concluir' },
];
const COUNTED = STEPS.filter(s => s.target);

let dlg = null, hole = null, i = 0, running = false, opener = null, startY = 0, raf = 0, busy = false;

function pick(t) {
  if (!t) return null;
  if (typeof t === 'function') t = t();
  const list = (Array.isArray(t) ? t : [t]).map(sel => document.querySelector(sel)).filter(el => el && el.getClientRects().length);
  return list.length ? list : null;
}
function targetsOf(s) {
  const list = pick(s.target);
  if (list && s.compact && tooTall(list)) return pick(s.compact) || list;
  return list;
}
/* o alvo não cabe na tela junto com o cartão? */
function tooTall(list) {
  const r = rectOf(list);
  if (!narrow()) return r.bottom - r.top > innerHeight - topBar() - 26;
  const limit = innerHeight - (dlg ? dlg.offsetHeight : 260) - 22;   // onde começa o cartão, preso embaixo
  if (list[0].closest('.viewer, .top')) return r.bottom > limit;      // fixo na tela: não dá para rolar até ele
  return r.bottom - r.top > limit - topBar() - 14;
}
function rectOf(list) {
  const rs = list.map(el => el.getBoundingClientRect());
  return { left: Math.min(...rs.map(r => r.left)), top: Math.min(...rs.map(r => r.top)), right: Math.max(...rs.map(r => r.right)), bottom: Math.max(...rs.map(r => r.bottom)) };
}
const topBar = () => ($('#topo') || { offsetHeight: 56 }).offsetHeight;
const viewerOpen = () => document.body.classList.contains('viewer-open');

/* o passo do documento abre o primeiro tema, como se a pessoa tivesse tocado em "Começar este tema" */
async function setViewer(on) {
  if (on === viewerOpen()) return;
  if (on) { const b = $('#themes [data-theme]'); if (!b) return; b.click(); }
  else { const c = $('#vClose'); if (c) c.click(); }
  await frame(); await frame(); await sleep(40);
}

/* espera a rolagem suave terminar */
function settle() {
  return new Promise(res => {
    let last = scrollY, still = 0; const t0 = performance.now();
    const tick = () => {
      if (Math.abs(scrollY - last) < 0.5) still++; else { still = 0; last = scrollY; }
      const t = performance.now() - t0;
      if ((t > 140 && still >= 4) || t > 1400) res(); else requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  });
}
async function bringIntoView(list) {
  if (list[0].closest('.viewer, .top')) return;           // o documento e o topo ficam fixos na tela; não rolam com a página
  const r = rectOf(list), top = topBar() + 14, vh = innerHeight, vw = document.documentElement.clientWidth;
  const h = r.bottom - r.top, G = 14, M = 12;
  let want;                                               // onde o alto do alvo deve ficar na tela
  if (narrow()) {                                         // cartão preso embaixo: o alvo vai para o espaço de cima
    const bottom = vh - dlg.offsetHeight - 36;
    if (r.top >= top && r.bottom <= bottom) return;
    const avail = bottom - top;
    want = top + (h < avail ? (avail - h) / 2 : 0);
  } else {
    const cw = dlg.offsetWidth, ch = dlg.offsetHeight, avail = vh - M - top;
    const side = r.left - G - cw >= M || r.right + G + cw <= vw - M;
    const visible = r.top >= top && r.bottom <= vh - M;
    if (side) {                                           // o cartão cabe ao lado: basta o alvo estar visível
      if (visible) return;
      want = top + (h < avail ? (avail - h) / 2 : 0);
    } else {                                              // o cartão vai acima ou abaixo: os dois precisam caber
      if (visible && (r.bottom + G + ch <= vh - M || r.top - G - ch >= top)) return;
      const need = h + G + ch;
      want = need <= avail ? top + (avail - need) / 2 : top;
    }
  }
  window.scrollTo({ top: Math.max(0, scrollY + r.top - want), behavior: reduce() ? 'instant' : 'smooth' });
  await settle();
}

/* recorte iluminado em volta do alvo e posição do cartão: abaixo, acima, ao lado ou no canto */
function place() {
  if (!dlg) return;
  const s = STEPS[i], list = targetsOf(s);
  const M = 12, G = 14, vw = document.documentElement.clientWidth, vh = innerHeight;
  const cw = dlg.offsetWidth, ch = dlg.offsetHeight;
  if (!list) {
    hole.classList.add('dim');
    hole.style.cssText = `left:${vw / 2}px;top:${vh / 2}px;width:0;height:0`;
    if (narrow()) { dlg.style.left = M + 'px'; dlg.style.top = Math.max(M, vh - ch - M) + 'px'; }
    else { dlg.style.left = Math.round((vw - cw) / 2) + 'px'; dlg.style.top = Math.round(Math.max(M, (vh - ch) / 2)) + 'px'; }
    return;
  }
  hole.classList.remove('dim');
  const r = rectOf(list), P = 6;
  const L = Math.max(2, r.left - P), T = r.top - P, W = Math.min(vw - 2, r.right + P) - L, H = r.bottom + P - T;
  hole.style.cssText = `left:${L}px;top:${T}px;width:${W}px;height:${H}px`;
  let x, y;
  if (narrow()) { x = M; y = Math.max(M, vh - ch - M); }
  else {
    const top = topBar() + M;
    const cx = v => Math.min(Math.max(v, M), vw - cw - M), cy = v => Math.min(Math.max(v, top), vh - ch - M);
    if (r.bottom + G + ch <= vh - M) { y = r.bottom + G; x = cx(r.left); }
    else if (r.top - G - ch >= top) { y = r.top - G - ch; x = cx(r.left); }
    else if (r.right + G + cw <= vw - M) { x = r.right + G; y = cy(r.top); }
    else if (r.left - G - cw >= M) { x = r.left - G - cw; y = cy(r.top); }
    else { x = vw - cw - M; y = vh - ch - M; }
  }
  dlg.style.left = Math.round(x) + 'px'; dlg.style.top = Math.round(y) + 'px';
}
function onMove() { if (raf) return; raf = requestAnimationFrame(() => { raf = 0; place(); }); }

async function show(n, dir = 1) {
  if (busy) return; busy = true;
  try {
    while (n > 0 && n < STEPS.length - 1 && STEPS[n].target && !STEPS[n].viewer && !targetsOf(STEPS[n])) n += dir;
    i = Math.max(0, Math.min(STEPS.length - 1, n));
    const s = STEPS[i];
    dlg.classList.add('moving');
    await setViewer(!!s.viewer);
    const k = COUNTED.indexOf(s);
    $('.tour-n', dlg).textContent = k >= 0 ? `Passo ${k + 1} de ${COUNTED.length}` : '';
    $('.tour-bar i', dlg).style.width = (k >= 0 ? (k + 1) / COUNTED.length * 100 : i === 0 ? 0 : 100) + '%';
    $('.tour-t', dlg).textContent = s.title;
    $('.tour-x', dlg).innerHTML = s.text;
    const back = $('[data-tour-act="back"]', dlg), next = $('[data-tour-act="next"]', dlg);
    back.textContent = s.secondary || 'Voltar';
    next.textContent = s.primary || 'Próximo';
    $('.tour-skip', dlg).hidden = !s.target;
    dlg.classList.toggle('is-step', !!s.target);
    const list = targetsOf(s);
    if (list) await bringIntoView(list);
    place();
    dlg.classList.remove('moving');
    next.focus({ preventScroll: true });
  } finally { busy = false; }
}

function act(a) {
  if (busy) return;
  if (a === 'skip') end();
  else if (a === 'next') { if (i >= STEPS.length - 1) end(); else show(i + 1, 1); }
  else if (a === 'back') { if (i === 0) end(); else show(i - 1, -1); }
}

function build() {
  hole = document.createElement('div'); hole.className = 'tour-hole dim'; hole.setAttribute('aria-hidden', 'true');
  dlg = document.createElement('dialog'); dlg.className = 'tour moving';
  dlg.setAttribute('aria-labelledby', 'tourT'); dlg.setAttribute('aria-describedby', 'tourX');
  dlg.innerHTML = `<div class="tour-bar" aria-hidden="true"><i></i></div>
    <div class="tour-top"><span class="tour-n"></span><button type="button" class="tour-skip" data-tour-act="skip">Pular tutorial</button></div>
    <h2 class="tour-t" id="tourT"></h2>
    <p class="tour-x" id="tourX" aria-live="polite"></p>
    <div class="tour-nav"><button type="button" class="btn" data-tour-act="back"></button><button type="button" class="btn primary" data-tour-act="next"></button></div>`;
  document.body.append(hole, dlg);
  dlg.addEventListener('click', e => { const b = e.target.closest('[data-tour-act]'); if (b) act(b.dataset.tourAct); });
  dlg.addEventListener('cancel', e => { e.preventDefault(); end(); });
  dlg.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight') { e.preventDefault(); act('next'); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); act('back'); }
  });
}

export function startTour(from) {
  if (running) return;
  running = true; hideHint();
  opener = from || document.activeElement; startY = scrollY;
  document.querySelectorAll('dialog[open]').forEach(d => d.close());
  const mob = $('#mobileNav'); if (mob && !mob.hidden) { mob.hidden = true; const mb = $('#menuBtn'); if (mb) mb.setAttribute('aria-expanded', 'false'); }
  build(); dlg.showModal();
  addEventListener('scroll', onMove, { passive: true, capture: true }); addEventListener('resize', onMove);
  show(0);
}

async function end() {
  if (!running) return;
  markSeen();
  removeEventListener('scroll', onMove, { capture: true }); removeEventListener('resize', onMove);
  if (dlg.open) dlg.close();
  dlg.remove(); hole.remove(); dlg = hole = null; running = false;
  await setViewer(false);
  window.scrollTo({ top: startY, behavior: 'instant' });
  if (opener && document.contains(opener) && opener.getClientRects().length) opener.focus({ preventScroll: true });
}

/* convite discreto para quem chega por um link compartilhado */
let hintEl = null;
function hideHint() { if (hintEl) { hintEl.remove(); hintEl = null; } }
function showHint() {
  if (running || hintEl || seen()) return;
  if (document.querySelector('dialog[open]')) {
    const d = document.querySelector('dialog[open]');
    d.addEventListener('close', () => setTimeout(showHint, 400), { once: true });
    return;
  }
  hintEl = document.createElement('div'); hintEl.className = 'tour-hint'; hintEl.setAttribute('role', 'region'); hintEl.setAttribute('aria-label', 'Tutorial do guia');
  hintEl.innerHTML = '<span>Primeira vez aqui?</span><button type="button" class="tour-hint-go">Ver como usar o guia</button><button type="button" class="tour-hint-no">Agora não</button>';
  hintEl.addEventListener('click', e => {
    if (e.target.closest('.tour-hint-go')) startTour();
    else if (e.target.closest('.tour-hint-no')) { markSeen(); hideHint(); }
  });
  document.body.append(hintEl);
  setTimeout(hideHint, 25000);
}

export function initTour() {
  if (new URLSearchParams(location.search).has('gerar')) return;   // gerador das prévias de link
  const fromHash = () => {
    if (location.hash !== HASH) return false;
    history.replaceState(null, '', location.pathname + location.search);
    startTour(); return true;
  };
  document.addEventListener('click', e => {
    const t = e.target.closest('[data-tour]'); if (!t) return;
    e.preventDefault(); startTour(t);
  });
  addEventListener('hashchange', fromHash);
  if (fromHash() || seen()) return;
  if (/^#(a|tema|p|d)=/.test(location.hash)) setTimeout(showHint, 1200);
  else setTimeout(() => { if (!running && !document.querySelector('dialog[open]')) startTour(); }, 600);
}
