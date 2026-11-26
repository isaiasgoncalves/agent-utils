# -*- coding: utf-8 -*-
"""
cena_base.py — Cena Manim cronometrada pela narração (gerada por narrar.py),
com a fonte padrão do vídeo e helpers para imagens baixadas da web.

Copie para a raiz do projeto (ao lado de video.py) e use:

    from cena_base import *

    class Cena2_Ideia(CenaSync):          # nome = "scene" no narration.json
        def construct(self):
            eixo = Axes(...); self.add(eixo)   # algo na tela já no quadro 0
            self.go("a curva sobe")             # espera até essa frase ser dita
            self.play(Create(curva), run_time=self.left("e depois estabiliza"))
            self.finish()                       # obrigatório: completa a fala e faz fade-out

API de tempo
  self.t("frase", nth=1, end=False) -> instante (s) em que a frase é dita
  self.go("frase", nth=1, off=0.0)  -> espera até lá (off<0 adianta); avisa [atrasado]
  self.left("frase", off=0, lo=0.3, hi=9) -> segundos até a frase (bom como run_time)
  self.finish(fade=0.5, tail=0.6)   -> espera o fim da fala, FadeOut de tudo, folga

Paleta
  BG, C_TEXTO, C_NEUTRO, C_AZUL (objeto), C_DEST (destaque), C_VERDE (acerto),
  C_ROSA (alerta), C_SERIES (lista) — lidas de video.config.json -> estilo.paleta.

Fonte
  Text/MarkupText/Paragraph usam FONTE (padrão "CMU Serif"; troque em
  video.config.json -> fonte.texto). MathTex/Tex usam Computer Modern, o mesmo
  desenho da CMU, então texto e fórmula combinam. Para outra fonte também no
  LaTeX: fonte.latex = "mesma-do-texto" (usa xelatex + fontspec).

Cenas 3D
  class Cena5_Gradiente(CenaSync3D): ...   -> mesma API, câmera 3D; helpers em helpers_3d.py

Imagens (baixadas com scripts/baixar_imagem.py para assets/imagens/)
  imagem("assets/imagens/x.jpg", altura=4)          -> ImageMobject/SVGMobject
  com_credito(img)                                  -> Group(img, crédito pequeno embaixo)
  credito_de("assets/imagens/x.jpg")                -> texto do crédito (de creditos.json)
"""
import json, os
import numpy as np
from manim import *

AUDIO_DIR = os.environ.get("NARR_DIR", os.path.join("media", "audio"))


# ------------------------------------------------------------ configuração --
def _cfg():
    p = os.environ.get("VIDEO_CONFIG", "video.config.json")
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


_CFG = _cfg()
_P = {"fundo": "#0d1117", "texto": "#ffffff", "neutro": "#9aa5b1", "objeto": "#4cc9f0",
      "destaque": "#ffd166", "acerto": "#80ed99", "alerta": "#f72585",
      "series": ["#4cc9f0", "#ffd166", "#80ed99", "#c77dff", "#ff9f1c"],
      **_CFG.get("estilo", {}).get("paleta", {})}
# Paleta do projeto (video.config.json -> estilo.paleta; significado em estilo.md)
BG, C_TEXTO, C_NEUTRO, C_AZUL = _P["fundo"], _P["texto"], _P["neutro"], _P["objeto"]
C_DEST, C_VERDE, C_ROSA, C_SERIES = _P["destaque"], _P["acerto"], _P["alerta"], _P["series"]
_F = _CFG.get("fonte", {})
_IMG = _CFG.get("imagens", {})


def _escolher_fonte(pref, reservas):
    try:
        import manimpango
        instaladas = set(manimpango.list_fonts())
    except Exception:
        return pref
    for f in [pref, *reservas]:
        if f in instaladas:
            if f != pref:
                print(f"  [fonte] '{pref}' não instalada; usando '{f}'")
            return f
    print(f"  [fonte] nenhuma de {[pref, *reservas]} instalada; usando a padrão do Pango")
    return None


FONTE = _escolher_fonte(_F.get("texto", "CMU Serif"),
                        _F.get("reserva", ["Latin Modern Roman", "DejaVu Serif"]))
if FONTE:
    for _cls in (Text, MarkupText, Paragraph):
        try:
            _cls.set_default(font=FONTE)
        except Exception:
            pass

if _F.get("latex") == "mesma-do-texto" and FONTE:
    _t = TexTemplate(tex_compiler="xelatex", output_format=".xdv")
    _t.add_to_preamble(r"\usepackage{fontspec}" + "\n" + r"\setmainfont{" + FONTE + "}")
    config.tex_template = _t


# ---------------------------------------------------------------- imagens --
def _creditos():
    p = os.path.join(_IMG.get("pasta", "assets/imagens"), "creditos.json")
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def credito_de(caminho):
    c = _creditos().get(os.path.basename(caminho))
    return c.get("credito_curto", "") if c else ""


def imagem(caminho, altura=None, largura=None):
    """PNG/JPG -> ImageMobject; SVG -> SVGMobject. Ajusta pela altura OU largura."""
    m = SVGMobject(caminho) if caminho.lower().endswith(".svg") else ImageMobject(caminho)
    if altura:
        m.height = altura
    elif largura:
        m.width = largura
    m._arquivo = caminho
    return m


def com_credito(img, caminho=None, texto=None, tam=0.28, cor="#9aa5b1"):
    """Agrupa a imagem com o crédito exigido pela licença, pequeno, logo abaixo.
    Desligue em video.config.json -> imagens.mostrar_credito_na_tela."""
    texto = texto if texto is not None else credito_de(caminho or getattr(img, "_arquivo", ""))
    if not texto or not _IMG.get("mostrar_credito_na_tela", True):
        return Group(img)
    t = Text(texto, color=cor).scale(tam)
    if t.width > max(img.width, 2.5):                  # nunca mais largo que a imagem
        t.width = max(img.width, 2.5)
    t.next_to(img, DOWN, buff=0.12)
    return Group(img, t)


def _norm(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


# ------------------------------------------------------------------ cena ---
class _Sync:
    """Tempo pela narração; misturado em Scene (2D) e ThreeDScene (3D)."""
    narracao = None            # sobrescreva se o nome no narration.json for outro

    def setup(self):
        super().setup()
        self.camera.background_color = BG
        nome = self.narracao or type(self).__name__
        p = os.path.join(AUDIO_DIR, nome + ".json")
        if not os.path.exists(p):
            raise FileNotFoundError(f"{p} não existe: rode narrar.py antes do Manim")
        d = json.load(open(p, encoding="utf-8"))
        self._nome, self._txt, self._ini = nome, _norm(d["text"]), d["start"]
        self.audio_len = d["duration"]

    def t(self, frase, nth=1, end=False):
        f, i = _norm(frase), -1
        for _ in range(nth):
            i = self._txt.find(f, i + 1)
            if i < 0:
                raise ValueError(f"{self._nome}: cue não encontrado: {frase!r}")
        if end:
            i = min(i + len(f), len(self._ini) - 1)
        return self._ini[i]

    def go(self, frase, nth=1, off=0.0, end=False):
        dt = self.t(frase, nth, end) + off - self.time
        if dt > 1 / 60:
            self.wait(dt)
        elif dt < -0.25:
            print(f"  [atrasado {-dt:.2f}s] {self._nome}: {frase!r}")

    def left(self, frase, nth=1, off=0.0, lo=0.3, hi=9.0):
        return float(np.clip(self.t(frase, nth) + off - self.time, lo, hi))

    def finish(self, fade=0.5, tail=0.6):
        dt = self.audio_len - fade - self.time
        if dt > 1 / 60:
            self.wait(dt)
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=fade)
        self.wait(tail)


class CenaSync(_Sync, Scene):
    """Cena 2D cronometrada pela fala."""


class CenaSync3D(_Sync, ThreeDScene):
    """Cena 3D cronometrada pela fala (veja references/animacoes_3d.md).

    self.fixo(*mobs)          -> texto/fórmula preso à tela (não gira com a câmera)
    self.orbitar(rate=0.12)   -> começa a girar a câmera devagar (pare com stop_ambient_camera_rotation)
    """

    def fixo(self, *mobs):
        self.add_fixed_in_frame_mobjects(*mobs)
        return mobs[0] if len(mobs) == 1 else VGroup(*mobs)

    def orbitar(self, rate=0.12):
        self.begin_ambient_camera_rotation(rate=rate)
