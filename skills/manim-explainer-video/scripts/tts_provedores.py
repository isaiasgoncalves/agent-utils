# -*- coding: utf-8 -*-
"""
tts_provedores.py — Provedores de voz trocáveis para narrar.py.

Cada provedor recebe o texto de uma cena e grava um .mp3. Quando o provedor
devolve o tempo de cada palavra/caractere (ElevenLabs, edge-tts), ele é usado
direto; quando não devolve (Gemini, OpenAI, comando próprio), o tempo vem de um
alinhamento com Whisper local sobre o áudio gerado.

Provedores (escolha em video.config.json -> tts.provedor, ou --provedor):
  elevenlabs  pago, melhor pt-BR, tempo por caractere nativo   ELEVENLABS_API_KEY
  gemini      barato/grátis no AI Studio, voz dirigível por estilo  GEMINI_API_KEY ou GOOGLE_API_KEY
  openai      barato, voz dirigível por instruções              OPENAI_API_KEY
  edge        grátis, sem chave (serviço da Microsoft)          —
  comando     qualquer TTS local (Piper, Chatterbox, F5, XTTS) via linha de comando
  auto        o primeiro de tts.ordem_auto que estiver configurado

Para incluir um provedor novo: escreva _sint_<nome>(texto, c, base, ctx) que
grave o áudio e devolva (caminho_audio, palavras|None), registre em PROVEDORES
e em DISPONIVEL. palavras = [(token, t0, t1)] em segundos, na ordem falada.
"""
import asyncio, base64, json, os, re, shlex, subprocess, sys, tempfile, urllib.error, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _comum import duracao, ffmpeg_ok, find_ffmpeg  # noqa: E402


class ErroTTS(RuntimeError):
    pass


# ---------------------------------------------------------------- HTTP -----
def _http(url, corpo=None, cabecalhos=None, segredo=None, timeout=180, metodo=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(url, data=dados, method=metodo or ("POST" if dados else "GET"),
                                 headers={"Content-Type": "application/json", **(cabecalhos or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(), r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")[:800]
        if segredo:
            msg = msg.replace(segredo, "[redacted]")
        raise ErroTTS(f"HTTP {e.code} em {url.split('?')[0]}: {msg}") from None
    except urllib.error.URLError as e:
        raise ErroTTS(f"sem conexão com {url.split('?')[0]}: {e.reason}") from None


def _chave(*nomes):
    for n in nomes:
        if os.environ.get(n):
            return os.environ[n]
    return None


def _para_mp3(origem, mp3):
    if os.path.abspath(origem) == os.path.abspath(mp3):
        return mp3
    ffmpeg_ok([find_ffmpeg(), "-y", "-loglevel", "error", "-i", origem,
               "-codec:a", "libmp3lame", "-q:a", "2", "-ar", "44100", mp3], "converter voz")
    os.remove(origem)
    return mp3


# ------------------------------------------------------------- provedores ---
def _sint_elevenlabs(texto, c, mp3, ctx):
    chave = _chave("ELEVENLABS_API_KEY", "XI_API_KEY")
    if not chave:
        raise ErroTTS("defina ELEVENLABS_API_KEY")
    if not c.get("voz_id"):
        raise ErroTTS("defina tts.elevenlabs.voz_id (liste com: narrar.py --listar-vozes elevenlabs)")
    modelo = c.get("modelo", "eleven_multilingual_v2")
    corpo = {"text": texto, "model_id": modelo,
             "voice_settings": {"stability": c.get("estabilidade", 0.45),
                                "similarity_boost": c.get("similaridade", 0.8),
                                "style": c.get("estilo", 0.15),
                                "use_speaker_boost": c.get("speaker_boost", True),
                                "speed": c.get("velocidade", 1.0)}}
    if c.get("idioma") and re.search(r"flash|turbo|v3", modelo):
        corpo["language_code"] = c["idioma"]          # só esses modelos aceitam forçar idioma
    if "v3" not in modelo:                            # continuidade de prosódia entre cenas
        if ctx.get("anterior"):
            corpo["previous_text"] = ctx["anterior"][-1000:]
        if ctx.get("seguinte"):
            corpo["next_text"] = ctx["seguinte"][:1000]
    url = (f"https://api.elevenlabs.io/v1/text-to-speech/{c['voz_id']}/with-timestamps"
           f"?output_format={c.get('formato', 'mp3_44100_128')}")
    bruto, _ = _http(url, corpo, {"xi-api-key": chave}, chave)
    d = json.loads(bruto)
    with open(mp3, "wb") as f:
        f.write(base64.b64decode(d["audio_base64"]))
    al = d.get("alignment") or d.get("normalized_alignment")
    if not al:
        return mp3, None
    palavras, tok, t0, t1 = [], "", None, None     # caracteres -> palavras
    for ch, a, b in zip(al["characters"], al["character_start_times_seconds"],
                        al["character_end_times_seconds"]):
        if ch.isspace():
            if tok:
                palavras.append((tok, t0, t1))
            tok, t0 = "", None
            continue
        if not tok:
            t0 = a
        tok += ch
        t1 = b
    if tok:
        palavras.append((tok, t0, t1))
    return mp3, palavras


def _sint_gemini(texto, c, mp3, ctx):
    chave = _chave("GEMINI_API_KEY", "GOOGLE_API_KEY")
    if not chave:
        raise ErroTTS("defina GEMINI_API_KEY (grátis em aistudio.google.com)")
    modelo = c.get("modelo", "gemini-3.8-flash-tts")
    moderno = modelo.startswith("gemini-3.8-")
    estilo = c.get("estilo", "")
    conteudo = {"type": "text",
                "text": (f"Read the following text with this delivery: {estilo}\n\n{texto}"
                         if estilo and not moderno else texto)}
    if estilo and moderno:
        conteudo["annotations"] = [{"type": "speech_metadata", "style": estilo}]
    corpo = {"model": modelo,
             "input": [{"type": "user_input", "content": [conteudo]}],
             "response_format": ({"type": "audio", "mime_type": "audio/wav"} if moderno
                                 else {"type": "audio"}),
             "generation_config": {"speech_config": [{"voice": c.get("voz", "Kore")}]},
             "store": False}
    bruto, _ = _http("https://generativelanguage.googleapis.com/v1beta/interactions",
                     corpo, {"x-goog-api-key": chave}, chave)
    d = json.loads(bruto)
    if d.get("status") != "completed":
        raise ErroTTS(f"Gemini não concluiu ({d.get('status')})")
    partes = [p for s in d.get("steps", []) if s.get("type") == "model_output"
              for p in s.get("content", []) if p.get("type") == "audio"]
    if len(partes) != 1 or not partes[0].get("data"):
        raise ErroTTS("Gemini não devolveu um bloco de áudio")
    dados, mime = base64.b64decode(partes[0]["data"]), partes[0].get("mime_type", "")
    wav = mp3[:-4] + ".wav"
    if dados[:4] == b"RIFF":
        open(wav, "wb").write(dados)
    else:                                            # PCM s16le cru (modelos antigos)
        m = re.search(r"rate=(\d+)", mime)
        taxa = m.group(1) if m else "24000"
        raw = mp3[:-4] + ".pcm"
        open(raw, "wb").write(dados)
        ffmpeg_ok([find_ffmpeg(), "-y", "-loglevel", "error", "-f", "s16le", "-ar", taxa,
                   "-ac", "1", "-i", raw, wav], "PCM -> wav")
        os.remove(raw)
    return _para_mp3(wav, mp3), None


def _sint_openai(texto, c, mp3, ctx):
    chave = _chave("OPENAI_API_KEY")
    if not chave:
        raise ErroTTS("defina OPENAI_API_KEY")
    corpo = {"model": c.get("modelo", "gpt-4o-mini-tts"), "voice": c.get("voz", "coral"),
             "input": texto, "response_format": "mp3", "speed": c.get("velocidade", 1.0)}
    if c.get("instrucoes") and "tts-1" not in corpo["model"]:
        corpo["instructions"] = c["instrucoes"]
    bruto, _ = _http("https://api.openai.com/v1/audio/speech", corpo,
                     {"Authorization": f"Bearer {chave}"}, chave)
    open(mp3, "wb").write(bruto)
    return mp3, None


def _sint_edge(texto, c, mp3, ctx):
    try:
        import edge_tts
    except ImportError:
        raise ErroTTS("pip install -U edge-tts") from None

    async def run():
        com = edge_tts.Communicate(texto, c.get("voz", "pt-BR-ThalitaNeural"),
                                   rate=c.get("rate", "-4%"), boundary="WordBoundary")
        palavras = []
        with open(mp3, "wb") as f:
            async for ch in com.stream():
                if ch["type"] == "audio":
                    f.write(ch["data"])
                elif ch["type"] == "WordBoundary":
                    t0 = ch["offset"] / 1e7
                    palavras.append((ch["text"], t0, t0 + ch["duration"] / 1e7))
        return palavras
    return mp3, asyncio.run(run())


def _sint_comando(texto, c, mp3, ctx):
    """Roda um TTS local qualquer. Em cmd: {texto} = arquivo .txt com o texto,
    {saida} = arquivo de áudio a gravar (extensão tts.comando.ext)."""
    if not c.get("cmd"):
        raise ErroTTS("defina tts.comando.cmd (veja o _exemplo em config_padrao.json)")
    saida = mp3[:-4] + "." + c.get("ext", "wav")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(texto)
        txt = f.name
    try:
        cmd = c["cmd"].format(texto=shlex.quote(txt), saida=shlex.quote(saida))
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(saida):
            raise ErroTTS(f"comando falhou ({r.returncode}): {r.stderr[-800:]}")
    finally:
        os.remove(txt)
    return _para_mp3(saida, mp3), None


PROVEDORES = {"elevenlabs": _sint_elevenlabs, "gemini": _sint_gemini,
              "openai": _sint_openai, "edge": _sint_edge, "comando": _sint_comando}

DISPONIVEL = {
    "elevenlabs": lambda c: bool(_chave("ELEVENLABS_API_KEY", "XI_API_KEY") and c.get("voz_id")),
    "gemini": lambda c: bool(_chave("GEMINI_API_KEY", "GOOGLE_API_KEY")),
    "openai": lambda c: bool(_chave("OPENAI_API_KEY")),
    "edge": lambda c: True,
    "comando": lambda c: bool(c.get("cmd")),
}

# o que, se mudar, obriga a regenerar o áudio
_CHAVES_ASSINATURA = {"elevenlabs": ["voz_id", "modelo", "estabilidade", "similaridade", "estilo", "velocidade"],
                      "gemini": ["modelo", "voz", "estilo"], "openai": ["modelo", "voz", "instrucoes", "velocidade"],
                      "edge": ["voz", "rate"], "comando": ["cmd"]}


def escolher(cfg_tts, forcado=None):
    nome = forcado or cfg_tts.get("provedor", "auto")
    if nome != "auto":
        if nome not in PROVEDORES:
            raise ErroTTS(f"provedor desconhecido: {nome} (opções: {', '.join(PROVEDORES)})")
        return nome
    for n in cfg_tts.get("ordem_auto", list(PROVEDORES)):
        if n in DISPONIVEL and DISPONIVEL[n](cfg_tts.get(n, {})):
            return n
    return "edge"


def assinatura(cfg_tts, nome):
    c = cfg_tts.get(nome, {})
    return {"provedor": nome, **{k: c.get(k) for k in _CHAVES_ASSINATURA.get(nome, [])}}


def sintetizar(texto, cfg_tts, nome, mp3, ctx=None, idioma="pt-BR"):
    """Grava mp3 e devolve (palavras, origem_do_tempo)."""
    audio, palavras = PROVEDORES[nome](texto, cfg_tts.get(nome, {}), mp3, ctx or {})
    if palavras:
        return palavras, nome
    modo = cfg_tts.get("alinhamento", "auto")
    if modo in ("auto", "whisper"):
        try:
            return alinhar_whisper(audio, texto, cfg_tts.get("whisper_modelo", "small"), idioma), "whisper"
        except ErroTTS as e:
            if modo == "whisper":
                raise
            print(f"  aviso: {e}; usando tempo proporcional (aproximado)")
    return alinhar_proporcional(texto, duracao(audio, 0.0)), "proporcional"


# -------------------------------------------------------------- alinhamento -
def alinhar_whisper(audio, texto, modelo="small", idioma="pt-BR"):
    lang = idioma.split("-")[0].lower()
    try:
        from faster_whisper import WhisperModel
        m = WhisperModel(modelo, device="auto", compute_type="int8")
        segs, _ = m.transcribe(audio, language=lang, word_timestamps=True,
                               initial_prompt=texto[:800], vad_filter=False)
        return [(w.word, w.start, w.end) for s in segs for w in (s.words or [])]
    except ImportError:
        pass
    exe = os.environ.get("WHISPER_CT2") or "whisper-ctranslate2"
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [exe, audio, "--model", modelo, "--language", lang, "--word_timestamps", "True",
               "--output_format", "json", "--output_dir", tmp, "--initial_prompt", texto[:800],
               "--compute_type", "int8", "--verbose", "False"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError:
            raise ErroTTS("Whisper não encontrado (uv tool install whisper-ctranslate2 "
                          "ou pip install faster-whisper)") from None
        js = [f for f in os.listdir(tmp) if f.endswith(".json")]
        if r.returncode != 0 or not js:
            raise ErroTTS(f"Whisper falhou: {r.stderr[-400:]}")
        d = json.load(open(os.path.join(tmp, js[0]), encoding="utf-8"))
    return [(w["word"], w["start"], w["end"]) for s in d.get("segments", []) for w in s.get("words", [])]


def alinhar_proporcional(texto, dur):
    toks = texto.split()
    peso = [len(t) + 2 for t in toks]
    total, t, out = sum(peso) or 1, 0.15, []
    util = max(dur - 0.4, 0.1)
    for tk, p in zip(toks, peso):
        d = util * p / total
        out.append((tk, t, t + d))
        t += d
    return out


# ------------------------------------------------------------------ vozes ---
def listar_vozes(nome, cfg_tts, idioma="pt-BR"):
    lang = idioma.split("-")[0].lower()
    if nome == "elevenlabs":
        chave = _chave("ELEVENLABS_API_KEY", "XI_API_KEY")
        if not chave:
            raise ErroTTS("defina ELEVENLABS_API_KEY")
        bruto, _ = _http("https://api.elevenlabs.io/v1/voices", None, {"xi-api-key": chave}, chave)
        print("== Suas vozes (use o voz_id em tts.elevenlabs.voz_id)")
        for v in json.loads(bruto).get("voices", []):
            lab = v.get("labels") or {}
            print(f"  {v['voice_id']}  {v['name']:<24} {lab.get('accent', '')} {lab.get('language', '')}")
        bruto, _ = _http(f"https://api.elevenlabs.io/v1/shared-voices?language={lang}&page_size=30"
                         "&sort=trending", None, {"xi-api-key": chave}, chave)
        print(f"\n== Biblioteca pública em '{lang}' (adicione em 'My Voices' no site antes de usar)")
        for v in json.loads(bruto).get("voices", []):
            print(f"  {v['voice_id']}  {v['name']:<24} {v.get('accent', '')} {v.get('gender', '')} "
                  f"{v.get('use_case', '')}")
    elif nome == "edge":
        r = subprocess.run([sys.executable, "-m", "edge_tts", "--list-voices"], capture_output=True, text=True)
        print("\n".join(l for l in r.stdout.splitlines() if l.startswith(idioma) or l.startswith("Name")))
    elif nome == "gemini":
        print("Vozes prebuilt do Gemini (multilíngues; o sotaque vem do texto e do 'estilo'):\n"
              "  femininas: Kore (firme), Aoede (leve), Leda (jovem), Callirrhoe, Autonoe, Despina,\n"
              "             Erinome, Laomedeia, Achernar, Gacrux, Pulcherrima, Vindemiatrix, Sulafat, Zephyr\n"
              "  masculinas: Charon (informativa), Puck (animada), Fenrir, Orus (firme), Iapetus (clara),\n"
              "              Enceladus, Algieba, Algenib, Rasalgethi, Alnilam, Schedar, Achird,\n"
              "              Zubenelgenubi, Sadachbia, Sadaltager, Umbriel")
    elif nome == "openai":
        print("Vozes OpenAI: alloy ash ballad coral echo fable nova onyx sage shimmer verse marin cedar")
    else:
        print(f"{nome}: sem listagem; veja a documentação do seu TTS.")
