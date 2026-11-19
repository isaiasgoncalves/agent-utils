# Ingestão de QUALQUER conteúdo (roteamento por tipo)

Leia na Etapa 1. O objetivo é transformar qualquer entrada do usuário numa
**síntese técnica fiel** (`1_sintese.md`) — a fonte de verdade do vídeo. Primeiro
identifique o TIPO de entrada e o ESCOPO; depois extraia o conteúdo com a
ferramenta certa; só então sintetize.

## Passo A — Identifique tipo e escopo (antes de extrair)
Olhe o que o usuário mandou e classifique. Se o escopo for grande ou ambíguo,
**pergunte antes de gerar** (evita produzir o vídeo errado):
- Fonte enorme (livro inteiro, vários papers, curso): pergunte se ele quer **um
  vídeo único da tese/ideia central** ou **uma série** (um vídeo por capítulo/tema).
- Tópico amplo ("explique machine learning"): proponha um recorte concreto e
  confirme o foco e o nível (introdutório vs avançado).
- Vários arquivos: confirme se é um só vídeo integrando tudo ou um por arquivo.
Quando o escopo já estiver claro no pedido, não pergunte — siga.

## Passo B — Extraia o conteúdo conforme o tipo

| Tipo de entrada | Como extrair |
|---|---|
| **Texto colado / notas** | Use direto como fonte. |
| **Tópico/conceito sem fonte** | Use seu conhecimento. Se for nicho, recente ou você tiver baixa confiança, faça `WebSearch`/`WebFetch` para fundamentar — fidelidade exige base, não memória vaga. |
| **PDF (paper, capítulo)** | `Read` com `pages` para PDFs grandes (leia em blocos). Anote figuras-chave: viram analogias visuais. |
| **PDF escaneado / sem texto** | Use a skill **`pdf`** (OCR) para extrair o texto antes. |
| **URL / artigo / blog / post** | `WebFetch` na URL. Para páginas longas, foque nas seções centrais. |
| **Aula / vídeo (YouTube etc.)** | `WebFetch` na página para pegar a transcrição/descrição; se não houver transcrição acessível, peça ao usuário o texto ou os pontos principais. |
| **.docx (Word)** | Use a skill **`docx`** para ler/extrair o texto. |
| **.pptx (slides)** | Use a skill **`pptx`** para extrair texto e notas dos slides. |
| **.xlsx / .csv (planilha/dados)** | Use a skill **`xlsx`** para entender os dados. Aqui o "vídeo" costuma explicar o que os dados mostram — gráficos animados (`Axes`) são o núcleo. |
| **Imagem (diagrama, figura, foto de quadro/anotação)** | Abra com `Read` (visão) e descreva/extraia o conteúdo técnico que ela representa. |
| **Áudio / mídia sem transcrição** | Não há transcritor embutido garantido; peça a transcrição ou um resumo em texto ao usuário. |

Combinações são comuns (ex.: um PDF + um pedido de foco). Trate o pedido do
usuário como o recorte e o arquivo como a fonte.

## Passo C — Sintetize (igual para todos os tipos)
Produza `1_sintese.md` (~1 página) com: fenômeno/tese central; setup e definições
(cada símbolo definido na 1ª aparição); resultado/mecanismo principal;
evidências/exemplos; e as figuras/exemplos concretos que darão boas analogias.
Mantenha **fidelidade**: não invente; onde simplificar, sinalize. Se a fonte for
longa, sintetize por partes e depois unifique o "fio condutor".

## Regra de ouro
Independentemente do tipo de entrada, a partir da Etapa 2 o fluxo é o MESMO
(roteiro → Manim → render → narração → montagem). A ingestão é o único ponto que
varia por modalidade; tudo converge para `1_sintese.md`.
