"""
    Author: Nick S
    Date: January 15th, 2025
    Description: houses the bullet entity and weapon classes
"""

# I - Import & Initialize
import pygame
import math
from . import entities
from . import utils

# Base class for all weapons
class WeaponBase(pygame.sprite.Sprite):
    """
        Description:
        Base class for all weapons
    """
    def __init__(self, screen, x, y, player):
        pygame.sprite.Sprite.__init__(self)
        self.window = screen
        self.player = player
        self.image = None
        self.rect = None
        self.damage = 0
        self.fireRate = 0

        # used to keep track of the last time the weapon was fired, then to ensure the fire rate is met
        self.lastFireTime = 0 
        self.lastReloadTime = 0
        self.affectedByGravity = False
        self.gravity = 0
        self.weaponX = x
        self.weaponY = y
        self.direction = 0
        self.bulletList = pygame.sprite.Group()
        self.ammo = 0
        self.magazineSize = 0
        self.bulletSpeed = 0
        self.isReloading = False

        # reload duration in milliseconds, doesnt really change
        self.reloadTime = 3000  
        self.controlScheme = player.controlScheme

        # offset for rotation point, 20 pixels
        self.handleOffset = 20  

        # store the last joystick angle to prevent snapback
        self.lastJoystickAngle = 0  
        self.flipped = False

    def startReload(self, reloadFx):
        """
            Description:
            Starts the reload process for the weapon

            Args:
            reloadFx: Reload sound effect

            Returns:
            None
        """

        self.lastReloadTime = pygame.time.get_ticks()

        # if it hasnt started reloading, then start
        if not self.isReloading:
            reloadFx.play()
            self.isReloading = True

    def checkReloadComplete(self):
        """
            Description:
            Checks if the reload is complete and updates the ammo count
        """
        if self.isReloading:
            elapsed_time = pygame.time.get_ticks() - self.lastReloadTime
            
            # if the elapsed time is greater than the reload time, then the reload is complete
            if elapsed_time >= self.reloadTime:
                self.ammo = self.magazineSize
                self.isReloading = False
                print("reload completed")

    def fire(self, shotFx):
        """
            Description:
            Fires a bullet from the weapon
            
            Args:
            shotFx: Sound effect for shooting
            
            Returns:
            None
        """
        # if the weapon is reloading or has no ammo, dont fire
        if self.isReloading:
            return

        if self.ammo <= 0:
            return

        # check if the fire rate has been met
        if pygame.time.get_ticks() - self.lastFireTime > self.fireRate:
            self.lastFireTime = pygame.time.get_ticks()

            # get control scheme
            if self.controlScheme == "mouse":
                mouseX, mouseY = pygame.mouse.get_pos()
                # use the arc tan function to get the angle between the player and the mouse. virtual triangle some may say 
                angle = math.degrees(math.atan2(mouseY - self.weaponY, mouseX - self.weaponX))
            elif self.controlScheme == "controller":
                joystick = self.player.joyStick
                joystick.init()

                # Rjoystick horizontal (x) and vertical (y)
                rightStickX = joystick.get_axis(2)  
                rightStickY = joystick.get_axis(3)

                # dead zone logic to prevent stick drift
                if rightStickX > 0.2 or rightStickX < -0.2 or rightStickY > 0.2 or rightStickY < -0.2:
                    angle = math.degrees(math.atan2(rightStickY, rightStickX))
                    self.player.weapon.lastJoystickAngle = angle  # Update lastJoystickAngle when firing
                else:
                    # Use lastJoystickAngle if the joystick is idle
                    angle = self.player.weapon.lastJoystickAngle

            bulletShotTime = pygame.time.get_ticks()
            # create a bullet object and add it to the bullet list
            bullet = Bullet(self.window, self.weaponX, self.weaponY, angle, self.bulletSpeed, bulletShotTime, self.damage)
            shotFx.play()
            self.bulletList.add(bullet)

            # subtract ammo
            self.ammo -= 1
            
    def update(self):
        """
            Description:
            Updates the weapon's position and rotation
        """
        self.rect.center = (self.weaponX, self.weaponY)
        self.window.blit(self.image, self.rect)

        # update the bullets
        self.bulletList.update()
        self.bulletList.draw(self.window)

    def updatePositionAndRotation(self):
        """
            Description:
            Updates the weapon's position and rotation based on the player's control scheme.
            This also flips the gun against their joycire
            
            Returns:
            None
        """
        # always follow the player's position
        self.weaponX = self.player.rect.centerx
        self.weaponY = self.player.rect.centery

        # determine the current control scheme from the player
        self.controlScheme = self.player.controlScheme

        # default to the last joystick angle if the joystick is idle
        angle = self.lastJoystickAngle  

        if self.controlScheme == "mouse":
            mouseX, mouseY = pygame.mouse.get_pos()

            # get the angle between the player and the mouse by calculating the arc tan using the x and y, virtually creating a triangle
            angle = math.degrees(math.atan2(mouseY - self.weaponY, mouseX - self.weaponX))
        elif self.controlScheme == "controller":
            joystick = self.player.joyStick
            joystick.init()

            rStickX = joystick.get_axis(2)  # Rjoy horizontal
            rStickY = joystick.get_axis(3)  # Rjoy vertical

            # subtle deadzones for joystick, prevent drift
            if rStickX > 0.2 or rStickX < -0.2 or rStickY > 0.2 or rStickY < -0.2:
                
                # get the angle between the player and the mouse by calculating the arc tan using the x and y, virtually creating a triangle
                angle = math.degrees(math.atan2(rStickY, rStickX))
                self.lastJoystickAngle = angle

        # adjust flipping based on if the cursor or joy is on the left side of the player
        if angle > 90 or angle < -90:
            self.flipped = True
        else:
            self.flipped = False

        # rotate the weapon image based on the angle
        if not self.flipped:
            rotatedImage = pygame.transform.rotate(self.baseImage, -angle)
        else:
            rotatedImage = pygame.transform.rotate(self.baseImage, angle)

        # flip the image or else it looks dumb
        if self.flipped:
            rotatedImage = pygame.transform.flip(rotatedImage, False, True)  # Flip horizontally

        # adjust the weapon's horizontal offset so its not in the player
        if self.flipped:
            self.weaponX -= self.handleOffset  # Move left for flipped
        else:
            self.weaponX += self.handleOffset  # Move right for normal

        # update the image and rectbox for positioning
        self.image = rotatedImage
        rotatedRect = self.image.get_rect()

        # if player is dead, hide the weapon
        if self.player.isDead:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)

        # update the rectbox to actively circle around the player's position
        self.rect = rotatedRect
        self.rect.center = (self.weaponX, self.weaponY)

class Bullet(entities.Entity):
    """
        Description:
        Bullet entity class. Bullets move in a straight line with a little bit of gravity and rotation
        For more info on the physics, see diagrams in src/concepts. also inherits from the entity class regardless that its in weaponmanager
    """

    def __init__(self, screen, x, y, direction, speed, bulletShotTime, damage, bulletTimeProtection=True):
        entities.Entity.__init__(self, screen)
        self.window = screen

        # Define the bullet's dimensions
        self.bulletSize = 10
        self.image = pygame.Surface((self.bulletSize, self.bulletSize))
        self.image.fill((255, 255, 255))  # bullet color

        # Initialize position and direction
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = math.radians(direction)  # convert direction to radians
        
        # horizontal velocity is calculated using the speed and the cosine of the direction using formula v = d * cos(theta)
        self.xVelocity = speed * math.cos(self.direction)  

        # vertical velocity is calculated using the speed and the sine of the direction using formula v = d * sin(theta)
        self.yVelocity = speed * math.sin(self.direction)
        
        self.drag = 0.99  # air resistance (drag force for x)
        self.gravity = 0.3  # gravity force (downward force for y)
        
        self.x = x
        self.y = y
        self.bulletTimeProtection = bulletTimeProtection

        self.bulletCastTime = bulletShotTime # used to prevent player from getting hit by their own bullets

        # count bounces if hits a bounce object
        self.bounces = 0

        self.damage = damage

    def update(self):
        """
            Description:
            Updates the bullet's position and velocity
            
            Returns:
            None
        """

        # apply gravity and drag
        self.yVelocity += self.gravity
        self.xVelocity *= self.drag

        # then update position
        self.x += self.xVelocity
        self.y += self.yVelocity
        self.rect.center = (self.x, self.y)
    
    def spawnBullet(self, i, bulletSpeed, damage):
        """
            Description:
            spawns a bullet in a specific direction. used when just creating the bullet class is not possible (see exploading bullets)
            
            Args:
            i: direction of the bullet
            bulletSpeed: speed of the bullet
            damage: damage of the bullet
            
            Returns:
            Bullet object
        """
        return Bullet(self.window, self.rect.centerx, self.rect.centery, i, bulletSpeed, pygame.time.get_ticks(), damage, False)

    def collisionDetection(self, mapSprites, players, bulletList):
        """
            Description:
            Detects collisions between the bullet and the map sprites
            
            Args:
            mapSprites: List of map sprites
            players: List of player objects
            bulletList: List of bullet sprites
            
            Returns:
            None
        """

        # Check if bullet collides with any map sprites
        for sprite in mapSprites:
            if pygame.sprite.collide_rect(self, sprite):
                # if the bullet his a decorative sprite, ignore
                if sprite.decorative:
                    continue

                if sprite.hasCollision:
                    if sprite.collisionType == "solid":
                        self.kill()
                    elif sprite.collisionType == "damage":
                        # shoot bullets in all directions
                        if sprite.blownUp:
                            return
                        else:
                            sprite.blownUp = True
                            utils.shootBulletsAllDirections(self, bulletList, 25, 60)
                            sprite.kill()
                            self.kill()
                    elif sprite.collisionType == "bounce":
                        # reverse direction on collision
                        if self.rect.bottom > sprite.rect.top and self.rect.top < sprite.rect.bottom:
                            self.yVelocity = -self.yVelocity  # Vertical bounce
                            # add to bounces
                            self.bounces += 1
                        if self.rect.right > sprite.rect.left and self.rect.left < sprite.rect.right:
                            self.xVelocity = -self.xVelocity  # Horizontal bounce
                            # add to bounces
                            self.bounces += 1
        
        # check if it hits the player and if so, deal damage
        for player in players:
            if player.exploadingBullets == True:
                if pygame.time.get_ticks() - player.exploadingBulletTime > 6000:
                    if pygame.sprite.collide_rect(self, player):
                        # set the time of
                        player.exploadingBulletTime = pygame.time.get_ticks()

                        # if its from your own bullets, ignore
                        if pygame.time.get_ticks() - self.bulletCastTime < 40:
                            return

                        # shoot bullets in all directions
                        utils.shootBulletsAllDirections(self, bulletList, 25, 4, 35)
                        self.kill()
                        return
                else:
                    print("exploading bullets on cooldown")

            # check if it his the player shield bubble
            if player.shieldBubble:
                if pygame.sprite.collide_rect(self, player.shieldBubble):
                    # if its from your own bullets, ignore
                    if pygame.time.get_ticks() - self.bulletCastTime < 40:
                        return

                    print("shield hit", player.shieldBubble.Health)
                    print("bullet damage", self.damage)
                    player.shieldBubble.dealDamageToShield(self.damage)
                    self.kill()

            if pygame.sprite.collide_rect(self, player):
                if pygame.time.get_ticks() - self.bulletCastTime > 30 or self.bulletTimeProtection == False:
                    # bullets shouldn't collide with isDead players
                    if not player.isDead:
                        player.Health -= self.damage
                        self.kill()

class BasicPistol(WeaponBase):
    """
        Description:
        Basic pistol weapon class. was used as a base for other weapons
    """
    def __init__(self, screen, player):
        # pass the player reference to the weaponbase
        WeaponBase.__init__(self, screen, player.rect.centerx, player.rect.centery, player)
        self.player = player  # store the reference to the player who wields the weapon
        self.weaponName = "Pistol"

        # load the weapon image
        self.baseImage = pygame.image.load("src/art/weapons/pistol/wo_pistol.png").convert_alpha()
        
        # scale it down
        self.baseImage = pygame.transform.scale(self.baseImage, (30, 30))
        
        # use it as base as we will rotate it and flip it
        self.image = self.baseImage

        # get the rect of the image to set x and y later
        self.rect = self.image.get_rect()
    
        # set the weapon's stats
        # higher number means slower fire rate
        self.fireRate = 500
        self.magazineSize = 12
        self.bulletSpeed = 20
        self.damage = 10
        self.ammo = self.magazineSize

    def update(self):
        """
            Description:
            Updates the weapon's position and rotation
        """
        self.updatePositionAndRotation()

class AssaultRifle(WeaponBase):
    """
        Description:
        Assault rifle weapon class. slightly faster with more shots than the basic pistol
    """
    def __init__(self, screen, player):
        # pass the player reference to the weaponbase
        WeaponBase.__init__(self, screen, player.rect.centerx, player.rect.centery, player)
        self.player = player
        self.weaponName = "Assault Rifle"

        # load the weapon image
        self.baseImage = pygame.image.load("src/art/weapons/ar/wo_ar.png").convert_alpha()
        
        # scale it down
        self.baseImage = pygame.transform.scale(self.baseImage, (60, 30))
        
        # use it as base as we will rotate it and flip it
        self.image = self.baseImage

        # get the rect of the image to set x and y later
        self.rect = self.image.get_rect()
    
        # set the weapon's stats
        self.fireRate = 220
        self.magazineSize = 25
        self.bulletSpeed = 30
        self.damage = 15
        self.ammo = self.magazineSize

    def update(self):
        """
            Description:
            Updates the weapon's position and rotation
        """
        self.updatePositionAndRotation()

class SMG(WeaponBase):
    """
        Description:
        Faster than the assault rifle but way less damage
    """
    def __init__(self, screen, player):
        # pass the player reference to the weaponbase
        WeaponBase.__init__(self, screen, player.rect.centerx, player.rect.centery, player)
        self.player = player
        self.weaponName = "Sub Machine Gun"

        # load the weapon image
        self.baseImage = pygame.image.load("src/art/weapons/smg/wo_smg.png").convert_alpha()
        
        # scale it down
        self.baseImage = pygame.transform.scale(self.baseImage, (28, 30))
        
        # use it as base as we will rotate it and flip it
        self.image = self.baseImage

        # get the rect of the image to set x and y later
        self.rect = self.image.get_rect()
    
        # set the weapon's stats
        self.fireRate = 80
        self.magazineSize = 45
        self.bulletSpeed = 20
        self.damage = 6
        self.ammo = self.magazineSize

    def update(self):
        """
            Description:
            Updates the weapon's position and rotation
        """
        self.updatePositionAndRotation()

class DesertEagle(WeaponBase):
    """
        Description:
        High damage, low ammo weapon, better be accurate
    """
    def __init__(self, screen, player):
        # pass the player reference to the weaponbase
        WeaponBase.__init__(self, screen, player.rect.centerx, player.rect.centery, player)
        self.player = player
        self.weaponName = "Desert Eagle"

        # load the weapon image
        self.baseImage = pygame.image.load("src/art/weapons/deagle/wo_deagle.png").convert_alpha()
        
        # scale it down
        self.baseImage = pygame.transform.scale(self.baseImage, (40, 36))
        
        # use it as base as we will rotate it and flip it
        self.image = self.baseImage

        # get the rect of the image to set x and y later
        self.rect = self.image.get_rect()
    
        # set the weapon's stats
        self.fireRate = 800 
        self.magazineSize = 3
        self.bulletSpeed = 46
        self.damage = 60
        self.ammo = self.magazineSize

    def update(self):
        """
            Description:
            Updates the weapon's position and rotation
        """
        self.updatePositionAndRotation()