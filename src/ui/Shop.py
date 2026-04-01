import pygame
from src.utilz.Constants import *


SHOP_ITEMS = [
    {
        "id":    "health",
        "name":  "Poção de vida",
        "desc":  "+1 HP (máx 5)",
        "cost":  30,
        "color": (220, 60, 60),
    },
    {
        "id":    "ammo",
        "name":  "Munição extra",
        "desc":  "+20 balas",
        "cost":  20,
        "color": (255, 180, 0),
    },
    {
        "id":    "speed",
        "name":  "Bota veloz",
        "desc":  "Velocidade +20%",
        "cost":  50,
        "color": (60, 200, 255),
    },
    {
        "id":    "damage",
        "name":  "Bala perfurante",
        "desc":  "Dano duplo",
        "cost":  60,
        "color": (180, 60, 255),
    },
    {
        "id":    "extra_life",
        "name":  "Vida extra",
        "desc":  "+1 HP máximo",
        "cost":  80,
        "color": (255, 100, 140),
    },
]

_N       = len(SHOP_ITEMS)
_GAP     = 16
_MARGIN  = 40
_ITEM_W  = (SCREEN_W - _MARGIN * 2 - _GAP * (_N - 1)) // _N
_ITEM_H  = 110
_ITEMS_Y = 180


class Shop:
    def __init__(self, level_num: int, checkpoint_type: str):
        self.level_num       = level_num
        self.checkpoint_type = checkpoint_type
        self.selected        = 0
        self.message         = ""
        self.message_timer   = 0

        try:
            self.font_title = pygame.font.SysFont("arial", 32, bold=True)
            self.font_item  = pygame.font.SysFont("arial", 17, bold=True)
            self.font_desc  = pygame.font.SysFont("arial", 14)
            self.font_coins = pygame.font.SysFont("arial", 20, bold=True)
            self.font_hint  = pygame.font.SysFont("arial", 13)
        except Exception:
            self.font_title = pygame.font.Font(None, 36)
            self.font_item  = pygame.font.Font(None, 22)
            self.font_desc  = pygame.font.Font(None, 18)
            self.font_coins = pygame.font.Font(None, 24)
            self.font_hint  = pygame.font.Font(None, 16)

    def handle_event(self, event, player) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(SHOP_ITEMS)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(SHOP_ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_z):
                self._buy(player, SHOP_ITEMS[self.selected])
            elif event.key in (pygame.K_e, pygame.K_ESCAPE, pygame.K_END):
                return True
        return False

    def _buy(self, player, item):
        if player.coins < item["cost"]:
            self._msg("Coins insuficientes!")
            return
        iid = item["id"]
        if iid == "health":
            if player.health >= player.max_health:
                self._msg("HP já está no máximo!")
                return
            player.health += 1
        elif iid == "ammo":
            player.ammo += 20
        elif iid == "speed":
            if getattr(player, "speed_upgraded", False):
                self._msg("Já comprado!")
                return
            player.speed_upgraded = True
        elif iid == "damage":
            if getattr(player, "damage_upgraded", False):
                self._msg("Já comprado!")
                return
            player.damage_upgraded = True
        elif iid == "extra_life":
            player.max_health = min(player.max_health + 1, 8)
            player.health     = min(player.health + 1, player.max_health)
        player.coins -= item["cost"]
        self._msg(f"{item['name']} comprado!")

    def _msg(self, text):
        self.message       = text
        self.message_timer = 120

    def draw(self, surf, player):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 210))
        surf.blit(ov, (0, 0))

        cx = SCREEN_W // 2

        if self.checkpoint_type == "mid":
            title_txt = f"Fase {self.level_num}  —  Checkpoint"
        else:
            title_txt = f"Fase {self.level_num} concluída!  Prepare-se..."
        t = self.font_title.render(title_txt, True, (255, 220, 80))
        surf.blit(t, (cx - t.get_width() // 2, 28))

        coins_s = self.font_coins.render(f"Coins: {player.coins}", True, (255, 215, 0))
        surf.blit(coins_s, (cx - coins_s.get_width() // 2, 72))

        total_w = _N * _ITEM_W + (_N - 1) * _GAP
        start_x = cx - total_w // 2

        for i, item in enumerate(SHOP_ITEMS):
            ix     = start_x + i * (_ITEM_W + _GAP)
            iy     = _ITEMS_Y
            is_sel = i == self.selected

            bg_col = (55, 55, 85) if is_sel else (30, 30, 50)
            pygame.draw.rect(surf, bg_col,
                pygame.Rect(ix, iy, _ITEM_W, _ITEM_H), border_radius=10)

            border_col = item["color"] if is_sel else (70, 70, 95)
            border_w   = 3 if is_sel else 1
            pygame.draw.rect(surf, border_col,
                pygame.Rect(ix, iy, _ITEM_W, _ITEM_H), border_w, border_radius=10)

            pygame.draw.rect(surf, item["color"],
                pygame.Rect(ix + 8, iy + 8, _ITEM_W - 16, 5), border_radius=3)

            name_s = self.font_item.render(item["name"], True, (235, 235, 255))
            desc_s = self.font_desc.render(item["desc"],  True, (170, 170, 195))
            cost_s = self.font_desc.render(f"{item['cost']} coins", True, (255, 215, 0))

            surf.blit(name_s, (ix + (_ITEM_W - name_s.get_width()) // 2, iy + 22))
            surf.blit(desc_s, (ix + (_ITEM_W - desc_s.get_width()) // 2, iy + 50))
            surf.blit(cost_s, (ix + (_ITEM_W - cost_s.get_width()) // 2, iy + 72))

            if item["id"] in ("speed", "damage"):
                bought = getattr(player, f"{item['id']}_upgraded", False)
                if bought:
                    sold_s = self.font_hint.render("comprado", True, (100, 220, 100))
                    surf.blit(sold_s,
                        (ix + (_ITEM_W - sold_s.get_width()) // 2, iy + 92))

        hint_s = self.font_hint.render(
            "← →  selecionar     Enter  comprar    End sair",
            True, (140, 140, 180))
        surf.blit(hint_s, (cx - hint_s.get_width() // 2, _ITEMS_Y + _ITEM_H + 18))

        if self.message_timer > 0:
            self.message_timer -= 1
            alpha = min(255, self.message_timer * 4)
            mc    = (100, 255, 120) if "comprado" in self.message else (255, 80, 80)
            ms    = self.font_item.render(self.message, True, mc)
            ms.set_alpha(alpha)
            surf.blit(ms, (cx - ms.get_width() // 2, _ITEMS_Y + _ITEM_H + 46))

        hp_s = self.font_desc.render(
            f"HP: {player.health} / {player.max_health}", True, (220, 80, 80))
        surf.blit(hp_s, (cx - hp_s.get_width() // 2, _ITEMS_Y + _ITEM_H + 74))