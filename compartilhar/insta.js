// Janela "Postar no Instagram": o post pronto de cada página, em Feed ou Stories,
// com a legenda. Qualquer link ou botão com data-insta="CHAVE" abre a janela
// (CHAVE: denuncia, suspeicao, cargo ou patrimonio; textos em posts.json).
// Sem JavaScript, o link leva direto à imagem do Feed.

const BASE = new URL('./', import.meta.url);
const CENSURA = 'https://censuradigital.lula.com.br/';

let dados = null;
let dlg = null;
let gatilho = null;
const est = { chave: null, fmt: 'feed', arquivo: null, vez: 0 };

const podeEnviar = (() => {
  try {
    return !!(navigator.canShare && navigator.canShare({ files: [new File(['x'], 'x.jpg', { type: 'image/jpeg' })] }));
  } catch (e) { return false; }
})();

const COMO = {
  feed: podeEnviar ? [
    'Toque em <b>Enviar</b> e escolha Instagram e depois Feed. A legenda vai copiada: cole no campo da legenda.',
    'No Instagram, link na legenda não abre. Por isso o endereço está na imagem; se puder, ponha o link também na sua bio.',
  ] : [
    'Baixe a imagem e copie a legenda.',
    'Publique pelo app do Instagram, ou pelo instagram.com no computador, e cole a legenda.',
    'No Instagram, link na legenda não abre. Por isso o endereço está na imagem; se puder, ponha o link também na sua bio.',
  ],
  stories: podeEnviar ? [
    'Toque em <b>Enviar</b> e escolha Instagram e depois Stories. O link da página vai copiado.',
    'No Stories, toque no ícone de figurinhas, escolha <b>Link</b> e cole. Ponha a figurinha no espaço livre embaixo do quadro branco.',
  ] : [
    'Baixe a imagem e mande para o celular: Stories só se publicam pelo app do Instagram.',
    'Copie o link. No Stories, toque no ícone de figurinhas, escolha <b>Link</b> e cole. Ponha a figurinha no espaço livre embaixo do quadro branco.',
  ],
};

async function carregar() {
  if (!dados) {
    const r = await fetch(new URL('posts.json', BASE));
    if (!r.ok) throw new Error('posts.json: ' + r.status);
    dados = await r.json();
  }
  return dados;
}

function q(sel) { return dlg.querySelector(sel); }

function montar() {
  dlg = document.createElement('dialog');
  dlg.className = 'igd';
  dlg.setAttribute('aria-labelledby', 'igd-t');
  dlg.innerHTML = `
<div class="igd-in">
  <div class="igd-head"><h2 id="igd-t">Postar no Instagram</h2><button type="button" class="igd-x">Fechar</button></div>
  <p class="igd-sub" id="igd-sub"></p>
  <div class="igd-fmt" role="group" aria-label="Formato do post">
    <button type="button" data-fmt="feed" aria-pressed="true">Feed</button><button type="button" data-fmt="stories" aria-pressed="false">Stories</button>
  </div>
  <div class="igd-grid">
    <figure class="igd-prev"><img alt=""></figure>
    <div>
      <div class="igd-acts">
        <button type="button" class="igd-btn main" data-act="enviar"${podeEnviar ? '' : ' hidden'}>Enviar para o Instagram</button>
        <a class="igd-btn${podeEnviar ? '' : ' main'}" data-act="baixar" href="#" download>Baixar imagem</a>
        <button type="button" class="igd-btn" data-act="copiar">Copiar legenda</button>
      </div>
      <p class="igd-status" role="status" aria-live="polite"></p>
      <ol class="igd-how"></ol>
      <div class="igd-capw">
        <label class="igd-cap-l" for="igd-cap">Legenda (pode editar antes de copiar)</label>
        <textarea class="igd-cap" id="igd-cap" rows="8"></textarea>
      </div>
    </div>
  </div>
  <p class="igd-foot">Se o Instagram derrubar o post ou restringir a sua conta, denuncie no canal da campanha de Lula: <a href="${CENSURA}" target="_blank" rel="noopener noreferrer">censuradigital.lula.com.br</a>.</p>
</div>`;
  document.body.append(dlg);

  q('.igd-x').addEventListener('click', () => dlg.close());
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('close', () => {
    est.vez++;
    if (gatilho && document.contains(gatilho)) gatilho.focus({ preventScroll: true });
  });
  dlg.querySelectorAll('[data-fmt]').forEach(b => b.addEventListener('click', () => {
    if (est.fmt === b.dataset.fmt) return;
    est.fmt = b.dataset.fmt;
    mostrar();
  }));
  q('[data-act="enviar"]').addEventListener('click', enviar);
  q('[data-act="copiar"]').addEventListener('click', async () => {
    const ok = await copiar(textoParaCopiar());
    aviso(ok ? (est.fmt === 'feed' ? 'Legenda copiada.' : 'Link copiado.') : 'Não deu para copiar. Selecione o texto e copie.');
  });
}

function post() { return dados.posts[est.chave]; }

function urlImagem(fmt) {
  return new URL(post()[fmt].img + '?v=' + encodeURIComponent(dados.versao), BASE).href;
}

function textoParaCopiar() {
  return est.fmt === 'feed' ? q('.igd-cap').value : post().url;
}

function aviso(t) { q('.igd-status').textContent = t || ''; }

function mostrar() {
  const p = post();
  const f = p[est.fmt];
  q('#igd-sub').textContent = `Um post pronto sobre ${p.nome}, com o endereço da página.`;
  dlg.querySelectorAll('[data-fmt]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.fmt === est.fmt)));
  const img = q('.igd-prev img');
  img.width = f.w; img.height = f.h;
  img.src = urlImagem(est.fmt);
  img.alt = f.alt;
  const baixar = q('[data-act="baixar"]');
  baixar.href = img.src;
  baixar.download = `guias-de-leitura-${est.chave}-${est.fmt}.jpg`;
  q('[data-act="copiar"]').textContent = est.fmt === 'feed' ? 'Copiar legenda' : 'Copiar link';
  q('.igd-capw').hidden = est.fmt !== 'feed';
  q('.igd-how').innerHTML = COMO[est.fmt].map(t => `<li>${t}</li>`).join('');
  aviso('');
  prepararArquivo();
}

// Baixa a imagem antes do toque em "Enviar": o compartilhamento precisa
// começar no mesmo toque, sem esperar a rede.
async function prepararArquivo() {
  est.arquivo = null;
  if (!podeEnviar) return;
  const vez = ++est.vez;
  const b = q('[data-act="enviar"]');
  b.disabled = true;
  try {
    const r = await fetch(urlImagem(est.fmt));
    if (!r.ok) throw new Error(String(r.status));
    const blob = await r.blob();
    if (vez !== est.vez) return;
    est.arquivo = new File([blob], `guias-de-leitura-${est.chave}-${est.fmt}.jpg`, { type: 'image/jpeg' });
    b.disabled = false;
  } catch (e) {
    if (vez !== est.vez) return;
    b.hidden = true;
    aviso('Não deu para preparar o envio. Use “Baixar imagem”.');
  }
}

function enviar() {
  if (!est.arquivo) return;
  const feed = est.fmt === 'feed';
  copiar(textoParaCopiar()).then(ok => {
    if (ok) aviso(feed ? 'Legenda copiada. Cole no Instagram.' : 'Link copiado. Cole na figurinha Link.');
  });
  navigator.share({ files: [est.arquivo] }).catch(e => {
    if (e && e.name === 'AbortError') return;
    aviso('O celular não abriu o compartilhamento. Use “Baixar imagem” e poste pelo Instagram.');
  });
}

async function copiar(texto) {
  try {
    await navigator.clipboard.writeText(texto);
    return true;
  } catch (e) { /* segue para o modo antigo */ }
  const ta = document.createElement('textarea');
  ta.value = texto;
  ta.setAttribute('readonly', '');
  ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
  (dlg || document.body).append(ta);
  ta.select();
  let ok = false;
  try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
  ta.remove();
  return ok;
}

async function abrir(chave, origem) {
  try {
    await carregar();
  } catch (e) {
    if (origem && origem.href) location.href = origem.href;
    return;
  }
  if (!dados.posts[chave]) return;
  if (!dlg) montar();
  const nova = est.chave !== chave;
  est.chave = chave;
  if (nova) q('.igd-cap').value = post().legenda;
  gatilho = origem;
  mostrar();
  if (!dlg.open) dlg.showModal();
}

document.addEventListener('click', e => {
  const b = e.target.closest && e.target.closest('[data-insta]');
  if (!b || e.defaultPrevented || e.button > 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  e.preventDefault();
  const aberta = b.closest('dialog[open]');
  if (aberta && aberta !== dlg) aberta.close();
  abrir(b.dataset.insta, b);
});
