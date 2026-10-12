# O cargo de Flávio na Câmara

Página curta, estática, sobre o cargo de assistente técnico de gabinete que Flávio Bolsonaro ocupou na liderança do PPB na Câmara dos Deputados, de dezembro de 2000 a junho de 2002, enquanto o próprio currículo dele o coloca no Rio, na faculdade e num estágio. Sem cookies, sem rastreadores, sem chamadas externas.

## O que tem na página
- **Três atividades, duas cidades**: as datas do cargo, da faculdade e do estágio lado a lado.
- **Em um minuto**: os pontos principais, cada um com etiqueta e o documento que o sustenta.
- **Uma semana**: o que as fontes dizem sobre a rotina da época, sem inventar horários.
- **Os documentos**: recortes com o trecho marcado em amarelo, a fonte, o link para o original e a transcrição. Toque para ampliar.
- **Se alguém disser…**: respostas curtas para copiar ou compartilhar.
- Linha do tempo, o que dizem os citados e a lista de fontes.

## Etiquetas
- `documentado`: está num documento público, mostrado na página e com link.
- `reportagem`: apurado pela BBC News Brasil (23/1/2019) com documentos que não são públicos, como a declaração de Imposto de Renda e a resposta da Câmara pela Lei de Acesso à Informação, ou com entrevistas.
- `interpretação`: leitura que liga os fatos. É o único lugar em que a página fala em “funcionário fantasma”.

## Documentos
- Boletim Administrativo da Câmara nº 215, de 13/11/1998, p. 3197: nomeação de Ana Cristina Siqueira Valle.
- Boletim Administrativo da Câmara nº 246, de 27/12/2000, pp. 3380 e 3384: exoneração dela e nomeação de Flávio, na mesma data (14/12/2000).
- Diário da Câmara, suplemento de 6/11/1996, pp. 69, 75 e 80: Ato da Mesa nº 45, de 1996, com as atribuições do cargo.
- Perfil de Flávio na Alerj, cópia do Wayback Machine de 30/1/2019.
- Diploma de Direito publicado por Flávio no X em 12/8/2026.
- Texto da Agência Senado de 18/1/2019, cópia do Wayback Machine de 3/2/2019.

A saída dele do cargo (junho de 2002, a pedido) ainda vem da reportagem da BBC: o ato não está nos boletins de junho de 2002 e deve ter saído nos de julho.

`fontes/` guarda cópias dos dois boletins, como saem do site da Câmara, e das quatro páginas do Diário (sem metadados). As cópias do Wayback Machine e o diploma aparecem só em recortes.

## Estrutura
- `index.html`: gerado por `ferramentas/montar.py`. Não edite à mão.
- `data/conteudo.json`: todos os textos (resumo, documentos, respostas, linha do tempo, citações, fontes).
- `data/docs.json` e `docs/*.webp`: recortes e retângulos do marca-texto, gerados por `ferramentas/recortes.py`.
- `p/ID/`: páginas pequenas com prévia própria (título, texto e imagem) para WhatsApp, Facebook, X etc. Levam a `../../#ID`.
- `og/`: imagens de prévia, desenhadas por `assets/card.js`.
- `assets/page.css`, `assets/page.js`, `assets/card.js`; `vendor/` tem as fontes e o gerador de QR code (as mesmas licenças dos guias).

## Atualizar
1. Textos: edite `data/conteudo.json` e rode `python3 -I ferramentas/montar.py`.
2. Recortes (só se mudar um documento): `python3 -I ferramentas/recortes.py PASTA_DAS_FONTES`, depois `montar.py`. A pasta das fontes não fica no site.
3. Prévias: `python3 ferramentas/gerar_previas.py` (precisa de Playwright com Chromium).

## Endereços
- `#ID` abre a página no ponto, documento ou resposta e pisca o trecho marcado (por exemplo, `#nomeacao`, `#atribuicoes`, `#se-trabalhava-do-rio`).
- `p/ID/` é o link usado ao compartilhar, com prévia própria.
