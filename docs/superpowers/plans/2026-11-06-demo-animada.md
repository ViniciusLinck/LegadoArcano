# Demo Animada Implementation Plan

> Execução nesta sessão, usando a demo Pygame existente e preservando as imagens originais.

**Objetivo:** Tornar a demo de plataforma mais animada e testável usando as pranchas fornecidas.

**Arquitetura:** `platform_art.py` extrai quadros e cenários; `platformer.py` controla estados, fases, combate e animações; os testes verificam progressão e comportamentos críticos.

**Tecnologias:** Python, Pygame, unittest.

**Especificação:** `docs/superpowers/specs/2026-11-06-demo-animada-design.md`.

## Riscos a verificar
- Ataque ou esquiva não devem continuar disponíveis durante pausa ou derrota.
- Reiniciar e trocar de fase devem limpar temporizadores e projéteis.
- As classes devem conseguir ferir todos os inimigos e o chefe.
- O chefe deve mudar de padrão na metade da vida e morrer apenas ao fim da vida.
- Animações de morte não devem bloquear a progressão indefinidamente.

## Tarefas
- [x] Corrigir o ciclo de animação: temporizadores próprios de ação, morte visível e progresso após derrotas.
- [x] Diversificar as quatro fases e melhorar a leitura das animações, efeitos e interface.
- [x] Dar ao chefe um aviso visual e ataques distintos nas duas etapas.
- [x] Testar menu, classes, reinício, progressão, combate e chefe; atualizar instruções.
