# Guia da suspeição: como funciona e como publicar

Guia de leitura do acórdão do STF no Habeas Corpus 164.493 (Segunda Turma, março de 2021), que declarou Sergio Moro parcial no caso do triplex de Lula, e de duas decisões ligadas a ele: a de Fachin no HC 193.726 (8/3/2021), que anulou as condenações de Curitiba, e a do Comitê de Direitos Humanos da ONU (2022, tradução não oficial). Pasta 100% estática (HTML, JS e os PDFs em partes). Sem cookies, sem rastreadores, sem chamadas externas.

## Testar no computador
    python3 -m http.server 8000     # dentro desta pasta; abra http://localhost:8000
(Não abre por duplo clique: o navegador bloqueia o carregamento local.)

## Os documentos
- `pdf/d01.pdf` a `pdf/d18.pdf`: acórdão (441 pp.). Os números de telefone citados nos votos (pp. 162, 163, 176, 237, 355 e 356) foram cobertos, com o texto removido do PDF.
- `pdf/fachin-1.pdf` e `pdf/fachin-2.pdf`: decisão de Fachin (46 pp.). Um endereço residencial na p. 44 foi coberto.
- `pdf/onu-1.pdf`: decisão do Comitê da ONU (27 pp.), tradução do Núcleo de Direitos Humanos da Unisinos. O e-mail pessoal da tradutora, na p. 1, foi coberto. O original em inglês é o documento CCPR/C/134/D/2841/2016.
- Os metadados dos arquivos foram apagados.
- Os "Fatos extras" e o "Desfecho" não vêm do acórdão, e sim de reportagens, sempre com link.

## Etiquetas
- documentado: registrado no documento (decisão, voto de ministro, conclusão do Comitê ou ato do processo), com data e página.
- alegado: o que um ministro, um membro do Comitê, uma das partes ou as mensagens hackeadas afirmam, sem ser a decisão.
- interpretação: leitura que liga fatos (hoje nenhum ponto usa).

## Tutorial "Como usar"
- `assets/tour.js` (o mesmo arquivo nos três guias) destaca cada parte do guia e explica para que serve: busca, mapa das páginas, etiquetas, Entenda, temas, o documento aberto com o trecho marcado, Roteiro de Tudo, "+ Argumento", Compartilhar e o menu.
- Abre sozinho na primeira visita. Quem chega por um link de ponto, tema ou página (`#a=`, `#tema=`, `#p=`, `#d=`) vê só um convite no canto, para não tapar o que veio ver.
- Depois abre por "Como usar" (no início da página, no menu e no rodapé) ou pelo endereço `#como-usar`.
- Guarda no navegador só que o tutorial já foi visto (`guia.tour.denuncia`, `guia.tour.suspeicao` ou `guia.tour.cargo`). O texto de cada guia fica no objeto `TXT`, conforme `<body data-guia>`.

## Compartilhar
- "Postar no Instagram" (no topo e no painel "Compartilhar") abre o post pronto do guia, em Feed ou Stories, com legenda. Os posts ficam em `../compartilhar/`.
- Cada ponto tem "+ Argumento" e "Compartilhar"; cada tema tem "Compartilhar tema"; no visualizador, "Compartilhar" envia o ponto aberto ou a página.
- Os textos seguem a voz do documento de cada ponto ("Segundo o acórdão do STF que declarou Moro parcial", "Segundo a decisão do ministro Edson Fachin…", "Segundo a decisão do Comitê de Direitos Humanos da ONU…"), com o peso de cada ponto e as páginas, e terminam com a linha "Base: N fatos registrados no acórdão e N afirmações de ministros ou das mensagens".
- Temas longos compartilham só os pontos principais (por exemplo, os sete fatos) e o link abre o tema inteiro.
- Para Instagram e TikTok, o painel cria uma imagem (Stories 9:16 ou Feed 4:5) com o ponto, o recorte da página com o trecho marcado e um QR code com o link.

### Endereços
- `ponto/ID/` e `tema/ID/`: páginas com prévia própria para WhatsApp, Facebook, X etc.; redirecionam para `#a=ID` e `#tema=ID`.
- `#a=id1.id2&t=Título`: argumento montado à mão. `#p=N`: página do acórdão. `#d=fachin&p=N` e `#d=onu&p=N`: páginas das outras decisões.
- `#como-usar`: abre o tutorial.

### Regerar as prévias
Depois de mudar `data/content.json`, rode `python3 ferramentas/gerar_previas.py https://ENDEREÇO-DO-SITE/` (Python com Playwright e Chromium). Ele recria `og/`, `ponto/` e `tema/` e atualiza as tags `og:` do `index.html`.

### Licenças
PDF.js (Apache 2.0, `vendor/`), fontes Source Serif 4 e Source Sans 3 (SIL Open Font License, `vendor/fonts/`), gerador de QR code de Kazuhiko Arase (MIT, `vendor/qrcode.mjs`).
