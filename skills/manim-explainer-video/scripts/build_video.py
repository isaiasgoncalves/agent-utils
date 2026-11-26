# -*- coding: utf-8 -*-
"""
build_video.py — Junta a narração de cada cena ao vídeo do Manim e concatena tudo.

Usa os áudios que narrar.py gerou (media/audio/cena{i}.mp3). Se algum faltar,
chama narrar.py com a configuração do projeto (video.config.json), então o
provedor de voz é sempre o mesmo da Etapa 3.

Por que "sem cortar nada": se a fala durar mais que a animação, o último quadro
(preto, pós fade-out) é congelado; se a animação durar mais, entra silêncio.

USO:
    python <SKILL>/scripts/build_video.py \
        --videos-dir media/videos/video/1080p60 \
        --narration narration.json --fps 60 --out video_final.mp4

Grava também media/scenes_av/cenas.json (início e duração de cada cena no vídeo
final), que pos_producao.py usa para capítulos e legendas.
"""
import argparse, json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from _comum import duracao as dur, ffmpeg_ok, find_ffmpeg  # noqa: E402


def mux_scene(it, idx, ffmpeg, vdir, sdir, fps):
    vid = os.path.join(vdir, it["scene"] + ".mp4")
    if not os.path.exists(vid):
        sys.exit(f"ERRO: vídeo não encontrado: {vid}")
    aud = it["audio"]
    out = os.path.join(sdir, f"cena{idx}.mp4")
    V, A = dur(vid), dur(aud)
    T = max(V, A) + 0.4               # folga no fim
    padv = (T - V) + 0.5             # congela último quadro
    flt = f"[0:v]tpad=stop_mode=clone:stop_duration={padv:.2f}[v];[1:a]apad[a]"
    ffmpeg_ok([ffmpeg, "-y", "-i", vid, "-i", aud,
               "-filter_complex", flt, "-map", "[v]", "-map", "[a]",
               "-t", f"{T:.2f}", "-r", str(fps),
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
               "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
               "-ac", "2", out], f"cena {idx}")
    d = dur(out)
    print(f"  cena {idx}: vídeo {V:.1f}s | voz {A:.1f}s -> {d:.1f}s")
    return out, d


def concat(parts, ffmpeg, sdir, out):
    lst = os.path.join(sdir, "lista.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    ffmpeg_ok([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], "concat")
    print(f"\nFINAL: {out}  ({dur(out):.1f}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos-dir", required=True, help="pasta com as cenas .mp4 do Manim")
    ap.add_argument("--narration", required=True, help="JSON ordenado [{scene,text}]")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--out", default="video_final.mp4")
    ap.add_argument("--ffmpeg", default=None)
    ap.add_argument("--audio-dir", default="media/audio")
    ap.add_argument("--work-dir", default="media/scenes_av")
    ap.add_argument("--provedor", default=None, help="repassado ao narrar.py se faltar áudio")
    ap.add_argument("--voice", "--voz", dest="voz", default=None, help="idem")
    a = ap.parse_args()

    ffmpeg = find_ffmpeg(a.ffmpeg)
    os.makedirs(a.work_dir, exist_ok=True)
    items = json.load(open(a.narration, encoding="utf-8"))
    if not isinstance(items, list):
        sys.exit("narration.json deve ser uma LISTA ordenada de {scene, text}.")
    for i, it in enumerate(items, 1):
        it["audio"] = os.path.join(a.audio_dir, f"cena{i}.mp3")

    print(f"ffmpeg: {ffmpeg}")
    if any(not os.path.exists(it["audio"]) for it in items):
        print("1) Narração: faltam áudios, rodando narrar.py...")
        cmd = [sys.executable, os.path.join(AQUI, "narrar.py"), a.narration, "--audio-dir", a.audio_dir]
        if a.provedor:
            cmd += ["--provedor", a.provedor]
        if a.voz:
            cmd += ["--voz", a.voz]
        if subprocess.run(cmd).returncode != 0:
            sys.exit("ERRO: narrar.py falhou.")
    else:
        print("1) Narração: reaproveitando media/audio/")
    print("2) Juntando voz a cada cena...")
    parts, mapa, t = [], [], 0.0
    for i, it in enumerate(items, 1):
        p, d = mux_scene(it, i, ffmpeg, a.videos_dir, a.work_dir, a.fps)
        parts.append(p)
        mapa.append({"scene": it["scene"], "titulo": it.get("titulo", ""), "inicio": round(t, 3),
                     "duracao": round(d, 3), "timing": os.path.join(a.audio_dir, it["scene"] + ".json")})
        t += d
    json.dump(mapa, open(os.path.join(a.work_dir, "cenas.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("3) Concatenando...")
    concat(parts, ffmpeg, a.work_dir, a.out)


if __name__ == "__main__":
    main()
