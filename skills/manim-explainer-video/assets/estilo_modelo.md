# Estilo do vídeo

Guia visual deste projeto. O produtor segue, o crítico de arte cobra. Edite à
vontade; mudanças de cor também vão para `video.config.json -> estilo.paleta`.

## Tom
Sóbrio, estilo 3Blue1Brown: fundo escuro, poucas cores com significado fixo,
movimento que explica (nada decorativo).

## Paleta (significado fixo em todo o vídeo)
| Papel | Cor | Uso |
|---|---|---|
| fundo | `#0d1117` | fundo de todas as cenas |
| texto | `#ffffff` | texto principal e fórmulas |
| neutro | `#9aa5b1` | eixos, rótulos secundários, créditos |
| objeto | `#4cc9f0` | objeto padrão, curva principal |
| destaque | `#ffd166` | o que a fala está explicando AGORA; uma coisa por vez |
| acerto | `#80ed99` | convergência, resposta certa, resultado |
| alerta | `#f72585` | erro, contraexemplo, concepção errada |
| séries | `#4cc9f0`, `#ffd166`, `#80ed99`, `#c77dff`, `#ff9f1c` | gráficos com várias séries, nesta ordem |

Não use vermelho×verde como única distinção. Mesma grandeza = mesma cor em
todas as cenas (ex.: se $\theta$ é azul na cena 2, é azul na cena 9).

## Tipografia
- Texto: **CMU Serif**; fórmulas: Computer Modern (MathTex).
- Escalas (Manim): título 0.9 · corpo 0.6–0.7 · rótulo 0.45–0.5 · crédito 0.28.
- Ênfase com cor de destaque ou `weight=BOLD`, nunca com sublinhado.

## Grade (quadro 14.2 × 8 unidades)
- Margem segura: 0.5 de cada borda (nada encostado).
- Título da cena (quando houver): topo, y ≈ 3.3, alinhado à esquerda.
- Área principal: centro, até ~70% da largura.
- Fórmula de apoio: lateral direita ou canto superior esquerdo, fixa.
- Faixa inferior (y < −2.9): livre se as legendas forem queimadas.
- No máximo 3 grupos de informação na tela ao mesmo tempo.

## Ritmo
- Texto fica na tela ≥ 1,5 s + 0,3 s por palavra.
- Nada parado > 3 s: sempre algo se movendo, destacando ou sendo apagado.
- Animações de entrada 0,6–1,2 s; transformações principais 1,5–3 s.
- Cenas de 15–70 s.

## Gráficos
- Eixos neutros, rótulo de eixo sempre presente, unidades quando houver.
- Valores reais calculados; esquemático leva o rótulo "esquemático".
- Legenda direta na série (rótulo ao lado da curva), não caixa de legenda.

## Imagens
- Até ~40% do quadro, com crédito pequeno embaixo; entram com FadeIn.

## 3D
- Só quando a 3ª dimensão é o conteúdo; texto sempre fixo na tela; rotação de
  câmera lenta (≤ 0.15 rad/s).
