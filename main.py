# I - Import
import pygame
import sys

from src.modules import character_sprites

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


pastel color palette:
red: (255,179,186)
orange: (255,223,186)
yellow: (255,255,186)
green: (186,255,201)
blue: (186,225,255)
purple: (227,218,255)


"""

version = "0.3.1.1"

# enables text debug on screen
debug = True

def main():
    # I - Initialize
    pygame.init()
    
    # D - Display configuration
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Gundown - " + version + " - Debug: " + str(debug))
    
    # E - Entities (just background for now)
    # make background space.gif in art
    background = pygame.image.load("src/art/space.gif")

    # change mouse cursor to a crosshair
    pygame.mouse.set_visible(False)
    crosshair = pygame.image.load("src/art/hud/cross/crosshair_320.png").convert_alpha()
    # add transparency to the crosshair
    crosshair.set_colorkey((0, 0, 0))
    # scale down
    crosshair = pygame.transform.scale(crosshair, (32, 32))


    screen.blit(background, (0,0))

    # create 4 walls that surround the screen
    top_wall = character_sprites.StaticMapObject(screen, 0, 0, 1280, 10, (5, 1, 23, 255), 255)
    left_wall = character_sprites.StaticMapObject(screen, -20, 0, 10, 720, (5, 1, 23, 50), 255)
    right_wall = character_sprites.StaticMapObject(screen, 1280, 0, 10, 720, (5, 1, 23, 50), 255)

    # latching testing wall 
    climable_wall = character_sprites.StaticMapObject(screen, 1260, 560, 10, 120, (200, 0, 200), 255, "solid", True)

    # extra platform
    platform = character_sprites.StaticMapObject(screen, 500, 600, 300, 20, (32, 4, 131), 100)
    floor = character_sprites.StaticMapObject(screen, 0, 710, 1280, 10, (255, 255, 255, 30), 255)

    # add a small 1/3rd green wall that is just bouncing around
    bounce_demo_wall = character_sprites.StaticMapObject(screen, 700, 10, 300, 10, (0, 255, 0), 255, "bounce")

    # add a box with physics
    box = character_sprites.StaticMapObject(screen, 500, 200, 50, 50, (255, 0, 0), 255, "solid", False, True, 1)

    # create a sprite group for all physics objects
    physicsObjects = pygame.sprite.Group(box) 
    mapSprites = pygame.sprite.Group(top_wall, left_wall, floor, platform, right_wall, bounce_demo_wall, climable_wall, physicsObjects)

    players = pygame.sprite.Group()
    # create a player sprite object from our mySprites module
    players.add(character_sprites.Player(screen, 100, 100, "mouse", character_sprites.Colors.purple))



    # add all sprites include the player, weapon, bullets, and map sprites to the allSprites group
    allSprites = pygame.sprite.OrderedUpdates(players, mapSprites)

    # for each player, append their weapon to the allSprites group
    for player in players:
        allSprites.add(player.weapon)

    # A - Action (broken into ALTER steps)
    
    # A - Assign values to key variables
    clock = pygame.time.Clock()
    keepGoing = True

    # L - Loop
    while keepGoing:
        # T - Timer to set frame rate
        clock.tick(60) 

        
    
        # E - Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False

        # make the mouse cursor the crosshair
        


        # if the L button is pressed, add 1 more player for a max of 2 players
        if pygame.key.get_pressed()[pygame.K_l] and len(players) < 2:
            players.add(character_sprites.Player(screen, 100, 100, "controller", (255, 255, 0)))
            allSprites.add(players)
            # add the new player's weapon to the allSprites group
            for player in players:
                # check if the players weapon is already in the allSprites group
                if player.weapon not in allSprites:
                    allSprites.add(player.weapon)

        # scan to see if a controller is detected and switch to controller if so 
        joystick_count = pygame.joystick.get_count()

        for player in players:
            # gravity logic
            player.runTimeGravityManager(mapSprites)

            # check if player is controller or mouse
            if player.controlScheme == "controller":
                    if joystick_count > 0:
                        joystick = pygame.joystick.Joystick(0)
                        joystick.init()
                        player.runTimeJoyMovement(joystick, mapSprites)
            else:
                player.runTimeMnkMovement(mapSprites)

            # if the player has a shieldBuble, draw it
            if player.shieldBubble != None:
                allSprites.add(player.shieldBubble)
                
            # allow bullets to have collision with walls
            for bullet in player.weapon.bulletList:
                bullet.collisionDetection(mapSprites, players)

        # put ammo count as black text top right
        font = pygame.font.SysFont("Arial", 16)

        
        
        if debug:
            # make it so its based on how many players there are and put it into list
            p1Name = font.render("Player 1", True, (150, 0, 0))
            p1AmmoText = font.render("Ammo: " + str(players.sprites()[0].weapon.ammo), True, (255, 255, 255))
            p1TextX = font.render("Player X: " + str(players.sprites()[0].rect.x), True, (255, 255, 255))
            p1TextY = font.render("Player Y: " + str(players.sprites()[0].rect.y), True, (255, 255, 255))
            p1TextDirection = font.render("Direction: " + str(players.sprites()[0].direction), True, (255, 255, 255))
            p1TextGunType = font.render("Gun Type: " + str(players.sprites()[0].weapon.weaponName), True, (255, 255, 255))
            p1TextHealth = font.render("Health: " + str(players.sprites()[0].Health), True, (255, 255, 255))
            p1TextIsReloading = font.render("Is Reloading: " + str(players.sprites()[0].weapon.isReloading), True, (255, 255, 255))
            p1TextCanLatch = font.render("Can Latch: " + str(players.sprites()[0].canLatch), True, (255, 255, 255))
            p1TextIsLatched = font.render("Is Latched: " + str(players.sprites()[0].latching), True, (255, 255, 255))

            # if there is a second player, add the debug text for player 2
            if len(players) > 1:
                p2Name = font.render("Player 2", True, (0, 0, 150))
                p2AmmoText = font.render("Ammo: " + str(players.sprites()[1].weapon.ammo), True, (255, 255, 255))
                p2TextX = font.render("Player X: " + str(players.sprites()[1].rect.x), True, (255, 255, 255))
                p2TextY = font.render("Player Y: " + str(players.sprites()[1].rect.y), True, (255, 255, 255))
                p2TextDirection = font.render("Direction: " + str(players.sprites()[1].direction), True, (255, 255, 255))
                p2TextGunType = font.render("Gun Type: " + str(players.sprites()[1].weapon.weaponName), True, (255, 255, 255))
                p2TextHealth = font.render("Health: " + str(players.sprites()[1].Health), True, (255, 255, 255))
                p2TextIsReloading = font.render("Is Reloading: " + str(players.sprites()[1].weapon.isReloading), True, (255, 255, 255))
                p2TextCanLatch = font.render("Can Latch: " + str(players.sprites()[1].canLatch), True, (255, 255, 255))
                p2TextIsLatched = font.render("Is Latched: " + str(players.sprites()[1].latching), True, (255, 255, 255))
                
        
        # make bold green or red text depending on if control scheme is controller or mouse and give it a bit more space "Using Controller" "Using MnK"
        if player.controlScheme == "controller":
            p1TextControlScheme = font.render("Using Controller", True, (0, 255, 0))
            if len(players) > 1:
                p2TextControlScheme = font.render("Using Controller", True, (0, 255, 0))
        else:
            p1TextControlScheme = font.render("Using MnK", True, (255, 0, 0))
            if len(players) > 1:
                p2TextControlScheme = font.render("Using MnK", True, (255, 0, 0))

        # for every physics object, call their internal function: runtimeGravity
        for physicsObject in physicsObjects:
            physicsObject.runtimeGravity(mapSprites)


        for player in players:
            # check if player is dead
            if player.Health <= 0:
                player.kill()
                # kill the gun
                player.weapon.kill()
                print("Player is dead")

            # the reload complete method checks if the reload time has passed and if so, sets the ammo back to the max
            player.weapon.checkReloadComplete()
            
            # allways add new bullets to the allSprites group
            allSprites.add(player.weapon.bulletList)

            # allows for reloading of the weapon
            player.update()
            player.weapon.update()

        # Refresh screen
        screen.blit(background, (0, 0))  # Redraw the full background first

        # draw the debug text
        if debug:
            screen.blit(p1Name, (1000, 20))
            screen.blit(p1AmmoText, (1000, 40))
            screen.blit(p1TextX, (1000, 60))
            screen.blit(p1TextY, (1000, 80))
            screen.blit(p1TextDirection, (1000, 100))
            screen.blit(p1TextGunType, (1000, 120))
            screen.blit(p1TextHealth, (1000, 140))
            screen.blit(p1TextIsReloading, (1000, 160))
            screen.blit(p1TextControlScheme, (1000, 180))
            screen.blit(p1TextCanLatch, (1000, 200))
            screen.blit(p1TextIsLatched, (1000, 220))

            if len(players) > 1:
                # same height other side of screen
                screen.blit(p2Name, (20, 20))
                screen.blit(p2AmmoText, (20, 40))
                screen.blit(p2TextX, (20, 60))
                screen.blit(p2TextY, (20, 80))
                screen.blit(p2TextDirection, (20, 100))
                screen.blit(p2TextGunType, (20, 120))
                screen.blit(p2TextHealth, (20, 140))
                screen.blit(p2TextIsReloading, (20, 160))
                screen.blit(p2TextCanLatch, (20, 200))
                screen.blit(p2TextIsLatched, (20, 220))
                screen.blit(p2TextControlScheme, (20, 180))


        allSprites.update()              # Update all sprites
        allSprites.draw(screen)          # Draw all sprites
        screen.blit(crosshair, pygame.mouse.get_pos())
        pygame.display.flip()            # Flip the display
    
    # Close the game window
    pygame.quit()

main()