/* Página "O cargo de Flávio na Câmara": menu, ampliar documentos, links diretos e compartilhar. */
import { renderCard } from './card.js';

const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const DATA = JSON.parse($('#dados').textContent);
const ROOT = location.origin + location.pathname.replace(/index\.html?$/, '');

/* ---------- menu no celular ---------- */
function wireMenu() {
  const btn = $('#menuBtn'), mob = $('#mobileNav');
  mob.innerHTML = $$('#nav a').map(a => `<a href="${a.getAttribute('href')}">${esc(a.textContent)}</a>`).join('');
  const close = () => { mob.hidden = true; btn.setAttribute('aria-expanded', 'false'); };
  btn.onclick = () => { const open = mob.hidden; mob.hidden = !open; btn.setAttribute('aria-expanded', String(open)); };
  mob.addEventListener('click', e => { if (e.target.closest('a')) close(); });
  addEventListener('keydown', e => { if (e.key === 'Escape' && !mob.hidden) { close(); btn.focus(); } });
}

/* ---------- avisos e cópia ---------- */
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('on'); clearTimeout(toast.k); toast.k = setTimeout(() => t.classList.remove('on'), 2200); }
async function copyText(txt, msg) {
  try { await navigator.clipboard.writeText(txt); }
  catch (_) { const a = document.createElement('textarea'); a.value = txt; a.style.position = 'fixed'; a.style.opacity = '0'; document.body.appendChild(a); a.select(); try { document.execCommand('copy'); } catch (e) { } a.remove(); }
  toast(msg || 'Copiado');
}
function quietCopy(txt) { try { navigator.clipboard.writeText(txt).catch(() => { }); } catch (_) { } }

/* ---------- ampliar um documento ---------- */
let zoomOpener = null;
function openZoom(id, opener) {
  const fig = document.querySelector(`#${CSS.escape(id)} .paper`); if (!fig) return;
  zoomOpener = opener || null;
  const it = DATA.itens[id];
  $('#zoomTitle').textContent = it ? it.title : 'Documento';
  const body = $('#zoomBody'); body.innerHTML = '';
  const c = fig.cloneNode(true); c.removeAttribute('tabindex'); c.removeAttribute('data-zoom'); c.removeAttribute('aria-label');
  c.querySelectorAll('img').forEach(i => i.loading = 'eager');
  c.querySelector('.zoom-hint')?.remove();
  body.appendChild(c);
  const dlg = $('#zoomDlg'); if (!dlg.open) dlg.showModal();
  body.scrollTop = 0; body.scrollLeft = 0;
}
function wireZoom() {
  document.addEventListener('click', e => {
    const t = e.target.closest('[data-zoom]'); if (!t || t.closest('#zoomDlg')) return;
    openZoom(t.dataset.zoom, t);
  });
  document.addEventListener('keydown', e => {
    if ((e.key === 'Enter' || e.key === ' ') && e.target.matches?.('figure.paper[data-zoom]')) { e.preventDefault(); openZoom(e.target.dataset.zoom, e.target); }
  });
  $('#zoomDlg').addEventListener('close', () => { if (zoomOpener && document.contains(zoomOpener)) zoomOpener.focus(); zoomOpener = null; });
}

/* ---------- link direto: realça o ponto ou o documento ---------- */
function pulse() {
  const id = decodeURIComponent(location.hash.slice(1)); if (!id) return;
  const el = document.getElementById(id); if (!el) return;
  el.querySelectorAll('.hl').forEach(h => { h.classList.remove('pulse'); void h.offsetWidth; h.classList.add('pulse'); });
}

/* ---------- recorte do documento para as imagens, com o marca-texto ---------- */
const imgCache = new Map();
function loadImg(src) {
  if (!imgCache.has(src)) imgCache.set(src, new Promise((ok, no) => { const i = new Image(); i.onload = () => ok(i); i.onerror = no; i.src = new URL(src, ROOT).href; }));
  return imgCache.get(src);
}
async function excerptCanvas(docId, aspect) {
  const doc = DATA.docs[docId]; if (!doc) return null;
  const g = doc.groups.find(gr => gr.segs.some(s => s.hl.length)) || doc.groups[0];
  const imgs = await Promise.all(g.segs.map(s => loadImg(s.src)));
  const W = Math.max(...g.segs.map(s => s.w)), GAP = 26;
  const H = g.segs.reduce((a, s) => a + Math.round(s.h * W / s.w), 0) + GAP * (g.segs.length - 1);
  const full = document.createElement('canvas'); full.width = W; full.height = H;
  const ctx = full.getContext('2d'); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H);
  let y = 0; const rects = [];
  g.segs.forEach((s, i) => {
    const h = Math.round(s.h * W / s.w);
    if (i) { ctx.strokeStyle = '#c3cad5'; ctx.lineWidth = 3; ctx.setLineDash([10, 8]); ctx.beginPath(); ctx.moveTo(0, y - GAP / 2); ctx.lineTo(W, y - GAP / 2); ctx.stroke(); ctx.setLineDash([]); }
    ctx.drawImage(imgs[i], 0, y, W, h);
    s.hl.forEach(([rx, ry, rw, rh]) => rects.push([rx * W, y + ry * h, rw * W, rh * h]));
    y += h + GAP;
  });
  ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = '#ffe14d';
  rects.forEach(r => ctx.fillRect(...r));
  ctx.globalCompositeOperation = 'source-over';
  // recorta em volta do trecho marcado quando o documento é mais alto que o espaço
  const ch = Math.round(W / aspect);
  if (ch >= H || !rects.length) return full;
  let y0 = Math.min(...rects.map(r => r[1])), y1 = Math.max(...rects.map(r => r[1] + r[3]));
  if (y1 - y0 > ch * 0.86) y1 = y0 + ch * 0.86;
  const top = Math.max(0, Math.min(H - ch, (y0 + y1) / 2 - ch / 2));
  const cut = document.createElement('canvas'); cut.width = W; cut.height = ch;
  cut.getContext('2d').drawImage(full, 0, top, W, ch, 0, 0, W, ch);
  return cut;
}

/* ---------- cartões de compartilhamento ---------- */
function cardOf(id) {
  if (id === 'pagina') {
    const p = DATA.pagina;
    return { ...p, id, url: ROOT, curto: DATA.curto[p.doc], excerpt: aspect => excerptCanvas(p.doc, aspect) };
  }
  const it = DATA.itens[id]; if (!it) return null;
  return { ...it, id, url: ROOT + 'p/' + id + '/', curto: it.doc ? DATA.curto[it.doc] : '', excerpt: it.doc ? aspect => excerptCanvas(it.doc, aspect) : null };
}
const cutText = (t, n) => t.length <= n ? t : t.slice(0, n - 1).replace(/\s+\S*$/, '').replace(/[\s,.;:–—-]+$/, '') + '…';
function baseLine(d) {
  if (d.kind === 'resposta') return `Base: ${d.fonte}.`;
  if (d.label === 'documentado') return `Base: documento público (${d.fonte}).`;
  if (d.label === 'reportagem') return 'Base: reportagem da BBC News Brasil, de 23/1/2019.';
  return 'Base: leitura que liga os fatos dos documentos.';
}
function msgText(d, wa, withUrl = true) {
  const B = t => (wa ? `*${t}*` : t), L = [];
  if (d.kind === 'pagina') {
    L.push(B(d.title), '', d.text);
    if (withUrl) L.push('', d.url);
    return L.join('\n');
  }
  if (d.kind === 'resposta') L.push('Se alguém disser: ' + B(`“${d.title}”`), '', d.text, '', baseLine(d));
  else L.push(B(d.title), '', d.text, '', baseLine(d));
  if (withUrl) L.push('', d.doc ? 'Veja o documento, com o trecho marcado:' : 'Veja os documentos:', d.url);
  return L.join('\n');
}
function shortText(d, max) {
  const t = d.kind === 'resposta' ? `Se alguém disser “${d.title}”: ${d.text}` : `${d.title}. ${d.text}`;
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
const SH = { d: null, fmt: 'story', blob: null, file: null, url: null, opener: null };
function openShare(d, opener) {
  SH.d = d; SH.opener = opener || null; SH.blob = SH.file = null; if (SH.url) { URL.revokeObjectURL(SH.url); SH.url = null; }
  $('#shWhat').textContent = d.kind === 'resposta' ? `Se alguém disser: “${d.title}”` : d.title;
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
    SH.blob = blob; SH.file = new File([blob], `cargo-na-camara-${d.id}-${fmt}.png`, { type: 'image/png' });
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
function wireShare() {
  document.addEventListener('click', e => {
    const s = e.target.closest('[data-share]');
    if (s) { const d = cardOf(s.dataset.share); if (d) openShare(d, s); return; }
    const c = e.target.closest('[data-copy-answer]');
    if (c) { const d = cardOf(c.dataset.copyAnswer); if (d) copyText(msgText(d, false), 'Resposta copiada, com o link'); }
  });
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
  dlg.addEventListener('close', () => { const o = SH.opener; SH.opener = null; if (o && document.contains(o)) o.focus(); });
}

/* usado só pelo script que gera as prévias de link (og:image) */
if (new URLSearchParams(location.search).has('gerar')) {
  window.__cargoCard = async (id, fmt = 'og', q = 0.86) => {
    const d = cardOf(id); d.host = 'guiadenunciaflavio.github.io';
    const cv = await renderCard(d, fmt);
    return cv.toDataURL('image/jpeg', q);
  };
}

wireMenu(); wireZoom(); wireShare();
addEventListener('hashchange', pulse);
if (location.hash) setTimeout(pulse, 400);
