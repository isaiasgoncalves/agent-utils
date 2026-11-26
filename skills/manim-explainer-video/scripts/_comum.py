# -*- coding: utf-8 -*-
"""
_comum.py — Configuração e utilitários compartilhados pelos scripts da skill.

Configuração em camadas (a de baixo sobrescreve a de cima):
  1. assets/config_padrao.json          (padrões da skill)
  2. <projeto>/video.config.json        (só as chaves que o projeto quer mudar)
  3. flags de linha de comando          (ex.: --provedor gemini)

Chaves de API vêm do ambiente ou de um .env na raiz do projeto (o .env nunca
sobrescreve uma variável já definida). Nada aqui imprime segredos.
"""
import copy, json, os, re, shutil, subprocess, sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PADRAO = os.path.join(SKILL_DIR, "assets", "config_padrao.json")
CONFIG_PROJETO = "video.config.json"


def _mesclar(base, extra):
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _mesclar(base[k], v)
        else:
            base[k] = v
    return base


def carregar_env(pasta="."):
    p = os.path.join(pasta, ".env")
    if not os.path.exists(p):
        return
    for linha in open(p, encoding="utf-8"):
        m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$", linha)
        if not m or linha.lstrip().startswith("#"):
            continue
        k, v = m.group(1), m.group(2).strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


def carregar_config(pasta=".", caminho=None):
    """Devolve o dict de configuração já mesclado."""
    carregar_env(pasta)
    cfg = json.load(open(PADRAO, encoding="utf-8"))
    proj = caminho or os.path.join(pasta, CONFIG_PROJETO)
    if os.path.exists(proj):
        _mesclar(cfg, json.load(open(proj, encoding="utf-8")))
    return cfg


def copia(cfg):
    return copy.deepcopy(cfg)


def find_ffmpeg(explicit=None, sair=True):
    """ffmpeg nem sempre está no PATH. Procura em: --ffmpeg, $FFMPEG, PATH,
    imageio-ffmpeg e alguns locais comuns."""
    cands = [explicit, os.environ.get("FFMPEG"), shutil.which("ffmpeg")]
    try:
        import imageio_ffmpeg
        cands.append(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        pass
    cands += [r"C:\ffmpeg\bin\ffmpeg.exe", "/usr/bin/ffmpeg",
              "/usr/local/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg"]
    for c in cands:
        if c and (os.path.exists(c) or shutil.which(c)):
            return c
    if sair:
        sys.exit("ERRO: ffmpeg não encontrado. Passe --ffmpeg <caminho> ou instale-o.")
    return None


def duracao(path, fallback=0.0):
    """Duração em segundos via PyAV; cai para ffprobe se PyAV faltar."""
    try:
        import av
        c = av.open(path)
        d = float(c.duration) / av.time_base if c.duration else fallback
        c.close()
        return d
    except ImportError:
        pass
    except Exception:
        return fallback
    ff = find_ffmpeg(sair=False)
    probe = ff and os.path.join(os.path.dirname(ff), "ffprobe")
    probe = probe if probe and os.path.exists(probe) else shutil.which("ffprobe")
    if not probe:
        return fallback
    r = subprocess.run([probe, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return fallback


def ffmpeg_ok(cmd, etapa):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ERRO ffmpeg ({etapa}):\n{r.stderr[-1500:]}")
    return r
