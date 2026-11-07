# Legado Arcano

Demo de ação e plataforma 2D lateral em Python e Pygame. Escolha Mago, Cavaleiro ou Arqueiro, atravesse quatro áreas e enfrente o Golem Ancião. Derrote-o e alcance o portal final. O projeto é uma demo linear, ainda não um metroidvania completo.

## Executar a partir do código

Requer Windows, Python 3.12 e Pygame. Na pasta do projeto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Controles

A/D ou setas movem, Espaço/W/seta para cima pula, J/Z ataca, K usa o especial, Shift esquiva e Esc pausa. Enter confirma; menus aceitam mouse. Na pausa, Enter continua, R reinicia e M retorna ao menu. Na derrota ou vitória, R reinicia e Enter retorna ao menu.

O mago lança projéteis e uma explosão, o cavaleiro usa espada e golpe pesado e o arqueiro dispara flechas e um disparo perfurante. Especiais possuem recarga. Espinhos e inimigos causam dano; goblins, ninjas e golens t?m velocidades e ataques diferentes. O chefe alterna proj?teis e ondas no ch?o. A barra mostra a vida. Ao zerá-la, a partida termina.

## Distribuição Windows

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\build-windows.ps1
```

O script gera `dist/LegadoArcano_Entrega.zip`. Extraia toda a pasta antes de executar `LegadoArcano.exe` e mantenha os assets junto ao executável. `main.py` inicia o jogo; `src/` contém lógica e carregamento; `assets/` guarda recursos; `tests/` guarda testes. Consulte `docs/REQUISITOS_ACADEMICOS.md`, `docs/ASSETS.md` e `docs/TESTES.md` para o estado da entrega.
