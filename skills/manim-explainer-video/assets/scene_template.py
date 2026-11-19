# -*- coding: utf-8 -*-
"""
Template inicial para um vídeo explicativo estilo 3Blue1Brown (Manim Community).

COPIE este arquivo para o projeto e edite. Ele já traz:
  - paleta sóbria de fundo escuro,
  - helpers reutilizáveis (distribuição de barras, etc.),
  - uma cena de exemplo demonstrando os idiomas mais comuns.

Versão-alvo: Manim Community v0.18+   (NÃO ManimGL)
Render rascunho:  manim -ql  arquivo.py NomeDaCena
Render final FHD: manim -qh  arquivo.py NomeDaCena   (1080p60)
Render de todas:  manim -qh  arquivo.py -a
"""
from manim import *
import numpy as np

# --- Paleta (alto contraste sobre fundo escuro) ----------------------------
BG       = "#0d1117"   # fundo
C_NEUTRO = "#9aa5b1"   # texto secundário / eixos
C_AZUL   = "#4cc9f0"   # objeto padrão
C_DEST   = "#ffd166"   # destaque / conceito-alvo
C_VERDE  = "#80ed99"   # acerto / convergência
C_ROSA   = "#f72585"   # alerta / contraexemplo


# --- Helpers ----------------------------------------------------------------
def fazer_barras(probs, largura=0.7, esp=0.55, altura_max=2.6, idx_dest=None):
    """Distribuição de barras a partir de probabilidades. Base em y=0.
    Útil para animar um posterior/distribuição colapsando via Transform."""
    barras = VGroup()
    n = len(probs)
    passo = largura + esp
    for i, p in enumerate(probs):
        h = altura_max * p + 1e-3
        cor = C_DEST if (idx_dest is not None and i == idx_dest) else C_AZUL
        b = Rectangle(width=largura, height=h, fill_color=cor, fill_opacity=0.9,
                      stroke_width=1.0, stroke_color=WHITE)
        x = (i - (n - 1) / 2) * passo
        b.move_to([x, h / 2, 0])
        barras.add(b)
    return barras


def rotulos_barras(labels, largura=0.7, esp=0.55, y=-0.35):
    grupo = VGroup()
    n = len(labels)
    passo = largura + esp
    for i, lab in enumerate(labels):
        t = MathTex(lab).scale(0.6).move_to([(i - (n - 1) / 2) * passo, y, 0])
        grupo.add(t)
    return grupo


# --- Cena de exemplo (demonstra os idiomas mais comuns) ---------------------
class CenaExemplo(Scene):
    def construct(self):
        self.camera.background_color = BG

        # 1) Texto/título por Write
        titulo = Text("Título da cena", color=WHITE).scale(0.8).to_edge(UP)
        self.play(Write(titulo))

        # 2) Fórmula com MathTex (define símbolos na 1ª aparição)
        formula = MathTex(r"p(y\mid x)=\int p(y\mid x,\theta)\,p(\theta)\,d\theta")
        formula.scale(0.9)
        self.play(Write(formula))
        self.wait(0.5)
        self.play(formula.animate.scale(0.7).to_edge(LEFT).shift(UP))

        # 3) Distribuição que colapsa (Transform entre dois VGroups de barras)
        labels = rotulos_barras([r"\theta_1", r"\theta_2", r"\theta_3", r"\theta_4"]).shift(DOWN)
        barras = fazer_barras([0.25, 0.25, 0.25, 0.25]).shift(DOWN)
        self.play(Create(barras), FadeIn(labels))
        novas = fazer_barras([0.05, 0.85, 0.06, 0.04], idx_dest=1).shift(DOWN)
        self.play(Transform(barras, novas))
        self.wait(0.5)

        # 4) Gráfico animado com Axes + Create
        self.play(FadeOut(VGroup(formula, barras, labels)))
        axes = Axes(x_range=[0, 8, 1], y_range=[0, 1, 0.25], x_length=7, y_length=4,
                    axis_config={"color": C_NEUTRO}).to_edge(DOWN)
        curva = axes.plot(lambda x: 1 - np.exp(-0.6 * x), x_range=[0, 8], color=C_VERDE)
        self.play(Create(axes))
        self.play(Create(curva), run_time=2)
        self.wait(0.5)

        # 5) IMPORTANTE: limpe TUDO antes de terminar (evita sobras na próxima cena)
        self.play(FadeOut(VGroup(titulo, axes, curva)))
