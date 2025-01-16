"""
    Author: Nick S
    Date: January 16th, 2025
    Description: Gundown, version 1.0.0
"""

# I - Import & Initialize
import pygame

pygame.init()
pygame.mixer.init()
pygame.font.init()

from src.modules import entities, utils, gui, abilityCards, weaponManager, sceneManager
from src.maps import mapA

"""
GENERAL NOTES:

- The player supports both mouse and controller input
- Shooting is with left click
- Jumping is with w

Controller Button Mapping (xbox one):
a - 0
b - 1
y - 3
x - 2

left bumper - 9
right bumper - 10

axis 5 - right trigger
axis 4 - left trigger


"""

version = "1.0"

# enables certain console logs, turns off background music
debug = False

def main():
    """
        Description:
        Main runtime game loop for Gundown

        Args:
        None

        Returns:
        None
    """

    # D - Display configuration
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Gundown - " + version + " - Debug: " + str(debug))

    # E - Entities

    # add background music if debug is false, we want music in the start screen
    if debug == False:
        pygame.mixer.music.load("src/music/pizzatronMusic.ogg")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    # Scene Manager houses the start screen, and ability card screen. This will return an array with the colors of the players
    selectedPlayerColors = sceneManager.showStartScreen(screen)


    # make background space.gif in art
    background = pygame.image.load("src/art/backgrounds/dark_background.gif")
    screen.blit(background, (0,0))

    # load sounds effects
    bellFx = pygame.mixer.Sound("src/sounds/bell.ogg")
    bellFx.set_volume(0.5)

    selectFx = pygame.mixer.Sound("src/sounds/select_2.ogg")
    selectFx.set_volume(0.7)

    shieldFx = pygame.mixer.Sound('src/sounds/cast_shield.ogg')
    shieldFx.set_volume(0.5)

    shotFx = pygame.mixer.Sound('src/sounds/shot.ogg')
    shotFx.set_volume(0.35)

    reloadFx = pygame.mixer.Sound('src/sounds/reload_gun.ogg')
    reloadFx.set_volume(0.8)

    # change mouse cursor to a crosshair
    pygame.mouse.set_visible(False)
    crosshair = pygame.image.load("src/art/hud/cross/crosshair_320.png").convert_alpha()

    # add transparency to the crosshair & scale down
    crosshair.set_colorkey((0, 0, 0))
    crosshair = pygame.transform.scale(crosshair, (32, 32))

    # Map A || Returns an array with the map sprites [0] and physics objects [1]
    importedMap = mapA.MapA(screen)

    # create a sprite group for all physics objects
    mapSprites = importedMap[0]
    physicsObjects = importedMap[1]
    
    # PLAYERS:

    # Used to store the dead players, will be used to detect when 1 player is alive and call for the new ability cards
    deadPlayers = []
    disableRespawns = False
    gameEnd = None

    # create the players with the colors selected
    players = pygame.sprite.Group()

    # create a player sprite object from our mySprites module. p1 is always mouse
    players.add(entities.Player(screen, 100, 100, "mouse", selectedPlayerColors[0], None))
    
    # pick up all game controllers that exist and create a player for each one
    # check if there is a controller available
    joystick_count = pygame.joystick.get_count()
    if joystick_count > 0:
        # add them do not set players yet
        for i in range(joystick_count):
            # initalize and add the joystick
            players.add(entities.Player(screen, 100, 100, "controller", selectedPlayerColors[i + 1], pygame.joystick.Joystick(i)))
    
    # attach pistols onto all the players using attachWeapon
    for player in players:
        player.attachWeapon(weaponManager.BasicPistol(screen, player))

    # now respawn them at the correct positions
    utils.generalizedRespawn(players)

    # for every player, create a scorekeeper object. its a 3 square bar top left corner with small rects for no points and scaled squares for points
    scoreKeepers = pygame.sprite.Group()
    for player in players:
        # for the index of player, make the location y 10 + 40 * index
        scoreKeepers.add(gui.ScoreKeeper(screen, player, (20, 10 + 40 * players.sprites().index(player))))

    # add all sprites include the player, weapon, bullets, and map sprites to the allSprites group
    allSprites = pygame.sprite.OrderedUpdates(mapSprites, players, scoreKeepers)

    # for each player, append their weapon to the allSprites group
    for player in players:
        allSprites.add(player.weapon)

    # A - Action (broken into ALTER steps)
    
    # A - Assign values to key variables
    clock = pygame.time.Clock()
    keepGoing = True

    # play bell noise because game is starting
    bellFx.play()

    # L - Loop
    while keepGoing:
        # T - Timer to set frame rate
        clock.tick(60) 

        # E - Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False

            # if the player presses the escape key, quit the game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False
        
        # scan to see if a controller is newly ocnnected 
        joystick_count = pygame.joystick.get_count()

        for player in players:
            if player.isDead and player not in deadPlayers:
                deadPlayers.append(player)

             # check if all players are dead except for 1, and see if the 1 dead player has 3 score
            if player.score == 3:
                if player not in deadPlayers:
                    disableRespawns = True

                    # this is my super smart way of passing over the color of the player to the font
                    gameEnd = player.colorScheme

            # if all players are dead except for 1, show the ability card screen
            if len(deadPlayers) == (len(players) - 1):
                if disableRespawns == False:
                    pygame.event.set_grab(False)
                    deadPlayers = utils.deathHandler(deadPlayers, players, sceneManager, screen, allSprites, abilityCards, selectFx)
                    pygame.event.set_grab(True)

                    bellFx.play()
                    if debug:
                        print("Respawning players...")
                else:
                    if debug:
                        print("Game over")
                
    
            # gravity logic
            player.runTimeGravityManager(mapSprites)

            if player.controlScheme == "controller":
                # if joystick is not none, initalize it and run the movement
                if player.joyStick != None:
                    player.joyStick.init()
                    player.runTimeJoyMovement(player.joyStick, mapSprites, shotFx, reloadFx, shieldFx)
            else:
                player.runTimeMnkMovement(mapSprites, shotFx, reloadFx, shieldFx)

            # if the player has a shieldBuble, draw it
            if player.shieldBubble != None:
                allSprites.add(player.shieldBubble)
                
            # allow bullets to have collision with walls
            for bullet in player.weapon.bulletList:
                bullet.collisionDetection(mapSprites, players, player.weapon.bulletList)
    
            if player.Health <= 0:
                player.isDead = True

            # the reload complete method checks if the reload time has passed and if so, sets the ammo back to the max
            player.weapon.checkReloadComplete()
            allSprites.add(player.weapon.bulletList)

            # allows for reloading of the weapon
            player.update()

        # for every physics object, call their internal function: runtimeGravity
        for physicsObject in physicsObjects:
            physicsObject.runtimeGravity(mapSprites)

        # Refresh screen
        screen.blit(background, (0, 0))  # Redraw the full background first
        allSprites.update()              # Update all sprites
        allSprites.draw(screen)          # Draw all sprites

        # if gameEnd not nothing (cuz colors), show the game over screen
        if gameEnd is not None:
            pixelArtFont = pygame.font.Font("src/fonts/ThaleahFat.ttf", 96)
            screen.blit(pixelArtFont.render("Game Over!", True, gameEnd), (560, 10))

        screen.blit(crosshair, pygame.mouse.get_pos()) # draw the crosshair on top of everything
        pygame.display.flip()            # Flip the display
    
    # Close the game window
    pygame.quit()

# using raw text string to print askii art
print(r"""   ______                    ______                                 
 .' ___  |                  |_   _ `.                               
/ .'   \_| __   _   _ .--.    | | `. \  .--.   _   _   __  _ .--.   
| |   ____[  | | | [ `.-. |   | |  | |/ .'`\ \[ \ [ \ [  ][ `.-. |  
\ `.___]  || \_/ |, | | | |  _| |_.' /| \__. | \ \/\ \/ /  | | | |  
 `._____.' '.__.'_/[___||__]|______.'  '.__.'   \__/\__/  [___||__] 
                                                                    """)
print("Gundown by Nick S - " + version + " - Debug: " + str(debug))

main()