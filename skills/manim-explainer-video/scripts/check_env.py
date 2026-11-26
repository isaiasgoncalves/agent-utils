# -*- coding: utf-8 -*-
"""
check_env.py — Verifica o ambiente ANTES de começar (rode da pasta do projeto,
para ele ler video.config.json e .env): Manim, LaTeX, ffmpeg, PyAV, provedores
de voz, Whisper (alinhamento), fonte do vídeo e ferramentas de pós-produção.

USO:  python <SKILL>/scripts/check_env.py
"""
import os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _comum import carregar_config, find_ffmpeg  # noqa: E402
import tts_provedores as tts  # noqa: E402


def linha(ok, nome, detalhe=""):
    print(f"[{'OK ' if ok else 'FALTA'}] {nome}{('  ' + detalhe) if detalhe else ''}")


def tem(mod):
    try:
        __import__(mod)
        return True
    except Exception:
        return False


def main():
    cfg = carregar_config(".")
    ct = cfg["tts"]
    print("== Base")
    try:
        import manim
        linha(True, f"manim {manim.__version__}")
    except Exception:
        linha(False, "manim", "-> pip install manim")
    latex = next((shutil.which(x) for x in ("latex", "pdflatex", "xelatex") if shutil.which(x)), None)
    linha(bool(latex), "LaTeX", latex or "instale TeX Live; sem ele MathTex/Tex falham")
    ff = find_ffmpeg(sair=False)
    linha(bool(ff), "ffmpeg", ff or "passe --ffmpeg aos scripts")
    linha(tem("av"), "PyAV (av)", "" if tem("av") else "-> pip install av (ou use ffprobe)")

    print("\n== Voz (tts.provedor = %s)" % ct.get("provedor"))
    for n in ["elevenlabs", "gemini", "openai", "edge", "comando"]:
        disp = tem("edge_tts") if n == "edge" else tts.DISPONIVEL[n](ct.get(n, {}))
        dica = {"elevenlabs": "ELEVENLABS_API_KEY + tts.elevenlabs.voz_id",
                "gemini": "GEMINI_API_KEY (grátis no AI Studio)", "openai": "OPENAI_API_KEY",
                "edge": "pip install -U edge-tts", "comando": "tts.comando.cmd"}[n]
        linha(disp, n, "" if disp else dica)
    try:
        print(f"  -> será usado: {tts.escolher(ct)}")
    except tts.ErroTTS as e:
        print(f"  -> ERRO: {e}")
    whisper = tem("faster_whisper") or bool(shutil.which("whisper-ctranslate2"))
    linha(whisper, "Whisper (alinha o tempo de Gemini/OpenAI/comando)",
          "" if whisper else "uv tool install whisper-ctranslate2  (sem ele: tempo aproximado)")

    print("\n== Visual")
    fonte = cfg["fonte"].get("texto", "CMU Serif")
    r = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True) if shutil.which("fc-list") else None
    achou = bool(r and fonte.lower() in r.stdout.lower())
    linha(achou, f"fonte '{fonte}'", "" if achou else
          "Debian/Ubuntu: sudo apt install fonts-cmu ; ou copie os .ttf da CMU para ~/.local/share/fonts")
    linha(tem("PIL"), "Pillow (converter WebP/GIF baixados)", "" if tem("PIL") else "pip install pillow (opcional)")

    print("\n== Pós-produção (opcional)")
    hf = os.path.expanduser("~/.claude/skills/hyperframes/scripts/plugin-cli.mjs")
    linha(bool(shutil.which("node")), "node", "" if shutil.which("node") else "necessário para HyperFrames")
    linha(os.path.exists(hf), "skill hyperframes", "" if os.path.exists(hf) else "letreiros/overlays indisponíveis")
    if ff:
        r = subprocess.run([ff, "-hide_banner", "-filters"], capture_output=True, text=True)
        linha(" subtitles " in r.stdout, "ffmpeg com libass (queimar legendas)")
        linha("loudnorm" in r.stdout and "sidechaincompress" in r.stdout, "ffmpeg loudnorm + ducking")

    net = False
    try:
        import urllib.request
        urllib.request.urlopen("https://pypi.org", timeout=8)
        net = True
    except Exception:
        pass
    linha(net, "internet", "" if net else "TTS em nuvem e download de imagens precisam")


if __name__ == "__main__":
    main()
