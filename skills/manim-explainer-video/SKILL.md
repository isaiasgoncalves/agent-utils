---
name: "manim-explainer-video"
description: "Cria um vídeo didático estilo 3Blue1Brown (animações 2D/3D em Manim + narração em voz neural trocável + imagens reais + pós-produção) a partir de QUALQUER conteúdo, em qualquer formato: paper/livro (PDF), artigo/URL, texto ou notas, um conceito/tópico, imagem, slides, documento ou planilha. Use SEMPRE que o usuário pedir vídeo explicativo, animação, explicação visual ou vídeo 3b1b/Manim."
---

# Vídeo explicativo estilo 3Blue1Brown (Manim + narração)

Transforma um conteúdo qualquer num vídeo animado e narrado. O fluxo tem 8
etapas encadeadas (0 a 7). Faça-as em ordem; cada etapa produz um artefato que
a seguinte consome. `<SKILL>` abaixo é a pasta desta skill (a "Base directory"
mostrada quando ela carrega); rode os scripts de dentro da pasta do projeto.

**Tudo é personalizável** por projeto em `video.config.json` (só as chaves que
mudam; os padrões estão em `assets/config_padrao.json`): provedor e voz da
narração, fonte, download de imagens e cada item da pós-produção. Se o usuário
pedir algo como "voz masculina", "sem música", "outra fonte", "sem imagens da
web", mude a config, não o código dos scripts.

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
  voz pelo provedor configurado (`tts.provedor = "auto"`: ElevenLabs → Gemini →
  OpenAI → edge-tts, o primeiro que tiver chave); fonte **CMU Serif**; imagens
  reais com licença livre quando ajudam; vídeo **aprofundado (~5–10 min)**,
  tipicamente 10–16 cenas. Ajuste conforme o pedido do usuário.

## Etapa 0 — Verificar o ambiente e a configuração
Na pasta do projeto, rode `python <SKILL>/scripts/check_env.py`. Ele confere
manim, **LaTeX**, **ffmpeg**, PyAV, quais **provedores de voz** têm chave (e
qual será usado), **Whisper** (alinha o tempo de vozes sem timestamps), a
**fonte** (CMU Serif) e o que a pós-produção precisa. Instale o que faltar
ANTES de renderizar: `pip install manim edge-tts av pillow`; LaTeX via TeX
Live; CMU: `sudo apt install fonts-cmu`; Whisper: `uv tool install whisper-ctranslate2`.

Se o pedido trouxer preferências (voz, duração, estilo, sem música...), crie
`video.config.json` só com essas chaves. Se nenhum provedor pago estiver
configurado e o vídeo for para publicar, diga em uma linha que a voz sai melhor
com ElevenLabs (pago) ou Gemini (grátis com chave do AI Studio) e siga com o
disponível; não pare o trabalho por isso. Detalhes e custos em
`references/narration_and_assembly.md`.

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

- **Imagens reais** (se `imagens.permitir_download`): onde uma foto, retrato ou
  figura do paper ancoraria a ideia, busque e baixe com
  `scripts/baixar_imagem.py` (licença e crédito ficam registrados). Olhe as
  prévias antes de escolher. Detalhes no Passo D de `references/ingestao_conteudo.md`.

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
- **Animação** — quais objetos entram e como se transformam; marque **2D ou 3D**
  (3D só quando a terceira dimensão é o conteúdo: superfície de perda e descida
  de gradiente, sólidos e geometria espacial, volumes, transformações de R³;
  veja `references/animacoes_3d.md`);
- **Imagem** (se houver) — arquivo baixado e onde entra.

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
Escreva `narration.json`, uma lista ORDENADA
`[{"scene": "Cena1_Gancho", "titulo": "O mistério", "text": "..."}]` com o texto
de cada cena (os do roteiro, refinados). `scene` precisa ser exatamente o nome
da classe Manim; `titulo` (opcional) vira o capítulo na Etapa 7. Rode:
```bash
python <SKILL>/scripts/narrar.py narration.json
```
Para cada cena ele gera `media/audio/cenaN.mp3` (que o `build_video.py`
reaproveita) e `media/audio/<Cena>.json` com o instante de cada caractere, e
imprime os cues (o segundo em que cada frase começa). A voz vem de
`video.config.json -> tts` (ou `--provedor gemini --voz Charon`); ElevenLabs e
edge-tts dão o tempo nativo, Gemini/OpenAI/comando local passam por alinhamento
Whisper. Trocar texto, voz ou provedor regenera só as cenas afetadas.
- Antes do vídeo inteiro, gere só a primeira cena e peça ao usuário para ouvir
  a voz se ela for nova para ele.
- "poucas palavras casadas": o TTS leu algo diferente do texto (número, sigla).
  Escreva por extenso ou use `tts.pronuncia` (`{"HMM": "agá eme eme"}`).
- "tempo APROXIMADO": não há Whisper; instale para sincronia fina.

## Etapa 4 — Código Manim cronometrado pela fala
Copie para o projeto `assets/cena_base.py` (obrigatório), `assets/scene_template.py`
(como `video.py`, ponto de partida) e, se houver cena 3D, `assets/helpers_3d.py`.
Escreva uma cena por item do `narration.json`, com `from cena_base import *`,
herdando de `CenaSync` (2D) ou `CenaSync3D` (3D) e com o nome da classe igual
ao `scene`. Deixe à vista a saída de `narrar.py narration.json --cues` e amarre
cada animação à frase que a explica: `self.go("a curva sobe")` espera até essa
frase ser dita, `self.left("e depois estabiliza")` devolve os segundos até a
próxima deixa (bom como `run_time`) e `self.t(...)` dá o instante. Os cues
ignoram maiúsculas e acentos e casam a primeira ocorrência; use `nth=2` para a
segunda e `off=-0.3` para adiantar um pouco. Onde o guia de estilo fala em
`self.wait(...)` entre ideias, prefira `self.go(...)`.
**Antes de escrever, leia `references/manim_style.md`** (estilo, fonte, imagens
e — o mais importante — o catálogo de armadilhas de layout); para 3D, leia
também `references/animacoes_3d.md`. Regras-chave:
- **Fonte:** o `cena_base.py` já põe CMU Serif em todo `Text`; `MathTex` usa
  Computer Modern (mesmo desenho). Não force outra fonte cena a cena; mude
  `fonte.texto` na config se o usuário pedir.
- **Imagens:** `com_credito(imagem("assets/imagens/x.jpg", altura=4))`.
- **3D:** texto e fórmulas com `self.fixo(...)`; câmera com `enquadrar(self, ax)`;
  números da animação calculados de verdade (`descida_gradiente`).
- Use a paleta e os helpers do template. `MathTex` para fórmulas, `Axes` +
  `ValueTracker` para gráficos animados, `Transform` para distribuições que
  colapsam, `VGroup` de `Dot`+`Arrow` para grafos/HMM.
- Comente cada bloco mapeando-o à cena do roteiro e ao trecho da fonte.
- **Toda cena termina com `self.finish()`.** Ele espera a narração acabar, faz
  `FadeOut` de tudo (tela preta, essencial para a montagem e para não vazar
  mobjects) e deixa uma folga curta.
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
   frase que deveria acompanhar; `[fonte]` avisa fonte ausente; `[3D]` avisa
   superfície fora dos eixos. Corrija até não sobrar nenhum.
2. Extraia quadros: `python <SKILL>/scripts/extract_frames.py media/videos/video/480p15 --out frames/`.
3. **Leia (Read) os `.jpg`** e procure pelos defeitos do catálogo: texto
   sobreposto, fórmula coberta por barra que cresceu, palavra fora da margem,
   crédito de imagem cortado, superfície 3D saindo do quadro, emoji virando
   "tofu", setas cruzando texto, sobras entre cenas.
4. Corrija no código e repita até cada cena estar limpa. Extraia quadros em
   instantes ESTÁTICOS (logo antes do cue seguinte), não no meio de um `Write`.
   Para mirar um momento específico, divida o instante do cue pela duração da
   cena e passe o resultado em `--fracs`.

Não pule esta etapa: é a única forma de pegar erros de layout sem assistir ao vídeo.

## Etapa 6 — Montar o vídeo único (FHD)
1. Render final em FHD: `manim -qh video.py -a` (gera `1080p60`).
2. Monte com voz:
   ```bash
   python <SKILL>/scripts/build_video.py --videos-dir media/videos/video/1080p60 \
     --narration narration.json --fps 60 --out video_final.mp4
   ```
   Ele reaproveita os áudios da Etapa 3 (mesma voz), junta voz+vídeo **sem
   cortar nada**, concatena e grava `media/scenes_av/cenas.json` para a Etapa 7.
   Acha o ffmpeg sozinho; se não achar, passe `--ffmpeg <caminho>`.
3. **Verifique o resultado** (não dá para ouvir aqui): use o trecho PyAV em
   `references/narration_and_assembly.md` (streams, resolução/fps, energia > 0).

## Etapa 7 — Pós-produção (acabamento; configurável)
Leia `references/pos_producao.md`. Se `pos_producao.ativar` (padrão), mostre o
plano com `python <SKILL>/scripts/pos_producao.py --video video_final.mp4 --mostrar`
e, com o ok do usuário, rode sem `--mostrar`. Ele faz legendas `.srt` a partir do
tempo exato da narração (queimadas na CMU Serif se pedido), capítulos, música
de fundo com ducking (arquivo próprio ou via skill **`media-use`**), loudness
normalizado e `CREDITOS.md` (voz, imagens, música). Saída: `video_final_pos.mp4`.
Para abertura, letreiros de capítulo, cartões de resumo ou créditos animados,
use a skill **`hyperframes`** sobre o vídeo pronto, planejando os elementos no
formato da skill **`plano-de-edicao`** e só renderizando depois da aprovação.
Para um vídeo gravado pelo usuário que entra como cena (ex.: ele falando),
use as skills **`transcricao`** e **`plano-de-edicao`** nele antes de montar.

Dica de iteração: faça a Etapa 5 em `-ql`/`480p15` (rápido) e só renderize
`-qh` quando o layout estiver aprovado. Mudou o texto de uma cena? Rode
`narrar.py` (ele regenera só aquele áudio) e re-renderize essa cena, porque os
tempos mudaram.

## Scripts e referências (mapa)
- `assets/config_padrao.json` — todos os padrões; o projeto sobrescreve em `video.config.json`.
- `scripts/check_env.py` — dependências, provedores de voz, fonte (Etapa 0).
- `scripts/narrar.py` + `scripts/tts_provedores.py` — narração com tempo por
  palavra, provedores trocáveis, `--listar-vozes` (Etapa 3).
- `scripts/baixar_imagem.py` — busca/baixa imagens com licença e crédito (Etapa 1).
- `assets/cena_base.py` — `CenaSync`/`CenaSync3D`, fonte padrão, helpers de imagem (Etapa 4).
- `assets/helpers_3d.py` — superfície, descida de gradiente, trajetos, curvas de nível (Etapa 4).
- `assets/scene_template.py` — paleta, helpers 2D e cena de exemplo (Etapa 4).
- `scripts/extract_frames.py` — quadros para verificação (Etapa 5).
- `scripts/build_video.py` — junção voz+vídeo e concatenação (Etapa 6).
- `scripts/pos_producao.py` — legendas, capítulos, música, loudness, créditos (Etapa 7).
- `references/ingestao_conteudo.md` — roteamento por tipo de entrada e imagens (Etapa 1).
- `references/manim_style.md` — estilo 3b1b, fonte, imagens e **armadilhas de layout**.
- `references/animacoes_3d.md` — quando e como usar 3D; receitas (gradiente, sólidos, volumes).
- `references/narration_and_assembly.md` — provedores de voz, custos, sincronização.
- `references/pos_producao.md` — acabamento, música, HyperFrames.
- `references/example_walkthrough.md` — exemplo de ponta a ponta (arco de cenas).

## Saídas que o usuário recebe
`1_sintese.md`, `2_roteiro.md`, `video.py`, `narration.json`, `video_final.mp4`
e, com a Etapa 7, `video_final_pos.mp4`, `video_final.srt`, `capitulos.txt` e
`CREDITOS.md`. Entregue na ordem síntese → roteiro → código → vídeo, deixando
claro o que foi verificado, o que ele deve revisar (ouvir a voz e a mixagem) e
quais imagens têm licença a verificar.
