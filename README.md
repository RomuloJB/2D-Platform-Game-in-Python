# Plataforma 2D — reestruturado com POO

Reescrita orientada a objetos, partindo do pull mais recente (com as mudanças
do colega: rebalanceamento de armas, loja com ícones e seções, limite de
alcance das balas — tudo preservado).

## Como rodar
```bash
pip install pygame
python __main__.py      # ou: python main.py  ou:  python -m src
```
Rode a partir da **raiz** (pasta que contém `__main__.py`).

Controles: `← →` / `A D` mover · `Espaço`/`↑`/`W` pular · clique esquerdo atirar ·
`1 2 3` trocar arma · `R` reiniciar (game over) · `Esc` menu.

## O que mudou (orientações do professor)

1. **Vetor em vez de x/y** — `pygame.math.Vector2` em posição e velocidade.
2. **Física × dt** — `dt = clock.tick(FPS)/1000` (tempo do frame anterior, em
   segundos); tudo multiplica por `dt`. Constantes em unidades por segundo.
   Testado: roda igual em 30/60/144 FPS (variação ~25px em 5s).
3. **Variáveis tipadas** — anotações de tipo nas assinaturas e atributos-chave.
4. **Herança / hierarquia**
   ```
   GameObject            (só POSIÇÃO + collider)
    └─ DynamicObject     (+ velocidade, gravidade, move_and_collide com dt)
        └─ Character      (+ vida, dano, i-frames, lógica de batalha)
            ├─ Player
            └─ Enemy
        └─ Bullet / EnemyBullet
    └─ Platform / Coin / Portal / Particle
   ```
   `Entity.py` e `Object.py` (que estavam vazios) viraram aliases:
   `Entity = Character`, `Object = GameObject`.
5. **Collider categorizado** — `src/physics/Collider.py`, com `category`/`mask`
   por bitmask (`Layer` em `Constants.py`). A bala do player não colide com o
   player, nem balas entre si — declarado, não improvisado.

## Mudanças do colega preservadas
- **Armas** (`Weapons.py`): Pistol dmg 34 / Shotgun speed 14 range 350 / MachineGun
  speed 20 cd 10 — valores exatos do pull.
- **Loja** (`Shop.py`): seções "Melhorias" e "Armas" com ícones PNG (`src/ui/img/`).
- **Balas**: limite de alcance por distância (`max_range`).
- Assets em `res/` e `src/ui/img/` mantidos.

## Estrutura
```
__main__.py / main.py    ← entry points (Game().run())
src/
  core/      Game (loop+estados), World (agrega a fase), Camera, Hud
  objects/   GameObject, DynamicObject, Platform, Coin*, Portal, Particle, Object(alias)
  entities/  Character, Entity(alias), Player, Enemy, Bullet, Weapon, Weapons, Coin
  physics/   Collider
  levels/    LevelConfig, LevelGenerator
  gamestates/ Gamestate, MenuState
  ui/        Shop (nova, com ícones), Ui
  input/     Inputs
  utilz/     Constants, Utilz
```

## Observação
O loop principal foi consolidado em `src/core/Game.py` (o `__main__.py` do pull
era a versão sem POO/sem dt). Toda a parte de desenho foi preservada igual.
Validado em modo headless; rode na sua máquina para conferir o visual.
