# Demo animada de Legado Arcano

## Objetivo
Entregar uma demo lateral jogável com três classes, quatro fases e chefe com duas etapas, aproveitando as cinco pranchas fornecidas e preservando os arquivos originais.

## Alternativas
1. Continuar em Pygame, extrair poses e efeitos das pranchas e animá-los na demo atual: mantém o jogo executável e aproveita o trabalho existente. Escolha de implementação.
2. Migrar para outra engine: facilitaria ferramentas de edição, mas descartaria a integração atual e exigiria uma migração fora do objetivo imediato.
3. Aguardar spritesheets originais transparentes: daria cortes mais precisos, mas impediria testar agora.

## Comportamento
Menu com jogar, opções e sair; seleção das três classes; movimentos de plataforma, ataque e esquiva; quatro fases com layouts e inimigos; chefe com mudança clara de comportamento na metade da vida; efeitos de ataque, dano e morte e interface explicando os controles. Cada fase deve ser concluível pelas três classes. Opções de som devem funcionar.

## Limites
As pranchas são imagens compostas e não contêm quadros de animação separados para todos os efeitos ou chefes. Recortes e animações procedurais complementam os quadros disponíveis. Não alterar nem remover os assets originais. Manter Python/Pygame e não introduzir dependências.
