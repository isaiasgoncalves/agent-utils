# -*- coding: utf-8 -*-
"""
check_env.py — Verifica o ambiente ANTES de começar, para evitar surpresas no
meio do pipeline (render que falha por falta de LaTeX, TTS sem internet, etc.).

USO:  python check_env.py
"""
import shutil, sys, os


def ok(b):
    return "OK " if b else "FALTA"


def main():
    print("== Ambiente para manim-explainer-video ==")

    # manim
    try:
        import manim
        print(f"[{ok(True)}] manim {manim.__version__}")
    except Exception:
        print(f"[{ok(False)}] manim  -> pip install manim")

    # LaTeX (necessário para MathTex/Tex)
    latex = shutil.which("latex") or shutil.which("pdflatex") or \
        shutil.which("xelatex") or shutil.which("miktex")
    print(f"[{ok(bool(latex))}] LaTeX  ({latex or 'instale MiKTeX/TeX Live; sem ele, MathTex/Tex falham'})")

    # ffmpeg
    ff = shutil.which("ffmpeg")
    if not ff:
        for c in [r"C:\Users\%s\AppData\Local\Programs\Stremio\ffmpeg.exe" % os.environ.get("USERNAME", ""),
                  "/usr/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg"]:
            if os.path.exists(c):
                ff = c
                break
    print(f"[{ok(bool(ff))}] ffmpeg ({ff or 'não no PATH; passe --ffmpeg ao build_video.py'})")

    # edge-tts
    try:
        import edge_tts  # noqa
        print(f"[{ok(True)}] edge-tts")
    except Exception:
        print(f"[{ok(False)}] edge-tts  -> pip install edge-tts")

    # PyAV
    try:
        import av  # noqa
        print(f"[{ok(True)}] PyAV (av)")
    except Exception:
        print(f"[{ok(False)}] PyAV  -> pip install av")

    # internet (TTS precisa)
    net = False
    try:
        import urllib.request
        urllib.request.urlopen("https://pypi.org", timeout=8)
        net = True
    except Exception:
        pass
    print(f"[{ok(net)}] internet (edge-tts precisa acessar o serviço da Microsoft)")

    print("\nDica: se faltar algo, instale antes de renderizar para não perder tempo.")


if __name__ == "__main__":
    main()
