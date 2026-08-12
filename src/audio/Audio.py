"""AudioManager — musica de fundo (loop) + efeitos sonoros (SFX).

Uso basico (ver integracao em Game.py e Player.py):

    from src.audio.Audio import AudioManager
    audio = AudioManager()

    audio.play_music("res/audio/music/theme.wav")   # comeca a tocar em loop
    audio.stop_music()                                # para (ex.: ao voltar ao menu)

    audio.play_sfx("shot")                            # toca um efeito ja pre-carregado

Todo o modulo e tolerante a falhas: se o mixer nao inicializar (ex.: ambiente
sem audio) ou algum arquivo nao existir, o jogo continua rodando normalmente,
apenas sem som.
"""

import os

import pygame


class AudioManager:
    # nome logico -> caminho do arquivo de SFX
    SFX_FILES = {
        "shot": os.path.join("res", "audio", "sfx", "shot.wav"),
    }

    def __init__(self):
        self.enabled = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            self.enabled = False

        self._sfx = {}
        self._music_playing = False
        self._current_music_path = None

        if self.enabled:
            self._load_sfx()

    def _load_sfx(self):
        for name, path in self.SFX_FILES.items():
            if not os.path.exists(path):
                continue
            try:
                self._sfx[name] = pygame.mixer.Sound(path)
            except Exception:
                pass

    # ── SFX ─────────────────────────────────────────────────────
    def play_sfx(self, name: str, volume: float = 2.5) -> None:
        if not self.enabled:
            return
        snd = self._sfx.get(name)
        if snd is None:
            return
        try:
            snd.set_volume(volume)
            snd.play()
        except Exception:
            pass

    # ── Musica de fundo ────────────────────────────────────────
    def play_music(self, path: str, volume: float = 0.3, loop: bool = True) -> None:
        """Toca uma musica em loop. Nao reinicia se ja for a musica atual."""
        if not self.enabled:
            return
        if self._music_playing and self._current_music_path == path:
            return
        if not os.path.exists(path):
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self._music_playing = True
            self._current_music_path = path
        except Exception:
            pass

    def stop_music(self) -> None:
        if not self.enabled or not self._music_playing:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self._music_playing = False
        self._current_music_path = None

    def set_music_volume(self, volume: float) -> None:
        if not self.enabled:
            return
        try:
            pygame.mixer.music.set_volume(volume)
        except Exception:
            pass
