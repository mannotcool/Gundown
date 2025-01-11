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

class Colors():
    red = (255, 179, 186)
    orange = (255, 223, 186)
    yellow = (255, 255, 186)
    green = (186, 255, 201)
    blue = (186, 225, 255)
    purple = (227, 218, 255)

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
    def __init__(self, screen, x, y, controlScheme, color=Colors.red):
        Entity.__init__(self, screen)

        # show boxie image
        self.image = pygame.image.load("src/art/character/boxie-white/default-51.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (39, 39))

        # lt the player choose their color, and use pygame's color blending to change the color of the player
        self.image.fill(color, special_flags=pygame.BLEND_RGB_MULT)

        # set the rect of the player to the image
        self.rect = self.image.get_rect()
        self.direction = 2
        self.speed = 5
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
        self.weapon = BasicPistol(screen, self)

    def displayGUI(self, screen):
        playerHealthBar = HealthBar(screen, self)
        playerAmmoCount = BulletBar(screen, self)
        return playerHealthBar, playerAmmoCount
    
    def createShieldBubble(self):
        # check if there is already a shield bubble, if so no need to create another
        print("creating")
        if self.shieldBubble:
            print("shield already exists")
            return
        
        # check if the player has created a shield bubble recently, if so, dont create another
        if pygame.time.get_ticks() - self.lastTimeShieldBubble < 8000:
            print("shield recently created")
            return
        
        # create a shield bubble
        self.shieldBubble = ShieldBubble(self.screen, self)
        self.shieldBubble.rect.center = self.rect.center

    def runTimeGravityManager(self, mapSprites):
        if self.latching:
            # greeze gravity while latched to a wall
            self.gravity = 0
        else:
            if self.gravity < 0:  # - during upward motion -
                self.moveVertical(self.gravity, mapSprites)  # move the player upward

                # If head collision, start falling
                if collisionCheck(self, mapSprites):
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
        if x < 0:
            # move the player to the left
            self.rect.left += x
            for sprite in mapSprites:
                if pygame.sprite.collide_rect(self, sprite):
                    if x < 0:
                        if sprite.latchable:
                            self.canLatch = True
                        # if the sprite is affected by physics, push the object and dont stop the collision
                        if sprite.affectedByGravity:
                            # use moveHorizontal to push the object from
                            sprite.moveHorizontal(x, mapSprites)
                        else:
                            self.rect.left = sprite.rect.right
                    elif x > 0:
                        if sprite.latchable:
                            self.canLatch = True

                        if sprite.affectedByGravity:
                            sprite.moveHorizontal(x, mapSprites)
                        else:
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
                        if sprite.affectedByGravity:
                            sprite.moveHorizontal(x, mapSprites)
                        else:
                            self.rect.right = sprite.rect.left
                    elif x < 0:
                        if sprite.latchable:
                            self.canLatch = True
                        if sprite.affectedByGravity:
                            sprite.moveHorizontal(x, mapSprites)
                        else:
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

    def runTimeJoyMovement(self, joystick, mapSprites):
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
        
        self.moveHorizontal(axis0 * 10, mapSprites)

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
                self.weapon.startReload()
        
        # shield if any trigger is pressed
        if joystick.get_button(9) or joystick.get_button(10):
            print("shield")
            self.createShieldBubble()
        
        # if the right trigger is pressed, fire the weapon
        right_trigger = joystick.get_axis(5) 
        if right_trigger > 0.5:  # Adjust threshold if needed
            if self.weapon.ammo > 0:
                self.weapon.fire()
            elif not self.weapon.isReloading:
                self.weapon.startReload()
        
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

    def runTimeMnkMovement(self, mapSprites):
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
            self.moveHorizontal(-10, mapSprites)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.moveHorizontal(10, mapSprites)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.jump(mapSprites)
        if keys[pygame.K_e]:
            self.createShieldBubble()
        if keys[pygame.K_r]:
            # reload the weapon if the magazine is not the same size as the ammo 
            if self.weapon.ammo < self.weapon.magazineSize:
                self.weapon.startReload()
            
        # add ability to shoot with spacebar or left mouse button
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            # fire using the weapon fire method using the x and y of the gun
            if self.weapon.ammo > 0:
                self.weapon.fire()
            elif not self.weapon.isReloading:  # if no ammo and not already reloading
                self.weapon.startReload()

    def respawnPlayerAtCords(self, x, y):
        self.rect.left = x
        self.rect.top = y
        self.x = x
        self.y = y
        self.Health = self.MaxHealth
        # reset ammo
        self.weapon.ammo = self.weapon.magazineSize



    def update(self):
        # update player's position
        self.rect.center = (self.x, self.y)

        # draw gui to player image using function
        player_health_bar, player_ammo_count = self.displayGUI(self.screen)
        player_health_bar.update()
        player_ammo_count.update()

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
    

        # add sideways collision detection in the future
    

class StaticMapObject(MapObject):
    def __init__(self, screen, x, y, width, height, color=(0, 0, 0), alpha=255, collisionType="solid", latchable=False, affectedByGravity=False, gravity=0):
        MapObject.__init__(self, screen)
        self.image = pygame.Surface((width, height))
        self.image = self.image.convert()
        self.image.fill(color)
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.hasCollision = True
        self.collisionRect = self.rect
        self.collisionType = collisionType  # solid, damage, bounce
        self.collisionDamage = 0
        self.canBeDestroyed = False
        self.objectHealth = 0
        self.latchable = latchable
        self.affectedByGravity = affectedByGravity
        self.gravity = gravity
        self.verticalVelocity = 0  # Add vertical velocity for smooth falling

    def runtimeGravity(self, mapSprites):
        if self.affectedByGravity:
            # Simulate gravity by increasing vertical velocity
            self.verticalVelocity += self.gravity  # Gravity acceleration
            if self.verticalVelocity > 12:  # Cap the falling speed
                self.verticalVelocity = 12

            # Move object vertically
            self.moveVertical(self.verticalVelocity, mapSprites)

    def moveVertical(self, y, mapSprites):
        # Move vertically and check for collisions
        self.rect.top += y
        for sprite in mapSprites:
            if sprite != self and pygame.sprite.collide_rect(self, sprite):
                if y > 0:  # Falling down
                    self.rect.bottom = sprite.rect.top
                    self.verticalVelocity = 0  # Stop falling
                elif y < 0:  # Moving up
                    self.rect.top = sprite.rect.bottom
                    self.verticalVelocity = 0  # Stop upward motion
        self.y = self.rect.center[1]

    def moveHorizontal(self, x, mapSprites):
        # use same logic as player to move horizontally, but ignore the player and latchable objects because the player can move map objects
        self.rect.left += x
        for sprite in mapSprites:
            if sprite != self and pygame.sprite.collide_rect(self, sprite):
                if x < 0:
                    if sprite.affectedByGravity:
                        sprite.moveHorizontal(x, mapSprites)
                    else:
                        self.rect.left = sprite.rect.right
                elif x > 0:
                    if sprite.affectedByGravity:
                        sprite.moveHorizontal(x, mapSprites)
                    else:
                        self.rect.right = sprite.rect.left
        self.x = self.rect.center[0]


    def update(self):
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
            bullet = Bullet(self.window, self.weaponX, self.weaponY, angle, self.bulletSpeed, bulletShotTime, self.damage)
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
    def __init__(self, screen, x, y, direction, speed, bulletShotTime, damage):
        Entity.__init__(self, screen)
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

        self.bulletCastTime = bulletShotTime # used to prevent player from getting hit by their own bullets

        # count bounces if hits a bounce object
        self.bounces = 0

        self.damage = damage


    def update(self):
        # apply gravity and drag
        self.yVelocity += self.gravity
        self.xVelocity *= self.drag

        # then update position
        self.x += self.xVelocity
        self.y += self.yVelocity
        self.rect.center = (self.x, self.y)

    def collisionDetection(self, mapSprites, players):
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
        for player in players:
            # check if it his the player shield bubble
            if player.shieldBubble:
                if pygame.sprite.collide_rect(self, player.shieldBubble):
                    # if its from your own bullets, ignore
                    if pygame.time.get_ticks() - self.bulletCastTime < 100:
                        return

                    print("shield hit", player.shieldBubble.Health)
                    print("bullet damage", self.damage)
                    player.shieldBubble.dealDamageToShield(self.damage)
                    self.kill()

            if pygame.sprite.collide_rect(self, player):
                if pygame.time.get_ticks() - self.bulletCastTime > 100:
                    print("player hit")
                    player.Health -= self.damage
                    self.kill()

            


        
                    


# Weapons

class BasicPistol(WeaponBase):
    def __init__(self, screen, player):
        # pass the player reference to the weaponbase
        WeaponBase.__init__(self, screen, player.rect.centerx, player.rect.centery)
        self.player = player  # store the reference to the player who wields the weapon
        self.weaponName = "Pistol"

        # load the weapon image
        self.baseImage = pygame.image.load("src/art/weapons/pistol/wo_pistol.png").convert_alpha()
        
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

class AssaultRifle(WeaponBase):
    def __init__(self, screen, player):
        # pass the player reference to the weaponbase
        WeaponBase.__init__(self, screen, player.rect.centerx, player.rect.centery)
        self.player = player  # store the reference to the player who wields the weapon
        self.weaponName = "Assault Rifle"

        # load the weapon image
        self.baseImage = pygame.image.load("src/art/weapons/ar/ar-no-outline.png").convert_alpha()
        
        # scale it down
        self.baseImage = pygame.transform.scale(self.baseImage, (60, 30))
        
        # use it as base as we will rotate it and flip it
        self.image = self.baseImage
        self.flipped = False

        # get the rect of the image to set x and y later
        self.rect = self.image.get_rect()
    
        # set the weapon's stats
        self.fireRate = 100 # higher number means slower fire rate
        self.magazineSize = 30
        self.bulletSpeed = 30
        self.damage = 15
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

            # if the player is reloading, draw the bullets in grey
            if self.player.weapon.isReloading:
                pygame.draw.rect(self.image, (100, 100, 100), (x, y, self.bulletSize, self.bulletSize))
            else:
                pygame.draw.rect(self.image, (255, 166, 43), (x, y, self.bulletSize, self.bulletSize)) # orange-ish bullet

        # bullet bar above the health bar
        self.rect.center = (self.player.rect.centerx, self.player.rect.top - 20 - self.imageH // 2)