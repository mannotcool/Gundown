# I - Import
import pygame # type: ignore

from src.modules import entities, utils, gui, abilityCards, weaponManager
from src.modules import sceneManager
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

version = "0.8.3"

# enables certain console logs, turns off background music
debug = True

def main():
    # I - Initialize
    pygame.init()
    
    # D - Display configuration
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Gundown - " + version + " - Debug: " + str(debug))
    
    # if debug is on, print number of joysticks connected
    if debug:
        print("Number of joysticks connected on boot: " + str(pygame.joystick.get_count()))

    selectedPlayerColors = sceneManager.showStartScreen(screen)

    # E - Entities (just background for now)
    # make background space.gif in art
    background = pygame.image.load("src/art/backgrounds/dark_background.gif")

    screen.blit(background, (0,0))

    # change mouse cursor to a crosshair
    pygame.mouse.set_visible(False)
    crosshair = pygame.image.load("src/art/hud/cross/crosshair_320.png").convert_alpha()

    # add transparency to the crosshair
    crosshair.set_colorkey((0, 0, 0))
    # scale down
    crosshair = pygame.transform.scale(crosshair, (32, 32))

    # MAP A:
    importedMap = mapA.MapA(screen)
    
    deadPlayers = []

    # create the players with the colors selected
    players = pygame.sprite.Group()
    # create a player sprite object from our mySprites module
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

    # now respawn them:
    utils.generalizedRespawn(players)
    if debug:
        print("Number of joysticks connected after respawn: " + str(pygame.joystick.get_count()))

    # create a sprite group for all physics objects
    mapSprites = importedMap[0]
    physicsObjects = importedMap[1]
    # -- END OF MAP --

    # PLAYERS:

    # for every player, create a scorekeeper object
    scoreKeepers = pygame.sprite.Group()
    for player in players:
        if debug:
            print("Creating scorekeeper...")
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
    disableRespawns = False
    keepGoing = True

    # L - Loop
    while keepGoing:
        # T - Timer to set frame rate
        clock.tick(60) 

        # E - Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False

        # Main game loop!

        
        # Detect round completion and show the ability card screen
        for player in players:
            if player.isDead and player not in deadPlayers:
                deadPlayers.append(player)
                
        # scan to see if a controller is detected and switch to controller if so 
        joystick_count = pygame.joystick.get_count()

        # initalize fonts
        pygame.font.init()
        font = pygame.font.SysFont("Arial", 16)
        pixelArtFont = pygame.font.Font("src/fonts/ThaleahFat.ttf", 96)

        # respawn system
        if len(deadPlayers) == (len(players) - 1):
            if disableRespawns == False:
                deadPlayers = utils.deathHandler(deadPlayers, players, sceneManager, screen, allSprites, abilityCards)
                if debug:
                    print("Respawning players...")
            else:
                if debug:
                    print("Respawns disabled, game over!")
                # print label Game over in the top middle using custom font, and color of winning player who is still alive
                for player in players:
                    if player not in deadPlayers:
                        screen.blit(pixelArtFont.render("Game Over!", True, player.colorScheme), (600, 10))
                
        # runtime manager
        for player in players:
            if player.score == 3:
                disableRespawns = True

            # gravity logic
            player.runTimeGravityManager(mapSprites)

            # check if player is controller or mouse
            if player.controlScheme == "controller":
                if player.joyStick != None:
                    player.joyStick.init()
                    player.runTimeJoyMovement(player.joyStick, mapSprites)
            else:
                player.runTimeMnkMovement(mapSprites)

            # if the player has a shieldBuble, draw it
            if player.shieldBubble != None:
                allSprites.add(player.shieldBubble)
                
            # allow bullets to have collision with walls
            for bullet in player.weapon.bulletList:
                bullet.collisionDetection(mapSprites, players, player.weapon.bulletList)
    
            # check if player is dead
            if player.Health <= 0:
                player.isDead = True

            # the reload complete method checks if the reload time has passed and if so, sets the ammo back to the max
            player.weapon.checkReloadComplete()
            
            # allways add new bullets to the allSprites group
            allSprites.add(player.weapon.bulletList)

            # allows for reloading of the weapon
            player.update()
            player.weapon.update()
           
            # print in bottom right corner if respawns are disabled
            if disableRespawns:
                screen.blit(font.render("Respawns Disabled", True, (255, 0, 0)), (1000, 680))

        # for every physics object, call their internal function: runtimeGravity
        for physicsObject in physicsObjects:
            physicsObject.runtimeGravity(mapSprites)

        # Refresh screen
        screen.blit(background, (0, 0))  # Redraw the full background first

        allSprites.update()              # Update all sprites
        allSprites.draw(screen)          # Draw all sprites
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