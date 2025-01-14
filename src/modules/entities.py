import pygame
import math

from . import utils
from . import gui

class Entity(pygame.sprite.Sprite):
    # Used by any entity that needs to have physics applied to it
    def __init__(self, screen):
        # Call the parent __init__() method
        pygame.sprite.Sprite.__init__(self)
        
        # Define all possible variables for an entity
        self.image = None
        self.rect = None
        self.direction = 0
        self.speed = 0
        self.MaxHealth = 0
        self.Health = 0
        self.damage = 0
        self.affectedByGravity = False
        self.gravity = 0
        self.x = 0
        self.y = 0
        
# Players are called boxies
class Player(Entity):
    def __init__(self, screen, x, y, controlScheme, color=utils.Colors.red, joystick=None):
        Entity.__init__(self, screen)
        self.colorScheme = color
        self.score = 0
        self.joyStick = joystick

        # show boxie image
        self.image = pygame.image.load("src/art/character/boxie-white/default-51.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (39, 39))

        # lt the player choose their color, and use pygame's color blending to change the color of the player
        self.image.fill(color, special_flags=pygame.BLEND_RGB_MULT)

        # set the rect of the player to the image
        self.rect = self.image.get_rect()
        self.direction = 2
        self.walkSpeed = 10
        self.screen = screen

        self.MaxHealth = 100
        self.Health = self.MaxHealth
        
        self.affectedByGravity = True
        self.gravity = 12
        self.lastJumpTime = 0
        self.controlScheme = controlScheme

        self.x = x
        self.y = y 
        self.rect.left = x
        self.rect.top = y 
        self.canLatch = False
        self.latching = False

        self.shieldBubble = None
        self.lastTimeShieldBubble = 0

        # Define variable where the type is the pistol class
        self.weapon = None
        self.isDead = False
        self.exploadingBullets = False
        self.exploadingBulletTime = 0

    def displayGUI(self, screen):
        playerHealthBar = gui.HealthBar(screen, self)
        playerAmmoCount = gui.BulletBar(screen, self)
        return playerHealthBar, playerAmmoCount
    
    def attachWeapon(self, weapon):
        self.weapon = weapon
    
    def createShieldBubble(self, shieldFx):
        # Ensure the cooldown for shield creation is respected
        current_time = pygame.time.get_ticks()
        if self.shieldBubble:
            return

        if current_time - self.lastTimeShieldBubble < 8000:
            return

        # Create the shield bubble
        print("creating shield")
        shieldFx.play()

        self.shieldBubble = ShieldBubble(self.screen, self)
        self.shieldBubble.rect.center = self.rect.center
        self.lastTimeShieldBubble = current_time

    def runTimeGravityManager(self, mapSprites):
        if self.latching:
            # greeze gravity while latched to a wall
            self.gravity = 0
        else:
            if self.gravity < 0:  # - during upward motion -
                self.moveVertical(self.gravity, mapSprites)  # move the player upward

                # If head collision, start falling
                if utils.collisionCheck(self, mapSprites):
                    self.gravity = 0.1  # start the falling phase immediately
                else:
                    self.gravity += 1.0  # normal upward deceleration

            else:  # - during falling motion -
                if self.gravity < 12:  # cap falling speed
                    self.gravity += 1.0  # gradually accelerate downward
                self.moveVertical(self.gravity, mapSprites)
    
    def getDirectionMouse(self, mousePos):
        # get the angle in radians between the player and the mouse, where self.rect.center[1] is the Y and self.rect.center[0] is the X
        angle = math.atan2(mousePos[1] - self.rect.center[1], mousePos[0] - self.rect.center[0])
        # convert the angle to degrees
        angle = angle * (180 / math.pi)
        # return the angle
        return angle
    
    def getDirectionJoy(self, joyPos):
        # get the angle between the player and the joystick
        angle = math.atan2(joyPos[1], joyPos[0])
        # convert the angle to degrees
        angle = angle * (180 / math.pi)
        # return the angle
        return angle
    
    # use x and y to keep track of the player's position, and thats the center of the player
    def moveHorizontal(self, x, mapSprites):
        # if player is dead, then dont allow movement
        if self.isDead:
            return
        
        # Reset the latchable flag to False initially
        self.canLatch = False

        # Move the player horizontally
        self.rect.left += x

        # Check collisions with map sprites
        for sprite in mapSprites:
            if pygame.sprite.collide_rect(self, sprite):
                if x < 0:  # Moving left
                    if sprite.latchable:
                        self.canLatch = True
                    if sprite.affectedByGravity:
                        sprite.moveHorizontal(x, mapSprites)
                    elif not sprite.decorative:  # Block movement if not decorative
                        self.rect.left = sprite.rect.right
                elif x > 0:  # Moving right
                    if sprite.latchable:
                        self.canLatch = True
                    if sprite.affectedByGravity:
                        sprite.moveHorizontal(x, mapSprites)
                    elif not sprite.decorative:  # Block movement if not decorative
                        self.rect.right = sprite.rect.left

        # Center the player's x-coordinate
        self.x = self.rect.center[0]



    def moveVertical(self, y, mapSprites):
        # if player is dead, then dont allow movement
        if self.isDead:
            return
        
        if not self.latching:
            self.rect.top += y
            for sprite in mapSprites:
                if pygame.sprite.collide_rect(self, sprite):
                    if y < 0:
                        if sprite.affectedByGravity:
                            sprite.moveVertical(y, mapSprites)
                        elif sprite.decorative:
                            pass
                        else:
                            self.rect.top = sprite.rect.bottom
                    elif y > 0:
                        if sprite.affectedByGravity:
                            self.rect.bottom = sprite.rect.top
                        elif sprite.decorative:
                            pass
                        else:
                            self.rect.bottom = sprite.rect.top
            # center the player's y to the rect
            self.y = self.rect.center[1]

    def jump(self, mapSprites):
        # if player is dead, then dont allow movement
        if self.isDead:
            return
        
        self.rect.top += 1
        on_ground = False
        for sprite in mapSprites:
            if pygame.sprite.collide_rect(self, sprite): 
                # if its in a decorative block it doesnt mean it can jump
                if sprite.decorative:
                    continue
                
                on_ground = True
                break
        self.rect.top -= 1

        # only allow jumping when on the ground and not latched
        if on_ground and not self.latching:
            self.gravity = -16  # negative gravity for upward motion, see main.py

    def weaponFire(self, shotFx):
        # if player is dead, then dont allow movement
        if self.isDead:
            return

        # play the shot sound
        shotFx.play()
        self.weapon.fire()

    def runTimeJoyMovement(self, joystick, mapSprites, shotFx, reloadFx, shieldFx):
        # if player is dead, then dont allow movement
        if self.isDead:
            return
        
        # shield if any trigger is pressed
        if joystick.get_button(9) or joystick.get_button(10):
            self.createShieldBubble(shieldFx)

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
        self.direction = self.getDirectionJoy((joystick.get_axis(2), joystick.get_axis(3)))
        
        self.moveHorizontal(axis0 * self.walkSpeed, mapSprites)

        # if player joystick is up, then jump
        if joystick.get_axis(1) < -0.8:
            # check if player has jumped recently, then if not jump
            if pygame.time.get_ticks() - self.lastJumpTime > 100:
                self.jump(mapSprites)
        
        # if a face button is pressed
        if joystick.get_button(0):
            # check if player has jumped recently, then if not jump
            if pygame.time.get_ticks() - self.lastJumpTime > 100:
                self.jump(mapSprites)

        # reload if x is pressed
        if joystick.get_button(2):
            # reload the weapon if the magazine is not the same size as the ammo 
            if self.weapon.ammo < self.weapon.magazineSize:
                self.weapon.startReload(reloadFx)
        
        # if the right trigger is pressed, fire the weapon
        right_trigger = joystick.get_axis(5) 
        if right_trigger > 0.5:  # Adjust threshold if needed
            if self.weapon.ammo > 0:
                self.weapon.fire(shotFx)
            elif not self.weapon.isReloading:
                self.weapon.startReload(reloadFx)
        
        # latching with left trigger
        left_trigger = joystick.get_axis(4)
        if left_trigger > 0.5:
            # only triggers when touching a wall with the latchable property
            if self.canLatch:
                self.latching = True
            else:
                self.latching = False
        else:
            self.latching = False

    def runTimeMnkMovement(self, mapSprites, shotFx, reloadFx, shieldFx):
        if self.isDead:
            return
        
        # if player is using mouse, then set the direction to the mouse
        self.direction = self.getDirectionMouse(pygame.mouse.get_pos())

        # K - Keys
        keys = pygame.key.get_pressed()

        if keys[pygame.K_q]:
            if self.canLatch:
                self.latching = True
            else:
                self.latching = False
        else:
            self.latching = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.moveHorizontal(-self.walkSpeed, mapSprites)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.moveHorizontal(self.walkSpeed, mapSprites)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.jump(mapSprites)
        if keys[pygame.K_e]:
            self.createShieldBubble(shieldFx)
        if keys[pygame.K_r]:
            # reload the weapon if the magazine is not the same size as the ammo 
            if self.weapon.ammo < self.weapon.magazineSize:
                self.weapon.startReload(reloadFx)
            
        # add ability to shoot with spacebar or left mouse button
        if pygame.mouse.get_pressed()[0]:
            # fire using the weapon fire method using the x and y of the gun
            if self.weapon.ammo > 0:
                self.weapon.fire(shotFx)
            elif not self.weapon.isReloading:  # if no ammo and not already reloading
                self.weapon.startReload(reloadFx)

    def respawnPlayerAtCords(self, x, y):
        self.isDead = False
        self.x = x
        self.y = y
        self.rect.left = x
        self.rect.top = y
        self.Health = self.MaxHealth
        # reset the player's weapon ammo
        self.weapon.ammo = self.weapon.magazineSize

        # fix alpha on weapon
        self.weapon.image.set_alpha(255)


    def update(self):
        # update player's position
        self.rect.center = (self.x, self.y)

        # ensure shield bubble is always following the player
        if self.shieldBubble:
            # check if shield bubble is destroyed, if so, remove it
            if self.shieldBubble.Health <= 0:
                self.shieldBubble.kill()
                self.lastTimeShieldBubble = pygame.time.get_ticks()
                self.shieldBubble = None
            else:
                self.shieldBubble.rect.center = self.rect.center

                # draw the shield bubble from here
                self.screen.blit(self.shieldBubble.image, self.shieldBubble.rect)

        # draw gui to player image using function
        player_health_bar, player_ammo_count = self.displayGUI(self.screen)
        player_health_bar.update()
        player_ammo_count.update()
    
        # if player is dead, make them invisible
        if self.isDead:
            self.image.set_alpha(35)
        else:
            self.image.set_alpha(255)

        # draw the player's health bar and ammo count
        self.screen.blit(player_health_bar.image, player_health_bar.rect)
        self.screen.blit(player_ammo_count.image, player_ammo_count.rect)

        # update the weapon's position and state
        self.weapon.update()
    


class ShieldBubble(Entity):
    def __init__(self, screen, player):
        Entity.__init__(self, screen)
        self.window = screen
        # make a near transparent light blue circle
        self.image = pygame.Surface((100, 100)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        # make an elipse 144,213,255,20
        pygame.draw.ellipse(self.image, (144, 213, 255, 40), (0, 0, 100, 100))
        
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center
        
        self.affectedByGravity = False
        self.gravity = 0
        self.MaxHealth = 6
        self.Health = self.MaxHealth   

    def dealDamageToShield(self, damage):
        self.Health -= damage  # deal damage to the shield   
        if self.Health <= 0:
            self.kill()

