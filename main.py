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

axis 5 - right trigger
axis 4 - left trigger

"""

version = "0.1.1"

# enables text debug on screen
debug = True

def main():
    # I - Initialize
    pygame.init()
    
    # D - Display configuration
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Gundown - " + version + " - Debug: " + str(debug))
    
    # E - Entities (just background for now)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))
    screen.blit(background, (0,0))

    # create 4 walls that surround the screen
    top_wall = character_sprites.StaticMapObject(screen, 0, 0, 1280, 10)
    left_wall = character_sprites.StaticMapObject(screen, 0, 0, 10, 720)
    right_wall = character_sprites.StaticMapObject(screen, 1270, 0, 10, 720)

    # latching testing wall 
    climable_wall = character_sprites.StaticMapObject(screen, 1260, 560, 10, 120, (200, 0, 200), "solid", True)

    # extra platform
    platform = character_sprites.StaticMapObject(screen, 500, 600, 300, 20)

    floor = character_sprites.StaticMapObject(screen, 0, 710, 1280, 10)

    # add a small 1/3rd green wall that is just bouncing around
    bounce_demo_wall = character_sprites.StaticMapObject(screen, 700, 10, 300, 10, (0, 255, 0), "bounce")

    mapSprites = pygame.sprite.Group(top_wall, left_wall, floor, platform, right_wall, bounce_demo_wall, climable_wall)

    # create a player sprite object from our mySprites module
    player = character_sprites.Player(screen, 100, 100, "mouse")

    player_health_bar = character_sprites.HealthBar(screen, player)
    player_ammo_count = character_sprites.BulletBar(screen, player)

    # add all sprites include the player, weapon, bullets, and map sprites to the allSprites group
    allSprites = pygame.sprite.OrderedUpdates(player, player_health_bar, player_ammo_count, mapSprites, player.weapon)
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

        # gravity logic
        if player.latching:
            # greeze gravity while latched to a wall
            player.gravity = 0
        else:
            if player.gravity < 0:  # - during upward motion -
                player.moveVertical(player.gravity, mapSprites)  # move the player upward

                # If head collision, start falling
                if character_sprites.collisionCheck(player, mapSprites):
                    player.gravity = 0.1  # start the falling phase immediately
                else:
                    player.gravity += 1.0  # normal upward deceleration

            else:  # - during falling motion -
                if player.gravity < 12:  # cap falling speed
                    player.gravity += 1.0  # gradually accelerate downward
                player.moveVertical(player.gravity, mapSprites)

        # scan to see if a controller is detected and switch to controller if so 
        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            player.controlScheme = "controller"
        else:
            player.controlScheme = "mouse"

        # check if player is controller or mouse
        if player.controlScheme == "controller":
            if joystick_count > 0:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()

                # add deadzones to axis
                axis0 = joystick.get_axis(0)
                axis1 = joystick.get_axis(1)

                # implement deadzone
                if axis0 < 0.1 and axis0 > -0.1:
                    axis0 = 0

                # implement deadzone
                if axis1 < 0.1 and axis1 > -0.1:
                    axis1 = 0

                # if player is using controller, then set the direction to the controller
                player.direction = player.getDirectionJoy((joystick.get_axis(2), joystick.get_axis(3)))
                
                player.moveHorizontal(axis0 * 10, mapSprites)

                # if player joystick is up, then jump
                if joystick.get_axis(1) < -0.8:
                    # check if player has jumped recently, then if not jump
                    if pygame.time.get_ticks() - player.lastJumpTime > 100:
                        player.jump(mapSprites)
                
                # if a face button is pressed
                if joystick.get_button(0):
                    # check if player has jumped recently, then if not jump
                    if pygame.time.get_ticks() - player.lastJumpTime > 100:
                        player.jump(mapSprites)
                
                # if the right trigger is pressed, fire the weapon
                right_trigger = joystick.get_axis(5) 
                if right_trigger > 0.5:  # Adjust threshold if needed
                    if player.weapon.ammo > 0:
                        player.weapon.fire()
                    elif not player.weapon.isReloading:
                        player.weapon.startReload()
                
                # latching with left trigger
                left_trigger = joystick.get_axis(4)
                if left_trigger > 0.5:
                    # only triggers when touching a wall with the latchable property
                    if player.canLatch:
                        player.latching = True
                    else:
                        player.latching = False
                else:
                    player.latching = False
        else:
            # if player is using mouse, then set the direction to the mouse
            player.direction = player.getDirectionMouse(pygame.mouse.get_pos())

            # K - Keys
            keys = pygame.key.get_pressed()

            if keys[pygame.K_q]:
                if player.canLatch:
                    player.latching = True
                else:
                    player.latching = False
            else:
                player.latching = False

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.moveHorizontal(-10, mapSprites)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.moveHorizontal(10, mapSprites)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player.jump(mapSprites)
            if keys[pygame.K_ESCAPE]:
                keepGoing = False

            # add ability to shoot with spacebar
            if keys[pygame.K_SPACE]:
                # fire using the weapon fire method using the x and y of the gun
                if player.weapon.ammo > 0:
                    player.weapon.fire()
                elif not player.weapon.isReloading:  # if no ammo and not already reloading
                    player.weapon.startReload()
            
        # allow bullets to have collision with walls
        for bullet in player.weapon.bulletList:
            bullet.collisionDetection(mapSprites, player)

        # put ammo count as black text top right
        font = pygame.font.SysFont("Arial", 16)
        
        if debug:
            # put debug text for player x, y, direction, guntype, ammo, health, is reloading
            p1Name = font.render("Player 1", True, (50, 0, 0))
            p1AmmoText = font.render("Ammo: " + str(player.weapon.ammo), True, (0, 0, 0))
            p1TextX = font.render("Player X: " + str(player.rect.x), True, (0, 0, 0))
            p1TextY = font.render("Player Y: " + str(player.rect.y), True, (0, 0, 0))
            p1TextDirection = font.render("Direction: " + str(player.direction), True, (0, 0, 0))
            p1TextGunType = font.render("Gun Type: " + str(player.weapon.weaponName), True, (0, 0, 0))
            p1TextHealth = font.render("Health: " + str(player.Health), True, (0, 0, 0))
            p1TextIsReloading = font.render("Is Reloading: " + str(player.weapon.isReloading), True, (0, 0, 0))
            p1TextCanLatch = font.render("Can Latch: " + str(player.canLatch), True, (0, 0, 0))
            p1TextIsLatched = font.render("Is Latched: " + str(player.latching), True, (0, 0, 0))
        
        # make bold green or red text depending on if control scheme is controller or mouse and give it a bit more space "Using Controller" "Using MnK"
        if player.controlScheme == "controller":
            p1TextControlScheme = font.render("Using Controller", True, (0, 255, 0))
        else:
            p1TextControlScheme = font.render("Using MnK", True, (255, 0, 0))

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


        allSprites.update()              # Update all sprites
        
        allSprites.draw(screen)          # Draw all sprites
        pygame.display.flip()            # Flip the display
    
    # Close the game window
    pygame.quit()

main()