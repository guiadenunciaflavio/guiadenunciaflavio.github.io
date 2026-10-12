# Guia da denúncia — como publicar

Pasta pronta, 100% estática (HTML + JS + PDF em 12 partes de ~25 páginas). Sem cookies, sem rastreadores, sem chamadas externas.

## Testar no seu computador
    cd guia && python3 -m http.server 8000     # abra http://localhost:8000
(Não abre direto por duplo clique: o navegador bloqueia o carregamento local.)

## Publicar sem expor seu nome
1. Crie um e-mail novo só para isso (sem seu nome).
2. Cloudflare Pages (ou Netlify / GitHub Pages) com esse e-mail: "Upload assets" e arraste a pasta `guia`. Limite do Cloudflare: 25 MiB por arquivo (maior parte aqui tem 2–5 MB).
3. Link bonito: compre um domínio com privacidade de WHOIS ligada (o registro .com/.org costuma oferecer). Domínios .br exigem CPF/CNPJ no registro; prefira .com/.org.
4. Pague com um meio que não exponha seu nome publicamente, se isso importar para você.
5. Tire os metadados de qualquer arquivo novo que acrescentar (o PDF já está limpo).

## Revisão antes de publicar (importante)
- O PDF teve tarjados CPF, RG, telefones, endereços residenciais, números de contas/agências, IMEIs, números de série de celulares e nome da escola. Foram três passadas: OCR da página inteira, uma busca por números lidos com letras trocadas (ex.: "D6410922868", "TEF7816.00698-0") e OCR em 300 dpi das imagens com números (tabelas e prints). O OCR não é perfeito: antes de divulgar, vale olhar com zoom as tabelas em imagem, principalmente pp. 20–24, 36–44, 75, 111–151, 168–253, 266 e 271.
- Os "Fatos extras" e o "Desfecho" vêm de reportagens com link. Confira as datas antes de divulgar.
- Uma revisão rápida de advogado(a) é recomendável: o texto usa "segundo a denúncia" e nunca afirma culpa.

## Estrutura
- `index.html`, `assets/` (CSS/JS), `vendor/` (PDF.js local)
- `data/content.json` (todo o conteúdo editorial), `data/search.json`, `data/boxes/` (busca e destaque)
- `pdf/` (documento em partes)

## Tutorial "Como usar"
- `assets/tour.js` (o mesmo arquivo nos três guias) destaca cada parte do guia e explica para que serve: busca, mapa das páginas, etiquetas, Entenda, temas, o documento aberto com o trecho marcado, Roteiro de Tudo, "+ Argumento", Compartilhar e o menu.
- Abre sozinho na primeira visita. Quem chega por um link de ponto, tema ou página (`#a=`, `#tema=`, `#p=`, `#d=`) vê só um convite no canto, para não tapar o que veio ver.
- Depois abre por "Como usar" (no início da página, no menu e no rodapé) ou pelo endereço `#como-usar`.
- Guarda no navegador só que o tutorial já foi visto (`guia.tour.denuncia`, `guia.tour.suspeicao` ou `guia.tour.cargo`). O texto de cada guia fica no objeto `TXT`, conforme `<body data-guia>`.

## Compartilhar
- Cada ponto do Roteiro e da Cronologia tem "+ Argumento" e "Compartilhar". Cada tema tem "Compartilhar tema". No visualizador, "Compartilhar" envia o ponto do passo a passo ou, fora dele, a página aberta.
- "Meu argumento" (canto inferior esquerdo) junta pontos: dá para ordenar, dar título e compartilhar.
- O painel "Compartilhar" tem botões para WhatsApp, Telegram, X, Facebook, Threads, Bluesky, LinkedIn, Reddit e e-mail, além de copiar link ou texto e, no celular, "Outros apps".
- Os textos e imagens seguem a voz da denúncia: "Segundo a denúncia do MPRJ", o que ela diz, a base de cada ponto (fato documentado, acusação do MP ou leitura que liga os fatos) e as páginas. Em temas e argumentos, os pontos vêm numerados como passos, com a linha "Base: N fatos documentados e N acusações do MP".
- Instagram e TikTok não aceitam links vindos de sites. Para essas redes, o painel cria uma imagem (Stories 9:16 ou Feed 4:5) com o ponto, o recorte da página com o trecho marcado e um QR code com o link. No celular, "Enviar imagem" abre o app; o link fica copiado para o adesivo de link do Stories.

### Endereços
- `/ponto/ID/` e `/tema/ID/`: páginas pequenas com prévia própria (título, texto e imagem) para WhatsApp, Facebook, X etc. Elas redirecionam para `/#a=ID` e `/#tema=ID`.
- `/#a=id1.id2&t=Título`: argumento montado à mão (a prévia é a geral do guia, porque o site é estático).
- `/#p=N`: página do documento.
- `#como-usar`: abre o tutorial.
- Os pontos da Cronologia usam ids `cr-NN` pela ordem atual. Se a ordem da cronologia mudar, links antigos apontam para outros pontos.

### Regerar as prévias
Depois de mudar `data/content.json`, rode `python3 ferramentas/gerar_previas.py` dentro da pasta do site (precisa de Python com Playwright e Chromium). Ele recria `og/`, `ponto/` e `tema/`. As imagens usam o domínio fixo `guiadenunciaflavio.github.io`; se trocar o domínio, altere `SITE` no script e as tags `og:` do `index.html`.

### Licenças
Fontes Source Serif 4 e Source Sans 3 (SIL Open Font License, em `vendor/fonts/`), gerador de QR code de Kazuhiko Arase (MIT, `vendor/qrcode.mjs`).
