# Narração (TTS trocável) e montagem final

Leia nas Etapas 3 e 6.

## Escrevendo a narração
- Idioma: **pt-BR por padrão** (`idioma` na config; outro só se o usuário pedir).
- Uma narração por cena, em texto corrido (sem marcação). Tom lúdico mas
  rigoroso: analogias concretas sem perder a fidelidade ao material.
- **Fidelidade acima de tudo:** não invente resultados. Onde a animação
  simplifica a matemática, sinalize ("de forma simplificada...").
- Ritmo: ~150–165 palavras/min. Escreva por extenso decimais, siglas e datas, ou
  use `tts.pronuncia` (abaixo).

## Formato do `narration.json`
Lista ORDENADA; `scene` = nome da classe Manim; `titulo` (opcional) vira o
capítulo na pós-produção:
```json
[
  {"scene": "Cena1_Gancho", "titulo": "O mistério", "text": "Texto da narração da cena 1..."},
  {"scene": "Cena2_ConceitoLatente", "text": "Texto da narração da cena 2..."}
]
```

## Provedores de voz

Escolha em `video.config.json -> tts.provedor` (ou `--provedor`). Com `"auto"`,
vale o primeiro de `tts.ordem_auto` que estiver configurado (chave no ambiente
ou no `.env` do projeto). Trocar provedor/voz/estilo regenera só o necessário.

| Provedor | Qualidade pt-BR | Tempo por palavra | Custo aproximado (confira o preço atual) | Quando usar |
|---|---|---|---|---|
| **elevenlabs** (`eleven_multilingual_v2`) | a melhor: natural, entonação de narrador, sotaque brasileiro real com voz nativa | **nativo, por caractere** (sincronia perfeita) | plano Starter ~US$ 5/mês ≈ 30 min de fala; Creator ~US$ 22/mês ≈ 100 min. Um vídeo de 8 min ≈ 7 mil caracteres | **recomendado** quando o vídeo vai ser publicado |
| **gemini** (`gemini-3.8-flash-tts`) | muito boa, dirigível por instrução de estilo ("professor caloroso, ritmo calmo") | por alinhamento Whisper local (~0,1 s de erro) | nível grátis no AI Studio com limite diário; pago fica na casa de centavos por minuto | **melhor custo-benefício**; grátis para iterar |
| **openai** (`gpt-4o-mini-tts`) | boa, dirigível; sotaque às vezes menos brasileiro | Whisper local | ~US$ 0,015/min | alternativa barata |
| **edge** (`pt-BR-ThalitaNeural`) | ok, robótica em frases longas | nativo, por palavra | grátis, sem chave | rascunho, fallback |
| **comando** | depende do modelo local | Whisper local | grátis | offline: Piper (`pt_BR-faber`), Chatterbox multilíngue, F5-TTS pt-BR, XTTS-v2 (melhor com GPU) |

Configuração mínima de cada um (`video.config.json`; só o que muda):
```json
{"tts": {"provedor": "elevenlabs", "elevenlabs": {"voz_id": "<id>"}}}
{"tts": {"provedor": "gemini", "gemini": {"voz": "Charon", "estilo": "..."}}}
{"tts": {"provedor": "comando", "comando": {"cmd": "piper --model ~/m/pt_BR-faber-medium.onnx --output_file {saida} < {texto}", "ext": "wav"}}}
```
Chaves: `ELEVENLABS_API_KEY`, `GEMINI_API_KEY` (ou `GOOGLE_API_KEY`),
`OPENAI_API_KEY` — no ambiente ou num `.env` na raiz do projeto (fora do git).

Escolher voz:
- `narrar.py --listar-vozes elevenlabs` lista as suas vozes e as mais usadas da
  biblioteca em português (adicione a escolhida em "My Voices" no site e use o
  `voice_id`). Prefira vozes **nativas pt-BR** de narração/educação.
- `--listar-vozes gemini|openai|edge` mostra as opções desses provedores.
- Teste rápido: rode `narrar.py` só com a primeira cena (um `narration.json`
  de um item) e peça ao usuário para ouvir antes de narrar o vídeo inteiro.

Ajustes finos:
- ElevenLabs: `estabilidade` (0,3–0,5 = mais expressiva), `similaridade`,
  `estilo` (0–0,3), `velocidade` (0,9–1,1). O script envia o texto da cena
  anterior/seguinte (`previous_text`/`next_text`) para a entonação não
  "reiniciar" a cada cena.
- Gemini: o `estilo` é uma instrução em linguagem natural; ritmo também se
  controla por ele ("ritmo calmo, pausas curtas").
- Pronúncia: `tts.pronuncia` troca grafias antes de sintetizar
  (`{"HMM": "agá eme eme", "R²": "erre dois"}`). Os cues continuam usando o
  texto original.
- Alinhamento (`tts.alinhamento`): `auto` (nativo, senão Whisper, senão
  proporcional), `whisper`, `proporcional`. `whisper_modelo`: `small` (padrão),
  `medium` para mais precisão. O proporcional é aproximado: o `narrar.py` avisa.

## Filosofia de sincronização (por que nada é cortado)
Por cena, duração final = `max(vídeo, voz) + folga`: se a voz é mais longa,
**congela o último quadro** (preto, pós fade-out); se o vídeo é mais longo,
**acrescenta silêncio**. Por isso **toda cena termina com fade-out para preto**
(`self.finish()`).

## Montagem (um comando)
```bash
python <SKILL>/scripts/build_video.py \
  --videos-dir media/videos/video/1080p60 \
  --narration narration.json --fps 60 --out video_final.mp4
```
- Reaproveita `media/audio/`; se faltar áudio, chama `narrar.py` com a mesma config.
- `--fps 15` + pasta `480p15` para um rascunho rápido com voz.
- Grava `media/scenes_av/cenas.json` (início/duração de cada cena) para a Etapa 7.

## Verificar o resultado final
Não dá para "ouvir" aqui. Confirme com PyAV que o arquivo tem fluxo de vídeo E
de áudio, a resolução/fps esperados e energia de áudio > 0:
```python
import av, numpy as np
c = av.open("video_final.mp4")
v, a = c.streams.video[0], c.streams.audio[0]
print(v.width, v.height, float(v.average_rate), a.codec_context.name)
e = cnt = 0
for fr in c.decode(audio=0):
    e += float(np.abs(fr.to_ndarray()).mean()); cnt += 1
    if cnt > 200: break
print("energia:", e/cnt)   # > 0 => tem som
```
Seja honesto com o usuário: você verificou streams/sincronia, mas não escutou —
sugira que ele dê um play para conferir pronúncia.
