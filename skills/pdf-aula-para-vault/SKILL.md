---
name: pdf-aula-para-vault
description: >-
  Converte PDFs de material de aula (notas do professor, slides/apresentações,
  handouts, listas) em markdown fiel dentro do vault do Obsidian do Isaías,
  preservando fórmulas em LaTeX e extraindo as figuras do próprio PDF. Também
  cria/atualiza um arquivo de "Visão Geral do Conteúdo" que orienta o estudo e
  liga o material no índice da disciplina. Use SEMPRE que o Isaías (ou o
  professor) soltar um ou mais PDFs de aula pra "processar", "transformar em
  markdown", "colocar no vault", "organizar o material da disciplina", "montar
  as notas da aula", ou quando chegar material novo de uma disciplina da FGV —
  mesmo que ele não diga a palavra "skill" nem "markdown". Vale para qualquer
  disciplina (Séries Temporais, Eng. de Software, PLN, etc.), não só uma.
---

# PDF de aula → markdown no vault

Este é o fluxo do **Cláudio** para transformar material bruto do professor (PDF)
em notas navegáveis e fiéis no vault, e produzir um mapa de estudo em cima delas.
A entrega tem duas naturezas bem diferentes que **não podem se misturar**:

1. **Transcrição fiel** dos PDFs → markdown. Conteúdo do professor, *sem editar*.
2. **Síntese própria** (a "Visão Geral do Conteúdo") → aí sim você organiza,
   conecta e comenta, porque foi isso que o Isaías pediu explicitamente.

Se você borrar essa fronteira — "melhorando" o texto do professor, resumindo,
cortando — o material perde valor como fonte primária de estudo. A regra de ouro:
**nas notas/slides, a sua opinião não entra; na visão geral, ela é o produto.**

## Antes de começar

- Liste o vault e a pasta da disciplina antes de escrever. Leia o índice da
  disciplina (`<Disciplina>/<Disciplina>.md`) e o template de aula
  (`_Templates/Aula.md`) para casar convenções (frontmatter, tags, nomes de
  wikilink que já existem). Reaproveitar os nomes que o índice já referencia faz
  os links resolverem sozinhos.
- Sincronização é do **Hermínio** (fluxo git). Você grava os arquivos no disco do
  vault; não dispute commit/pull. Se `git pull` pelo canal do desktop falhar (sem
  SSH ali), siga em frente — os arquivos persistem no disco local mesmo assim.
- Se houver dúvida real de escopo (onde salvar, que disciplina) e o Isaías estiver
  presente, pergunte uma coisa só. Se estiver operando sozinho, assuma o caminho
  mais provável e diga qual assunção fez.

## Passo 1 — Extrair o conteúdo (texto E matemática E figuras)

O erro clássico aqui é confiar só no `pdftotext`. Ele **descarta as equações**
(elas somem, viram espaços em branco) e não traz as figuras. Como o material de
séries/estatística é cheio de fórmula e de gráfico, isso destrói a fidelidade.
Então use três fontes juntas:

- `scripts/extract_pdf.sh <arquivo.pdf>` roda `pdftotext -layout` (para pegar a
  espinha textual e a ordem) e `pdfimages -png` (para extrair as figuras
  embutidas) num diretório temporário. É o ponto de partida rápido.
- **Leia o PDF como imagem** com a tool `Read` (parâmetro `pages`), página a
  página. É assim que você recupera as equações e transcreve para LaTeX com a
  **mesma notação do professor** ($y_t$, $\beta$, $\epsilon_t$, $T_t+S_t+R_t$…),
  e é assim que você lê as legendas das figuras exatamente como estão.
- Confira o mapeamento das figuras **abrindo cada PNG extraído** (Read) antes de
  embutir. `pdfimages` numera na ordem de aparição; renomeie para nomes
  descritivos (`st-13-06-boxplot-por-mes.png`) e verifique visualmente que a
  legenda bate com a imagem. Slides e notas da mesma aula costumam compartilhar
  os mesmos PNGs — extraia uma vez.

## Passo 2 — Escrever os markdowns fiéis

Frontmatter padrão do vault (ajuste `disciplina`, `data`, `autor`, `fonte`):

```yaml
---
tipo: material-aula
subtipo: notas-professor   # ou: apresentacao
disciplina: "[[Séries Temporais]]"
data: 2026-08-13
autor: Thiago Guerrera Martins
fonte: 20260813notasaula.pdf
tags: [st, material/notas]   # material/slides para apresentação
---
```

Logo abaixo do frontmatter, um callout curto que marca a natureza do arquivo e a
origem — isso protege o "você do futuro" de tratar a transcrição como se fosse
editável:

```markdown
> [!info] Transcrição fiel
> Conversão em markdown do material do professor, **sem edição de conteúdo**.
> Texto, notação (LaTeX) e legendas preservados do original (`arquivo.pdf`).
> Figuras extraídas do próprio PDF.
```

Convenções de corpo:

- **Notas do professor:** preserve a hierarquia de títulos do PDF (tamanho da
  fonte → nível de `#`). Equações em `$…$` (inline) e `$$…$$` (display). Não
  reordene, não resuma, não "conserte" o texto.
- **Slides/apresentação:** um bloco por slide, na ordem, cabeçalho
  `## Slide N — <título do slide>`. Bullets e ênfases como no slide.
- **Figuras:** embuta por nome de arquivo — `![[nome-do-arquivo.png]]` — e a
  legenda em itálico na linha de baixo (`*Legenda exatamente como no PDF*`).
  Embed por wildcard de nome resolve em qualquer pasta do vault, então você não
  precisa amarrar caminho relativo.

Nomes de arquivo que casam com o índice da disciplina:

- `Notas do Professor — AAAA-MM-DD.md`
- `Apresentação — AAAA-MM-DD (<tema curto>).md`

## Passo 3 — A Visão Geral do Conteúdo (síntese)

Este é o arquivo que o Isaías pediu para "orientar o estudo". Aqui você **não**
transcreve — você organiza. Nome: `<Disciplina> — Visão Geral do Conteúdo.md`,
na raiz da pasta da disciplina. Frontmatter com `tipo: visao-geral` e um campo
`cobre_ate: AAAA-MM-DD` (a data da última aula processada), porque essa nota é
**viva**: cada vez que chegar material novo, você a estende, não recria.

Estrutura que funciona bem (adapte ao conteúdo real, não force seções vazias):

- **O fio condutor até aqui** — a ideia que costura as aulas, em 1–2 parágrafos.
- **Uma seção por aula** — o que foi estabelecido, com os resultados/fórmulas
  centrais e links para `[[Notas do Professor — …]]` e `[[Apresentação — …]]`.
- **Modelo mental de uma página** — um bloco de código-arte / esquema que o
  Isaías possa bater o olho e lembrar tudo.
- **O que eu já consigo fazer** — capacidades concretas destravadas até aqui.
- **O que vem por aí** — sinalizado pelo professor (próximos tópicos, projeto).
- **Datas que importam** — provas, entregas, liberação de enunciado.
- **Dúvidas / pontos a fechar depois** — as pontas soltas honestas.

O tom é do Isaías: direto, concreto, traduz formalismo em intuição e (quando
couber) em Python, que ele domina. É material de estudo dele, não relatório.

## Passo 4 — Ligar no índice da disciplina

Abra `<Disciplina>/<Disciplina>.md` e:

- Nas linhas de cada aula, acrescente os links do material processado:
  `+ [[Notas do Professor — DATA|Notas]] + [[Apresentação — DATA (tema)|Slides]]`.
- Adicione perto do topo um atalho para a visão geral (um callout `> [!tip]
  Comece por aqui`).
- Atualize o campo `atualizado:` do frontmatter.
- Não crie as notas de aula *pessoais* do Isaías (`AAAA-MM-DD — Aula N …`) — essas
  ele preenche pelo template, à mão. Deixe os wikilinks prontos, só.

## Passo 5 — Gravar no vault e conferir

Tudo é construído no workspace da sessão e depois copiado pro disco do vault:

1. `SendUserFile` em cada `.md` (deliverables) e nos PNGs (agrupe os PNGs numa
   única chamada, `display: attach`, pra não poluir a conversa com um card por
   figura). Guarde os `file_uuid`.
2. `device_commit_files` gravando:
   - materiais `.md` → `FGV <ano.sem>/<Disciplina>/Aulas/`
   - figuras `.png` → `FGV <ano.sem>/<Disciplina>/Aulas/attachments/`
   - visão geral `.md` → raiz `FGV <ano.sem>/<Disciplina>/`
   - índice atualizado → sobrescreve `<Disciplina>.md` (use `expectedMtimeMs` do
     staging para não pisar em escrita do Hermínio; se rejeitar, re-stage e
     reaplique).
   Crie a pasta `attachments/` antes (via `device_bash mkdir -p`) se não existir.
3. Liste a pasta no final (`device_list_dir` recursivo) para confirmar que tudo
   caiu, e cheque que cada `![[…png]]` tem o PNG correspondente em `attachments/`.

## Checklist de fidelidade (rode mentalmente antes de entregar)

- Nenhuma equação virou texto solto ou sumiu — todas em LaTeX com a notação do
  professor.
- Nenhuma figura ficou órfã; legendas idênticas às do PDF.
- Nada do texto do professor foi resumido, reescrito ou reordenado nas notas.
- A visão geral é claramente síntese sua (frontmatter + tom), separada das notas.
- Os wikilinks resolvem (nomes batem com o que o índice já espera).
