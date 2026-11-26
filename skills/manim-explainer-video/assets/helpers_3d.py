# -*- coding: utf-8 -*-
"""
helpers_3d.py — Peças prontas para cenas 3D didáticas (Manim Community v0.18+).
Copie para o projeto junto com cena_base.py e use em cenas CenaSync3D.

    from cena_base import *
    from helpers_3d import *

    class Cena6_Descida(CenaSync3D):
        def construct(self):
            f  = lambda x, y: 0.1 * (x**2 + 2 * y**2)           # perda L(w1, w2), máx 2.7 < z 3
            gf = lambda x, y: np.array([0.2 * x, 0.4 * y])      # gradiente exato
            ax = eixos_3d()
            enquadrar(self, ax)
            sup = superficie(ax, f)
            self.add(ax, sup)
            pts = descida_gradiente(f, gf, (2.6, 1.4), lr=0.9, passos=14)   # números reais
            self.go("a bolinha desce")
            bola, trilha = trajeto(ax, pts)
            self.play(Create(trilha), MoveAlongPath(bola, trilha), run_time=self.left("até o mínimo"))
            self.finish()

Todas as contas são feitas de verdade (sem trajetória desenhada à mão), então o
que a narração disser sobre passos e valores bate com o que aparece.
"""
import numpy as np
from manim import *

C_AZUL, C_DEST, C_VERDE, C_ROSA, C_NEUTRO = "#4cc9f0", "#ffd166", "#80ed99", "#f72585", "#9aa5b1"


def eixos_3d(x=(-3, 3, 1), y=(-3, 3, 1), z=(0, 3, 1), tam=(6, 6, 3), rotulos=("w_1", "w_2", "L")):
    ax = ThreeDAxes(x_range=x, y_range=y, z_range=z, x_length=tam[0], y_length=tam[1],
                    z_length=tam[2], axis_config={"color": C_NEUTRO, "include_tip": True})
    if rotulos:
        lab = ax.get_axis_labels(*[MathTex(r).scale(0.7) for r in rotulos])
        ax.add(lab)
    return ax


def enquadrar(cena, ax, phi=65, theta=-50, zoom=0.85):
    """Câmera padrão: de cima e de lado, centrada no meio da caixa dos eixos."""
    zc = (ax.z_range[0] + ax.z_range[1]) / 2
    cena.set_camera_orientation(phi=phi * DEGREES, theta=theta * DEGREES, zoom=zoom,
                                frame_center=ax.c2p(0, 0, zc))


def superficie(ax, f, u=(-3, 3), v=(-3, 3), res=28, opacidade=0.75, cores=(C_AZUL, C_VERDE, C_DEST, C_ROSA)):
    """Superfície z = f(x, y), colorida pela altura (frio = baixo, quente = alto).
    Avisa se f sair da faixa z dos eixos (a superfície passaria do quadro)."""
    zz = [f(a, b) for a in np.linspace(*u, 9) for b in np.linspace(*v, 9)]
    if max(zz) > ax.z_range[1] or min(zz) < ax.z_range[0]:
        print(f"  [3D] f vai de {min(zz):.2f} a {max(zz):.2f}, fora de z_range={tuple(ax.z_range[:2])}: "
              "reduza o domínio (u, v), escale f ou aumente z dos eixos")
    s = Surface(lambda a, b: ax.c2p(a, b, f(a, b)), u_range=u, v_range=v,
                resolution=(res, res), fill_opacity=opacidade, stroke_width=0.3,
                stroke_color=WHITE, checkerboard_colors=False)
    s.set_fill_by_value(axes=ax, colorscale=list(cores), axis=2)
    return s


def descida_gradiente(f, grad, x0, lr=0.1, passos=20, momento=0.0):
    """Pontos (x, y, f) da descida de gradiente (com momento opcional)."""
    p, vel, out = np.array(x0, float), np.zeros(2), []
    for _ in range(passos + 1):
        out.append((p[0], p[1], f(*p)))
        vel = momento * vel - lr * np.asarray(grad(*p), float)
        p = p + vel
    return out


def trajeto(ax, pontos, cor=C_DEST, raio=0.08, levantar=0.04):
    """Bolinha + trilha poligonal ligando os pontos sobre a superfície."""
    xyz = [ax.c2p(x, y, z) + OUT * levantar for x, y, z in pontos]
    trilha = VMobject(stroke_color=cor, stroke_width=4).set_points_as_corners(xyz)
    bola = Sphere(radius=raio, resolution=(12, 12)).set_color(cor).move_to(xyz[0])
    return bola, trilha


def passos_marcados(ax, pontos, cor=C_DEST, raio=0.05):
    """Um ponto por iteração: deixa ver que os passos encurtam perto do mínimo."""
    return VGroup(*[Dot3D(ax.c2p(x, y, z), radius=raio, color=cor) for x, y, z in pontos])


def curvas_nivel(ax2d, f, niveis, cor=C_NEUTRO):
    """Curvas de nível f(x, y) = c desenhadas num Axes 2D (vista de cima da perda)."""
    x0, y0, _ = ax2d.c2p(ax2d.x_range[0], ax2d.y_range[0])
    x1, y1, _ = ax2d.c2p(ax2d.x_range[1], ax2d.y_range[1])
    def em_coord(X, Y):
        u, v = ax2d.p2c(np.array([X, Y, 0]))[:2]
        return u, v
    return VGroup(*[ImplicitFunction(lambda X, Y, c=c: f(*em_coord(X, Y)) - c,
                                     x_range=(x0, x1), y_range=(y0, y1), color=cor, stroke_width=2)
                    for c in niveis])


def seta_gradiente(ax, f, grad, x, y, escala=0.6, cor=C_ROSA):
    """Seta 3D do −gradiente no plano tangente (direção de maior descida)."""
    gx, gy = grad(x, y)
    a = ax.c2p(x, y, f(x, y))
    dx, dy = -escala * gx, -escala * gy
    b = ax.c2p(x + dx, y + dy, f(x, y) - escala * (gx * gx + gy * gy))
    return Arrow3D(a, b, color=cor, thickness=0.015)


def plano_secao(z, lado=4, cor=C_DEST, opacidade=0.35):
    """Plano horizontal z = cte para mostrar seções de sólidos (geometria espacial)."""
    return Square(side_length=lado, fill_color=cor, fill_opacity=opacidade,
                  stroke_width=1, stroke_color=cor).shift(OUT * z)
