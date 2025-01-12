import pygame

from .weaponManager import Bullet

        
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
       
class StaticMapObject(MapObject):
    def __init__(self, screen, x, y, width, height, color=(0, 0, 0), alpha=255, collisionType="solid", latchable=False, affectedByGravity=False, gravity=0, decorative=False):
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
        self.decorative = decorative
        self.blownUp = False

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
                    if sprite.decorative:
                        continue

                    self.rect.bottom = sprite.rect.top
                    self.verticalVelocity = 0  # Stop falling
                elif y < 0:  # Moving up
                    if sprite.decorative:
                        continue

                    self.rect.top = sprite.rect.bottom
                    self.verticalVelocity = 0  # Stop upward motion
        self.y = self.rect.center[1]

    def moveHorizontal(self, x, mapSprites):
        # use same logic as player to move horizontally, but ignore the player and latchable objects because the player can move map objects
        self.rect.left += x
        for sprite in mapSprites:
            if sprite != self and pygame.sprite.collide_rect(self, sprite):
                if x < 0:
                    # if it interacts with a map object thats decorative, ignore
                    if sprite.decorative:
                        continue

                    if sprite.affectedByGravity:
                        sprite.moveHorizontal(x, mapSprites)
                    else:
                        self.rect.left = sprite.rect.right
                elif x > 0:
                    if sprite.decorative:
                        continue

                    if sprite.affectedByGravity:
                        sprite.moveHorizontal(x, mapSprites)
                    else:
                        self.rect.right = sprite.rect.left
        self.x = self.rect.center[0]

    def shootBulletsAllDirections(self, bulletList, bulletSpeed, damage):
        if self.blownUp:
            return
        else:
            self.blownUp = True

            for i in range(0, 360, 10):
                bullet = Bullet(self.window, self.rect.centerx, self.rect.centery, i, bulletSpeed, pygame.time.get_ticks(), damage, False)
                bulletList.add(bullet)
            
            self.kill()
            
        

    def update(self):
        MapObject.update(self)
        
