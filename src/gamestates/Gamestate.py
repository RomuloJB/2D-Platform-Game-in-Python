from enum import Enum, auto


class State(Enum):
    PLAYING         = auto()   # jogando a fase normalmente
    CHECKPOINT      = auto()   # tela de loja no checkpoint
    LEVEL_CLEAR     = auto()   # animação/tela de fase concluída
    GAME_OVER       = auto()   # morreu — regenera mapa mas mantém coins/arma
    VICTORY         = auto()   # completou todas as 5 fases


class Gamestate:
    def __init__(self):
        self.state = State.PLAYING
        self.current_level = 1       # 1-5
        self.checkpoint_type = None  # "mid" ou "end"

    # ── conveniências ──────────────────────────────────────────
    @property
    def playing(self):
        return self.state == State.PLAYING

    @property
    def at_checkpoint(self):
        return self.state == State.CHECKPOINT

    @property
    def game_over(self):
        return self.state == State.GAME_OVER

    @property
    def victory(self):
        return self.state == State.VICTORY

    @property
    def level_clear(self):
        return self.state == State.LEVEL_CLEAR

    # ── transições ─────────────────────────────────────────────
    def enter_checkpoint(self, kind: str):
        """kind = 'mid' ou 'end'"""
        self.state = State.CHECKPOINT
        self.checkpoint_type = kind

    def leave_checkpoint(self):
        """Sai da loja e volta a jogar (ou avança fase se era 'end')."""
        if self.checkpoint_type == "end":
            self.advance_level()
        else:
            self.state = State.PLAYING
            self.checkpoint_type = None

    def advance_level(self):
        if self.current_level >= 5:
            self.state = State.VICTORY
        else:
            self.current_level += 1
            self.state = State.PLAYING
        self.checkpoint_type = None

    def player_died(self):
        self.state = State.GAME_OVER

    def restart_level(self):
        """Regenera mapa da fase atual sem alterar progresso."""
        self.state = State.PLAYING