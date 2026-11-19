# -*- coding: utf-8 -*-
"""
extract_frames.py — Extrai quadros de um vídeo para VERIFICAÇÃO VISUAL.

Por que existe: você (o modelo) não consegue assistir ao vídeo. A única forma
confiável de pegar erros de layout do Manim (texto sobreposto, fórmula coberta
por uma barra que cresceu, palavra estourando a margem, emoji virando "tofu") é
extrair quadros em vários instantes e OLHAR para eles com a ferramenta Read.

Usa PyAV (não depende de ffmpeg/ffprobe no PATH).

USO:
    # frações da duração (padrão: 0.2, 0.45, 0.65, 0.85)
    python extract_frames.py CENA.mp4 --out frames/

    # frações específicas
    python extract_frames.py CENA.mp4 --fracs 0.5 0.9 --out frames/

    # uma pasta inteira de cenas, 4 quadros cada
    python extract_frames.py media/videos/.../1080p60 --out frames/

Depois, leia os .jpg gerados (Read) e procure por sobreposições/cortes.
"""
import argparse, glob, os, sys


def grab(path, fracs, out_dir, quality=80):
    import av
    base = os.path.splitext(os.path.basename(path))[0]
    c = av.open(path)
    st = c.streams.video[0]
    fps = float(st.average_rate)
    total = int(float(c.duration) / av.time_base * fps) if c.duration else 0
    if total <= 0:
        # fallback: decodifica tudo contando
        frames = list(c.decode(video=0))
        total = len(frames)
        targets = {int(f * (total - 1)): int(f * 100) for f in fracs}
        for i, fr in enumerate(frames):
            if i in targets:
                fr.to_image().save(os.path.join(out_dir, f"{base}_p{targets[i]:02d}.jpg"),
                                   quality=quality)
        c.close()
        return
    targets = {int(f * total): int(f * 100) for f in fracs}
    last = max(targets)
    for i, fr in enumerate(c.decode(video=0)):
        if i in targets:
            fr.to_image().save(os.path.join(out_dir, f"{base}_p{targets[i]:02d}.jpg"),
                               quality=quality)
        if i > last:
            break
    c.close()
    print(f"  {base}: {len(targets)} quadros")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="arquivo .mp4 ou pasta com .mp4")
    ap.add_argument("--fracs", type=float, nargs="+",
                    default=[0.2, 0.45, 0.65, 0.85])
    ap.add_argument("--out", default="frames")
    ap.add_argument("--quality", type=int, default=80)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if os.path.isdir(a.target):
        vids = sorted(glob.glob(os.path.join(a.target, "*.mp4")))
    else:
        vids = [a.target]
    if not vids:
        sys.exit("Nenhum .mp4 encontrado.")
    for v in vids:
        grab(v, a.fracs, a.out, a.quality)
    print(f"Quadros em: {a.out}/  (abra com Read)")


if __name__ == "__main__":
    main()
