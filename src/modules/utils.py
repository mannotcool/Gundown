import pygame

def collisionCheck(player, mapSprites):
    # check for head collision
    player.rect.top -= 1  # temporarily move up to check collision
    headCollision = False
    for sprite in mapSprites:
        if pygame.sprite.collide_rect(player, sprite):
            if sprite.decorative:
                continue # ignore decorative sprites
            headCollision = True
            break
    player.rect.top += 1  # reset position after checking

    # if there is a head collision, return True
    return headCollision

def generalizedRespawn(players):
    for player in players:
        # check if they are mouse, and spawn them on the left side of the screen
        if player.controlScheme == "mouse":
            player.respawnPlayerAtCords(100, 100)
        else:
            # joystick 1 spawns in the middle and joystick 2 spawns on the right
            # check their joystick
            if player.joyStick.get_id() == 0:
                # spawn in middle
                player.respawnPlayerAtCords(600, 100)
            else:
                # spawn far right
                player.respawnPlayerAtCords(1140, 100)

class Colors():
    red = (255, 179, 186)
    orange = (255, 223, 186)
    yellow = (255, 255, 186)
    green = (186, 255, 201)
    blue = (186, 225, 255)
    purple = (227, 218, 255)
