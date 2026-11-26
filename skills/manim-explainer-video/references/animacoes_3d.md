# Animações 3D (e outros recursos visuais para a didática)

Leia na Etapa 3 (ao decidir se uma cena pede 3D) e na Etapa 6 (ao escrever).
3D custa render mais lento e confunde se for decorativo. Use quando a terceira
dimensão **é** o conteúdo: uma superfície de perda, um sólido, um campo no
espaço, uma transformação de R³. Para o resto, 2D é mais legível.

## Quando o 3D paga o custo

| Conteúdo | Cena 3D | Par 2D que ajuda |
|---|---|---|
| Descida de gradiente, otimização, mínimos locais, sela | superfície `L(w1,w2)` + bolinha descendo com passos REAIS | curvas de nível com o mesmo trajeto, vista de cima |
| Geometria espacial (prismas, pirâmides, cones, esferas) | sólido girando, seções planas, planificação | a fórmula montada termo a termo |
| Volume por fatias (Cavalieri, integral de volume, sólido de revolução) | fatias empilhando, curva girando em torno do eixo | soma de Riemann das áreas |
| Álgebra linear (base, determinante como volume, autovetores em R³) | cubo unitário virando paralelepípedo | matriz ao lado, fixa na tela |
| Cálculo vetorial (gradiente, campos, fluxo) | `ArrowVectorField` 3D, plano tangente | derivadas parciais como cortes da superfície |
| Probabilidade conjunta, gaussiana 2D | sino 3D da densidade | elipses de nível e a matriz de covariância |

## A base: `CenaSync3D`

Mesma API de tempo da `CenaSync` (`go`, `left`, `t`, `finish`), sobre `ThreeDScene`.
Copie `assets/helpers_3d.py` para o projeto junto com `cena_base.py`.

```python
from cena_base import *
from helpers_3d import *

class Cena6_Descida(CenaSync3D):
    def construct(self):
        f  = lambda x, y: 0.1 * (x**2 + 2 * y**2)            # cabe em z de 0 a 3
        gf = lambda x, y: np.array([0.2 * x, 0.4 * y])        # gradiente analítico
        ax = eixos_3d()
        enquadrar(self, ax)                                    # câmera centrada na caixa
        sup = superficie(ax, f)
        formula = self.fixo(MathTex(r"w \leftarrow w - \eta\,\nabla L(w)").to_corner(UL))
        self.add(ax, sup)                                      # algo na tela no quadro 0
        self.go("o gradiente aponta")
        self.play(Create(seta_gradiente(ax, f, gf, 2.6, 1.4)))
        pts = descida_gradiente(f, gf, (2.6, 1.4), lr=0.9, passos=14)
        bola, trilha = trajeto(ax, pts)
        self.go("passo a passo")
        self.orbitar(0.08)                                     # gira devagar enquanto desce
        self.play(Create(trilha), MoveAlongPath(bola, trilha),
                  run_time=self.left("chega ao fundo do vale"), rate_func=linear)
        self.stop_ambient_camera_rotation()
        self.finish()
```

Helpers (`helpers_3d.py`): `eixos_3d`, `enquadrar`, `superficie` (cor pela altura),
`descida_gradiente` (com `momento`), `trajeto`, `passos_marcados`,
`seta_gradiente`, `curvas_nivel` (num `Axes` 2D), `plano_secao`.

## Receitas

**Descida de gradiente que ensina de verdade.** Mostre três taxas de
aprendizado lado a lado ou em sequência, todas calculadas: `lr` pequeno (lento),
bom, e grande demais (oscila ou diverge). Na vista de cima (`curvas_nivel`) fica
claro o zigue-zague num vale alongado (ex.: `0.1*(x**2 + 6*y**2)`) e por que o momento ajuda
(`momento=0.8`). Narre os números: "depois de 5 passos a perda caiu de 2,3 para 0,4"
— tire esses valores de `pts`, não invente.

**Ponto de sela e mínimos locais.** `f = x**2 - y**2` (sela) ou uma soma de
gaussianas invertidas para vários vales; comece duas bolinhas em pontos
diferentes e mostre que caem em mínimos diferentes.

**Geometria espacial.** Sólidos nativos: `Cube`, `Prism(dimensions=[a,b,c])`,
`Cone`, `Cylinder`, `Sphere`, `Torus`, `Polyhedron(vertices, faces)`
(pirâmides e poliedros quaisquer). Seção: `plano_secao(z)` subindo com
`.animate.shift(OUT*dz)` enquanto a área da seção aparece fixa na tela.
Volume da pirâmide = 1/3 do prisma: três pirâmides montando o cubo.

**Cavalieri / sólido de revolução.** `Surface(lambda u, v: ax.c2p(r(u)*np.cos(v), r(u)*np.sin(v), u))`
gera o sólido de revolução de `r(u)`; anime `v` de 0 a 2π com um `ValueTracker` e
`always_redraw` para a curva "girar e varrer" o sólido.

**Transformação linear em R³.** `Cube(side_length=1)` + `ApplyMatrix(M, cubo)`;
mostre `det(M)` fixo na tela crescendo junto do volume.

## Câmera e legibilidade

- Texto e fórmula: SEMPRE `self.fixo(...)` (`add_fixed_in_frame_mobjects`),
  senão giram com a cena e ficam ilegíveis.
- Câmera: `set_camera_orientation(phi, theta, zoom)` para enquadrar;
  `move_camera(phi=..., theta=..., run_time=...)` para mudar de ângulo numa
  frase-chave; `orbitar(rate)` pequeno (0.05–0.15) dá profundidade sem enjoar.
  Pare a rotação antes de `finish()`.
- Superfícies: escolha `f` e o domínio para caber na faixa z dos eixos (`superficie` avisa quando não cabe); `res` 20–32; `fill_opacity` 0.6–0.8 deixa ver a trilha; levante a
  trilha (`levantar=0.04`) para não sumir dentro da malha (z-fighting).
- Contraste: bolinha/trilha em `C_DEST`, superfície em tons frios.

## Desempenho e verificação

- 3D renderiza bem mais devagar. Itere em `-ql`, `res` baixo (16) e sem
  `orbitar`; suba tudo só no render final.
- Na extração de quadros (Etapa 7), confira: fórmula fixa legível, trilha
  visível sobre a superfície, eixos com rótulo, nada cortado pela câmera.

## Outras formas de enriquecer (além do Manim 3D)

- **Imagens reais** (`scripts/baixar_imagem.py`): retrato do autor, foto do
  fenômeno, figura do paper — ancoram o abstrato no concreto.
- **HyperFrames 3D** (skill `hyperframes`, `references/types/3d.md`): Three.js
  para cenas fotorealistas ou com materiais/iluminação que o Manim não faz
  (um objeto físico, um globo, partículas). Renderize como cena à parte e entre
  com ela no `narration.json` como mais uma cena (mesmo nome do `.mp4`).
- **Overlays da pós-produção** (Etapa 9): letreiros de capítulo, cartões de
  "resumo até aqui", destaque de termos — sem poluir as cenas do Manim.
- **Simulações numéricas**: rode o modelo de verdade em NumPy (um SGD num
  dataset pequeno, uma cadeia de Markov) e anime os resultados; vale mais que
  qualquer curva desenhada à mão.
