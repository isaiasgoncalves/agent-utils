# Pós-produção (Etapa 7)

Leia depois do `build_video.py`. Tudo aqui é opcional e configurável em
`video.config.json -> pos_producao`. A regra das skills de edição vale aqui
também: **mostre o plano e espere o "sim" antes de renderizar acabamento**.

## Nível 1 — acabamento automático (`pos_producao.py`, só ffmpeg, grátis)

```bash
python <SKILL>/scripts/pos_producao.py --video video_final.mp4 --mostrar   # plano, sem renderizar
python <SKILL>/scripts/pos_producao.py --video video_final.mp4 [--musica trilha.mp3] [--queimar]
```

| Item | Config | Observação |
|---|---|---|
| Legendas `.srt` | `legendas.srt` | Geradas do tempo EXATO da narração (não transcreve de novo). 42 car./linha, 2 linhas. Suba o `.srt` junto no YouTube. |
| Legendas queimadas | `legendas.queimar` / `--queimar` | Na fonte do vídeo (CMU Serif). Só ligue se as cenas deixarem livre a faixa inferior (~15% da altura); senão a legenda cobre conteúdo. |
| Capítulos | `capitulos` | Embutidos no `.mp4` + `capitulos.txt` para a descrição. Título = campo `titulo` do item no `narration.json` (ou o nome da cena). |
| Música + ducking | `musica.arquivo`, `volume_db` (-24), `ducking`, `fade_s` | A música abaixa sozinha sob a voz (sidechain). Fonte da música: abaixo. |
| Loudness | `loudness.lufs` (-16), `true_peak` (-1.5) | Duas passadas de `loudnorm`. -14 LUFS para YouTube agressivo, -16 é o equilíbrio para fala. |
| Créditos | sempre | `CREDITOS.md`: voz, imagens (de `creditos.json`) e música. Cole na descrição. |

Saída: `video_final_pos.mp4` (o original fica intacto).

## De onde vem a música e os efeitos (skill `media-use`)

- Arquivo próprio: `--musica caminho.mp3` ou `pos_producao.musica.arquivo`.
- Catálogo HeyGen (grátis com login) ou geração (créditos):
  `npx hyperframes media-use resolve --type bgm --intent "lo-fi calmo, piano, para explicação de matemática" --project .`
  Siga as regras da skill `media-use`: rode `auth status`, peça o login ao
  usuário, não gaste créditos sem ele saber. Para efeitos sonoros pontuais
  (`--type sfx`), use com parcimônia: um "whoosh" por troca de capítulo no
  máximo; vídeo didático fica cansativo com SFX demais.
- Música para explicação: instrumental, sem vocais, andamento lento, -24 a -30 dB.

## Nível 2 — letreiros, abertura e créditos com HyperFrames (opcional)

Use quando `pos_producao.hyperframes.usar = true` ou o usuário pedir
abertura/letreiros/cartões. O Manim continua dono do conteúdo; o HyperFrames só
**sobrepõe** acabamento ao vídeo pronto.

1. **Plano (formato da skill `plano-de-edicao`).** Monte `pos/plano.json` com
   `cortes: []` (a narração sintética não tem pausas a cortar) e `elementos`
   com `tipo` (`letreiro`, `lista`, `grafico`, `zoom`), `inicio`, `fim` em
   segundos do `video_final_pos.mp4` (use `media/scenes_av/cenas.json` +
   os cues de `narrar.py --cues`), `descricao` e `conteudo`. Mostre a tabela
   de elementos e **espere aprovação**, como a skill `plano-de-edicao` manda.
   Bons elementos aqui: letreiro de capítulo (3–4 s, canto inferior esquerdo),
   cartão "resumo até aqui" entre blocos, créditos finais com `CREDITOS.md`.
   Não repita o que a cena Manim já mostra.
2. **Projeto HyperFrames** (leia a skill `hyperframes` antes: contrato e work loop):
   ```bash
   npx hyperframes init pos/hf --skip-skills --skill=hyperframes
   cp video_final_pos.mp4 pos/hf/assets/base.mp4
   mkdir -p pos/hf/assets/fonts && cp ~/.local/share/fonts/CMU/cmunrm.ttf ~/.local/share/fonts/CMU/cmunbx.ttf pos/hf/assets/fonts/
   ```
   - Raiz `index.html`: `<video id="base" class="clip" data-start="0" data-duration="<D>" data-has-audio="true" src="assets/base.mp4">` + um host por elemento aprovado.
   - Fonte: `@font-face { font-family: "CMU Serif"; src: url("assets/fonts/cmunrm.ttf"); }` (a regra 9 do contrato exige o arquivo local). Mesma paleta do Manim (`#0d1117`, `#ffd166`, `#4cc9f0`).
   - Procure o efeito no registro antes de escrever à mão (`/hyperframes-registry`: lower thirds, títulos, transições).
3. `npx hyperframes check --json`, depois `snapshot --review`, abra o preview para
   o usuário e só renderize com o "sim" dele. Saída sugerida: `video_final_hf.mp4`.

## Verificação final (qualquer nível)

Use o trecho PyAV de `narration_and_assembly.md` no arquivo de saída e extraia
2–3 quadros com `ffmpeg -ss <t> -i <saida> -frames:v 1 q.jpg` nos instantes de
legenda/letreiro para olhar (Read). Diga ao usuário o que foi conferido e que
ele precisa ouvir a mixagem (volume da música) pelo menos uma vez.
