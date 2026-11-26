# -*- coding: utf-8 -*-
"""
pos_producao.py — Acabamento do vídeo montado (Etapa 7), tudo configurável em
video.config.json -> pos_producao.

O que faz (cada item liga/desliga na config ou por flag):
  - legendas .srt a partir do tempo EXATO da narração (sem transcrever de novo);
    opcionalmente queimadas no vídeo, na fonte do vídeo (CMU Serif);
  - capítulos embutidos no .mp4 + capitulos.txt no formato do YouTube;
  - música de fundo com fade e ducking (abaixa sob a voz);
  - loudness normalizado em duas passadas (padrão -16 LUFS, -1.5 dBTP);
  - CREDITOS.md com voz, imagens (creditos.json) e música, para a descrição.

USO (de dentro da pasta do projeto, depois do build_video.py):
  python <SKILL>/scripts/pos_producao.py --video video_final.mp4 --mostrar   # só mostra o plano
  python <SKILL>/scripts/pos_producao.py --video video_final.mp4 \
         [--musica assets/audio/trilha.mp3] [--queimar] [--sem-musica] [--out video_pos.mp4]

Títulos de capítulo: campo opcional "titulo" em cada item do narration.json;
sem ele, o nome da cena vira título ("Cena3_ConceitoLatente" -> "Conceito Latente").
"""
import argparse, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _comum import carregar_config, duracao, ffmpeg_ok, find_ffmpeg  # noqa: E402


def titulo_de(item):
    if item.get("titulo"):
        return item["titulo"]
    nome = re.sub(r"^Cena\d+_?", "", item["scene"])
    return re.sub(r"(?<=[a-zà-ú])(?=[A-ZÀ-Ú])", " ", nome).replace("_", " ").strip() or item["scene"]


def hms(t, srt=False):
    h, r = divmod(max(t, 0), 3600)
    m, s = divmod(r, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    return f"{int(h)}:{int(m):02d}:{int(s):02d}" if h else f"{int(m):02d}:{int(s):02d}"


def blocos_legenda(texto, ini, dur, maxc):
    """Quebra o texto em blocos de até 2 linhas de maxc caracteres, preferindo
    pontuação; devolve [(t0, t1, texto)] em segundos relativos à cena."""
    lim = 2 * maxc
    partes, atual, i0 = [], "", 0
    for m in re.finditer(r"\S+\s*", texto):
        pal = m.group()
        if atual and len(atual) + len(pal.rstrip()) > lim:
            partes.append((i0, atual.strip()))
            atual, i0 = "", m.start()
        if not atual:
            i0 = m.start()
        atual += pal
        if re.search(r"[.?!;:]\s*$", pal) and len(atual) > maxc * 0.6:
            partes.append((i0, atual.strip()))
            atual = ""
    if atual.strip():
        partes.append((i0, atual.strip()))
    out = []
    for k, (ic, txt) in enumerate(partes):
        t0 = ini[min(ic, len(ini) - 1)]
        t1 = ini[min(partes[k + 1][0], len(ini) - 1)] - 0.05 if k + 1 < len(partes) else dur - 0.1
        if len(txt) > maxc:                                # 2 linhas equilibradas
            meio = len(txt) // 2
            corte = min((p.start() for p in re.finditer(" ", txt)), key=lambda p: abs(p - meio), default=None)
            if corte:
                txt = txt[:corte] + "\n" + txt[corte + 1:]
        out.append((t0, max(t1, t0 + 0.6), txt))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="video_final.mp4")
    ap.add_argument("--narration", default="narration.json")
    ap.add_argument("--cenas", default="media/scenes_av/cenas.json")
    ap.add_argument("--out", default=None)
    ap.add_argument("--musica", default=None)
    ap.add_argument("--sem-musica", action="store_true")
    ap.add_argument("--queimar", action="store_true", help="queima as legendas no vídeo")
    ap.add_argument("--mostrar", action="store_true", help="só mostra o que seria feito")
    ap.add_argument("--ffmpeg", default=None)
    a = ap.parse_args()

    cfg = carregar_config(".")
    pp, fonte = cfg["pos_producao"], cfg["fonte"].get("texto", "CMU Serif")
    leg, mus, ln = pp["legendas"], pp["musica"], pp["loudness"]
    musica = None if a.sem_musica else (a.musica or mus.get("arquivo") or None)
    queimar = a.queimar or leg.get("queimar", False)
    base = os.path.splitext(a.video)[0]
    out = a.out or base + "_pos.mp4"
    if not os.path.exists(a.cenas):
        sys.exit(f"ERRO: {a.cenas} não existe; rode build_video.py antes.")
    cenas = json.load(open(a.cenas, encoding="utf-8"))
    itens = {it["scene"]: it for it in json.load(open(a.narration, encoding="utf-8"))}
    D = duracao(a.video)

    print("Plano de pós-produção:")
    print(f"  legendas .srt: {'sim' if leg.get('srt', True) else 'não'}"
          f"{' (queimadas, fonte ' + fonte + ')' if queimar else ''}")
    print(f"  capítulos: {'sim' if pp.get('capitulos', True) else 'não'} ({len(cenas)})")
    det_mus = " ({} dB, ducking {})".format(mus.get("volume_db"), mus.get("ducking")) if musica else ""
    det_ln = "{} LUFS / {} dBTP".format(ln.get("lufs"), ln.get("true_peak")) if ln.get("normalizar") else "não"
    print(f"  música: {musica or 'nenhuma'}{det_mus}")
    print(f"  loudness: {det_ln}")
    print(f"  saída: {out}  (de {a.video}, {D:.1f}s)")
    if pp.get("capitulos", True):
        for c in cenas:
            print(f"    {hms(c['inicio'])}  {titulo_de(itens.get(c['scene'], c))}")
    if a.mostrar:
        return

    ffmpeg = find_ffmpeg(a.ffmpeg)
    # --- legendas
    srt = base + ".srt"
    if leg.get("srt", True) or queimar:
        n, linhas = 0, []
        for c in cenas:
            d = json.load(open(c["timing"], encoding="utf-8"))
            for t0, t1, txt in blocos_legenda(d["text"], d["start"], d["duration"], leg.get("max_caracteres", 42)):
                n += 1
                linhas.append(f"{n}\n{hms(c['inicio'] + t0, True)} --> {hms(c['inicio'] + t1, True)}\n{txt}\n")
        open(srt, "w", encoding="utf-8").write("\n".join(linhas))
        print(f"legendas: {srt} ({n} blocos)")
    # --- capítulos
    meta = base + ".capitulos.ffmeta"
    if pp.get("capitulos", True):
        txt = [";FFMETADATA1"]
        yt = []
        for k, c in enumerate(cenas):
            fim = cenas[k + 1]["inicio"] if k + 1 < len(cenas) else D
            t = titulo_de(itens.get(c["scene"], c))
            txt += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(c['inicio'] * 1000)}",
                    f"END={int(fim * 1000)}", f"title={t}"]
            yt.append(f"{hms(c['inicio'])} {t}")
        open(meta, "w", encoding="utf-8").write("\n".join(txt) + "\n")
        open("capitulos.txt", "w", encoding="utf-8").write("\n".join(yt) + "\n")
        print("capítulos: capitulos.txt (cole na descrição do YouTube)")

    # --- áudio: música + ducking
    entradas = ["-i", a.video]
    if musica:
        entradas += ["-stream_loop", "-1", "-i", musica]
    fade = mus.get("fade_s", 2.0)
    if musica:
        f = (f"[1:a]volume={mus.get('volume_db', -24)}dB,atrim=0:{D:.2f},asetpts=N/SR/TB,"
             f"afade=t=in:d={fade},afade=t=out:st={max(D - fade, 0):.2f}:d={fade}[m];")
        if mus.get("ducking", True):
            f += ("[0:a]asplit[v1][v2];[m][v2]sidechaincompress=threshold=0.02:ratio=6:"
                  "attack=30:release=500[md];[v1][md]amix=inputs=2:duration=first:normalize=0[mix]")
        else:
            f += "[0:a][m]amix=inputs=2:duration=first:normalize=0[mix]"
    else:
        f = "[0:a]anull[mix]"
    # --- loudness (2 passadas)
    alvo = f"I={ln.get('lufs', -16)}:TP={ln.get('true_peak', -1.5)}:LRA=11"
    if ln.get("normalizar", True):
        r = subprocess.run([ffmpeg, "-hide_banner", "-nostats", *entradas, "-filter_complex",
                            f + f";[mix]loudnorm={alvo}:print_format=json[o]", "-map", "[o]",
                            "-t", f"{D:.2f}", "-f", "null", "-"], capture_output=True, text=True)
        m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)
        if m:
            d = json.loads(m.group())
            alvo += (f":measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
                     f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true")
            print(f"loudness medido: {d['input_i']} LUFS -> {ln.get('lufs', -16)}")
        f += f";[mix]loudnorm={alvo},aresample=48000[aout]"
    else:
        f += ";[mix]anull[aout]"
    # --- vídeo
    if queimar:
        esc = srt.replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
        estilo = (f"FontName={fonte},FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
                  "BorderStyle=1,Outline=1.2,Shadow=0,MarginV=36")
        f += f";[0:v]subtitles='{esc}':force_style='{estilo}'[vout]"
        vmap, vcod = "[vout]", ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p"]
    else:
        vmap, vcod = "0:v", ["-c:v", "copy"]
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", *entradas]
    if pp.get("capitulos", True):
        cmd += ["-i", meta]
    cmd += ["-filter_complex", f, "-map", vmap, "-map", "[aout]", *vcod,
            "-c:a", "aac", "-b:a", "192k", "-t", f"{D:.2f}"]
    if pp.get("capitulos", True):
        idx = 2 if musica else 1
        cmd += ["-map_metadata", str(idx), "-map_chapters", str(idx)]
    cmd += ["-movflags", "+faststart", out]
    ffmpeg_ok(cmd, "pós-produção")
    print(f"FINAL: {out} ({duracao(out):.1f}s)")

    # --- créditos
    linhas = ["# Créditos", ""]
    vozes = {json.dumps(json.load(open(c["timing"], encoding="utf-8")).get("voz", {}), sort_keys=True) for c in cenas}
    for v in vozes:
        v = json.loads(v)
        if v:
            linhas.append(f"- Narração: voz sintética ({v.get('provedor')}"
                          f"{', ' + str(v.get('voz') or v.get('voz_id')) if (v.get('voz') or v.get('voz_id')) else ''})")
    linhas.append("- Animações: Manim Community")
    cp = os.path.join(cfg["imagens"].get("pasta", "assets/imagens"), "creditos.json")
    if os.path.exists(cp):
        for arq, m in json.load(open(cp, encoding="utf-8")).items():
            linhas.append(f"- Imagem “{m.get('titulo') or arq}”: {m.get('autor') or 'autor não informado'}, "
                          f"{m.get('licenca') or 'licença a verificar'} — {m.get('pagina', '')}")
    if musica:
        linhas.append(f"- Música: {os.path.basename(musica)} (preencha autor e licença)")
    open("CREDITOS.md", "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    print("créditos: CREDITOS.md")


if __name__ == "__main__":
    main()
