# -*- coding: utf-8 -*-
"""
narrar.py — Gera a narração de cada cena JÁ com o tempo de cada palavra.

Roda ANTES de escrever o código Manim, de dentro da pasta do projeto. Para cada
item do narration.json:
  media/audio/cena{i}.mp3      -> o áudio (o build_video.py reaproveita este arquivo)
  media/audio/<scene>.json     -> início (s) de cada caractere da narração,
                                  lido pela CenaSync para cronometrar as animações
e imprime os "cues": o instante em que cada frase começa.

O provedor de voz é trocável (veja tts_provedores.py): ElevenLabs, Gemini,
OpenAI, edge-tts ou um comando local. Configure em video.config.json -> tts.

USO:
    python <SKILL>/scripts/narrar.py narration.json                 # gera o que faltar + cues
    python <SKILL>/scripts/narrar.py narration.json --cues          # só imprime cues
    python <SKILL>/scripts/narrar.py narration.json --force Cena3_X # regenera essa(s) cena(s)
    python <SKILL>/scripts/narrar.py narration.json --provedor gemini --voz Charon
    python <SKILL>/scripts/narrar.py --listar-vozes elevenlabs
    python <SKILL>/scripts/narrar.py --qual                         # mostra o provedor escolhido
Trocar provedor/voz/estilo regenera sozinho as cenas afetadas (a assinatura fica no JSON).
"""
import argparse, json, os, re, sys, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _comum import carregar_config, duracao  # noqa: E402
import tts_provedores as tts  # noqa: E402


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def limpar(texto):
    return re.sub(r"\s+", " ", texto).strip()


def aplicar_pronuncia(texto, mapa):
    """Troca grafias que o TTS lê mal (ex.: {"HMM": "agá eme eme"}) e devolve
    (texto_falado, mapa_indice) para levar os tempos de volta ao texto original."""
    if not mapa:
        return texto, list(range(len(texto)))
    padrao = re.compile("|".join(r"(?<!\w)" + re.escape(k) + r"(?!\w)"
                                 for k in sorted(mapa, key=len, reverse=True)))
    falado, idx, ult = [], [], 0
    for m in padrao.finditer(texto):
        for j in range(ult, m.start()):
            idx.append(len(falado)); falado.append(texto[j])
        rep, ini = mapa[m.group()], len(falado)
        for k in range(m.start(), m.end()):    # caracteres trocados apontam para o início
            idx.append(ini + int((k - m.start()) * len(rep) / max(1, m.end() - m.start())))
        falado.extend(rep)
        ult = m.end()
    for j in range(ult, len(texto)):
        idx.append(len(falado)); falado.append(texto[j])
    return "".join(falado), idx


def alinhar(texto, palavras):
    """palavras: [(token, t0, t1)] na ordem falada. Devolve início por caractere."""
    alvo = norm(texto)
    ini = [None] * len(texto)
    cur = 0
    for tok, t0, t1 in palavras:
        tk = norm(tok).strip().strip(".,;:!?\"'()[]«»“”")
        if not tk:
            continue
        pos = alvo.find(tk, cur, cur + 80 + len(tk))
        if pos < 0:
            continue                      # token que o TTS normalizou: interpola abaixo
        n = len(tk)
        for k in range(n):
            ini[pos + k] = t0 + (t1 - t0) * k / n
        cur = pos + n
    casados = sum(1 for m in re.finditer(r"\S+", texto)
                  if any(ini[j] is not None for j in range(m.start(), m.end())))
    ult = 0.0                            # lacunas herdam o último instante conhecido
    for i in range(len(ini)):
        if ini[i] is None:
            ini[i] = ult
        else:
            ult = ini[i]
    return ini, casados


def cues(texto, ini):
    out = []
    for m in re.finditer(r"[^.?!:;]+[.?!:;]?", texto):
        s = m.start() + (len(m.group()) - len(m.group().lstrip()))
        if m.group().strip():
            out.append(f"{ini[s]:7.2f}s  {m.group().strip()}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("narration", nargs="?")
    ap.add_argument("--config", default=None, help="caminho de um video.config.json")
    ap.add_argument("--provedor", default=None, help="elevenlabs|gemini|openai|edge|comando|auto")
    ap.add_argument("--voz", "--voice", dest="voz", default=None, help="voz do provedor escolhido")
    ap.add_argument("--rate", default=None, help="ritmo (edge-tts), ex.: -4%%")
    ap.add_argument("--audio-dir", default="media/audio")
    ap.add_argument("--cues", action="store_true", help="só imprime os cues")
    ap.add_argument("--force", nargs="*", default=[], help="cenas a regenerar")
    ap.add_argument("--listar-vozes", metavar="PROVEDOR", default=None)
    ap.add_argument("--qual", action="store_true", help="mostra qual provedor seria usado")
    a = ap.parse_args()

    cfg = carregar_config(".", a.config)
    ct, idioma = cfg["tts"], cfg.get("idioma", "pt-BR")
    if a.listar_vozes:
        tts.listar_vozes(a.listar_vozes, ct, idioma)
        return
    nome = tts.escolher(ct, a.provedor)
    if a.voz:
        ct.setdefault(nome, {})["voz_id" if nome == "elevenlabs" else "voz"] = a.voz
    if a.rate:
        ct.setdefault("edge", {})["rate"] = a.rate
    assin = tts.assinatura(ct, nome)
    if a.qual or not a.narration:
        print(f"provedor: {nome}  {json.dumps(assin, ensure_ascii=False)}")
        if not a.narration:
            return

    itens = json.load(open(a.narration, encoding="utf-8"))
    os.makedirs(a.audio_dir, exist_ok=True)
    if not a.cues:
        print(f"Voz: {nome} {json.dumps({k: v for k, v in assin.items() if k != 'provedor'}, ensure_ascii=False)}")
    total, erros = 0.0, 0
    for i, it in enumerate(itens, 1):
        cena, texto = it["scene"], limpar(it["text"])
        mp3 = os.path.join(a.audio_dir, f"cena{i}.mp3")
        js = os.path.join(a.audio_dir, cena + ".json")
        velho = False
        if os.path.exists(js):            # texto, posição ou voz mudaram
            d0 = json.load(open(js, encoding="utf-8"))
            velho = (d0.get("text") != texto or d0.get("idx") != i
                     or (not a.cues and d0.get("voz", assin) != assin))
        if not a.cues and (cena in a.force or velho or not (os.path.exists(mp3) and os.path.exists(js))):
            falado, mapa = aplicar_pronuncia(texto, ct.get("pronuncia") or {})
            ctx = {"anterior": limpar(itens[i - 2]["text"]) if i > 1 else "",
                   "seguinte": limpar(itens[i]["text"]) if i < len(itens) else ""}
            try:
                palavras, origem = tts.sintetizar(falado, ct, nome, mp3, ctx, idioma)
            except tts.ErroTTS as e:
                print(f"[{cena}] ERRO: {e}")
                erros += 1
                continue
            dur = duracao(mp3, palavras[-1][2] + 0.3 if palavras else 0.0)
            ini_f, ok = alinhar(falado, palavras)
            ini = [ini_f[min(j, len(ini_f) - 1)] for j in mapa] if ini_f else [0.0] * len(texto)
            nt = len(falado.split())
            json.dump({"scene": cena, "idx": i, "text": texto, "start": ini, "duration": dur,
                       "voz": assin, "tempo": origem},
                      open(js, "w", encoding="utf-8"), ensure_ascii=False)
            aviso = "" if ok >= 0.9 * nt else "  <- poucas palavras casadas: confira cues"
            if origem == "proporcional":
                aviso += "  <- tempo APROXIMADO (instale Whisper para sincronia fina)"
            print(f"[{cena}] {dur:.1f}s, {ok}/{nt} palavras com tempo ({origem}){aviso}")
        if not os.path.exists(js):
            print(f"[{cena}] sem timing (rode sem --cues)")
            continue
        d = json.load(open(js, encoding="utf-8"))
        total += d["duration"]
        print(f"== {cena}  ({d['duration']:.1f}s)")
        print("\n".join(cues(d["text"], d["start"])))
    print(f"\nTotal de fala: {total/60:.1f} min")
    if erros:
        sys.exit(f"{erros} cena(s) sem áudio; corrija o erro acima ou troque o provedor (--provedor edge).")


if __name__ == "__main__":
    main()
