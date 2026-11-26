# Manim — estilo 3Blue1Brown e armadilhas de layout

Leia ao escrever o código Manim (Etapa 3) e SEMPRE ao corrigir layout (Etapa 4).

## Estilo visual (referência: vídeos do 3Blue1Brown)
- Fundo escuro (`self.camera.background_color = BG`), paleta sóbria com poucos
  tons de destaque. Use as constantes do `assets/scene_template.py`.
- **Um conceito novo por vez.** Não polua a tela. Introduza, destaque, remova.
- Objetos matemáticos aparecem por `Write`/`Create` e se transformam por
  `Transform`/`ReplacementTransform`. Movimento por `.animate`.
- Ritmo pausado: `self.wait(0.4..1.5)` entre ideias. Narração constrói a
  intuição ANTES do formalismo.
- Guie o olhar: `SurroundingRectangle`, `Arrow`/`CurvedArrow`, `Brace`,
  `Indicate`, e zoom (`.animate.scale().move_to()`).

## Fonte (padrão: CMU Serif)
- `cena_base.py` define **CMU Serif** como fonte padrão de `Text`, `MarkupText` e
  `Paragraph`; `MathTex`/`Tex` já usam Computer Modern (o mesmo desenho), então
  texto e fórmula combinam como num livro em LaTeX. Não passe `font=` à toa.
- Trocar: `video.config.json -> fonte.texto` (e `fonte.reserva`). Se a fonte não
  estiver instalada, cai na primeira reserva e avisa no render.
- Para outra fonte também nas fórmulas: `fonte.latex = "mesma-do-texto"` (xelatex).
- Ênfase: `Text("...", weight=BOLD)` ou `slant=ITALIC` (a CMU tem os dois).
- Para tom mais técnico/código: `Text(..., font="CMU Typewriter Text")`.

## Imagens reais
- Baixe com `scripts/baixar_imagem.py` (Etapa 1) e use `imagem(caminho, altura=...)`
  + `com_credito(img)` do `cena_base.py`. Créditos ficam pequenos sob a imagem.
- Imagem é coadjuvante: ocupe até ~40% do quadro, deixe o texto/fórmula ao
  lado; `FadeIn` (não `Write`) para entrar; fundo escuro em volta (sem moldura branca grossa).
- Fotos claras sobre fundo escuro podem "estourar": reduza com
  `img.set_opacity(0.9)` ou use `SurroundingRectangle` fino na cor neutra.

## 3D
Para superfícies, sólidos e descida de gradiente, use `CenaSync3D` e
`assets/helpers_3d.py`; leia `references/animacoes_3d.md`.

## Idiomas (API estável do Manim Community v0.18+, NÃO ManimGL)
- Texto: `Text(...)` (Pango). Fórmulas: `MathTex(r"...")` / `Tex(r"...")` (exigem LaTeX).
- Gráficos: `Axes`, `axes.plot(lambda x: ...)`, `axes.c2p(x,y)`; anime com
  `Create(curva)` e ponto móvel com `ValueTracker` + `always_redraw`.
- Distribuições/barras: veja `fazer_barras` no template; anime colapso com `Transform`.
- Grafos/HMM: `VGroup` de `Circle`/`Dot` + `Arrow`; emissões com setas para baixo.
- Render: rascunho `manim -ql`, final `manim -qh` (1080p60). Uma `Scene` por cena.

## Catálogo de armadilhas de layout (vistas na prática) — e a correção

Você NÃO consegue assistir ao vídeo. Renderize em `-ql`, extraia quadros com
`scripts/extract_frames.py` e OLHE. Estes são os erros recorrentes:

1. **Sobras de mobjects entre cenas/etapas.**
   Sintoma: texto antigo aparece sobreposto ao novo.
   Causa comum: `Transform(algo.copy(), destino)` anima uma CÓPIA e deixa o
   original na tela; ou você esqueceu de remover um grupo.
   Correção: ao final de cada bloco/cena, `FadeOut` de TUDO que entrou. Não
   transforme cópias se quiser que o original suma.

2. **Emoji vira "tofu" (quadradinhos).**
   Sintoma: "⚡", "✦" etc. saem como caixas/glifos quebrados.
   Causa: a fonte não tem o glifo.
   Correção: desenhe a forma (ex.: um raio como `VMobject().set_points_as_corners(...)`),
   ou use um marcador geométrico (`Triangle`, `Cross`, `Dot`).

3. **Rótulo/fórmula coberto por uma barra (ou objeto) que cresce.**
   Sintoma: ao animar barras para cima, a barra alta tapa um texto ancorado
   `next_to(barras, UP)` calculado quando as barras eram baixas.
   Correção: posicione o texto em coordenada FIXA acima da altura MÁXIMA possível
   (ex.: `.move_to(UP*1.9)`), não relativo ao estado inicial.

4. **Texto estourando a largura do quadro.**
   Sintoma: frase tocando/saindo das bordas, letras cortadas.
   Referência: o quadro 16:9 tem ~14.2 unidades de largura, ~8 de altura.
   Correção: reduza `.scale(...)` e/ou quebre em duas linhas (`VGroup(...).arrange(DOWN)`).

5. **Rótulos/legendas sobrepostos entre si ou sobre a figura.**
   Correção: empilhe com `next_to(..., buff>=0.3)`; dê a cada elemento seu
   espaço. Coloque rótulos de eixo claramente fora da área de plotagem.

6. **Setas curvas atravessando o texto.**
   Sintoma: `CurvedArrow` entre o "pé" de duas palavras arqueia POR CIMA delas e
   a ponta cai sobre a palavra seguinte.
   Correção: desenhe as setas num "corredor" próprio, em `y` fixo bem abaixo do
   texto, quase retas (ângulo pequeno, ex.: `angle=-TAU/14`). Confira o sinal do
   ângulo: ele define para que lado o arco curva.

7. **Palavra de resposta cobrindo uma seta / caixa de destaque desalinhada.**
   Sintoma: ao trocar "?" por uma palavra maior centralizada na mesma posição,
   ela invade a seta vizinha; e uma `SurroundingRectangle` criada no "?" fica do
   tamanho errado.
   Correção: posicione a nova palavra com `next_to(seta, RIGHT, buff=...)` (cresce
   para o lado livre) e RECRIE/`Transform` a caixa para a nova palavra.

8. **Ordem semântica trocada / palavras coladas.**
   Sintoma: frase com sentido errado, ou palavras sobrepostas.
   Causa: `Text(" ")` vazio no meio de um `arrange`, ou ordem errada no `VGroup`.
   Correção: cada palavra é um mobject separado, na ordem correta, espaçadas por
   `buff` no `arrange(RIGHT)`. Não use `Text(" ")` como espaçador.

9. **Quadro extraído no meio de uma animação parece "quebrado".**
   Um `Write` pela metade mostra texto parcial — isso é normal. Para julgar
   layout, extraia quadros em frações onde a cena está ESTÁTICA (após o `wait`),
   não no meio das transições.

10. **Legenda queimada cobrindo conteúdo.**
   Só acontece com `pos_producao.legendas.queimar = true`. Nesse caso, mantenha
   os ~15% inferiores do quadro livres (nada abaixo de `y ≈ -2.9`).

## Checklist antes de declarar uma cena pronta
- [ ] Renderizei em `-ql` e extraí ao menos 3-4 quadros estáticos.
- [ ] Olhei cada quadro: nada sobreposto, nada cortado, nada fora da margem.
- [ ] Cada cena termina limpando seus mobjects (fade-out), pronta para concatenar.
