# I - Import
import pygame # type: ignore

from src.modules import mapManager, entities, utils, gui, abilityCards
from src.modules import sceneManager

"""
GENERAL NOTES:

- The player supports both mouse and controller input
- Shooting is with space
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

version = "0.8.0.1"

# enables text debug on screen
debug = False

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
    background = pygame.image.load("src/art/dark_background.gif")

    screen.blit(background, (0,0))

    # change mouse cursor to a crosshair
    pygame.mouse.set_visible(False)
    crosshair = pygame.image.load("src/art/hud/cross/crosshair_320.png").convert_alpha()
    # add transparency to the crosshair
    crosshair.set_colorkey((0, 0, 0))
    # scale down
    crosshair = pygame.transform.scale(crosshair, (32, 32))


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



    # make a box that you can walk through
    # box_walkthrough = character_sprites.StaticMapObject(screen, 600, 400, 50, 50, (200, 0, 0), 100, "solid", False, False, 1, True)

    # create the players with the colors selected

    deadPlayers = []

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
            

    # now respawn them:
    utils.generalizedRespawn(players)

    # create a sprite group for all physics objects
    mapSprites = pygame.sprite.Group(decorative_pillars, left_wall, right_wall, floor, physicsObjects)

    # -- END OF MAP --

    # PLAYERS



    # for every player, create a scorekeeper object
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

        # Main game loop

        
        

        # Detect round completion and show the ability card screen
        for player in players:
            if player.isDead and player not in deadPlayers:
                deadPlayers.append(player)
                
        # scan to see if a controller is detected and switch to controller if so 
        joystick_count = pygame.joystick.get_count()
        font = pygame.font.SysFont("Arial", 16)

        # respawn system
        if len(deadPlayers) == (len(players) - 1) and disableRespawns == False:
            deadPlayers = utils.deathHandler(deadPlayers, players, sceneManager, screen, allSprites, abilityCards)

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
print("Gundown by Nick S- " + version + " - Debug: " + str(debug))
if debug:
    print("Hello! If you are seeing this, debug mode is enabled. You may turn it off by setting debug to False in main.py")
    print("Debug mode will display player stats, such as ammo, health, and position on screen")

main()