from enum import Enum, auto

from src.levels.LevelConfig import MAX_LEVEL


class State(Enum):
    PLAYING         = auto()
    PAUSED          = auto()
    CHECKPOINT      = auto()
    LEVEL_CLEAR     = auto()
    GAME_OVER       = auto()
    VICTORY         = auto()


class Gamestate:
    def __init__(self):
        self.state = State.PLAYING
        self.current_level = 1
        self.checkpoint_type = None

    @property
    def playing(self):
        return self.state == State.PLAYING

    @property
    def paused(self):
        return self.state == State.PAUSED

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

    def pause(self) -> bool:
        """Congela a fase. Só pausa se estiver realmente jogando."""
        if self.state != State.PLAYING:
            return False
        self.state = State.PAUSED
        return True

    def resume(self) -> bool:
        """Volta exatamente de onde parou."""
        if self.state != State.PAUSED:
            return False
        self.state = State.PLAYING
        return True

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
        if self.current_level >= MAX_LEVEL:
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