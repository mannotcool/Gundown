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
    red = (255, 103, 117)
    orange = (255, 188, 110)
    yellow = (255, 255, 135)
    green = (135,255,161)
    blue = (110,192,255)
    purple = (188,167,255)

def deathHandler(deadPlayers, players, sceneManager, screen, allSprites, abilityCards):
    # find the 1 not dead player and award them 1 score
    for player in players:
        if player not in deadPlayers:
            player.score += 1
            break
    
    # show the mouse so p1 can select a card
    pygame.mouse.set_visible(True)

    # show the ability card screen
    changedWeapons = sceneManager.showAbilityCardScreen(screen, players, abilityCards.availableCards)

    # append the player's weapons that are in the changedWeapons list to allsprites
    for playerWhoseWeaponChanged in changedWeapons:
        allSprites.add(playerWhoseWeaponChanged.weapon)

    # undie the rest lul
    for player in players:
        player.isDead = False

    # Respawn players after card selection
    generalizedRespawn(players)

    pygame.mouse.set_visible(False)
    
    # reset dead Player count
    return []

            