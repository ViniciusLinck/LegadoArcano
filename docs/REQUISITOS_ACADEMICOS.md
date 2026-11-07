# Auditoria dos requisitos acadêmicos

O PDF original não estava disponível no repositório ou anexos acessíveis. Esta lista verifica apenas os requisitos transcritos pelo usuário; a correspondência literal com o enunciado depende de conferir o PDF.

| Requisito informado | Evidência / situação |
|---|---|
| Python e 2D gráfico | `main.py`, `src/platformer.py`: janela Pygame e projeção lateral. |
| Demo e controle do jogador | Movimento, pulo, esquiva e ataques em `src/platformer.py`. |
| Desafio | Inimigos, espinhos, quatro áreas e chefe. |
| Vitória e derrota | Chefe derrotado e portal final; vida esgotada e tela de derrota. |
| Menu e comandos visíveis | Menu inicial de `PlatformGame.draw`, seleção de classes e opções. |
| Código próprio | Implementação no repositório; autoria integral e possíveis fontes externas exigem revisão humana. |
| ZIP Windows com EXE e assets | Gerado por `build-windows.ps1`; consultar `TESTES.md` para validação realizada. |
| Caminhos portáteis | `src/assets.py` usa raiz do projeto ou `_MEIPASS` do PyInstaller. |

## Limitações da especificação expandida

As quatro áreas são lineares; não há estrutura completa de metroidvania nem exploração interligada. Os inimigos usam essencialmente a mesma lógica de perseguição e contato; não há três IAs completas. O chefe não possui ataque especial de impacto no chão nem animação de derrota dedicada. Animações derivam de pranchas compostas e ainda precisam de revisão manual de recortes e alinhamento. Não foram demonstradas todas as combinações de jogo real até o fim.
