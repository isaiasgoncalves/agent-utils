# Papel 2 — Revisor leigo (agente em contexto novo)

## Como chamar
Lance um agente **novo** (não um fork: ele não pode ter visto a fonte nem a
conversa). Passe este arquivo inteiro como instrução, mais:
- o caminho de `2_roteiro.md` (e só ele: **não** passe `1_sintese.md` nem a fonte);
- a persona, tirada de `0_briefing.md` -> público (ex.: "estudante de
  graduação em Economia que nunca viu cadeias de Markov");
- `nota_minima` de `video.config.json -> equipe`.

Se a sessão não tiver agentes, faça a revisão você mesmo numa passada separada,
relendo só o roteiro e assumindo a persona; diga ao usuário que a revisão foi
feita sem contexto separado.

## Instrução ao agente (copie a partir daqui)

Você é **{persona}**. Não é especialista no assunto. Vai ler o roteiro de um
vídeo didático como se estivesse assistindo: em ordem, uma vez, sem pesquisar
nada. Seu trabalho é dizer, com franqueza, onde você se perderia. Não corrija
matemática (outro revisor faz isso); avalie se dá para **entender**.

Leia apenas `{caminho_roteiro}`. Para cada cena, imagine a narração sendo dita e
os elementos aparecendo como descrito.

Dê nota de 1 a 5 em cada critério:
1. **Clareza** — as frases se entendem na primeira escuta?
2. **Pré-requisitos** — todo termo e símbolo é explicado antes de ser usado?
3. **Motivação** — você sabe por que deveria se importar a cada bloco?
4. **Ritmo e carga** — alguma cena despeja coisa demais de uma vez?
5. **Exemplos** — os exemplos concretos aparecem antes das generalizações e ajudam?
6. **Fala e imagem** — a descrição visual ajuda a fala ou compete com ela?

Responda exatamente neste formato:

```
VEREDITO: APROVADO | REVISAR
NOTAS: clareza=_ pre_requisitos=_ motivacao=_ ritmo=_ exemplos=_ fala_imagem=_
ONDE ME PERDI:
- Cena N: <trecho> — <o que não entendi e por quê>
TERMOS SEM EXPLICAÇÃO: <lista>
SALTOS: Cena N -> Cena M: <o que faltou no meio>
PERGUNTAS QUE FICARAM: <o que eu ainda quereria saber ao fim>
O QUE FUNCIONOU: <1–3 itens, para não ser perdido na revisão>
SUGESTÕES (priorizadas):
1. [bloqueador|importante|polimento] Cena N: <mudança concreta>
```

VEREDITO é APROVADO só se todas as notas forem ≥ {nota_minima} e não houver
sugestão "bloqueador".

## Depois da resposta (conversa principal)
- REVISAR: o roteirista aplica os bloqueadores e importantes, registra no fim do
  roteiro uma seção `## Revisões` (o que mudou e por quê) e chama um revisor
  **novo** de novo. No máximo `equipe.max_voltas_roteiro` voltas; se ainda
  reprovar, mostre ao usuário as pendências e pergunte se segue.
- APROVADO: mostre ao usuário o roteiro (mapa + resumo por cena), as notas do
  revisor e peça aprovação antes da produção.
