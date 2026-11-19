# Narração (TTS) e montagem final

Leia nas Etapas 5 e 6 (gerar voz e montar o vídeo único).

## Escrevendo a narração
- Idioma: **pt-BR por padrão** (use outro só se o usuário pedir, ou narre no
  idioma da fonte se ele preferir).
- Uma narração por cena, em texto corrido (sem marcação). Tom lúdico mas
  rigoroso: analogias concretas ("detetive", "afinar o rádio") sem perder a
  fidelidade ao material.
- **Fidelidade acima de tudo:** não invente resultados. Onde a animação
  simplifica a matemática, sinalize ("de forma simplificada...").
- Tamanho: a fala neural roda a ~2,5–3 palavras/seg. Não precisa casar exato com
  a animação — a montagem ajusta (veja abaixo) —, mas evite narrações MUITO mais
  longas que a cena, senão muitos segundos tocam sobre tela preta no fim.

## Formato do `narration.json`
Lista ORDENADA mapeando cada cena (nome do `.mp4` sem extensão) ao texto:
```json
[
  {"scene": "Cena1_Gancho",          "text": "Texto da narração da cena 1..."},
  {"scene": "Cena2_ConceitoLatente", "text": "Texto da narração da cena 2..."}
]
```
A ordem da lista é a ordem final do vídeo.

## Vozes neurais (edge-tts), pt-BR
- `pt-BR-ThalitaNeural` — feminina, natural (padrão desta skill).
- `pt-BR-FranciscaNeural` — feminina, clara.
- `pt-BR-AntonioNeural` — masculina, calma (boa para tom "3b1b").
- Outros idiomas: `edge-tts --list-voices` mostra todas (ex.: `en-US-AriaNeural`).
- `--rate` controla o ritmo (ex.: `-4%` deixa um pouco mais pausado).
- edge-tts precisa de **internet** (usa o serviço da Microsoft). Sem internet,
  não há voz neural em pt-BR de boa qualidade (SAPI offline do Windows só tem
  inglês e pronuncia mal o português).

## Filosofia de sincronização (por que nada é cortado)
A fala costuma durar um pouco mais que a animação silenciosa. O `build_video.py`
resolve assim, por cena: duração final = `max(vídeo, voz) + folga`.
- Se a voz é mais longa: **congela o último quadro** do vídeo (que, no estilo
  desta skill, já é PRETO após o fade-out — então o congelamento é invisível).
- Se o vídeo é mais longo: **acrescenta silêncio** ao áudio.
Resultado: a narração toca inteira e a animação nunca é truncada. Por isso é
importante que **toda cena termine com fade-out para preto**.

## Montagem (um comando)
```bash
python scripts/build_video.py \
  --videos-dir media/videos/<arquivo>/1080p60 \
  --narration narration.json \
  --voice pt-BR-ThalitaNeural \
  --fps 60 \
  --out video_final.mp4
```
- Use `--fps 15` + a pasta `480p15` para um rascunho rápido com voz.
- O script acha o ffmpeg sozinho (PATH, imageio-ffmpeg, locais comuns); se não
  achar, passe `--ffmpeg <caminho>`.
- Os áudios ficam em `media/audio/` e são reaproveitados em re-execuções (apague
  a pasta para regerar com outra voz).

## Verificar o resultado final
Não dá para "ouvir" aqui. Confirme com PyAV que o arquivo tem fluxo de vídeo E
de áudio, a resolução/fps esperados e energia de áudio > 0 (tem som):
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
