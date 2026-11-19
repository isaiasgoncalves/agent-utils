# Exemplo de ponta a ponta (arco de cenas)

Exemplo real: vídeo sobre o paper *"An Explanation of In-context Learning as
Implicit Bayesian Inference"* (Xie et al.). Mostra como o arco
intuição → formalismo → evidência vira cenas concretas. Use como MODELO de
ritmo e estrutura — não copie o conteúdo; adapte ao material do usuário.

## Como o arco virou 9 cenas
1. **Gancho** — um prompt com exemplos `entrada→saída` e a pergunta "como ele
   acerta sem treinar?". Cria o mistério. (texto por `Write`, destaque no `?`)
2. **Intuição central** — documento coerente (bio: nome→ocupação→nacionalidade);
   introduz o "conceito latente" com a analogia da estação de rádio.
3. **Construção** — pré-treino como aprender a inferir o tema; distribuição sobre
   conceitos se estreitando (barras via `Transform`).
4. **Tensão/contraexemplo** — o prompt "não natural" que concatena exemplos
   independentes; o mismatch de distribuição. (marcadores de "emenda")
5. **Formalização** — fórmula de Bayes/marginalização (`MathTex`) + o posterior
   colapsando no conceito-alvo (barras coloridas).
6. **Mecanismo** — a mistura de HMMs: estados ocultos que transitam e emitem
   tokens (`Dot`+`Arrow`); o conceito seleciona um componente.
7. **Por que funciona** — intuição do teorema: risco caindo até o risco de Bayes
   (`Axes` + curva por `Create` + `ValueTracker`).
8. **Evidência** — experimentos (GINC): curvas de acurácia subindo com nº de
   exemplos e tamanho do modelo (várias curvas por `Create`).
9. **Síntese** — recapitulação em 3 ícones + frase final.

(Para "aprofundado ~5–10 min", esse mesmo arco se expande para 12–16 cenas:
mais exemplos trabalhados, mais passos do formalismo, mais experimentos.)

## Lições aprendidas neste exemplo (já incorporadas ao catálogo)
- A barra do posterior, ao crescer, cobria a fórmula ancorada nela → fixe a
  fórmula em coordenada absoluta acima da altura máxima.
- "⚡" virou tofu → desenhe o raio como `VMobject`.
- A frase final estourava a largura → quebre em duas linhas + reduza a escala.
- "tulipa → planta": a palavra cobria a seta e a caixa ficou desalinhada →
  `next_to(seta, RIGHT)` e recrie a caixa.
- Setas de transição arqueavam por cima das palavras → corredor em `y` fixo
  abaixo do texto, quase retas.

## Sincronização que funcionou
Narração ~2,5–3 palavras/seg; cenas de 9–20 s. A fala ficou um pouco mais longa
que a animação em quase todas as cenas; o `build_video.py` estendeu o último
quadro (preto, pós fade-out) — invisível — e o resultado final teve ~2,5 min
para 9 cenas curtas. Para vídeo aprofundado, espere proporcionalmente mais.
