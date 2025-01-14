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

    def moveHorizontal(self, x, mapSprites, movedSprites=None):
        if x == 0:  # no movement so dont run it
            return

        if movedSprites is None:
            movedSprites = []  # initialize the list of already moved sprites

        if self in movedSprites:
            return  # Prevent infinite recursion by skipping already processed sprites

        movedSprites.append(self)  # Mark this sprite as processed
        self.rect.left += x  # Update the position

        for sprite in mapSprites:
            if sprite != self and pygame.sprite.collide_rect(self, sprite):
                if sprite.decorative:  # decorative objects shouldnt have collision
                    continue

                if x < 0:  # obj moving left
                    if sprite.affectedByGravity:
                        # allow for the sprite to move
                        sprite.moveHorizontal(x, mapSprites, movedSprites)
                    else:  # Solid object
                        self.rect.left = sprite.rect.right
                        # stop further movement
                        return  
                    
                elif x > 0:  # obj moving right
                    if sprite.affectedByGravity:
                        sprite.moveHorizontal(x, mapSprites, movedSprites)
                    else:  # solid object
                        self.rect.right = sprite.rect.left
                        return 

        # update the center position to ensure it is accurate
        self.x = self.rect.center[0]

      

    def update(self):
        MapObject.update(self)
        
