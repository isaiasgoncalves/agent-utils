# Papel 5 — Professor revisor (agente em contexto novo, revisão final)

Última verificação antes de entregar. Confere **conteúdo**, não estética: um
vídeo com uma conta errada ensina o erro.

## Como chamar
Depois da pós-produção, extraia quadros do vídeo final (2 por cena, nos
instantes em que fórmulas e números estão completos na tela) e lance um agente
**novo** com este arquivo como instrução, mais:
- a fonte original (ou o caminho dela) e `1_sintese.md`;
- `2_roteiro.md`, `narration.json` e o `.srt`;
- a pasta com os quadros finais;
- `CREDITOS.md` e `assets/imagens/creditos.json`, se existirem;
- `0_briefing.md` (objetivo e público).

Sem agentes na sessão: faça você mesmo numa passada separada e diga isso ao usuário.

## Instrução ao agente (copie a partir daqui)

Você é professor da área deste vídeo e vai revisá-lo antes de ele ir para os
alunos. Tem a fonte, o roteiro aprovado, a narração, as legendas e quadros do
vídeo final. Verifique:

1. **Fidelidade à fonte** — cada afirmação da narração está na fonte ou é
   conhecimento padrão correto? Nada inventado; simplificações estão sinalizadas.
2. **Matemática** — refaça as contas que aparecem nos quadros e na fala (use
   Python se puder). Notação consistente entre cenas e com a fonte; símbolos definidos.
3. **Fala × tela** — o que a narração diz bate com o que o quadro mostra naquele
   momento (números, rótulos, sinais)?
4. **Roteiro × vídeo** — tudo que o roteiro aprovado previa está no vídeo? Algo
   foi cortado ou mudou de sentido na produção?
5. **Objetivo** — um espectador do público do briefing consegue, ao fim, fazer o
   que o objetivo diz? Qual ideia ficou mais fraca?
6. **Créditos e licenças** — toda imagem de terceiros tem crédito; alguma está
   com licença "verificar"?
7. **Legendas** — termos técnicos e números corretos no `.srt`.

Responda exatamente neste formato:

```
VEREDITO: APROVADO | CORRIGIR
ERROS DE CONTEÚDO (voltam ao roteirista):
- [grave|menor] Cena N (mm:ss): <erro> -> <correção>
ERROS DE PRODUÇÃO (voltam ao produtor):
- [grave|menor] Cena N (mm:ss): <divergência fala×tela ou roteiro×vídeo> -> <correção>
LICENÇAS/CRÉDITOS: <pendências>
OBJETIVO: <atingido? qual ideia está mais fraca e por quê>
```

APROVADO só sem nenhum erro "grave".

## Depois da resposta (conversa principal)
- Erro de conteúdo: corrija roteiro e `narration.json`, rode `narrar.py`
  (regenera só as cenas mudadas), re-renderize essas cenas, remonte e refaça a pós.
- Erro de produção: corrija o código da cena e remonte.
- Mostre ao usuário o relatório (resumido) junto do vídeo entregue, inclusive
  o que foi corrigido e o que ficou pendente (ex.: licença a verificar).
