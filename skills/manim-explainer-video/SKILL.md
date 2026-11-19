---
name: "manim-explainer-video"
description: "Cria um vídeo didático estilo 3Blue1Brown (animações em Manim + narração em voz neural) a partir de QUALQUER conteúdo, em qualquer formato: paper/livro (PDF), artigo/URL, texto ou notas, um conceito/tópico, imagem, slides, documento ou planilha. Use SEMPRE que o usuário pedir vídeo explicativo, animação, explicação visual ou vídeo 3b1b/Manim."
---

# Vídeo explicativo estilo 3Blue1Brown (Manim + narração)

Transforma um conteúdo qualquer num vídeo animado e narrado. O fluxo tem 6
etapas encadeadas. Faça-as em ordem; cada etapa produz um artefato que a
seguinte consome.

## Princípios (valem para tudo)
- **Fidelidade ao material acima de tudo.** Não invente resultados. Onde a
  animação simplificar a matemática, sinalize que é simplificação.
- **Intuição antes do formalismo.** Construa a ideia com analogias concretas e
  só então mostre a fórmula. Um conceito novo por vez.
- **Profundidade real, não superfície.** Este é o ponto mais importante e o erro
  mais comum: tratar o assunto raso demais. O objetivo é que o espectador
  ENTENDA o mecanismo, não só ouça um resumo. Para cada ideia central, vá além
  do "o que é" e mostre **por que funciona**: trabalhe pelo menos um exemplo
  concreto com números reais, exponha a fórmula E o significado de cada termo,
  anime o mecanismo passo a passo (não só o resultado), e conecte com a
  evidência/consequências. Prefira aprofundar 3–4 ideias-chave a tocar 10 de
  raspão. "Curto" reduz a QUANTIDADE de tópicos, nunca a profundidade de cada um.
- **Você não consegue assistir ao vídeo.** A verificação é por EXTRAÇÃO DE
  QUADROS (Etapa 4). Trate isso como obrigatório, não opcional.
- **A fala manda no tempo.** A narração é gerada antes da animação, já com o
  instante de cada palavra, e cada animação é disparada pela frase que a explica
  (`self.go("frase")`). Assim imagem e voz andam juntas, em vez de a voz tocar
  sobre uma animação que já acabou ou ainda nem começou.
- **Padrões desta skill:** narração em **pt-BR** (outro idioma só sob demanda);
  voz **`pt-BR-ThalitaNeural`**; vídeo **aprofundado (~5–10 min)**, tipicamente
  10–16 cenas. Ajuste conforme o pedido do usuário.

## Etapa 0 — Verificar o ambiente
Rode `python scripts/check_env.py`. Ele confere manim, **LaTeX** (necessário
para `MathTex`/`Tex`), **ffmpeg** (pode não estar no PATH), **edge-tts**, **PyAV**
e **internet** (o TTS precisa). Instale o que faltar ANTES de renderizar — assim
você não descobre no meio que o render quebra. Faltando algo:
`pip install manim edge-tts av` ; LaTeX via MiKTeX/TeX Live.

## Etapa 1 — Ingerir o conteúdo (qualquer formato) e sintetizar
Esta skill aceita QUALQUER entrada; a única coisa que muda por formato é COMO
extrair o conteúdo. Faça o roteamento por tipo seguindo `references/ingestao_conteudo.md`:
- Identifique **tipo e escopo**. Se a fonte for enorme (livro, vários arquivos) ou
  o tópico for amplo/ambíguo, **pergunte o recorte antes de gerar** (vídeo único da
  tese central vs série; nível introdutório vs avançado).
- Extraia com a ferramenta certa: `Read` (texto/PDF/imagem), `WebFetch`/`WebSearch`
  (URL/tópico a fundamentar), e as skills **`pdf`** (PDF escaneado/OCR), **`docx`**,
  **`pptx`**, **`xlsx`** (Word/slides/planilha). Para tópico sem fonte, use seu
  conhecimento e fundamente com pesquisa se for nicho/recente.

Convergindo tudo: produza uma **síntese técnica de ~1 página** (`1_sintese.md`)
cobrindo o fenômeno/tese central, o setup/definições (cada símbolo na 1ª
aparição), o resultado/mecanismo principal, as evidências/exemplos, e as
figuras/exemplos concretos que virem boas analogias visuais. Mantenha
**fidelidade** (não invente; sinalize simplificações). Esta síntese é a fonte de
verdade das próximas etapas — se ela estiver errada, o vídeo estará errado.

## Etapa 2 — Roteiro por cenas
Escreva `2_roteiro.md` dividido em **cenas numeradas**, seguindo o arco
**intuição → formalismo → evidência**. Para conteúdo aprofundado, mire 10–16
cenas. Para CADA cena especifique:
- **Objetivo pedagógico** (o que o espectador entende ao fim);
- **Narração (voz over)** — texto corrido em pt-BR, lúdico mas rigoroso;
- **Animação** — quais objetos entram e como se transformam.

Arco típico (adapte ao material): gancho/mistério → intuição central com
analogia → construção do conceito → formalização (fórmulas) → mecanismo/prova
(visual) → evidência/experimentos (gráficos) → síntese. Veja a estrutura do
exemplo em `references/example_walkthrough.md`.

Escreva a narração já pensando no ritmo. A voz neural fala cerca de 150–165
palavras por minuto (30 s dão umas 80 palavras; 5 min, umas 800), e cenas entre
15 e 70 s funcionam melhor. Escreva por extenso o que o TTS pode ler de forma
ambígua (decimais, siglas, datas) e garanta que cada momento-chave tenha uma
expressão distinta de três ou mais palavras, porque é ela que vai servir de deixa
para a animação na Etapa 4.

**Garanta a profundidade (não pule isto).** Antes de fechar o roteiro, faça um
"orçamento de profundidade": liste as 3–5 ideias-chave do material e, para CADA
uma, confirme que o roteiro tem cena(s) que mostram (a) a intuição, (b) a
formalização com os símbolos definidos e (c) o mecanismo animado passo a passo —
e que pelo menos uma ideia central tem um **exemplo trabalhado com números
reais**. Se uma ideia aparece só de passagem na narração sem virar animação, ela
está rasa: ou aprofunde-a, ou corte-a do escopo. Sinais de roteiro raso a evitar:
cenas que só exibem definições/bullets, fórmulas sem o significado dos termos,
"resultado" sem mostrar o "porquê", e conteúdo de 5–10 min comprimido em poucas
cenas superficiais. Para um pedido "curto", mantenha menos tópicos, mas cada um
com o mesmo tratamento (intuição + mecanismo + exemplo), em vez de muitos rasos.

## Etapa 3 — Narração com tempo por palavra
A narração vem antes do código, porque é ela que define o tempo das animações.
Escreva `narration.json`, uma lista ORDENADA `[{"scene": "Cena1_Gancho", "text": "..."}]`
com o texto de cada cena (os do roteiro, refinados; estilo e vozes em
`references/narration_and_assembly.md`). O campo `scene` precisa ser exatamente
o nome da classe Manim daquela cena.

Na primeira vez, grave no projeto os arquivos `narrar.py` e `cena_base.py` do
Apêndice, copiando o código como está, e rode:
```bash
python narrar.py narration.json --voice pt-BR-ThalitaNeural
```
Para cada cena ele gera `media/audio/cenaN.mp3`, que o `build_video.py`
reaproveita na montagem, e `media/audio/<Cena>.json` com o instante de cada
palavra; depois imprime os cues, isto é, o segundo em que cada frase começa. Se
uma cena avisar poucas palavras casadas, o TTS leu algo diferente do texto (um
número, uma sigla), então reescreva por extenso e rode de novo. Alterar o texto
de uma cena regenera só o áudio dela. É preciso edge-tts 7 ou superior
(`pip install -U edge-tts`) e internet.

## Etapa 4 — Código Manim cronometrado pela fala
Copie `assets/scene_template.py` para o projeto (ex.: `video.py`) e escreva uma
cena por item do `narration.json`, herdando de `CenaSync` (`from cena_base import *`)
em vez de `Scene`, com o nome da classe igual ao `scene`. Deixe à vista a saída de
`python narrar.py narration.json --cues` e amarre cada animação à frase que a
explica: `self.go("a curva sobe")` espera até essa frase ser dita,
`self.left("e depois estabiliza")` devolve os segundos até a próxima deixa (bom
como `run_time`) e `self.t(...)` dá o instante. Os cues ignoram maiúsculas e
acentos e casam a primeira ocorrência; use `nth=2` para a segunda e `off=-0.3`
para adiantar um pouco. Onde o guia de estilo fala em `self.wait(...)` entre
ideias, prefira `self.go(...)`.
**Antes de escrever, leia `references/manim_style.md`** (estilo, idiomas e — o
mais importante — o catálogo de armadilhas de layout). Regras-chave:
- Use a paleta e os helpers do template. `MathTex` para fórmulas, `Axes` +
  `ValueTracker` para gráficos animados, `Transform` para distribuições que
  colapsam, `VGroup` de `Dot`+`Arrow` para grafos/HMM.
- Comente cada bloco mapeando-o à cena do roteiro e ao trecho da fonte.
- **Toda cena termina com `self.finish()`.** Ele espera a narração acabar, faz
  `FadeOut` de tudo (tela preta, essencial para a montagem da Etapa 6 e para não
  vazar mobjects) e deixa uma folga curta.
- **Ritmo.** Abra no gancho, com algo na tela já no quadro 0 e sem cartão de
  título. Faça algo acontecer a cada frase, porque qualquer coisa parada por mais
  de uns 3 s parece travada. Apague rótulos que já cumpriram seu papel antes de
  reutilizar o espaço, dê contraste alto a texto sobre forma preenchida, anime
  números reais calculados de verdade (rotulando como esquemático o que for
  esquemático) e termine na última ideia, sem frase de despedida.
- Indique no topo a versão-alvo (v0.18+) e o comando de render.

## Etapa 5 — Renderizar rascunho e VERIFICAR (loop)
1. Render rápido: `manim -ql video.py -a` (gera em `media/videos/video/480p15/`).
   Leia a saída: cada `[atrasado Ns]` é uma animação que só começou depois da
   frase que deveria acompanhar. Encurte os `run_time` anteriores ou use `off`
   negativo até não sobrar nenhum.
2. Extraia quadros: `python scripts/extract_frames.py media/videos/video/480p15 --out frames/`.
3. **Leia (Read) os `.jpg`** e procure pelos defeitos do catálogo: texto
   sobreposto, fórmula coberta por barra que cresceu, palavra fora da margem,
   emoji virando "tofu", setas cruzando texto, sobras entre cenas.
4. Corrija no código e repita até cada cena estar limpa. Extraia quadros em
   instantes ESTÁTICOS (logo antes do cue seguinte), não no meio de um `Write`.
   Para mirar um momento específico, divida o instante do cue pela duração da
   cena e passe o resultado em `--fracs`.

Não pule esta etapa: é a única forma de pegar erros de layout sem assistir ao vídeo.

## Etapa 6 — Montar o vídeo único (e versão FHD)
1. Render final em FHD: `manim -qh video.py -a` (gera `1080p60`).
2. Monte com voz:
   ```bash
   python scripts/build_video.py \
     --videos-dir media/videos/video/1080p60 \
     --narration narration.json \
     --voice pt-BR-ThalitaNeural --fps 60 \
     --out video_final.mp4
   ```
   Como os `media/audio/cenaN.mp3` da Etapa 3 já existem, o script os
   reaproveita em vez de sintetizar de novo (por isso use a mesma voz e o mesmo
   `--rate` nos dois comandos). Ele junta voz+vídeo **sem cortar nada** e
   concatena tudo; como cada cena já dura o tempo da sua fala, a voz cai sobre as
   animações certas. Acha o ffmpeg
   sozinho; se não achar, passe `--ffmpeg <caminho>`.
3. **Verifique o resultado** (não dá para ouvir aqui): use o trecho PyAV em
   `references/narration_and_assembly.md` para confirmar fluxo de vídeo+áudio,
   resolução/fps e energia de áudio > 0. Relate honestamente ao usuário que
   conferiu streams/sincronia mas não escutou — sugira um play final.

Dica de iteração: faça a Etapa 5 em `-ql`/`480p15` (rápido) e só renderize
`-qh` quando o layout estiver aprovado. Mudou o texto de uma cena? Rode
`narrar.py` (ele regenera só aquele áudio) e re-renderize essa cena, porque os
tempos mudaram. Para trocar a voz, apague `media/audio/` e rode `narrar.py` de novo.

## Scripts e referências (mapa)
- `scripts/check_env.py` — confere dependências (Etapa 0).
- `scripts/extract_frames.py` — extrai quadros para verificação (Etapa 4).
- `scripts/build_video.py` — junção voz+vídeo e concatenação (Etapa 6);
  reaproveita os áudios da Etapa 3.
- `narrar.py` e `cena_base.py` (Apêndice) — TTS com tempo por palavra e a
  `CenaSync` com `go`/`left`/`t`/`finish` (Etapas 3 e 4).
- `assets/scene_template.py` — paleta, helpers e cena de exemplo (Etapa 3).
- `references/ingestao_conteudo.md` — **roteamento por tipo de entrada** (Etapa 1).
- `references/manim_style.md` — estilo 3b1b, idiomas e **armadilhas de layout**.
- `references/narration_and_assembly.md` — narração, vozes edge-tts, sincronização.
- `references/example_walkthrough.md` — exemplo de ponta a ponta (arco de cenas).

## Saídas que o usuário recebe
`1_sintese.md`, `2_roteiro.md`, `video.py`, `narration.json` e o vídeo final
`video_final.mp4` (FHD com narração). Entregue na ordem síntese → roteiro →
código → vídeo, deixando claro o que foi verificado e o que ele deve revisar.

## Apêndice — `narrar.py` e `cena_base.py`
Grave os dois na raiz do projeto, exatamente como estão.

### narrar.py
```python
# -*- coding: utf-8 -*-
"""
narrar.py — Gera a narração de cada cena (edge-tts) JÁ com o tempo de cada palavra.

Roda ANTES de escrever o código Manim. Para cada item do narration.json:
  media/audio/cena{i}.mp3      -> o áudio (o build_video.py reaproveita este arquivo)
  media/audio/<scene>.json     -> início (s) de cada caractere da narração,
                                  lido pela CenaSync para cronometrar as animações
e imprime os "cues": o instante em que cada frase começa.

USO:
    python narrar.py narration.json                 # gera o que faltar + imprime cues
    python narrar.py narration.json --cues          # só imprime cues (não gera nada)
    python narrar.py narration.json --force Cena3_X # regenera essa(s) cena(s)
Opções: --voice pt-BR-ThalitaNeural  --rate -4%  --audio-dir media/audio
Requisitos: edge-tts >= 7 (boundary="WordBoundary") e internet.
"""
import argparse, asyncio, json, os, re, sys, unicodedata


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def limpar(texto):
    return re.sub(r"\s+", " ", texto).strip()


def alinhar(texto, palavras, duracao):
    """palavras: [(token, t0, t1)] na ordem falada. Devolve início por caractere."""
    alvo = norm(texto)
    ini = [None] * len(texto)
    cur = 0
    for tok, t0, t1 in palavras:
        tk = norm(tok).strip()
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


def duracao_mp3(path, fallback):
    try:
        import av
        c = av.open(path)
        d = float(c.duration) / av.time_base if c.duration else fallback
        c.close()
        return d
    except Exception:
        return fallback


async def sintetizar(texto, voz, rate, mp3):
    import edge_tts
    com = edge_tts.Communicate(texto, voz, rate=rate, boundary="WordBoundary")
    palavras = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                t0 = ch["offset"] / 1e7
                palavras.append((ch["text"], t0, t0 + ch["duration"] / 1e7))
    return palavras


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("narration")
    ap.add_argument("--voice", default="pt-BR-ThalitaNeural")
    ap.add_argument("--rate", default="-4%")
    ap.add_argument("--audio-dir", default="media/audio")
    ap.add_argument("--cues", action="store_true", help="só imprime os cues")
    ap.add_argument("--force", nargs="*", default=[], help="cenas a regenerar")
    a = ap.parse_args()

    itens = json.load(open(a.narration, encoding="utf-8"))
    os.makedirs(a.audio_dir, exist_ok=True)
    total = 0.0
    for i, it in enumerate(itens, 1):
        cena, texto = it["scene"], limpar(it["text"])
        mp3 = os.path.join(a.audio_dir, f"cena{i}.mp3")
        js = os.path.join(a.audio_dir, cena + ".json")
        velho = False
        if os.path.exists(js):                # texto mudou ou cena mudou de posição
            d0 = json.load(open(js, encoding="utf-8"))
            velho = d0.get("text") != texto or d0.get("idx") != i
        if not a.cues and (cena in a.force or velho or not (os.path.exists(mp3) and os.path.exists(js))):
            palavras = asyncio.run(sintetizar(texto, a.voice, a.rate, mp3))
            fim = palavras[-1][2] + 0.3 if palavras else 0.0
            dur = duracao_mp3(mp3, fim)
            ini, ok = alinhar(texto, palavras, dur)
            nt = len(texto.split())
            json.dump({"scene": cena, "idx": i, "text": texto, "start": ini, "duration": dur},
                      open(js, "w", encoding="utf-8"), ensure_ascii=False)
            aviso = "" if ok >= 0.9 * nt else "  <- poucas palavras casadas: confira cues"
            print(f"[{cena}] {dur:.1f}s, {ok}/{nt} palavras com tempo{aviso}")
        if not os.path.exists(js):
            print(f"[{cena}] sem timing (rode sem --cues)")
            continue
        d = json.load(open(js, encoding="utf-8"))
        total += d["duration"]
        print(f"== {cena}  ({d['duration']:.1f}s)")
        print("\n".join(cues(d["text"], d["start"])))
    print(f"\nTotal de fala: {total/60:.1f} min")


if __name__ == "__main__":
    main()
```

### cena_base.py
```python
# -*- coding: utf-8 -*-
"""
cena_base.py — Cena Manim cronometrada pela narração (gerada por narrar.py).

    from cena_base import *

    class Cena2_Ideia(CenaSync):          # nome = "scene" no narration.json
        def construct(self):
            eixo = Axes(...); self.add(eixo)   # algo na tela já no quadro 0
            self.go("a curva sobe")             # espera até essa frase ser dita
            self.play(Create(curva), run_time=self.left("e depois estabiliza"))
            self.finish()                       # obrigatório: completa a fala e faz fade-out

API
  self.t("frase", nth=1, end=False) -> instante (s) em que a frase é dita
  self.go("frase", nth=1, off=0.0)  -> espera até lá (off<0 adianta); avisa [atrasado]
  self.left("frase", off=0, lo=0.3, hi=9) -> segundos até a frase (bom como run_time)
  self.finish(fade=0.5, tail=0.6)   -> espera o fim da fala, FadeOut de tudo, folga
"""
import json, os
import numpy as np
from manim import *

AUDIO_DIR = os.environ.get("NARR_DIR", os.path.join("media", "audio"))
BG = "#0d1117"


def _norm(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


class CenaSync(Scene):
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
```