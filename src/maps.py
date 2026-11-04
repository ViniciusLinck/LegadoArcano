"""Eleven authored arena layouts built from licensed Ninja Adventure tiles."""

from dataclasses import dataclass

import pygame

from src import settings
from src.assets import resource_path


@dataclass(frozen=True)
class MapSpec:
    name: str
    floor: tuple[int, int]
    tint: tuple[int, int, int]
    border: tuple[int, int, int]
    prop: str
    obstacles: tuple[tuple[int, int, int, int], ...]
    walls: tuple[tuple[int, int, int, int], ...] = ()

    @property
    def solids(self):
        return self.obstacles + self.walls


A = (105, 145, 24, 24)
B = (490, 150, 24, 24)
C = (250, 215, 24, 24)
D = (370, 215, 24, 24)
E = (215, 145, 24, 24)
F = (405, 145, 24, 24)
G = (250, 75, 24, 24)
H = (370, 75, 24, 24)
I = (535, 215, 24, 24)
J = (85, 220, 24, 24)
K = (260, 175, 20, 20)
L = (365, 165, 20, 20)
WALL = (48, 42, 544, 16)

MAPS = (
    MapSpec('Santuário de Treino', (16, 15), (155, 155, 170), (139, 113, 153), 'crystal', ()),
    MapSpec('Masmorra Abandonada', (16, 15), (150, 140, 145), (146, 113, 124), 'pillar', (A, B), (WALL,)),
    MapSpec('Ruínas Cobertas de Musgo', (2, 12), (150, 165, 125), (117, 151, 104), 'tree', (C, D)),
    MapSpec('Caverna de Gelo', (5, 18), (150, 170, 190), (126, 182, 202), 'crystal', (E, F), (WALL,)),
    MapSpec('Forja em Brasas', (5, 11), (175, 110, 100), (193, 115, 82), 'pillar', (G, H), (WALL,)),
    MapSpec('Salão do Golem', (17, 15), (135, 138, 155), (165, 157, 170), 'rock', (A, I), (WALL,)),
    MapSpec('Bosque Arruinado', (1, 12), (125, 160, 115), (118, 154, 112), 'tree', (B, J, K)),
    MapSpec('Deserto das Ruínas', (5, 4), (180, 150, 115), (205, 163, 101), 'rock', (C, F, H)),
    MapSpec('Templo Submerso', (5, 18), (105, 145, 180), (102, 170, 193), 'crystal', (D, E, I), (WALL,)),
    MapSpec('Vila Medieval Esquecida', (16, 15), (170, 130, 115), (184, 137, 105), 'pillar', (A, H, L), (WALL,)),
    MapSpec('Núcleo Arcano', (16, 15), (140, 115, 170), (183, 131, 206), 'crystal', (B, J), (WALL,)),
)


def map_for_level(level):
    if not 0 <= level < len(MAPS):
        raise ValueError('Mapa inexistente')
    return MAPS[level]


class MapRenderer:
    def __init__(self, bounds):
        self.bounds = pygame.Rect(bounds)
        self.cache = {}
        self.atlases = {}
        for name in ('TilesetFloor', 'TilesetNature', 'TilesetDungeon', 'TilesetElement',
                     'TilesetDesert', 'TilesetVillageAbandoned', 'TilesetWater'):
            try:
                self.atlases[name] = pygame.image.load(str(resource_path('assets', 'maps', name + '.png'))).convert_alpha()
            except (OSError, pygame.error):
                pass

    def get(self, level):
        if level not in self.cache:
            self.cache[level] = self._build(map_for_level(level), level)
        return self.cache[level]

    def _tile(self, atlas, rect, tint=None):
        image = self.atlases.get(atlas)
        if not image:
            return None
        tile = image.subsurface(pygame.Rect(rect)).copy()
        if tint:
            tile.fill(tint, special_flags=pygame.BLEND_RGB_MULT)
        return tile

    @staticmethod
    def _path(level, col, row):
        """Distinct fixed floor plans; these markings are traversable terrain."""
        center = (col - 16) ** 2 + (row - 8) ** 2
        patterns = (
            abs(col - 16) <= 2 or abs(row - 8) <= 1,
            abs(col - (6 + row)) <= 2,
            20 <= center <= 50,
            abs(row - 8) <= 2 or abs(col - 9) <= 1 or abs(col - 23) <= 1,
            25 <= center <= 65 or abs(col - 16) <= 1,
            abs(col - (24 - row)) <= 2 or abs(row - 4) <= 1,
            abs(col - 11) <= 2 or abs(col - 22) <= 2,
            12 <= center <= 40 or abs(row - 8) <= 1,
            abs(row - 5) <= 1 or abs(row - 12) <= 1 or abs(col - 16) <= 1,
            25 <= center <= 75 or abs(col - 16) <= 1 or abs(row - 8) <= 1,
        )
        return patterns[(max(1, level) - 1) % len(patterns)]

    def _build(self, spec, level):
        surface = pygame.Surface(settings.LOGICAL_SIZE)
        surface.fill((14, 16, 29))
        pygame.draw.rect(surface, (40, 43, 53), self.bounds)
        x, y = spec.floor
        floor = self._tile('TilesetFloor', (x * 16, y * 16, 16, 16), spec.tint)
        path_tint = tuple(min(255, component + 38) for component in spec.tint)
        path = self._tile('TilesetFloor', (x * 16, y * 16, 16, 16), path_tint)
        if floor:
            surface.set_clip(self.bounds)
            for row, py in enumerate(range(self.bounds.top, self.bounds.bottom, 16)):
                for col, px in enumerate(range(self.bounds.left, self.bounds.right, 16)):
                    surface.blit(path if path and self._path(level, col, row) else floor, (px, py))
                    if (row * 17 + col * 31 + level * 13) % 29 == 0:
                        pygame.draw.rect(surface, spec.border, (px + 3, py + 4, 2, 1))
            surface.set_clip(None)
        pygame.draw.rect(surface, (10, 12, 21), self.bounds.inflate(8, 8), 4)
        pygame.draw.rect(surface, spec.border, self.bounds, 3)
        for wall_spec in spec.walls:
            wall = pygame.Rect(wall_spec)
            wall_tint = tuple(max(40, value - 55) for value in spec.tint)
            wall_tile = self._tile('TilesetFloor', (16 * 16, 15 * 16, 16, 16), wall_tint)
            pygame.draw.rect(surface, (45, 43, 53), wall)
            if wall_tile:
                for px in range(wall.left, wall.right, 16):
                    surface.blit(wall_tile, (px, wall.top))
            pygame.draw.line(surface, spec.border, wall.bottomleft, wall.bottomright, 2)
        # Source pieces are decorative structures; collision boxes match their on-screen placement.
        images = {'pillar': ('TilesetDungeon', (32, 32, 16, 16)),
                  'crystal': ('TilesetNature', (16, 224, 16, 16)),
                  'rock': ('TilesetNature', (240, 192, 32, 32)),
                  'tree': ('TilesetNature', (0, 0, 32, 32))}
        atlas, source_rect = images[spec.prop]
        sprite = self._tile(atlas, source_rect)
        for item in spec.obstacles:
            rect = pygame.Rect(item)
            pygame.draw.ellipse(surface, (28, 30, 35), rect.move(1, 3))
            if sprite:
                surface.blit(pygame.transform.scale(sprite, rect.size), rect)
            else:
                pygame.draw.rect(surface, spec.border, rect)
        # Emblems on the side walls identify the theme without blocking paths.
        torch = self._tile('TilesetDungeon', (32, 32, 16, 16))
        if torch:
            for px in (self.bounds.left - 17, self.bounds.right + 1):
                for py in (self.bounds.top + 24, self.bounds.bottom - 40):
                    surface.blit(torch, (px, py))
        # Trees, rocks and crystals frame the arena beyond its solid perimeter.
        frame_art = {'tree': ('TilesetNature', (0, 0, 32, 32)),
                     'rock': ('TilesetNature', (240, 192, 32, 32)),
                     'crystal': ('TilesetNature', (16, 224, 16, 16)),
                     'pillar': ('TilesetElement', (0, 0, 16, 16))}
        edge_atlas, edge_source = frame_art[spec.prop]
        if level == 7:
            edge_atlas, edge_source = 'TilesetDesert', (0, 0, 48, 48)
        elif level == 8:
            edge_atlas, edge_source = 'TilesetWater', (0, 0, 48, 48)
        elif level == 9:
            edge_atlas, edge_source = 'TilesetVillageAbandoned', (176, 0, 48, 48)
        edge_sprite = self._tile(edge_atlas, edge_source)
        if edge_sprite:
            edge_sprite = pygame.transform.scale(edge_sprite, (28, 28))
            for px in (self.bounds.left - 31, self.bounds.right + 3):
                for py in (self.bounds.top + 72, self.bounds.bottom - 108):
                    surface.blit(edge_sprite, (px, py))
        return surface
