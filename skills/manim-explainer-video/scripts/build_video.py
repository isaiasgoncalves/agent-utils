# -*- coding: utf-8 -*-
"""
build_video.py — Gera narração (edge-tts) e monta o vídeo final.

Pega as cenas já renderizadas pelo Manim + um arquivo de narração e produz UM
único arquivo: sintetiza a voz de cada cena, junta voz+vídeo (sem cortar nada)
e concatena tudo.

Por que "sem cortar nada": a fala neural costuma durar um pouco mais que a
animação silenciosa. Em vez de acelerar a voz ou truncar, estendemos o vídeo
congelando o ÚLTIMO quadro (que nas cenas estilo 3b1b já é preto, pós fade-out,
então o congelamento é invisível) e/ou acrescentamos silêncio ao áudio. Assim a
narração toca inteira e a animação nunca é cortada.

USO:
    python build_video.py \
        --videos-dir media/videos/<arquivo>/1080p60 \
        --narration narration.json \
        --voice pt-BR-ThalitaNeural \
        --fps 60 \
        --out video_final.mp4

narration.json: lista ORDENADA, mapeando cada cena (pelo nome do arquivo .mp4,
sem extensão) ao texto da narração:
[
  {"scene": "Cena1_Gancho",         "text": "..."},
  {"scene": "Cena2_ConceitoLatente","text": "..."}
]

Requisitos: edge-tts (pip install edge-tts) + ffmpeg + internet (para o TTS).
"""
import argparse, asyncio, json, os, shutil, subprocess, sys


def find_ffmpeg(explicit=None):
    """ffmpeg nem sempre está no PATH. Procura em ordem: --ffmpeg, $FFMPEG,
    PATH, imageio-ffmpeg, e alguns locais comuns no Windows."""
    cands = []
    if explicit:
        cands.append(explicit)
    if os.environ.get("FFMPEG"):
        cands.append(os.environ["FFMPEG"])
    w = shutil.which("ffmpeg")
    if w:
        cands.append(w)
    try:
        import imageio_ffmpeg
        cands.append(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        pass
    cands += [
        r"C:\Users\%s\AppData\Local\Programs\Stremio\ffmpeg.exe" % os.environ.get("USERNAME", ""),
        r"C:\ffmpeg\bin\ffmpeg.exe",
        "/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg",
    ]
    for c in cands:
        if c and os.path.exists(c):
            return c
        if c and shutil.which(c):
            return c
    sys.exit("ERRO: ffmpeg não encontrado. Passe --ffmpeg <caminho> ou instale-o.")


def dur(path):
    """Duração em segundos via PyAV (sem depender de ffprobe)."""
    import av
    c = av.open(path)
    d = float(c.duration) / av.time_base if c.duration else 0.0
    c.close()
    return d


async def gen_audio(items, voice, rate, adir):
    import edge_tts
    os.makedirs(adir, exist_ok=True)
    for i, it in enumerate(items, 1):
        out = os.path.join(adir, f"cena{i}.mp3")
        it["audio"] = out
        if os.path.exists(out):
            print(f"  áudio {i} ({it['scene']}): (existente) {dur(out):.1f}s")
            continue
        await edge_tts.Communicate(it["text"], voice, rate=rate).save(out)
        print(f"  áudio {i} ({it['scene']}): {dur(out):.1f}s")


def mux_scene(it, idx, ffmpeg, vdir, sdir, fps):
    vid = os.path.join(vdir, it["scene"] + ".mp4")
    if not os.path.exists(vid):
        sys.exit(f"ERRO: vídeo não encontrado: {vid}")
    aud = it["audio"]
    out = os.path.join(sdir, f"cena{idx}.mp4")
    V, A = dur(vid), dur(aud)
    T = max(V, A) + 0.4               # folga no fim
    padv = (T - V) + 0.5             # congela último quadro
    flt = (f"[0:v]tpad=stop_mode=clone:stop_duration={padv:.2f}[v];"
           f"[1:a]apad[a]")
    cmd = [ffmpeg, "-y", "-i", vid, "-i", aud,
           "-filter_complex", flt, "-map", "[v]", "-map", "[a]",
           "-t", f"{T:.2f}", "-r", str(fps),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
           "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
           "-ac", "2", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ERRO ffmpeg (cena {idx}):\n{r.stderr[-1500:]}")
    print(f"  cena {idx}: vídeo {V:.1f}s | voz {A:.1f}s -> {dur(out):.1f}s")
    return out


def concat(parts, ffmpeg, sdir, out):
    lst = os.path.join(sdir, "lista.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    r = subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", out], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ERRO ffmpeg (concat):\n{r.stderr[-1500:]}")
    print(f"\nFINAL: {out}  ({dur(out):.1f}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos-dir", required=True, help="pasta com as cenas .mp4 do Manim")
    ap.add_argument("--narration", required=True, help="JSON ordenado [{scene,text}]")
    ap.add_argument("--voice", default="pt-BR-ThalitaNeural")
    ap.add_argument("--rate", default="-4%", help="ritmo da fala, ex.: -4%%")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--out", default="video_final.mp4")
    ap.add_argument("--ffmpeg", default=None)
    ap.add_argument("--audio-dir", default="media/audio")
    ap.add_argument("--work-dir", default="media/scenes_av")
    a = ap.parse_args()

    ffmpeg = find_ffmpeg(a.ffmpeg)
    os.makedirs(a.work_dir, exist_ok=True)
    with open(a.narration, encoding="utf-8") as f:
        items = json.load(f)
    if not isinstance(items, list):
        sys.exit("narration.json deve ser uma LISTA ordenada de {scene, text}.")

    print(f"ffmpeg: {ffmpeg}")
    print("1) Narração (edge-tts)...")
    asyncio.run(gen_audio(items, a.voice, a.rate, a.audio_dir))
    print("2) Juntando voz a cada cena...")
    parts = [mux_scene(it, i, ffmpeg, a.videos_dir, a.work_dir, a.fps)
             for i, it in enumerate(items, 1)]
    print("3) Concatenando...")
    concat(parts, ffmpeg, a.work_dir, a.out)


if __name__ == "__main__":
    main()
