# Testes

A suíte automatizada usa `python -m unittest discover -s tests`. `tests/test_platformer.py` verifica menu, classes, danos, especiais, armadilha, reinício e progressão incluindo o chefe e portal. Testes automatizados não substituem uma partida completa manual de cada classe.

Para testar manualmente, execute `main.py` ou extraia o ZIP; navegue pelo menu, selecione cada classe, experimente todos os comandos, avance por todas as áreas e confira vitória, derrota e reinício. Verifique som ativado/desativado e abra o executável a partir de outro diretório. Consulte a auditoria para limitações conhecidas.

## Resultado desta validação — 06/11/2026

- Suíte completa: 62 testes, todos aprovados, com SDL em modo sem janela e áudio fictício.
- Menu inicial renderizado e inspecionado visualmente com os comandos.
- ZIP verificado quanto à integridade e presença do executável, instruções e pranchas necessárias.
- ZIP extraído para uma pasta temporária fora do projeto; executável permaneceu aberto por cinco segundos com diretório de trabalho externo. Isso verifica inicialização, não uma partida completa.
- Não foi realizada partida manual completa com cada classe nem teste em outro computador.

## Atualização — inimigos e chefe

A suíte completa passou com 64 testes em modo sem janela. Os testes adicionais verificaram comportamentos distintos dos três inimigos, preparação do golem, ondas do chefe e atraso da abertura do portal durante sua derrota. Não foi feita uma partida manual completa com cada classe nem teste em outro computador.

## Atualização — animações e ataques

A suíte completa passou com 71 testes em modo sem janela. Há testes para transparência da explosão, tempo dos efeitos, golpe do cavaleiro e ataques de goblin, ninja e golem. A cena do efeito e das plataformas foi inspecionada em uma captura; ainda é necessária uma partida manual completa para avaliar ritmo e balanceamento.
