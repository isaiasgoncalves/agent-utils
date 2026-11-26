# Papel 3 — Produtor: direção criativa + técnica (conversa principal)

Um papel só, de propósito: posição, cor e tempo se decidem testando no código,
e separar quem decide de quem executa perde detalhe a cada volta. A crítica
independente fica com o crítico de arte (papel 4).

## 1. Direção criativa: `estilo.md` do projeto
Antes de escrever código, copie `assets/estilo_modelo.md` para a raiz do
projeto como `estilo.md` e ajuste ao briefing e ao roteiro:
- **Tom visual** (sóbrio 3b1b, mais lúdico, mais técnico) a partir do público e
  do tom pedidos na entrevista.
- **Paleta**: papel de cada cor (fundo, neutro, objeto padrão, destaque,
  acerto, alerta) e as cores de séries para gráficos. Se mudar cores, mude
  também `video.config.json -> estilo.paleta` (o `cena_base.py` lê de lá).
- **Grade de layout**: zonas (título, área principal, lateral de fórmula,
  faixa inferior livre se houver legenda queimada).
- **Tipografia**: CMU Serif (padrão) e as escalas de título/corpo/rótulo.
- **Ritmo**: tempos mínimos de leitura e máximo de tela parada.
- **Gráficos, imagens e 3D**: regras do projeto.
O usuário pode pedir mudanças de estilo a qualquer momento: edite `estilo.md`
(e a config), não cena a cena.

## 2. Plano de cenas (antes do código)
Para cada cena do roteiro, uma linha no topo do `video.py` (comentário) com:
layout escolhido (zonas), objetos e suas cores, a deixa (cue) de cada
animação, e se é 2D/3D. Isso é o que o crítico vai comparar com os quadros.

## 3. Direção técnica
Siga as Etapas 5 a 7 do SKILL.md (narração, código, render e quadros): narração com `narrar.py`, código com
`CenaSync`/`CenaSync3D` cronometrado pelos cues, render `-ql`, quadros com
`extract_frames.py`. Leia `references/manim_style.md` (armadilhas) antes de
codar e `references/animacoes_3d.md` para cenas 3D.

Antes de chamar o crítico, faça sua própria passada rápida nos quadros e
corrija o óbvio; o crítico é para o que você não vê, não para o que você já sabia.

## 4. Com o crítico
Aplique as correções na ordem bloqueador → importante → polimento; só
re-renderize as cenas tocadas. Polimento fica a seu juízo se o prazo apertar.
