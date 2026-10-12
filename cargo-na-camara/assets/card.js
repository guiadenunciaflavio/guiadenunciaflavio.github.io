/* Imagens de compartilhamento (Stories 9:16, Feed 4:5 e prévia de link 1200x630), desenhadas em canvas.
   Mesmo desenho dos guias (denuncia/assets/card.js), com os textos desta página.
   Recebe um "cartão" montado pelo page.js:
   { kind: 'ponto'|'doc'|'resposta'|'pagina', title, label, text, fonte, curto?, url,
     excerpt?: async (aspect, larguraPx) => canvas com o recorte do documento e o trecho marcado } */

const K = {
  ink: '#16202e', ink2: '#4a5568', sheet: '#ffffff', line: '#d8dee7', paper: '#f3f5f8',
  mark: '#ffe14d', link: '#0b4fa8',
  tags: { documentado: ['#0b6b5c', '#dff3ee'], reportagem: ['#1d4f91', '#e2ebf8'], 'interpretação': ['#5b3ba8', '#ebe5f8'] },
};
const SERIF = 'GuiaSerif, Georgia, "Times New Roman", serif';
const SANS = 'GuiaSans, "Segoe UI", Roboto, Arial, sans-serif';
export const FORMATS = { story: [1080, 1920], feed: [1080, 1350], og: [1200, 630] };
const SOURCE = 'Fontes: atos da Câmara dos Deputados (Boletim Administrativo e Diário da Câmara), perfil de Flávio Bolsonaro na Alerj, diploma publicado por ele e reportagem da BBC News Brasil (23/1/2019).';
export const PESO_CURTO = { documentado: 'documento público', reportagem: 'BBC News Brasil, 2019', 'interpretação': 'leitura que liga os fatos' };

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
/* título com marca-texto amarelo atrás de cada linha, como os trechos marcados nos documentos */
function markedTitle(ctx, lines, x, y, size, lh) {
  lines.forEach((ln, i) => {
    const by = y + i * lh, w = ctx.measureText(ln).width;
    ctx.fillStyle = K.mark; ctx.fillRect(x - size * 0.1, by - size * 0.4, w + size * 0.2, size * 0.52);
  });
  ctx.fillStyle = K.ink; lines.forEach((ln, i) => ctx.fillText(ln, x, y + i * lh));
}
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
  ctx.fillText('Guias de leitura', x + size * 1.35, y + size * 0.78);
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
async function drawExcerpt(ctx, d, x, y, w, h, lblSize, center = false) {
  if (!d.excerpt) return false;
  const capH = d.curto ? Math.round(lblSize * 1.9) : 0;
  let ex; try { ex = await d.excerpt(w / Math.max(1, h - capH), Math.round(w)); } catch (e) { return false; }
  if (!ex) return false;
  const s = Math.min(w / ex.width, (h - capH) / ex.height), dw = ex.width * s, dh = ex.height * s;
  const dx = x + (w - dw) / 2, dy = center ? y + Math.max(0, (h - dh - capH) / 2) : y;
  ctx.save(); rr(ctx, dx, dy, dw, dh, 10); ctx.clip(); ctx.fillStyle = '#fff'; ctx.fillRect(dx, dy, dw, dh); ctx.drawImage(ex, dx, dy, dw, dh); ctx.restore();
  ctx.strokeStyle = K.line; ctx.lineWidth = 2; rr(ctx, dx, dy, dw, dh, 10); ctx.stroke();
  if (d.curto) {
    // a origem do recorte vai embaixo dele, sem cobrir o documento
    setFont(ctx, 600, lblSize, SANS); ctx.fillStyle = K.ink2;
    ctx.fillText(wrap(ctx, d.curto, dw, 1)[0], dx + 2, dy + dh + lblSize * 1.35);
  }
  return dh + capH;
}
function kicker(d) {
  if (d.kind === 'resposta') return 'Se alguém disser:';
  if (d.kind === 'doc') return 'Documento de ' + (d.data || '');
  if (d.kind === 'pagina') return 'Flávio Bolsonaro, 2000 a 2002';
  return 'O cargo de Flávio Bolsonaro na Câmara';
}
const titleOf = d => d.kind === 'resposta' ? `“${d.title}”` : d.title;
function baseText(d) {
  if (d.kind === 'resposta' || d.kind === 'pagina') return 'Base: ' + d.fonte;
  return (PESO_CURTO[d.label] || '') + (d.label === 'documentado' && d.fonte ? ': ' + d.fonte : '');
}

/* ---------- formatos altos: Stories e Feed ---------- */
async function layoutTall(ctx, d, W, H, story) {
  const M = story ? 52 : 40, top = story ? 168 : 40, bottom = story ? H - 168 : H - 40;
  ctx.fillStyle = K.sheet; rr(ctx, M, top, W - 2 * M, bottom - top, 30); ctx.fill();
  const P = story ? 64 : 56, x = M + P, maxW = W - 2 * (M + P);
  let y = top + P;
  brand(ctx, x, y, 40);
  setFont(ctx, 600, 26, SANS); ctx.fillStyle = K.ink2; ctx.textAlign = 'right'; ctx.fillText('Câmara, 2000 a 2002', x + maxW, y + 30); ctx.textAlign = 'left';
  y += 40 + (story ? 52 : 38);

  // rodapé: QR, chamada, endereço e fonte
  const qrS = story ? 220 : 180;
  setFont(ctx, 400, story ? 25 : 23, SANS); const disc = wrap(ctx, SOURCE, maxW, 4); const discLh = story ? 33 : 30;
  const footTop = bottom - P - disc.length * discLh - 24 - qrS;
  ctx.strokeStyle = K.line; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x, footTop - 30); ctx.lineTo(x + maxW, footTop - 30); ctx.stroke();
  await drawQR(ctx, d.url, x - 8, footTop, qrS);
  const cx = x + qrS + 26, cw = maxW - qrS - 26;
  setFont(ctx, 700, story ? 38 : 33, SANS); ctx.fillStyle = K.ink;
  const call = wrap(ctx, 'Veja os documentos, com o trecho marcado', cw, 2);
  let cy = footTop + (story ? 50 : 44); call.forEach(l => { ctx.fillText(l, cx, cy); cy += story ? 46 : 40; });
  let hs = story ? 32 : 28; const host = d.host || location.host;
  do { setFont(ctx, 700, hs, SANS); hs -= 1; } while (ctx.measureText(host).width > cw && hs > 16);
  ctx.fillStyle = K.link; ctx.fillText(host, cx, cy + 6); cy += story ? 46 : 40;
  setFont(ctx, 400, story ? 25 : 23, SANS); ctx.fillStyle = K.ink2; ctx.fillText('Aponte a câmera do celular para o código.', cx, cy + 4);
  setFont(ctx, 400, story ? 25 : 23, SANS); ctx.fillStyle = K.ink2;
  disc.forEach((l, i) => ctx.fillText(l, x, footTop + qrS + 24 + 22 + i * discLh));

  const limit = footTop - 60;
  setFont(ctx, 600, story ? 30 : 27, SANS); ctx.fillStyle = K.ink2; ctx.fillText(kicker(d), x, y + 26); y += story ? 60 : 50;
  const T = fitTitle(ctx, titleOf(d), maxW, story ? [72, 64, 58, 52, 48] : [62, 56, 50, 46], story ? 4 : 3);
  const tlh = Math.round(T.size * 1.16);
  setFont(ctx, 700, T.size, SERIF); markedTitle(ctx, T.lines, x, y + T.size * 0.82, T.size, tlh);
  y += T.lines.length * tlh + (story ? 30 : 22);

  const tsize = story ? 33 : 29, lh = Math.round(tsize * 1.38);
  const exMin = d.excerpt ? (story ? 300 : 210) : 0, pesoH = story ? 78 : 64;
  if (d.text) {
    setFont(ctx, 400, tsize, SANS); const room = Math.floor((limit - y - exMin - pesoH - (d.excerpt ? 30 : 0)) / lh);
    const L = wrap(ctx, d.text, maxW, Math.max(2, Math.min(story ? 8 : 5, room)));
    ctx.fillStyle = K.ink; L.forEach((l, i) => ctx.fillText(l, x, y + tsize + i * lh)); y += L.length * lh + (story ? 30 : 22);
  }
  if (d.label) {
    const p = pill(ctx, d.label, x, y, story ? 26 : 24);
    setFont(ctx, 600, story ? 26 : 24, SANS); ctx.fillStyle = K.ink2;
    const L = wrap(ctx, baseText(d), maxW - p.w - 16, 2);
    L.forEach((l, i) => ctx.fillText(l, x + p.w + 16, y + p.h * 0.7 + i * (story ? 32 : 30)));
    y += pesoH + (L.length > 1 ? (story ? 26 : 24) : 0);
  }
  if (d.excerpt && limit - y > 140) await drawExcerpt(ctx, d, x, y, maxW, limit - y, story ? 24 : 22, true);
}

/* ---------- prévia de link (WhatsApp, Facebook, X...) ---------- */
async function layoutOG(ctx, d, W, H) {
  ctx.fillStyle = K.sheet; rr(ctx, 26, 26, W - 52, H - 52, 22); ctx.fill();
  const x = 64, maxW = W - 128; let y = 58;
  brand(ctx, x, y, 34);
  const host = d.host || location.host; setFont(ctx, 700, 24, SANS); ctx.fillStyle = K.link; ctx.textAlign = 'right'; ctx.fillText(host, x + maxW, y + 26); ctx.textAlign = 'left';
  y += 34 + 30;
  if (d.label && d.kind !== 'pagina') {
    const p = pill(ctx, d.label, x, y, 22);
    setFont(ctx, 600, 24, SANS); ctx.fillStyle = K.ink2;
    ctx.fillText(wrap(ctx, d.kind === 'resposta' ? 'Se alguém disser:' : (d.curto || PESO_CURTO[d.label] || ''), maxW - p.w - 14, 1)[0], x + p.w + 14, y + p.h * 0.7);
    y += p.h + 18;
  } else {
    setFont(ctx, 600, 25, SANS); ctx.fillStyle = K.ink2; ctx.fillText(kicker(d), x, y + 22); y += 44;
  }
  const hasEx = !!d.excerpt;
  const T = fitTitle(ctx, titleOf(d), maxW, hasEx ? [54, 48, 44, 40] : [64, 58, 52, 46], hasEx ? 2 : 3);
  const tlh = Math.round(T.size * 1.15);
  setFont(ctx, 700, T.size, SERIF); markedTitle(ctx, T.lines, x, y + T.size * 0.82, T.size, tlh);
  y += T.lines.length * tlh + 18;
  if (hasEx) {
    await drawExcerpt(ctx, { ...d, curto: d.kind === 'doc' ? '' : d.curto }, x, y, maxW, H - 56 - y, 20);
  } else if (d.text) {
    setFont(ctx, 400, 30, SANS); ctx.fillStyle = K.ink2;
    const L = wrap(ctx, d.text, maxW, 4); L.forEach((l, i) => ctx.fillText(l, x, y + 30 + i * 41));
  }
}

export async function renderCard(d, fmt = 'story') {
  await loadFonts();
  const [W, H] = FORMATS[fmt];
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = K.ink; ctx.fillRect(0, 0, W, H);
  if (fmt === 'og') await layoutOG(ctx, d, W, H); else await layoutTall(ctx, d, W, H, fmt === 'story');
  return cv;
}
