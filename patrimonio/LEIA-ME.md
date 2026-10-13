# Flávio e Lula, conta por conta

Página estática que compara as contas do patrimônio de Flávio Bolsonaro e de Lula: o que cada um ganhou de 2003 a 2026, o que declarou à Justiça Eleitoral em cada eleição (de 2002 a 2026) e onde a conta não fecha. Usa o mesmo método e as mesmas premissas para os dois, só com dados públicos, e traz a fonte de cada número. Sem cookies, sem rastreadores, sem chamadas externas.

## O que tem
- `index.html`: a comparação. Gráfico do patrimônio declarado, tabela "lado a lado", trajetória dos dois ano a ano, os picos que pedem explicação, o que a Justiça decidiu, o que pode explicar as diferenças, a pergunta final (etiqueta `interpretação`), compartilhar (inclusive o post pronto para o Instagram, em `../compartilhar/`) com QR code, o bloco "Divulgue também" e as fontes.
- `flavio/` e `lula/`: as duas contas completas, interativas (cenários de gastos e de rendimento, ganhos e saídas documentados), com um link de volta para a comparação.
- `og.jpg`: prévia de link. `../inicio/patrimonio.jpg`: imagem do cartão na página inicial.

## Etiquetas
- documentado: está em documento (declaração ao TSE, decisão, extrato citado na denúncia).
- alegado: acusação de uma das partes (Ministério Público, MPF).
- reportagem: apurado pela imprensa, com link.
- estimado: conta desta página, com premissas à vista.
- interpretação: leitura nossa (só a pergunta final).

## Atualizar
1. As contas completas são montadas a partir de `modelo.py` e `modelo_lula.py` (cópias nesta pasta `ferramentas/`) e dos modelos de página, fora do site.
2. `python3 -I ferramentas/montar.py PASTA_DAS_CONTAS` recria `index.html`, `flavio/` e `lula/`. Os números da comparação saem dos mesmos modelos, no cenário padrão das contas (gastos documentados ou estimados, dinheiro guardado rendendo a inflação).
3. `python3 -I ferramentas/previa.py PASTA_DAS_CONTAS` recria `og.jpg` e `../inicio/patrimonio.jpg` (Playwright com Chromium).

## Licenças
Gerador de QR code de Kazuhiko Arase (MIT, `vendor/qrcode.mjs`).
