/* Imagens de compartilhamento (Stories 9:16, Feed 4:5 e prévia de link 1200x630), desenhadas em canvas.
   Recebe um "cartão" montado pelo app.js:
   { kind: 'ponto'|'tema'|'argumento'|'pagina', doc?, title, label?, text?, refs?, items?, total?, url,
     excerpt?: async (aspect, larguraPx) => canvas com o recorte da página e o trecho marcado, excerptPage?, excerptDoc? }
   Cada referência é { d?: documento, p: página (ordem no PDF) }; sem d, é o documento principal. Os textos de cada
   documento, e o número impresso de cada página (labels), vêm de setDocs(). */

const K = {
  ink: '#16202e', ink2: '#4a5568', sheet: '#ffffff', line: '#d8dee7', paper: '#f3f5f8',
  mark: '#ffe14d', link: '#0b4fa8',
  tags: { documentado: ['#0b6b5c', '#dff3ee'], alegado: ['#9a4a00', '#fdebd3'], reportagem: ['#1d4f91', '#e2ebf8'], 'interpretação': ['#5b3ba8', '#ebe5f8'] },
};
const SERIF = 'GuiaSerif, Georgia, "Times New Roman", serif';
const SANS = 'GuiaSans, "Segoe UI", Roboto, Arial, sans-serif';
export const FORMATS = { story: [1080, 1920], feed: [1080, 1350], og: [1200, 630] };
export const BRAND = 'Guia do cargo na Câmara';

/* documentos do guia (boletins da Câmara, Ato da Mesa, perfil na Alerj, Agência Senado e diplomas), com os textos
   de cada um; o primeiro é o principal */
let DOCS = {}, MAIN = '';
export function setDocs(list) { DOCS = Object.fromEntries(list.map(d => [d.id, d])); MAIN = list[0].id; }
export const docOf = id => DOCS[id || MAIN] || DOCS[MAIN];
const refDoc = r => (r && r.d) || MAIN;
const itemDoc = it => it.doc || refDoc((it.refs || [])[0]);
export const cap = t => t ? t[0].toUpperCase() + t.slice(1) : t;
/* número impresso da página ("3384", "capa") ou, sem ele, a ordem no PDF */
const labelOf = (d, p) => { const D = docOf(d); return (D.labels && D.labels[p]) || String(p); };
/* nome de uma página para botões e para o visualizador: "Boletim 2000, p. 3384", "Diploma de Direito", "Agência Senado".
   withDoc=false: só a página ("p. 3384") */
export function pageName(d, p, withDoc = true) {
  const D = docOf(d), nm = D.names && D.names[p];
  if (nm) return cap(nm);
  const lab = labelOf(d, p), pg = D.n === 1 ? '' : /^\d+$/.test(lab) ? 'p. ' + lab : lab;
  return withDoc ? (pg ? `${D.chip}, ${pg}` : D.chip) : (pg || D.chip);
}
const joinE = a => a.length > 1 ? a.slice(0, -1).join(', ') + ' e ' + a[a.length - 1] : (a[0] || '');
const docsIn = items => [...new Set((items || []).map(itemDoc))];
/* documento único do cartão (null se mistura documentos) */
function cardDoc(d) {
  if (d.kind === 'ponto' || d.kind === 'pagina') return d.doc || MAIN;
  const ds = docsIn(d.items); return ds.length === 1 ? ds[0] : null;
}
/* quem fala: "o boletim da Câmara de 27/12/2000" ou "o boletim da Câmara de 27/12/2000 e o perfil de Flávio na Alerj" */
export function sujeito(items) {
  const ds = docsIn(items);
  return ds.length === 1 ? { t: docOf(ds[0]).sujeito, pl: !!docOf(ds[0]).pl } : { t: joinE(ds.map(x => docOf(x).what)), pl: true };
}
/* de onde vem o ponto: "Segundo o boletim da Câmara de 27/12/2000"; a interpretação é do guia, não do documento */
export const vozDe = d => d.label === 'interpretação' ? 'Leitura do guia, a partir dos documentos' : d.label === 'reportagem' ? 'Segundo reportagem' : docOf(d.doc).voz;

/* como cada etiqueta entra no raciocínio do compartilhamento (mesmas definições da seção "Como ler") */
export function pesoLongo(label, doc) {
  const D = docOf(doc);
  return label === 'documentado' ? `fato registrado ${D.em}, com data e página` : label === 'alegado' ? D.aleg
    : label === 'reportagem' ? 'informação de reportagem, com link para a fonte' : 'leitura que liga os fatos';
}
export function pesoCurto(label, doc) {
  const D = docOf(doc);
  return label === 'documentado' ? `registrado ${D.em}` : label === 'alegado' ? D.alegCurto : label === 'reportagem' ? 'segundo reportagem' : 'leitura que liga os fatos';
}
export function pesoItem(label, doc) {
  const D = docOf(doc);
  return label === 'documentado' ? `registrado ${D.em}` : label === 'alegado' ? D.alegItem : label === 'reportagem' ? 'reportagem' : 'leitura que liga os fatos';
}
const plural = (n, um, varios) => n + ' ' + (n === 1 ? um : varios);
export function pesoResumo(items, detalhe = false) {
  const by = l => (items || []).filter(it => it.label === l);
  const doc = by('documentado'), ale = by('alegado'), rep = by('reportagem'), int = by('interpretação'), parts = [];
  if (doc.length) parts.push(plural(doc.length, 'fato registrado', 'fatos registrados') + ' ' + joinE(docsIn(doc).map(x => docOf(x).em)) + (detalhe ? ' (ato oficial, currículo ou diploma)' : ''));
  if (ale.length) {
    const ds = docsIn(ale);
    parts.push(ds.length === 1 ? plural(ale.length, docOf(ds[0]).aleg1, docOf(ds[0]).alegN) : plural(ale.length, 'afirmação que não é decisão', 'afirmações que não são decisões'));
  }
  if (rep.length) parts.push(plural(rep.length, 'informação de reportagem', 'informações de reportagem'));
  if (int.length) parts.push(plural(int.length, 'leitura que liga os fatos', 'leituras que ligam os fatos'));
  return joinE(parts);
}
/* páginas de um ponto, com o número impresso: "p. 3384" no documento do ponto; os outros documentos vêm com o nome.
   Documento de uma página só, ou cujas páginas não têm número (os diplomas): só o nome */
export function refsTxt(refs = [], main = MAIN) {
  const groups = [];
  for (const r of refs) {
    const d = refDoc(r); let g = groups.find(x => x.d === d);
    if (!g) groups.push(g = { d, ps: [] });
    if (!g.ps.includes(r.p)) g.ps.push(r.p);
  }
  groups.sort((a, b) => (a.d === main ? -1 : b.d === main ? 1 : 0));
  return groups.map(g => {
    const D = docOf(g.d), pg = D.n === 1 || D.nopg ? '' : pagesTxt(g.ps.sort((a, b) => a - b).map(p => labelOf(g.d, p)));
    return g.d === main ? pg : D.short + (pg ? ', ' + pg : '');
  }).filter(Boolean).join('; ');
}
function cardSource(d) {
  const ds = d.kind === 'ponto' ? [...new Set((d.refs || []).map(refDoc))] : null;
  const one = ds ? (ds.length === 1 ? ds[0] : null) : cardDoc(d);
  if (one) return `Fonte: ${docOf(one).source}. Cada ponto traz a página do documento original.`;
  return `Fontes: ${joinE((ds || docsIn(d.items)).map(x => docOf(x).src))}. Cada ponto traz a página do documento original.`;
}
const cardWhen = d => { const one = cardDoc(d); return one ? docOf(one).when : 'Documentos originais'; };

let fontsP = null;
export function loadFonts() {
  if (!fontsP) {
    const list = [['GuiaSerif', 'source-serif-4-latin-700-normal.woff2', '700'], ['GuiaSans', 'source-sans-3-latin-400-normal.woff2', '400'],
      ['GuiaSans', 'source-sans-3-latin-600-normal.woff2', '600'], ['GuiaSans', 'source-sans-3-latin-700-normal.woff2', '700']];
    fontsP = Promise.all(list.map(([fam, file, weight]) =>
      new FontFace(fam, `url(${new URL('../vendor/fonts/' + file, import.meta.url).href})`, { weight }).load().then(f => document.fonts.add(f))
    )).catch(() => { });
  }
  return fontsP;
}
let qrP = null;
const qrLib = () => (qrP ||= import('../vendor/qrcode.mjs').then(m => m.default));

/* ---------- utilidades de desenho ---------- */
const setFont = (ctx, w, size, fam) => { ctx.font = `${w} ${size}px ${fam}`; };
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y, w, h, r); else ctx.rect(x, y, w, h); }

function wrap(ctx, text, maxW, maxLines = 99) {
  const words = String(text || '').split(/\s+/).filter(Boolean);
  const lines = []; let cur = '';
  for (let i = 0; i < words.length; i++) {
    const t = cur ? cur + ' ' + words[i] : words[i];
    if (!cur || ctx.measureText(t).width <= maxW) cur = t;
    else { lines.push(cur); cur = words[i]; if (lines.length === maxLines) break; }
  }
  if (lines.length < maxLines) { if (cur) lines.push(cur); return lines; }
  let last = lines[maxLines - 1];
  while (last && ctx.measureText(last + '…').width > maxW) { const k = last.lastIndexOf(' '); last = k > 0 ? last.slice(0, k) : last.slice(0, -1); }
  lines[maxLines - 1] = last.replace(/[\s,.;:–—-]+$/, '') + '…';
  return lines;
}
export function pagesTxt(ps = []) {
  if (!ps.length) return '';
  const a = ps.slice(0, 5), pre = /^\d/.test(a[0]) ? 'p. ' : '';
  const s = a.length === 1 ? pre + a[0] : pre + a.slice(0, -1).join(', ') + ' e ' + a[a.length - 1];
  return s + (ps.length > 5 ? ' e outras' : '');
}
/* título com marca-texto amarelo atrás de cada linha, como os trechos marcados no documento */
function markedTitle(ctx, lines, x, y, size, lh) {
  lines.forEach((ln, i) => {
    const by = y + i * lh, w = ctx.measureText(ln).width;
    ctx.fillStyle = K.mark; ctx.fillRect(x - size * 0.1, by - size * 0.4, w + size * 0.2, size * 0.52);
  });
  ctx.fillStyle = K.ink; lines.forEach((ln, i) => ctx.fillText(ln, x, y + i * lh));
}
/* tamanho do título que cabe em maxLines; devolve {size, lines} */
function fitTitle(ctx, text, maxW, sizes, maxLines) {
  for (const s of sizes) { setFont(ctx, 700, s, SERIF); const l = wrap(ctx, text, maxW, 99); if (l.length <= maxLines) return { size: s, lines: l }; }
  const s = sizes[sizes.length - 1]; setFont(ctx, 700, s, SERIF); return { size: s, lines: wrap(ctx, text, maxW, maxLines) };
}
function pill(ctx, label, x, y, size) {
  const [fg, bg] = K.tags[label] || [K.ink2, K.paper];
  setFont(ctx, 700, size, SANS); const tw = ctx.measureText(label).width;
  const px = size * 0.62, h = Math.round(size * 1.62);
  ctx.fillStyle = bg; rr(ctx, x, y, tw + 2 * px, h, h / 2); ctx.fill();
  ctx.fillStyle = fg; ctx.textBaseline = 'middle'; ctx.fillText(label, x + px, y + h / 2 + size * 0.05); ctx.textBaseline = 'alphabetic';
  return { w: tw + 2 * px, h };
}
function brand(ctx, x, y, size) {
  // mesma marca do site: quadrado escuro com uma faixa de marca-texto
  ctx.fillStyle = K.ink; rr(ctx, x, y, size, size, size * 0.14); ctx.fill();
  ctx.fillStyle = K.mark; ctx.fillRect(x + size * 0.09, y + size * 0.55, size * 0.82, size * 0.33);
  setFont(ctx, 700, Math.round(size * 0.8), SANS); ctx.fillStyle = K.ink;
  ctx.fillText(BRAND, x + size * 1.35, y + size * 0.78);
}
async function drawQR(ctx, url, x, y, size) {
  const qrcode = await qrLib();
  const qr = qrcode(0, 'M'); qr.addData(url); qr.make();
  const n = qr.getModuleCount(), q = 2, cell = size / (n + 2 * q);
  ctx.fillStyle = '#fff'; ctx.fillRect(x, y, size, size);
  ctx.fillStyle = K.ink;
  for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) if (qr.isDark(r, c)) {
    const x0 = Math.floor(x + (c + q) * cell), y0 = Math.floor(y + (r + q) * cell);
    ctx.fillRect(x0, y0, Math.floor(x + (c + q + 1) * cell) - x0, Math.floor(y + (r + q + 1) * cell) - y0);
  }
}
/* recorte da página com o trecho marcado; o nome da página ("Boletim 2000, p. 3384") vai numa etiqueta logo acima,
   para não cobrir o texto do documento */
async function drawExcerpt(ctx, d, x, y, w, h, pgLabelSize) {
  if (!d.excerpt) return false;
  const t = d.excerptPage ? pageName(d.excerptDoc || MAIN, d.excerptPage) : '';
  const ph = t ? Math.round(pgLabelSize * 1.6) : 0, gap = t ? 8 : 0, eh = h - ph - gap;
  let ex; try { ex = await d.excerpt(w / eh, Math.round(w)); } catch (e) { return false; }
  if (!ex) return false;
  const s = Math.min(w / ex.width, eh / ex.height), dw = ex.width * s, dh = ex.height * s, dx = x + (w - dw) / 2, dy = y + ph + gap;
  ctx.save(); rr(ctx, dx, dy, dw, dh, 10); ctx.clip(); ctx.drawImage(ex, dx, dy, dw, dh); ctx.restore();
  ctx.strokeStyle = K.line; ctx.lineWidth = 2; rr(ctx, dx, dy, dw, dh, 10); ctx.stroke();
  if (t) {
    setFont(ctx, 700, pgLabelSize, SANS); const tw = ctx.measureText(t).width;
    ctx.fillStyle = K.ink; rr(ctx, dx, y, tw + pgLabelSize * 1.2, ph, ph / 2); ctx.fill();
    ctx.fillStyle = '#fff'; ctx.textBaseline = 'middle'; ctx.fillText(t, dx + pgLabelSize * 0.6, y + ph / 2 + 1); ctx.textBaseline = 'alphabetic';
  }
  return dh + ph + gap;
}
function kicker(d) {
  const one = cardDoc(d), D = docOf(one);
  if (d.kind === 'tema') return `Tema ${one ? D.de : 'do guia'}, em ${d.total || d.items.length} pontos`;
  if (d.kind === 'argumento') return one ? `O que ${D.what} ${D.pl ? 'apontam' : 'aponta'}, em ${d.items.length} passos` : `O que os documentos apontam, em ${d.items.length} passos`;
  if (d.kind === 'pagina') return D.label;
  if (d.label === 'interpretação') return 'Leitura do guia, a partir dos documentos';
  return `O que ${D.pl ? 'dizem' : 'diz'} ${D.what}`;
}
/* "Base: 5 fatos registrados no acórdão e 2 afirmações de ministros ou das mensagens", com o rótulo em negrito */
function baseLine(ctx, items, x, y, maxW, size) {
  setFont(ctx, 700, size, SANS); ctx.fillStyle = K.ink; const lab = 'Base: '; ctx.fillText(lab, x, y);
  const lw = ctx.measureText(lab).width;
  setFont(ctx, 600, size, SANS); ctx.fillStyle = K.ink2;
  const L = wrap(ctx, pesoResumo(items) + '.', maxW - lw, 2);
  L.forEach((l, i) => ctx.fillText(l, x + lw, y + i * Math.round(size * 1.3)));
  return L.length * Math.round(size * 1.3);
}

/* ---------- item de lista (tema e argumento) ---------- */
function itemBox(ctx, it, maxW, sc) {   // it.pagesLine: páginas já formatadas
  const r = 24 * sc, tx = 2 * r + 22 * sc, tw = maxW - tx;
  setFont(ctx, 600, Math.round(34 * sc), SANS); const lines = wrap(ctx, it.title, tw, 2);
  const lh = 41 * sc, pillH = Math.round(22 * sc * 1.62);
  return { r, tx, tw, lines, lh, pillH, h: Math.max(2 * r, lines.length * lh + 10 * sc + pillH) };
}
function drawItem(ctx, it, n, x, y, b, sc) {
  ctx.fillStyle = K.ink; ctx.beginPath(); ctx.arc(x + b.r, y + b.r, b.r, 0, Math.PI * 2); ctx.fill();
  setFont(ctx, 700, Math.round(24 * sc), SANS); ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(String(n), x + b.r, y + b.r + 1); ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  setFont(ctx, 600, Math.round(34 * sc), SANS); ctx.fillStyle = K.ink;
  b.lines.forEach((ln, i) => ctx.fillText(ln, x + b.tx, y + 30 * sc + i * b.lh));
  const my = y + b.lines.length * b.lh + 10 * sc;
  const p = pill(ctx, it.label, x + b.tx, my, Math.round(22 * sc));
  if (it.pagesLine) { setFont(ctx, 600, Math.round(24 * sc), SANS); ctx.fillStyle = K.ink2; ctx.fillText(wrap(ctx, it.pagesLine, b.tw - p.w - 14 * sc, 1)[0], x + b.tx + p.w + 14 * sc, my + p.h * 0.7); }
}

/* ---------- formatos altos: Stories e Feed ---------- */
async function layoutTall(ctx, d, W, H, story) {
  const M = story ? 52 : 40, top = story ? 168 : 40, bottom = story ? H - 168 : H - 40;
  ctx.fillStyle = K.sheet; rr(ctx, M, top, W - 2 * M, bottom - top, 30); ctx.fill();
  const P = story ? 64 : 56, x = M + P, maxW = W - 2 * (M + P);
  let y = top + P;
  brand(ctx, x, y, 40);
  setFont(ctx, 600, 26, SANS); ctx.fillStyle = K.ink2; ctx.textAlign = 'right'; ctx.fillText(cardWhen(d), x + maxW, y + 30); ctx.textAlign = 'left';
  y += 40 + (story ? 52 : 38);

  // rodapé: QR, chamada, endereço e fonte
  const qrS = story ? 220 : 180;
  setFont(ctx, 400, story ? 25 : 23, SANS); const disc = wrap(ctx, cardSource(d), maxW, 4); const discLh = story ? 33 : 30;
  const footTop = bottom - P - disc.length * discLh - 24 - qrS;
  ctx.strokeStyle = K.line; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x, footTop - 30); ctx.lineTo(x + maxW, footTop - 30); ctx.stroke();
  await drawQR(ctx, d.url, x - 8, footTop, qrS);
  const cx = x + qrS + 26, cw = maxW - qrS - 26;
  setFont(ctx, 700, story ? 38 : 33, SANS); ctx.fillStyle = K.ink;
  const more = d.kind === 'tema' && (d.total || 0) > (d.items || []).length;
  const call = wrap(ctx, d.kind === 'pagina' ? 'Veja esta página no guia, com o trecho marcado'
    : more ? `Veja os ${d.total} pontos, cada um marcado no documento` : 'Veja cada trecho marcado no documento', cw, 2);
  let cy = footTop + (story ? 50 : 44); call.forEach(l => { ctx.fillText(l, cx, cy); cy += story ? 46 : 40; });
  let hs = story ? 32 : 28; const host = d.host || location.host;
  do { setFont(ctx, 700, hs, SANS); hs -= 1; } while (ctx.measureText(host).width > cw && hs > 16);
  ctx.fillStyle = K.link; ctx.fillText(host, cx, cy + 6); cy += story ? 46 : 40;
  setFont(ctx, 400, story ? 25 : 23, SANS); ctx.fillStyle = K.ink2; ctx.fillText('Aponte a câmera do celular para o código.', cx, cy + 4);
  setFont(ctx, 400, story ? 25 : 23, SANS); ctx.fillStyle = K.ink2;
  disc.forEach((l, i) => ctx.fillText(l, x, footTop + qrS + 24 + 22 + i * discLh));

  const limit = footTop - 60; // fim da área de conteúdo
  // linha de etiqueta ou subtítulo
  setFont(ctx, 600, story ? 30 : 27, SANS); ctx.fillStyle = K.ink2; ctx.fillText(kicker(d), x, y + 26); y += story ? 60 : 50;
  // título
  const T = fitTitle(ctx, d.title, maxW, story ? [76, 68, 62, 56, 50] : [66, 60, 54, 48], story ? 4 : 3);
  const tlh = Math.round(T.size * 1.16);
  setFont(ctx, 700, T.size, SERIF); markedTitle(ctx, T.lines, x, y + T.size * 0.82, T.size, tlh);
  y += T.lines.length * tlh + (story ? 30 : 22);

  if (d.kind === 'ponto' || d.kind === 'pagina') {
    const tsize = story ? 34 : 30, lh = Math.round(tsize * 1.38);
    const exMin = d.excerpt ? (story ? 320 : 230) : 0;
    const pesoH = d.kind === 'ponto' ? (story ? 78 : 64) : 0;
    if (d.text) {
      setFont(ctx, 400, tsize, SANS); const room = Math.floor((limit - y - exMin - pesoH - (d.excerpt ? 30 : 0)) / lh);
      const L = wrap(ctx, d.text, maxW, Math.max(2, Math.min(story ? 7 : 4, room)));
      ctx.fillStyle = K.ink; L.forEach((l, i) => ctx.fillText(l, x, y + tsize + i * lh)); y += L.length * lh + (story ? 30 : 22);
    }
    if (d.kind === 'ponto') {
      const p = pill(ctx, d.label, x, y, story ? 26 : 24);
      const pg = refsTxt(d.refs, d.label === 'interpretação' ? null : d.doc), t = pesoCurto(d.label, d.doc) + (pg ? ', ' + pg : '');
      setFont(ctx, 600, story ? 28 : 26, SANS); ctx.fillStyle = K.ink2;
      ctx.fillText(wrap(ctx, t, maxW - p.w - 16, 1)[0], x + p.w + 16, y + p.h * 0.7);
      y += pesoH;
    }
    if (d.excerpt && limit - y > 140) await drawExcerpt(ctx, d, x, y, maxW, limit - y, story ? 24 : 22);
  } else {
    if (d.text) {
      const tsize = story ? 32 : 28, lh = Math.round(tsize * 1.38);
      setFont(ctx, 400, tsize, SANS); const L = wrap(ctx, d.text, maxW, story ? 4 : 2);
      ctx.fillStyle = K.ink2; L.forEach((l, i) => ctx.fillText(l, x, y + tsize + i * lh)); y += L.length * lh + (story ? 30 : 22);
    }
    y += baseLine(ctx, d.items, x, y + (story ? 30 : 27), maxW, story ? 30 : 27) + (story ? 30 : 22);
    const items = d.items || [], tot = d.total || items.length, moreH = story ? 44 : 38; let shown = 0;
    // diminui um pouco a lista para caber inteira (ex.: os sete fatos), até um limite de legibilidade;
    // se couber, o "e mais N pontos" do tema fica no rodapé ("Veja os N pontos")
    let sc = story ? 1 : 0.92; const gap0 = story ? 26 : 20;
    const listH = k => items.reduce((h, it) => h + itemBox(ctx, it, maxW, k).h + gap0 * k, 0) - gap0 * k;
    while (sc > 0.77 && listH(sc) > limit - y) sc -= 0.03;
    const gap = gap0 * sc, allFit = listH(sc) <= limit - y;
    for (const it of items) {
      const b = itemBox(ctx, it, maxW, sc);
      const needMore = !allFit && shown + 1 < tot ? moreH : 0;
      if (y + b.h + needMore > limit) break;
      drawItem(ctx, it, shown + 1, x, y, b, sc); y += b.h + gap; shown++;
    }
    if (shown < tot && !(allFit && more)) {
      setFont(ctx, 700, story ? 30 : 27, SANS); ctx.fillStyle = K.link;
      ctx.fillText(`E mais ${tot - shown} ${tot - shown === 1 ? 'ponto' : 'pontos'} no link`, x, y + 28);
    }
  }
}

/* ---------- prévia de link (WhatsApp, Facebook, X...) ---------- */
async function layoutOG(ctx, d, W, H) {
  ctx.fillStyle = K.sheet; rr(ctx, 26, 26, W - 52, H - 52, 22); ctx.fill();
  const x = 64, maxW = W - 128; let y = 58;
  brand(ctx, x, y, 34);
  let hs = 24; const host = d.host || location.host; setFont(ctx, 700, hs, SANS); ctx.fillStyle = K.link; ctx.textAlign = 'right'; ctx.fillText(host, x + maxW, y + 26); ctx.textAlign = 'left';
  y += 34 + 30;
  const hasEx = !!d.excerpt;
  if (d.kind === 'ponto') {
    const p = pill(ctx, d.label, x, y, 22);
    const pg = refsTxt(d.refs, d.doc);
    const who = d.label === 'interpretação' ? 'Leitura do guia: ' + refsTxt(d.refs, null) : docOf(d.doc).voz + (pg ? ', ' + pg : '');
    setFont(ctx, 600, 24, SANS); ctx.fillStyle = K.ink2; ctx.fillText(wrap(ctx, who, maxW - p.w - 14, 1)[0], x + p.w + 14, y + p.h * 0.7);
    y += p.h + 18;
  } else {
    setFont(ctx, 600, 25, SANS); ctx.fillStyle = K.ink2; ctx.fillText(d.kicker || kicker(d), x, y + 22); y += 44;
  }
  const T = fitTitle(ctx, d.title, maxW, hasEx ? [54, 48, 44, 40] : [64, 58, 52, 46], hasEx ? 2 : 3);
  const tlh = Math.round(T.size * 1.15);
  setFont(ctx, 700, T.size, SERIF); markedTitle(ctx, T.lines, x, y + T.size * 0.82, T.size, tlh);
  y += T.lines.length * tlh + 18;
  if (hasEx) {
    await drawExcerpt(ctx, d, x, y, maxW, H - 56 - y, 20);
  } else {
    if (d.items && d.items.length) {
      y += baseLine(ctx, d.items, x, y + 26, maxW, 26) + 16;
    } else if (d.text) {
      setFont(ctx, 400, 30, SANS); ctx.fillStyle = K.ink2;
      const L = wrap(ctx, d.text, maxW, 3); L.forEach((l, i) => ctx.fillText(l, x, y + 30 + i * 41)); y += L.length * 41 + 26;
    }
    const items = d.items || [], tot = d.total || items.length, lh = 44, end = H - 60; let shown = 0;
    for (const it of items) {
      if (y + lh + (shown + 1 < tot ? lh : 0) > end) break;
      ctx.fillStyle = K.mark; ctx.fillRect(x, y + 8, 14, 14);
      setFont(ctx, 600, 27, SANS); ctx.fillStyle = K.ink; ctx.fillText(wrap(ctx, it.title, maxW - 30, 1)[0], x + 30, y + 24);
      y += lh; shown++;
    }
    if (shown && shown < tot) { setFont(ctx, 700, 25, SANS); ctx.fillStyle = K.link; ctx.fillText(`E mais ${tot - shown} ${tot - shown === 1 ? 'ponto' : 'pontos'}, cada um com a página marcada`, x + 30, y + 22); }
  }
}

export async function renderCard(d, fmt = 'story') {
  await loadFonts();
  const main = cardDoc(d) || MAIN;
  (d.items || []).forEach(it => { it.pagesLine = refsTxt(it.refs, it.label === 'interpretação' ? null : main); });
  const [W, H] = FORMATS[fmt];
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = K.ink; ctx.fillRect(0, 0, W, H);
  if (fmt === 'og') await layoutOG(ctx, d, W, H); else await layoutTall(ctx, d, W, H, fmt === 'story');
  return cv;
}
