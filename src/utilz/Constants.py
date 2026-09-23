"""
Constantes globais do jogo.

FÍSICA BASEADA EM TEMPO (delta time / dt):
Velocidades/acelerações estão em UNIDADES POR SEGUNDO. O loop principal
calcula dt (tempo do frame anterior, em segundos) e a física multiplica
tudo por dt — assim o jogo roda igual em 30, 60 ou 144 FPS.

Conversão (o jogo antigo era calibrado a 60 FPS):
    por_segundo = por_frame * 60          (velocidades)
    por_segundo = por_frame * 60 * 60     (acelerações, ex.: gravidade)
"""

SCREEN_W, SCREEN_H = 1024, 600
FPS = 60
TITLE = "Plataforma 2D"

TILE_SIZE = 40
CHUNK_WIDTH = 20
RENDER_CHUNKS = 4

GRAVITY = 0.6 * 60 * 60
MAX_FALL = 18 * 60
JUMP_POWER = -14 * 60
JUMP_HOLD_FORCE = 0.7 * 60 * 60
JUMP_HOLD_TIME = 12 / 60

PLAYER_SPEED = 5 * 60
PLAYER_ACCEL = 0.8 * 60
PLAYER_FRICTION = 0.75

COYOTE_TIME = 8 / 60
JUMP_BUFFER = 8 / 60

BULLET_SPEED = 14 * 60
BULLET_COOLDOWN = 12 / 60

FRAME_RATE = 60

class Layer:
    NONE        = 0
    PLAYER      = 1 << 0
    ENEMY       = 1 << 1
    PLATFORM    = 1 << 2
    HAZARD      = 1 << 3
    PLAYER_SHOT = 1 << 4
    ENEMY_SHOT  = 1 << 5
    PICKUP      = 1 << 6
    PORTAL      = 1 << 7
    ALL         = 0xFFFF

C_BG_TOP    = (10,  10,  30)
C_BG_BTM    = (20,  20,  60)
C_PLATFORM  = (70, 130, 180)
C_PLAT_TOP  = (110, 170, 220)
C_PLAT_DARK = (40,  80, 120)
C_GROUND    = (80,  60,  40)
C_GROUND_T  = (100, 140,  60)
C_PLAYER    = (60, 220, 120)
C_PLAYER_E  = (200, 60,  60)
C_PLAYER_EY = (255, 255, 100)
C_ENEMY     = (220,  60,  60)
C_ENEMY_EY  = (255, 255,  80)
C_COIN      = (255, 215,   0)
C_COIN_S    = (255, 255, 150)
C_HUD       = (255, 255, 255)
C_HUD_BG    = (0,   0,   0, 140)
C_DMGFLASH  = (255,  50,  50, 80)
C_SPIKE     = (200, 200, 220)
C_PARTICLE  = [(255,200,50),(255,150,50),(255,100,50),(200,200,200)]
C_BULLET    = (255, 140,   0)
C_BULLET_GL = (255, 220, 100)
