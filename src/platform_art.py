"""Extract animation frames from the supplied reference sheets at runtime."""
from collections import deque
from functools import lru_cache
import pygame
from src.assets import resource_path


def cut(sheet, box, dark=28):
    """Remove connected dark backdrop while preserving enclosed dark details."""
    image = sheet.subsurface(pygame.Rect(box)).copy().convert_alpha()
    w, h = image.get_size()
    seen = set()
    queue = deque([(x, 0) for x in range(w)] + [(x, h-1) for x in range(w)] + [(0, y) for y in range(h)] + [(w-1, y) for y in range(h)])
    while queue:
        x, y = queue.popleft()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h): continue
        seen.add((x, y))
        c = image.get_at((x,y))
        if max(c.r, c.g, c.b) > dark: continue
        image.set_at((x,y), (0,0,0,0))
        queue.extend(((x+1,y),(x-1,y),(x,y+1),(x,y-1)))
    return image


def align_actor(image):
    """Keep a stable foot anchor across the uneven frames in the concept sheet."""
    bounds = image.get_bounding_rect(min_alpha=1)
    canvas = pygame.Surface((76, 94), pygame.SRCALPHA)
    if bounds.width and bounds.height:
        part = image.subsurface(bounds)
        canvas.blit(part, ((canvas.get_width()-bounds.width)//2, canvas.get_height()-bounds.height))
    return canvas


@lru_cache(maxsize=1)
def load_art():
    classes = pygame.image.load(str(resource_path('assets','effects','Animações classes.png'))).convert_alpha()
    enemies = pygame.image.load(str(resource_path('assets','sprites','Mobs - Boss.png'))).convert_alpha()
    maps = pygame.image.load(str(resource_path('assets','maps','Fases-mapas.png'))).convert_alpha()
    select = pygame.image.load(str(resource_path('assets','sprites','Tela de selecionar classe.png'))).convert_alpha()
    abilities = pygame.image.load(str(resource_path('assets','effects','Animações Habilidades.png'))).convert_alpha()
    # Individual poses are laid out in rows, with different spacing per action.
    ranges = {
        'idle': [(220,273),(273,324),(324,378)],
        'run': [(405,453),(453,502),(502,550),(550,599),(599,650)],
        'jump': [(676,720),(720,767),(767,810)],
        'fall': [(830,872),(872,916)],
        'dash': [(981,1044),(1044,1103)],
        'attack': [(1128,1197),(1198,1261),(1262,1324),(1325,1391)],
        'hit': [(1412,1467),(1468,1525)],
        'death': [(1558,1620),(1621,1683),(1684,1752)],
    }
    rows = [(241,331), (453,545), (675,769)]
    actors = []
    for y0,y1 in rows:
        actors.append({name:[align_actor(cut(classes,(x0,y0,x1-x0,y1-y0),32)) for x0,x1 in spans] for name,spans in ranges.items()})
    # Background previews are complete painted scenes; they are not tile atlases.
    scene_boxes = [(15,114,258,158), (282,114,230,158), (524,114,245,158), (782,114,247,158), (1046,114,229,158)]
    scenes = [pygame.transform.scale(maps.subsurface(pygame.Rect(b)), (960,540)) for b in scene_boxes]
    # Extract several poses for pirate, ninja, goblin and golem.
    mob_spans = [([(178,238),(238,299),(299,360)],195,254), ([(756,818),(818,879),(879,940)],195,254), ([(1334,1406),(1406,1477),(1477,1548)],195,254), ([(193,264),(264,337),(337,407)],316,377)]
    mobs = [[cut(enemies,(x,y0,end-x,y1-y0),45) for x,end in spans] for spans,y0,y1 in mob_spans]
    # The golem reference includes several animated walking poses.
    effects = [cut(abilities,(x, 250, 48, 60),32) for x in (253,303,353,405)]
    return {'actors':actors, 'mobs':mobs, 'scenes':scenes, 'selection':pygame.transform.scale(select,(960,480)), 'effects':effects}
