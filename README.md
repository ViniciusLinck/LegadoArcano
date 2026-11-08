# Legado Arcano

Uma aventura de a??o e plataforma 2D para Windows. Escolha entre Mago, Cavaleiro e Arqueiro, explore quatro ?reas, derrote os inimigos e enfrente o Guardi?o Anci?o. Esta ? uma **demo linear**, n?o um jogo completo.

![Tela inicial de Legado Arcano, com as op??es Jogar, Op??es e Sair](docs/imagens/tela-inicial-atual.png)

## Como baixar e jogar no Windows

### Se voc? recebeu o jogo pronto

1. Baixe o arquivo **`LegadoArcano_Entrega.zip`** disponibilizado pelo respons?vel pela entrega.
2. Clique com o bot?o direito no ZIP e escolha **Extrair Tudo**.
3. Abra a pasta extra?da `LegadoArcano` e execute **`LegadoArcano.exe`**.
4. No menu inicial, escolha **Jogar** e selecione uma classe com o mouse ou com as setas e Enter.

N?o ? necess?rio instalar Python para jogar a vers?o pronta. Extraia a pasta inteira e mantenha todos os arquivos, incluindo `assets`, junto ao execut?vel. O ZIP de entrega precisa ser fornecido separadamente: baixar o c?digo do reposit?rio n?o cria o execut?vel automaticamente.

### Se voc? baixou o c?digo-fonte

O bot?o **Code ? Download ZIP** do GitHub baixa o c?digo do projeto. Extraia o arquivo, instale [Python 3.12 para Windows](https://www.python.org/downloads/) e, na pasta extra?da que cont?m `main.py`, abra o PowerShell e execute:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

? necess?rio acesso ? internet para instalar as depend?ncias. Se o comando `py -3.12` n?o funcionar, confira se o Python 3.12 e o inicializador `py` est?o instalados. Para jogar novamente depois da instala??o, execute apenas o ?ltimo comando na pasta do projeto.

## Como jogar

![Tela de sele??o das classes Mago, Cavaleiro e Arqueiro](docs/imagens/selecao-classes.png)

Escolha o **Mago** para atacar com proj?teis e uma explos?o, o **Cavaleiro** para lutar com espada e golpe pesado ou o **Arqueiro** para disparar flechas e um tiro perfurante. A habilidade especial possui tempo de recarga.

Derrote todos os inimigos de cada ?rea e siga para o portal ? direita. Evite os espinhos e observe os avisos dos ataques inimigos. Na arena final, derrote o Guardi?o Anci?o e alcance o portal para vencer. A vida ? parcialmente recuperada entre ?reas; se chegar a zero, a partida termina. As bordas claras mostram onde ? poss?vel aterrissar nas plataformas.

![Jogabilidade em uma ?rea, mostrando personagem, inimigo, plataformas e barra de vida](docs/imagens/jogabilidade-atual.png)

## Controles

| A??o | Teclas |
| --- | --- |
| Mover | A / D ou setas esquerda / direita |
| Pular | W, seta para cima ou Espa?o |
| Descer de plataforma elevada | S ou seta para baixo |
| Ataque b?sico | J ou Z |
| Habilidade especial | K |
| Esquiva | Shift |
| Pausar / continuar | Esc |
| Navegar e confirmar nos menus | Mouse ou setas e Enter |

Na pausa, use **Enter** para continuar, **R** para reiniciar ou **M** para voltar ao menu. Ap?s vit?ria ou derrota, **R** reinicia e **Enter** retorna ao menu. Em **Op??es**, ? poss?vel ligar ou desligar o som.

## Gerar o pacote de entrega

Para quem vai distribuir o jogo no Windows, primeiro instale as depend?ncias do c?digo-fonte conforme os passos acima. Em seguida, na pasta do projeto, execute:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\build-windows.ps1
```

O pacote ser? criado em `dist/LegadoArcano_Entrega.zip`. Envie esse ZIP ao jogador; ele cont?m o execut?vel, os recursos e as instru??es. Se o PowerShell bloquear a execu??o do script, use `powershell -ExecutionPolicy Bypass -File .\build-windows.ps1` na pasta do projeto.

## Informa??es do projeto

- `main.py`: inicia o jogo.
- `src/`: c?digo do jogo; `assets/`: imagens, fontes, sons e respectivas licen?as.
- `tests/`: testes automatizados; `docs/`: documenta??o complementar.
- Consulte [cr?ditos dos recursos](docs/ASSETS.md), [testes](docs/TESTES.md) e [requisitos acad?micos](docs/REQUISITOS_ACADEMICOS.md).
