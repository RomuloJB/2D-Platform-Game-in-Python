from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class LevelConfig:
    level_num: int          # 1-5
    name: str
    length_chunks: int      # quantos chunks até o portal de fim
    mid_chunk: int          # chunk onde aparece o checkpoint do meio

    # Dificuldade
    enemy_speed_mult: float
    enemy_hp: int           # hp base dos inimigos
    spike_chance: float     # probabilidade de spike em plataformas
    moving_chance: float    # probabilidade de plataforma móvel
    enemy_spawn_chance: float
    gap_max: int            # largura máxima dos buracos (em tiles)
    num_gaps_max: int       # máximo de buracos por chunk

    # Visual (cores do background)
    bg_top: Tuple[int, int, int]
    bg_btm: Tuple[int, int, int]
    ground_top: Tuple[int, int, int]
    ground_btm: Tuple[int, int, int]

    # Tema das plataformas flutuantes: "grass" | "wood" | "metal" | "sand".
    # Trocar aqui muda o visual das plataformas daquela fase.
    platform_theme: str = "grass"

    # Imagem de fundo (parallax com loop). None = usa o fundo procedural
    # (gradiente + estrelas + montanhas).
    bg_image: str = None


LEVELS: list[LevelConfig] = [
    LevelConfig(
        level_num=1,
        name="Floresta",
        length_chunks=18,
        mid_chunk=9,
        enemy_speed_mult=1.0,
        enemy_hp=1,
        spike_chance=0.05,
        moving_chance=0.10,
        enemy_spawn_chance=0.35,
        gap_max=3,
        num_gaps_max=2,
        bg_top=(10, 20, 10),
        bg_btm=(20, 40, 20),
        ground_top=(80, 140, 50),
        ground_btm=(60, 90, 30),
        platform_theme="grass",
        bg_image="src/ui/backgrounds/forest.png",
    ),
    LevelConfig(
        level_num=2,
        name="Caverna",
        length_chunks=20,
        mid_chunk=10,
        enemy_speed_mult=1.4,
        enemy_hp=1,
        spike_chance=0.12,
        moving_chance=0.18,
        enemy_spawn_chance=0.45,
        gap_max=4,
        num_gaps_max=3,
        bg_top=(10, 10, 20),
        bg_btm=(20, 15, 40),
        ground_top=(70, 60, 80),
        ground_btm=(50, 40, 60),
        platform_theme="wood",
        bg_image="src/ui/backgrounds/cave.png",

    ),
    LevelConfig(
        level_num=3,
        name="Ruínas",
        length_chunks=22,
        mid_chunk=11,
        enemy_speed_mult=1.8,
        enemy_hp=2,
        spike_chance=0.18,
        moving_chance=0.25,
        enemy_spawn_chance=0.55,
        gap_max=4,
        num_gaps_max=3,
        bg_top=(25, 15, 10),
        bg_btm=(45, 25, 10),
        ground_top=(120, 100, 60),
        ground_btm=(80, 65, 35),
        platform_theme="metal",
    ),
    LevelConfig(
        level_num=4,
        name="Vulcão",
        length_chunks=24,
        mid_chunk=12,
        enemy_speed_mult=2.2,
        enemy_hp=2,
        spike_chance=0.25,
        moving_chance=0.30,
        enemy_spawn_chance=0.60,
        gap_max=5,
        num_gaps_max=4,
        bg_top=(30, 10, 5),
        bg_btm=(60, 20, 5),
        ground_top=(180, 80, 30),
        ground_btm=(120, 40, 15),
        platform_theme="sand",
    ),
    LevelConfig(
        level_num=5,
        name="Castelo",
        length_chunks=26,
        mid_chunk=13,
        enemy_speed_mult=2.8,
        enemy_hp=3,
        spike_chance=0.30,
        moving_chance=0.35,
        enemy_spawn_chance=0.65,
        gap_max=5,
        num_gaps_max=4,
        bg_top=(5, 5, 15),
        bg_btm=(15, 10, 35),
        ground_top=(100, 100, 120),
        ground_btm=(60, 60, 80),
        platform_theme="metal",
    ),
]