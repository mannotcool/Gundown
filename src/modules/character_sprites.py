import pygame
import math

def collisionCheck(player, mapSprites):
    # check for head collision
    player.rect.top -= 1  # temporarily move up to check collision
    headCollision = False
    for sprite in mapSprites:
        if pygame.sprite.collide_rect(player, sprite):
            headCollision = True
            break
    player.rect.top += 1  # reset position after checking

    # if there is a head collision, return True
    return headCollision

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
        
# Player class that inherits from Entity
class Player(Entity):
    def __init__(self, screen, x, y, controlScheme):
        Entity.__init__(self, screen)
        self.image = pygame.Surface((30, 30))
        self.image = self.image.convert()
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.direction = 2
        self.speed = 5

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

        # define variable where the type is the pistol class
        self.weapon = BasicPistol(screen, self)
    
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
        if x < 0:
            # move the player to the left
            self.rect.left += x
            for sprite in mapSprites:
                if pygame.sprite.collide_rect(self, sprite):
                    if x < 0:
                        if sprite.latchable:
                            self.canLatch = True
                        self.rect.left = sprite.rect.right
                    elif x > 0:
                        if sprite.latchable:
                            self.canLatch = True
                        self.rect.right = sprite.rect.left
                else:
                    self.canLatch = False
        elif x > 0:
            # move the player to the right
            self.rect.left += x
            for sprite in mapSprites:
                if pygame.sprite.collide_rect(self, sprite):
                    if x > 0:
                        if sprite.latchable:
                            self.canLatch = True
                        self.rect.right = sprite.rect.left
                    elif x < 0:
                        if sprite.latchable:
                            self.canLatch = True
                        self.rect.left = sprite.rect.right
                    else:
                        self.canLatch = False
        # center the player's x to the rect
        self.x = self.rect.center[0]

    def moveVertical(self, y, mapSprites):
        if not self.latching:
            self.rect.top += y
            for sprite in mapSprites:
                if pygame.sprite.collide_rect(self, sprite):
                    if y < 0:
                        self.rect.top = sprite.rect.bottom
                    elif y > 0:
                        self.rect.bottom = sprite.rect.top
            # center the player's y to the rect
            self.y = self.rect.center[1]

    def jump(self, mapSprites):
        self.rect.top += 1
        on_ground = False
        for sprite in mapSprites:
            if pygame.sprite.collide_rect(self, sprite):
                on_ground = True
                break
        self.rect.top -= 1

        # only allow jumping when on the ground and not latched
        if on_ground and not self.latching:
            self.gravity = -16  # negative gravity for upward motion, see main.py

    def weaponFire(self):
        self.weapon.fire()

    def update(self):
        # update player's position
        self.rect.center = (self.x, self.y)

        # update the weapon's position and state
        self.weapon.update()
        
class MapObject(pygame.sprite.Sprite):
    # General class for Map Components
    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        self.window = screen
        self.image = None
        self.rect = None
        self.affectedByGravity = False
        self.gravity = 0
        self.hasCollision = False
        self.collisionRect = None
        self.collisionType = "solid"
        self.collisionDamage = 0
        self.canBeDestroyed = False
        self.objectHealth = 0
        self.latchable = False
    
    def update(self):
        if self.affectedByGravity:
            self.rect.top += self.gravity
            if self.rect.bottom > self.window.get_height():
                self.rect.bottom = self.window.get_height()
                self.gravity = 0
            else:
                self.gravity += 1

        # add sideways collision detection in the future
    

class StaticMapObject(MapObject):
    def __init__(self, screen, x, y, width, height, color=(0, 0, 0), collisionType="solid", latchable=False):
        MapObject.__init__(self, screen)
        self.image = pygame.Surface((width, height))
        self.image = self.image.convert()
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.hasCollision = True
        self.collisionRect = self.rect
        self.collisionType = collisionType # solid, damage, bounce
        self.collisionDamage = 0
        self.canBeDestroyed = False
        self.objectHealth = 0
        self.latchable = latchable
        self.affectedByGravity = False
    
    def update(self):
        # call parent update
        MapObject.update(self)

        
class WeaponBase(pygame.sprite.Sprite):
    def __init__(self, screen, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.window = screen
        self.image = None
        self.rect = None
        self.damage = 0
        self.fireRate = 0
        self.lastFireTime = 0 # used to keep track of the last time the weapon was fired, then to ensure the fire rate is met
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
        self.reloadTime = 3000  # reload duration in milliseconds

    def startReload(self):
        self.lastReloadTime = pygame.time.get_ticks()
        self.isReloading = True
        print("reloading started")

    def checkReloadComplete(self):
        if self.isReloading:
            elapsed_time = pygame.time.get_ticks() - self.lastReloadTime
            if elapsed_time >= self.reloadTime:
                self.ammo = self.magazineSize
                self.isReloading = False
                print("reload completed")

    def fire(self):
        if self.isReloading:
            print("cannot fire while reloading")
            return

        if self.ammo <= 0:
            print("no ammo")
            return

        # check if the fire rate has been met
        if pygame.time.get_ticks() - self.lastFireTime > self.fireRate:
            self.lastFireTime = pygame.time.get_ticks()

            # get control scheme
            if self.controlScheme == "mouse":
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # use the arc tan function to get the angle between the player and the mouse
                angle = math.degrees(math.atan2(mouse_y - self.weaponY, mouse_x - self.weaponX))
            elif self.controlScheme == "controller":
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
                rightStickX = joystick.get_axis(2)  # Rjoystick horizontal
                rightStickY = joystick.get_axis(3)  # Rjoystick vertical

                # dead zone logic to prevent stick drift
                if rightStickX > 0.2 or rightStickX < -0.2 or rightStickY > 0.2 or rightStickY < -0.2:
                    angle = math.degrees(math.atan2(rightStickY, rightStickX))
                    self.player.weapon.lastJoystickAngle = angle  # Update lastJoystickAngle when firing
                else:
                    # Use lastJoystickAngle if the joystick is idle
                    angle = self.player.weapon.lastJoystickAngle

            bulletShotTime = pygame.time.get_ticks()
            # create a bullet object and add it to the bullet list
            bullet = Bullet(self.window, self.weaponX, self.weaponY, angle, self.bulletSpeed, bulletShotTime)
            self.bulletList.add(bullet)

            # subtract ammo
            self.ammo -= 1
            
    def update(self):
        self.rect.center = (self.weaponX, self.weaponY)
        self.window.blit(self.image, self.rect)
        self.bulletList.update()
        self.bulletList.draw(self.window)


# bullets are entities that move in a straight line with a little bit of gravity and rotation
class Bullet(Entity):
    def __init__(self, screen, x, y, direction, speed, bulletShotTime):
        Entity.__init__(self, screen)
        self.window = screen

        # Define the bullet's dimensions
        self.bulletSize = 10
        self.image = pygame.Surface((self.bulletSize, self.bulletSize))
        self.image.fill((0, 0, 0))  # bullet color

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

        self.bulletCastTime = bulletShotTime # used to prevent player from getting hit by their own bullets

        # count bounces if hits a bounce object
        self.bounces = 0

    def update(self):
        # apply gravity and drag
        self.yVelocity += self.gravity
        self.xVelocity *= self.drag

        # then update position
        self.x += self.xVelocity
        self.y += self.yVelocity
        self.rect.center = (self.x, self.y)

    def collisionDetection(self, mapSprites, player):
        # Check if bullet collides with any map sprites
        for sprite in mapSprites:
            if pygame.sprite.collide_rect(self, sprite):
                if sprite.hasCollision:
                    if sprite.collisionType == "solid":
                        self.kill()
                    elif sprite.collisionType == "damage":
                        self.kill()
                    elif sprite.collisionType == "bounce":
                        # Reverse direction on collision
                        if self.rect.bottom > sprite.rect.top and self.rect.top < sprite.rect.bottom:
                            self.yVelocity = -self.yVelocity  # Vertical bounce
                            # add to bounces
                            self.bounces += 1
                        if self.rect.right > sprite.rect.left and self.rect.left < sprite.rect.right:
                            self.xVelocity = -self.xVelocity  # Horizontal bounce
                            # add to bounces
                            self.bounces += 1
        
        # check if it hits the player and if so, deal damage
        if pygame.sprite.collide_rect(self, player):
            # check if the player got hit within the last 100ms to prevent player from getting hit multiple times and shooting themselves
            if pygame.time.get_ticks() - self.bulletCastTime > 100:
                print("player hit")
                player.Health -= player.weapon.damage
                self.kill()

class BasicPistol(WeaponBase):
    def __init__(self, screen, player):
        # pass the player reference to the weaponbase
        WeaponBase.__init__(self, screen, player.rect.centerx, player.rect.centery)
        self.player = player  # store the reference to the player who wields the weapon
        self.weaponName = "Pistol"

        # load the weapon image
        self.baseImage = pygame.image.load("src/art/weapons/pistol/b_pistol.png").convert_alpha()
        
        # scale it down
        self.baseImage = pygame.transform.scale(self.baseImage, (30, 30))
        
        # use it as base as we will rotate it and flip it
        self.image = self.baseImage
        self.flipped = False

        # get the rect of the image to set x and y later
        self.rect = self.image.get_rect()
    
        # set the weapon's stats
        self.fireRate = 500 # higher number means slower fire rate
        self.magazineSize = 12
        self.bulletSpeed = 20
        self.damage = 10
        self.ammo = self.magazineSize
        
        self.controlScheme = player.controlScheme

        # gun positioning data
        self.handleOffset = 20  # Offset for rotation point
        self.lastJoystickAngle = 0  # Store the last joystick angle

    def update(self):
        # always follow the player's position
        self.weaponX = self.player.rect.centerx
        self.weaponY = self.player.rect.centery

        # determine the current control scheme from the player
        self.controlScheme = self.player.controlScheme

        # default to the last joystick angle if the joystick is idle
        angle = self.lastJoystickAngle  

        if self.controlScheme == "mouse":
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # get the angle between the player and the mouse by calculating the arc tan using the x and y, virtually creating a triangle
            angle = math.degrees(math.atan2(mouse_y - self.weaponY, mouse_x - self.weaponX))
        elif self.controlScheme == "controller":
            joystick = pygame.joystick.Joystick(0)
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

        # update the rectbox to actively circle around the player's position
        self.rect = rotatedRect
        self.rect.center = (self.weaponX, self.weaponY)

# Gui Elements
class HealthBar(pygame.sprite.Sprite):
    def __init__(self, screen, player):
        pygame.sprite.Sprite.__init__(self)
        self.window = screen
        self.player = player
        self.image = pygame.Surface((self.player.rect.width, 6))
        self.rect = self.image.get_rect()
        self.rect.center = (self.player.rect.centerx, self.player.rect.top - 10) # put it above the player
        self.maxHealth = self.player.MaxHealth

    def update(self):
        self.image.fill((0, 255, 0))  # green for full health

        # red overlay width based on lost health
        lostHealthPercentage = 1 - (self.player.Health / self.maxHealth)
        redWidth = int(self.player.rect.width * lostHealthPercentage)

        # drawing it the on the right side
        redRectBar = pygame.Rect(self.player.rect.width - redWidth, 0, redWidth, 6)
        pygame.draw.rect(self.image, (255, 0, 0), redRectBar)

        # and updating the position to follow the player
        self.rect.center = (self.player.rect.centerx, self.player.rect.top - 10)

class BulletBar(pygame.sprite.Sprite):
    def __init__(self, screen, player):
        pygame.sprite.Sprite.__init__(self)
        self.window = screen
        self.player = player
        self.bulletSize = 5  # size of bullet squares
        self.bulletsPerRow = 5  # fixed number of bullets per row
        self.spacing = 2  # and spacing between bullets

        # calc dimensions of the bullet bar. no remainders allowed because you cant have half a bullet
        self.maxRows = (player.weapon.magazineSize + self.bulletsPerRow - 1) // self.bulletsPerRow

        # based on the dimensions, calculate the width and height of the bullet bar
        self.imageW = self.bulletsPerRow * (self.bulletSize + self.spacing) - self.spacing
        self.imageH = self.maxRows * (self.bulletSize + self.spacing) - self.spacing

        # use the dimensions to create the surface
        self.image = pygame.Surface((self.imageW, self.imageH))
        self.image.set_colorkey((0, 0, 0))  # make black transparent

        # put the rect of the image as the rect of the sprite
        self.rect = self.image.get_rect()

    def update(self):
        # clear the image, fill it with black which is transparent due to colorkey
        self.image.fill((0, 0, 0))  

        # add bullets to a grid
        remainingAmmo = self.player.weapon.ammo

        # draw bullets based on the remaining ammo
        for i in range(remainingAmmo):
            # calculate the row and column of the bullet
            row = i // self.bulletsPerRow
            col = i % self.bulletsPerRow

            # calculate the x and y position of the bullet
            x = col * (self.bulletSize + self.spacing)
            y = row * (self.bulletSize + self.spacing)
            pygame.draw.rect(self.image, (255, 166, 43), (x, y, self.bulletSize, self.bulletSize)) # orange-ish bullet

        # bullet bar above the health bar
        self.rect.center = (self.player.rect.centerx, self.player.rect.top - 20 - self.imageH // 2)