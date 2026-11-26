# Entrevista inicial (Etapa 1)

Antes de trabalhar, alinhe com o usuário o que ele quer. Um vídeo de 8 minutos
para o público errado custa horas; três perguntas custam um minuto.

## Regras
- Pule o que o pedido já respondeu. Se tudo estiver claro, ou o usuário disser
  "pode decidir"/"sem perguntas", ou `entrevista.fazer` for `false`, não
  pergunte: anote as suposições no briefing e siga.
- Use a ferramenta de perguntas de múltipla escolha quando existir (até 4
  perguntas por rodada, sua recomendação como primeira opção, sempre com
  "Outro" livre). Sem ela, pergunte em uma mensagem curta e numerada.
- No máximo **2 rodadas**. A primeira cobre o essencial; a segunda só se uma
  resposta abriu dúvida real.
- Toda pergunta tem um padrão sensato; diga qual é, para ele poder só confirmar.

## Rodada 1 — essencial (escolha as que faltam, até 4)
1. **Público e nível** — leigo curioso · ensino médio · graduação (de outra
   área / da área) · pós/especialista. *Padrão: graduação da área.*
2. **Objetivo** — entender a intuição · dominar o mecanismo com exemplo
   numérico · revisar para prova · apresentar para alguém. *Padrão: mecanismo.*
3. **Duração e recorte** — curto (2–4 min, 1–2 ideias) · médio (5–10 min) ·
   série (um vídeo por parte). Para fonte grande, proponha o recorte. *Padrão: médio.*
4. **Tom** — sóbrio estilo 3b1b · lúdico com analogias · técnico e direto. *Padrão: sóbrio.*

## Rodada 2 — produção (só o que importar para este vídeo)
5. **Voz** — feminina/masculina; provedor (mostre o que o `check_env.py` achou
   disponível; recomende ElevenLabs/Gemini se for publicar).
6. **Recursos** (múltipla escolha) — imagens reais da web · cenas 3D ·
   perguntas "prever" na tela · exemplo numérico detalhado.
7. **Acabamento** (múltipla escolha) — legendas (.srt / queimadas) · música de
   fundo · capítulos · abertura/letreiros com HyperFrames.
8. **Revisões da equipe** — completo (revisor leigo + crítico de arte +
   professor revisor) · só a revisão final · nenhuma (mais rápido). *Padrão: completo.*

## Saídas
- `0_briefing.md`: público (como persona, ex.: "aluna de Economia que nunca viu
  Markov"), objetivo como frase verificável ("ao fim, o espectador consegue
  calcular a distribuição estacionária de uma cadeia 2×2"), duração, tom,
  recursos, acabamento, suposições feitas sem perguntar.
- `video.config.json`: só as chaves que mudaram (voz, `equipe.modo`,
  `pos_producao.*`, `imagens.permitir_download`).
