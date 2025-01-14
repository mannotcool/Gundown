import pygame
from src.modules import mapManager

def MapA(screen):
        # MAP A:

    # border walls
    left_wall = mapManager.StaticMapObject(screen, -20, 0, 10, 720, (5, 1, 23), 255)
    right_wall = mapManager.StaticMapObject(screen, 1280, 0, 10, 720, (5, 1, 23), 255)

    floor = mapManager.StaticMapObject(screen, 20, 655, 1240, 20, (60, 60, 255), 255)

    # add decorative pillars below the floor, 6 total evenly spaced
    decorative_pillars = pygame.sprite.Group()

    for i in range(6):
        pillar = mapManager.StaticMapObject(screen, 100 + (i * 200), 675, 40, 90, (60, 60, 255), 50, "solid", False, False, 1, True)
        decorative_pillars.add(pillar)

    # create 2 pillars above the floor, spaced evenly between the first 2 ground pillars of each equivalent side
    # left pillar
    left_pillar = mapManager.StaticMapObject(screen, 200, 380, 40, 290, (60, 60, 255), 50, "solid", False, False, 1, True)
    # right pillar
    right_pillar = mapManager.StaticMapObject(screen, 1000, 380, 40, 290, (60, 60, 255), 50, "solid", False, False, 1, True)
    decorative_pillars.add(left_pillar, right_pillar)

    # now add solid blocks on the top of the pillars
    # left pillar top
    left_pillar_mid = mapManager.StaticMapObject(screen, 200, 560, 40, 40, (60, 60, 255), 255, "solid", True)
    # right pillar top
    right_pillar_mid = mapManager.StaticMapObject(screen, 1000, 560, 40, 40, (60, 60, 255), 255, "solid", True)
    decorative_pillars.add(left_pillar_mid, right_pillar_mid)
    
    # add 2 actual top blocks
    # left pillar top
    left_pillar_top = mapManager.StaticMapObject(screen, 130, 360, 180, 20, (60, 60, 255), 255, "solid", True)
    # right pillar top
    right_pillar_top = mapManager.StaticMapObject(screen, 930, 360, 180, 20, (60, 60, 255), 255, "solid", True)
    
    decorative_pillars.add(left_pillar_top, right_pillar_top)

    # d pillars between the next set of ground pillars inwards from the ones we just created, 4 total evenly spaced, 2 on each side
    # left pillar
    left_pillar_2 = mapManager.StaticMapObject(screen, 400, 540, 40, 120, (60, 60, 255), 50, "solid", False, False, 1, True)
    # right pillar
    right_pillar_2 = mapManager.StaticMapObject(screen, 800, 540, 40, 120, (60, 60, 255), 50, "solid", False, False, 1, True)
    
    # 2 L shapes
    left_L = mapManager.StaticMapObject(screen, 360, 500, 100, 40, (60, 60, 255), 255, "solid", True)
    left_L2 = mapManager.StaticMapObject(screen, 440, 460, 40, 80, (60, 60, 255), 255, "solid", True)
   
    right_L = mapManager.StaticMapObject(screen, 780, 500, 100, 40, (60, 60, 255), 255, "solid", True)
    right_L2 = mapManager.StaticMapObject(screen, 760, 460, 40, 80, (60, 60, 255), 255, "solid", True)


    decorative_pillars.add(left_L, left_L2, right_L, right_L2)
    

    decorative_pillars.add(left_pillar_2, right_pillar_2)

    # now add a middle pillar with a platform on top
    middle_pillar = mapManager.StaticMapObject(screen, 600, 420, 40, 240, (60, 60, 255), 50, "solid", False, False, 1, True)
    middle_pillar_top = mapManager.StaticMapObject(screen, 540, 410, 160, 20, (60, 60, 255), 255, "solid", True)
    decorative_pillars.add(middle_pillar, middle_pillar_top)

    # now add 2 movable physics blocks 40 by 40 on each side of the middle pillar exactly
    left_movable = mapManager.StaticMapObject(screen, 570, 420, 40, 40, (60, 60, 255), 225, "solid", False, True, 1)
    right_movable = mapManager.StaticMapObject(screen, 630, 420, 40, 40, (60, 60, 255), 225, "solid", False, True, 1)
    # put in the middle of the 2 a block that is of type "damage" instead of solid, movable, and 
    
    # add a 40,40 block with physics that is in the middle where the floor is so its touching the flor
    middle_pedestal = mapManager.StaticMapObject(screen, 600, 635, 40, 40, (60, 60, 255), 225, "solid", False)
    middle_damage = mapManager.StaticMapObject(screen, 600, 500, 40, 40, (255, 60, 60), 225, "damage", False, True, 1)

    decorative_pillars.add(middle_pedestal)

    physicsObjects = pygame.sprite.Group(left_movable, right_movable, middle_damage)
    
    return [pygame.sprite.Group(decorative_pillars, left_wall, right_wall, floor, physicsObjects), physicsObjects]

