"""
    Author: Nick S
    Date: January 15th, 2025
    Description: Houses all the entities for the game, excluding bullets.
"""

# I - Import & Initialize
import pygame
import math
from . import utils
from . import gui

class Entity(pygame.sprite.Sprite):
    """
        Description:
        Parent class for all entities in the game
    """
    def __init__(self, screen):
        # Call the parent __init__() method
        pygame.sprite.Sprite.__init__(self)
        
        # Define all possible variables for an entity
        self.image = None
        self.rect = None
        self.screen = screen
        self.direction = 0
        self.speed = 0
        self.MaxHealth = 0
        self.Health = 0
        self.damage = 0
        self.affectedByGravity = False
        self.gravity = 0
        self.x = 0
        self.y = 0
        
class Player(Entity):
    """
        Description:
        Player class, the main character of the game (boxie)
    """
    def __init__(self, screen, x, y, controlScheme, color=utils.Colors.RED, joystick=None):
        Entity.__init__(self, screen)
        # the color from the startscreen
        self.colorScheme = color

        # your points, will be passed to gui
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

        # mouse or controller
        self.controlScheme = controlScheme

        self.x = x
        self.y = y 
        self.rect.left = x
        self.rect.top = y 

        # latch onto latchable objects
        self.canLatch = False
        self.latching = False

        # your bumper q shield
        self.shieldBubble = None
        self.lastTimeShieldBubble = 0

        # define variable where the type is the pistol class
        self.weapon = None
        self.isDead = False
        self.exploadingBullets = False
        self.exploadingBulletTime = 0

    def displayGUI(self, screen):
        """
        Description: Display the player's health bar and ammo count on the screen
        args: screen - the screen to display the gui on
        return: playerHealthBar, playerAmmoCount - the health bar and ammo count objects
        """

        playerHealthBar = gui.HealthBar(screen, self)
        playerAmmoCount = gui.BulletBar(screen, self)
        return playerHealthBar, playerAmmoCount
    
    def attachWeapon(self, weapon):
        """
        Description: Attach a weapon to the player
        args: weapon - the weapon to attach to the player
        """

        self.weapon = weapon
    
    def createShieldBubble(self, shieldFx):
        """
        Description: Create a shield bubble around the player
        args: shieldFx - the sound effect to play when the shield is created
        """

        # Ensure the cooldown for shield creation is respected
        current_time = pygame.time.get_ticks()

        # don't create a shield if one already exists or if the cooldown is not respected
        if self.shieldBubble:
            return

        if current_time - self.lastTimeShieldBubble < 8000:
            return

        # Create the shield bubble
        print("creating shield")
        shieldFx.play()

        # create a shield bubble object and set it to the player's shieldBubble attribute
        self.shieldBubble = ShieldBubble(self.screen, self)
        self.shieldBubble.rect.center = self.rect.center
        self.lastTimeShieldBubble = current_time

    def runTimeGravityManager(self, mapSprites):
        """
        Description: Manage the player's gravity during runtime
        args: mapSprites - the map sprites to check for collisions
        """

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
        """
        Description: Get the direction of the player based on the mouse position
        args: mousePos - the position of the mouse
        return: angle - the angle of the player in degrees
        """

        # get the angle between the player and the mouse by creating a triangle with the x and y of the mouse (it is in radians)
        angle = math.atan2(mousePos[1] - self.rect.center[1], mousePos[0] - self.rect.center[0])
        # convert the angle to degrees
        angle = angle * (180 / math.pi)
        # return the angle
        return angle
    
    def getDirectionJoy(self, joyPos):
        """
        Description: Get the direction of the player based on the joystick position
        args: joyPos - the position of the joystick
        return: angle - the angle of the player in degrees
        """

        # get the angle between the player and the joystick by creating a triangle with the x and y of the joystick (it is in radians)
        angle = math.atan2(joyPos[1], joyPos[0])
        # convert the angle to degrees
        angle = angle * (180 / math.pi)
        # return the angle
        return angle
    
    # use x and y to keep track of the player's position, and thats the center of the player
    def moveHorizontal(self, x, mapSprites):
        """
        Description: Move the player horizontally. This additionally handles collisions with map sprites
        args: x - the amount to move the player horizontally
              mapSprites - the map sprites to check for collisions
        """ 

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
                # moving left
                if x < 0:
                    if sprite.latchable:
                        self.canLatch = True
                    if sprite.affectedByGravity:
                        sprite.moveHorizontal(x, mapSprites)
                    elif not sprite.decorative:  
                        # block movement if not decorative by setting the player's right side to the sprite's left side
                        self.rect.left = sprite.rect.right

                # moving right
                elif x > 0: 
                    if sprite.latchable:
                        self.canLatch = True
                    if sprite.affectedByGravity:
                        sprite.moveHorizontal(x, mapSprites)
                    elif not sprite.decorative:  
                        # block movement if not decorative by setting the player's left side to the sprite's right side
                        self.rect.right = sprite.rect.left

        # center the player's xcoord
        self.x = self.rect.center[0]

    def moveVertical(self, y, mapSprites):
        """
        Description: Move the player vertically. This additionally handles collisions with map sprites
        args: y - the amount to move the player vertically
              mapSprites - the map sprites to check for collisions
        """
        
        # if player is dead, then dont allow movement
        if self.isDead:
            return
        
        # move the player vertically
        if not self.latching:
            self.rect.top += y
            for sprite in mapSprites:
                if pygame.sprite.collide_rect(self, sprite):
                    # if the player is moving down
                    if y < 0:
                        if sprite.affectedByGravity:
                            sprite.moveVertical(y, mapSprites)
                        elif sprite.decorative:
                            # if the sprite is decorative, then ignore it
                            pass
                        else:
                            self.rect.top = sprite.rect.bottom

                    # if the player is moving up
                    elif y > 0:
                        if sprite.affectedByGravity:
                            self.rect.bottom = sprite.rect.top
                        elif sprite.decorative:
                            # if the sprite is decorative, then ignore it
                            pass
                        else:
                            self.rect.bottom = sprite.rect.top
            # center the player's y to the rect
            self.y = self.rect.center[1]

    def jump(self, mapSprites):
        """
        Description: Make the player jump. This additionally handles collisions with map sprites
        args: mapSprites - the map sprites to check for collisions
        """
        
        # if player is dead, then dont allow movement
        if self.isDead:
            return
        
        # custom script for checking head collisions:

        # we put the players head by 1 pixel into the block above
        self.rect.top += 1
        onGround = False
        for sprite in mapSprites:
            # and if the player doesnt collide with a block, then they are on the ground
            if pygame.sprite.collide_rect(self, sprite): 
                # if its in a decorative block it doesnt mean it can jump
                if sprite.decorative:
                    continue
                
                onGround = True
                break

        # move the player back to the original position
        self.rect.top -= 1

        # only allow jumping when on the ground and not latched
        if onGround and not self.latching:
            self.gravity = -16  # negative gravity for upward motion, see runtimeGravity

    def weaponFire(self, shotFx):
        """
        Description: Fire the player's weapon
        args: shotFx - the sound effect to play when the weapon is fired
        """

        # if player is dead, then dont allow movement
        if self.isDead:
            return

        # play the shot sound
        shotFx.play()
        self.weapon.fire()

    def runTimeJoyMovement(self, joystick, mapSprites, shotFx, reloadFx, shieldFx):
        """
        Description: Manage the player's movement during runtime using a joystick
        args: joystick - the joystick to get input from
              mapSprites - the map sprites to check for collisions
              shotFx - the sound effect to play when the weapon is fired
              reloadFx - the sound effect to play when the weapon is reloaded
              shieldFx - the sound effect to play when the shield is created
        """
        
        # if player is dead, then dont allow movement
        if self.isDead:
            return
        
        # shield if any trigger is pressed
        if joystick.get_button(9) or joystick.get_button(10):
            self.createShieldBubble(shieldFx)

        # implement deadzones because lets be real all controllers have stickdrift
        axis0 = joystick.get_axis(0)
        axis1 = joystick.get_axis(1)

        if axis0 < 0.1 and axis0 > -0.1:
            axis0 = 0

        if axis1 < 0.1 and axis1 > -0.1:
            axis1 = 0

        # if player is using controller, then set the direction to the controller
        self.direction = self.getDirectionJoy((joystick.get_axis(2), joystick.get_axis(3)))
        self.moveHorizontal(axis0 * self.walkSpeed, mapSprites)

        # if player joystick is up or a is pressed, then jump
        if joystick.get_axis(1) < -0.8:
            # check if player has jumped recently, then if not jump
            if pygame.time.get_ticks() - self.lastJumpTime > 100:
                self.jump(mapSprites)

        if joystick.get_button(0):
            if pygame.time.get_ticks() - self.lastJumpTime > 100:
                self.jump(mapSprites)

        # reload if x is pressed
        if joystick.get_button(2):
            # reload the weapon if the magazine is not the same size as the ammo 
            if self.weapon.ammo < self.weapon.magazineSize:
                self.weapon.startReload(reloadFx)
        
        # if the right trigger is pressed, fire the weapon
        rightTrigger = joystick.get_axis(5) 

        if rightTrigger > 0.5:
            if self.weapon.ammo > 0:
                self.weapon.fire(shotFx)
            elif not self.weapon.isReloading:
                self.weapon.startReload(reloadFx)
        
        # latching with left trigger
        leftTrigger = joystick.get_axis(4)
        if leftTrigger > 0.5:
            # only triggers when touching a wall with the latchable property
            if self.canLatch:
                self.latching = True
            else:
                self.latching = False
        else:
            self.latching = False

    def runTimeMnkMovement(self, mapSprites, shotFx, reloadFx, shieldFx):
        """
        Description: Manage the player's movement during runtime using the mouse and keyboard
        args: mapSprites - the map sprites to check for collisions
              shotFx - the sound effect to play when the weapon is fired
              reloadFx - the sound effect to play when the weapon is reloaded
              shieldFx - the sound effect to play when the shield is created
        """
        
        if self.isDead:
            return
        
        # if player is using mouse, then set the direction to the mouse
        self.direction = self.getDirectionMouse(pygame.mouse.get_pos())

        # K - Keys
        keys = pygame.key.get_pressed()

        # latch with q
        if keys[pygame.K_q]:
            if self.canLatch:
                self.latching = True
            else:
                self.latching = False
        else:
            self.latching = False

        # general movement and reload
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.moveHorizontal(-self.walkSpeed, mapSprites)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.moveHorizontal(self.walkSpeed, mapSprites)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.jump(mapSprites)
        if keys[pygame.K_e]:
            self.createShieldBubble(shieldFx)
        if keys[pygame.K_r]:
            if self.weapon.ammo < self.weapon.magazineSize:
                self.weapon.startReload(reloadFx)
            
        # add ability to shoot with left mouse button, also without scanning in the event loop
        if pygame.mouse.get_pressed()[0]:
            if self.weapon.ammo > 0:
                self.weapon.fire(shotFx)
            elif not self.weapon.isReloading:  # if no ammo and not already reloading
                self.weapon.startReload(reloadFx)

    def respawnPlayerAtCords(self, x, y):
        """
        Description: Respawn the player at the given coordinates
        args: x - the x coordinate to respawn the player at
              y - the y coordinate to respawn the player at
        """

        self.isDead = False
        self.x = x
        self.y = y
        self.rect.left = x
        self.rect.top = y
        self.Health = self.MaxHealth
        self.weapon.ammo = self.weapon.magazineSize

        # fix transparancy on weapon
        self.weapon.image.set_alpha(255)

    def update(self):
        """
        Description: Update the player's position and state
        args: None
        """
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

        # draw and update gui to player image using function
        playerHealthBar, playerAmmoCount = self.displayGUI(self.screen)
        playerHealthBar.update()
        playerAmmoCount.update()
    
        # if player is dead, make them invisible-ish
        if self.isDead:
            self.image.set_alpha(35)
        else:
            self.image.set_alpha(255)

        # draw the player's health bar and ammo count
        self.screen.blit(playerHealthBar.image, playerHealthBar.rect)
        self.screen.blit(playerAmmoCount.image, playerAmmoCount.rect)

        # update the weapon's position and state
        self.weapon.update()
    

class ShieldBubble(Entity):
    """
        Description:
        Shield bubble class, a bubble that protects the player from damage
    """
    def __init__(self, screen, player):
        Entity.__init__(self, screen)
        self.window = screen
        # make a near transparent light blue circle
        self.image = pygame.Surface((100, 100)).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        # circle that is light blue and near transparent
        pygame.draw.ellipse(self.image, (144, 213, 255, 40), (0, 0, 100, 100))
        
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center
        self.affectedByGravity = False
        self.gravity = 0
        self.MaxHealth = 5
        self.Health = self.MaxHealth   

    def dealDamageToShield(self, damage):
        """
        Description: Deal damage to the shield bubble
        args: damage - the amount of damage to deal to the shield bubble
        """
        
        self.Health -= damage  # deal damage to the shield   
        if self.Health <= 0:
            self.kill()

