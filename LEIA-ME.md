# Guias de leitura

Site estático com guias de leitura de documentos públicos. Sem cookies, sem rastreadores, sem chamadas externas.

- `index.html`: página inicial, para escolher o guia. Imagens em `inicio/`.
- `denuncia/`: guia da denúncia do MPRJ contra Flávio Bolsonaro e mais 16 pessoas (caso das rachadinhas, outubro de 2020). Detalhes em `denuncia/LEIA-ME.md`.
- `suspeicao/`: guia do acórdão do STF que declarou Sergio Moro parcial no caso de Lula (HC 164.493), com a decisão de Fachin no HC 193.726 e a do Comitê de Direitos Humanos da ONU. Detalhes em `suspeicao/LEIA-ME.md`.
- `cargo-na-camara/`: página curta sobre o cargo de Flávio Bolsonaro na Câmara (2000–2002), com os atos da Câmara, o currículo dele na Alerj, o diploma e respostas prontas. Detalhes em `cargo-na-camara/LEIA-ME.md`.
- `ponto/` e `tema/`: endereços antigos do guia da denúncia, de quando ele ficava na raiz. Mostram a mesma prévia e levam ao endereço novo em `denuncia/`. A página inicial também leva os links antigos `#a=`, `#tema=` e `#p=` para `denuncia/`.

Os dois guias têm um tutorial "Como usar", que abre sozinho na primeira visita e depois pelo botão "Como usar" ou pelo endereço `#como-usar` (por exemplo, `denuncia/#como-usar`). A página inicial resume as funções e leva aos dois tutoriais.

## Testar no computador
    python3 -m http.server 8000     # nesta pasta; abra http://localhost:8000

## Regerar as prévias
- Guia da denúncia: `python3 denuncia/ferramentas/gerar_previas.py --so-paginas --legado .` recria as páginas de prévia (as novas e as dos endereços antigos) sem refazer as imagens; sem `--so-paginas`, refaz também as imagens.
- Guia da suspeição: `python3 suspeicao/ferramentas/gerar_previas.py https://guiadenunciaflavio.github.io/suspeicao/`.
- Página do cargo: `python3 -I cargo-na-camara/ferramentas/montar.py` e depois `python3 cargo-na-camara/ferramentas/gerar_previas.py`.
