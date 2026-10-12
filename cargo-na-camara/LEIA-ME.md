# Guia do cargo na Câmara: como funciona e como publicar

Guia de leitura dos documentos públicos sobre o cargo de assistente técnico de gabinete que Flávio Bolsonaro ocupou na liderança do PPB na Câmara dos Deputados, de dezembro de 2000 a junho de 2002, enquanto o próprio currículo dele o coloca no Rio, na faculdade e num estágio. Funciona como os guias da denúncia e da suspeição: os documentos ficam no site, cada ponto abre a página com o trecho marcado, e há busca, temas, Roteiro de Tudo, "+ Argumento", compartilhar e o tutorial "Como usar". Pasta 100% estática. Sem cookies, sem rastreadores, sem chamadas externas.

## Testar no computador
    python3 -m http.server 8000     # dentro desta pasta; abra http://localhost:8000
(Não abre por duplo clique: o navegador bloqueia o carregamento local.)

## Os documentos (`pdf/`, 70 páginas)
- `b2000.pdf`: Boletim Administrativo da Câmara nº 246, de 27/12/2000 (pp. 3373 a 3398). Na p. 3380, a exoneração de Ana Cristina Siqueira Valle; na p. 3384, a nomeação de Flávio, as duas com data de 14/12/2000. É o documento principal (`#p=N`).
- `b1998.pdf`: Boletim nº 215, de 13/11/1998 (pp. 3197 a 3203). Na p. 3197, a nomeação de Ana Cristina.
- `b2002.pdf`: Boletim nº 145, de 31/7/2002 (pp. 1877 a 1890). Na p. 1879, a exoneração de Flávio, a pedido, a partir de 28/6/2002.
- `ato.pdf`: capa e pp. 69 a 81 do suplemento do Diário da Câmara de 6/11/1996, com o Ato da Mesa nº 45, de 1996 (as tarefas de cada cargo em comissão; as do cargo de Flávio estão na p. 75). Páginas escaneadas: o texto da busca vem de OCR.
- `alerj.pdf`: perfil de Flávio no site da Alerj, cópia do Wayback Machine de 30/1/2019. Os contatos do gabinete (telefone, e-mail e endereço) foram cobertos, com o texto removido do arquivo, e os links foram tirados.
- `senado.pdf`: texto da Agência Senado de 18/1/2019, cópia do Wayback Machine de 3/2/2019 (reprodução autorizada com citação).
- `diplomas.pdf`: os três diplomas que Flávio publicou no X em 12/8/2026 (Direito, especialização em Políticas Públicas e MBA). Texto da busca por OCR.

Os boletins são os arquivos do site da Câmara, sem nenhuma alteração. Nos outros, os metadados foram apagados. A reportagem da BBC News Brasil (23/1/2019) não está hospedada: o que vem dela fica em "Fatos extras", com link.

## Etiquetas
- documentado: está num dos documentos do guia, com a página.
- reportagem: apurado por um veículo de imprensa (BBC News Brasil, Band, Poder360), com link. Só aparece na cronologia, em "Fatos extras" e em "Depois do cargo".
- interpretação: leitura que liga os fatos. É o único lugar em que o guia fala em "funcionário fantasma".

## Estrutura
- `index.html`, `assets/app.js`, `assets/app.css`: a página e o visualizador (mesma base dos outros guias).
- `assets/card.js`: imagens e textos de compartilhamento. `assets/tour.js`: tutorial, o mesmo arquivo nos três guias.
- `data/content.json`: todos os textos e os trechos marcados, gerado por `ferramentas/montar_conteudo.py`. Não edite à mão.
- `data/chunks.json`, `data/search.json`, `data/paginas.json` e `data/boxes/DOC/pNNN.json`: gerados por `ferramentas/preparar_documentos.py` (palavras com as caixas, usadas na busca e no marca-texto).
- `ponto/ID/` e `tema/ID/`: páginas com prévia própria para WhatsApp, Facebook, X etc.; redirecionam para `#a=ID` e `#tema=ID`. `og/`: as imagens dessas prévias.
- `p/ID/`: endereços da primeira versão desta página. Levam ao ponto novo equivalente (ou à seção) com a mesma prévia.

## Atualizar
1. Documentos (só se mudar um): `TESSDATA_PREFIX=PASTA_DO_por.traineddata python3 -I ferramentas/preparar_documentos.py PASTA_DAS_FONTES`. A pasta das fontes não fica no site.
2. Textos e trechos: edite `ferramentas/montar_conteudo.py` e rode `python3 -I ferramentas/montar_conteudo.py`. Cada trecho é achado pelas palavras da página (da primeira à última) ou, nas páginas escaneadas, pelas faixas de altura das linhas.
3. Prévias: `python3 ferramentas/gerar_previas.py https://ENDEREÇO-DO-SITE/cargo-na-camara/` (Python com Playwright e Chromium). Recria `og/`, `ponto/`, `tema/` e `p/` e atualiza as tags `og:` do `index.html`.

## Endereços
- `#p=N`: página N do boletim de 2000 (na ordem do PDF; o número impresso aparece no visualizador). `#d=DOC&p=N`: página de outro documento (`b1998`, `b2002`, `ato`, `alerj`, `senado`, `diplomas`).
- `#a=id1.id2&t=Título`: argumento montado à mão. `#tema=ID`: tema. `#como-usar`: tutorial.

## Licenças
PDF.js (Apache 2.0, `vendor/`), fontes Source Serif 4 e Source Sans 3 (SIL Open Font License, `vendor/fonts/`), gerador de QR code de Kazuhiko Arase (MIT, `vendor/qrcode.mjs`).
