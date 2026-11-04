"""Resource paths and optional audio."""

from pathlib import Path
import sys

import pygame


def resource_path(*parts):
    root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
    return root.joinpath(*parts)


class Sounds:
    def __init__(self):
        self.clips = {}
        if pygame.mixer.get_init():
            for name, filename in (('cast', 'click_001.wav'), ('confirm', 'confirmation_001.wav'),
                                   ('impact', 'bong_001.wav')):
                try:
                    sound = pygame.mixer.Sound(str(resource_path('assets', 'audio', filename)))
                    sound.set_volume(0.25)
                    self.clips[name] = sound
                except (OSError, pygame.error):
                    pass

    def play(self, name):
        sound = self.clips.get(name)
        if sound is not None:
            sound.play()
