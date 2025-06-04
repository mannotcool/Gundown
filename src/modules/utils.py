"""
    Author: Nick S
    Date: January 15th, 2025
    Description: a bunch of utility functions that are used throughout the game
"""

# I - Import & Initialize
import pygame

# head collision check, returns True if there is a head collision
def collisionCheck(player, mapSprites):
    """
        Description:
        Checks if the player has a head collision with any of the map sprites
        
        Args:
        player: Player object
        mapSprites: List of map sprites

        Returns:
        headCollision: True if there is a head collision
    """
    # move the player up by 1 pixel
    player.rect.top -= 1  
    headCollision = False
    for sprite in mapSprites:
        if pygame.sprite.collide_rect(player, sprite):
            if sprite.decorative:
                continue 
            headCollision = True
            break
    # reset position after checking
    player.rect.top += 1  

    # if there is a head collision, return True
    return headCollision

def generalizedRespawn(players):
    """
        Description:
        Respawns all players at their respective spawn points
        
        Args:
        players: List of Player objects

        Returns:
        None
    """

    for player in players:
        if player.controlScheme == "mouse":
            player.respawnPlayerAtCords(100, 100)
        else:
            # joystick 1 spawns in the middle and joystick 2 spawns on the right

            if player.joyStick.get_id() == 0:
                # spawn in middle
                player.respawnPlayerAtCords(600, 100)
            else:
                # spawn far right
                player.respawnPlayerAtCords(1140, 100)

class Colors():
    """
        Description:
        Contains color constants that I use throughout the game
    """

    RED = (255, 103, 117)
    ORANGE = (255, 188, 110)
    YELLOW = (255, 255, 135)
    GREEN = (135,255,161)
    BLUE = (110,192,255)
    PURPLE = (188,167,255)

def deathHandler(deadPlayers, players, sceneManager, screen, allSprites, abilityCards, selectFx):
    """
        Description:
        Handles the death of players

        Args:
        deadPlayers: List of dead Player objects
        players: List of Player objects
        sceneManager: SceneManager object
        screen: Pygame screen object
        allSprites: List of all sprites
        abilityCards: AbilityCards object
        selectFx: Sound object

        Returns:
        []: empty array which is what deadPlayers is set to

    """

    for player in players:
        if player not in deadPlayers:
            player.score += 1
            break
    
    # show the mouse so p1 can select a card
    pygame.mouse.set_visible(True)

    # show the ability card screen
    changedWeapons = sceneManager.showAbilityCardScreen(screen, players, abilityCards.AVAILABLECARDS, selectFx)

    # append the player's weapons that are in the changedWeapons list to allsprites
    for playerWhoseWeaponChanged in changedWeapons:
        allSprites.add(playerWhoseWeaponChanged.weapon)

    for player in players:
        player.isDead = False
        
        # go into their weapons and kill every bulletList sprite to prevent bullets from lasting into next round
        for bullet in player.weapon.bulletList:
            bullet.kill()

    # Respawn players after card selection
    generalizedRespawn(players)

    pygame.mouse.set_visible(False)

    # reset dead Player count
    return []

def shootBulletsAllDirections(self, bulletList, bulletSpeed, damage, ratio=10):
    """
        Description:
        Shoots bullets in all directions, used by the physics bomb and exploading bullets ability cards

        Args:
        self: Player object
        bulletList: List of bullet sprites
        bulletSpeed: Speed of the bullet
        damage: Damage of the bullet
        ratio: Ratio of the bullet spread. ratio skips via this

        Returns:
        None
    """
    for i in range(0, 360, ratio):
        bullet = self.spawnBullet(i, bulletSpeed, damage)
        bulletList.add(bullet)