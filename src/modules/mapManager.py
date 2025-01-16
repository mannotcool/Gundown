"""
    Author: Nick S
    Date: January 15th, 2025
    Description: mapManager.py is responsible for managing the map components and their interactions
"""

# I - Import & Initialize
import pygame

class MapObject(pygame.sprite.Sprite):
    """
        Description:
        General class for Map Components.
    """

    # general class for Map Components
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
    """
        Description:
        StaticMapObject class, originally
        for static map components but also supports physics objects
    """
    
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
        """
            Description:
            Simulates gravity for the object by increasing its vertical velocity
        """
        if self.affectedByGravity:
            # simulate gravity by increasing vertical velocity
            self.verticalVelocity += self.gravity  # Gravity acceleration
            if self.verticalVelocity > 12:  # Cap the falling speed
                self.verticalVelocity = 12

            # move object vertically
            self.moveVertical(self.verticalVelocity, mapSprites)

    def moveVertical(self, y, mapSprites):
        """
            Description:
            Moves the object vertically and checks for collisions

            args:
                y: int, the amount to move vertically
                mapSprites: list, the list of sprites to check for collisions
        """

        # move vertically and check for collisions
        self.rect.top += y
        for sprite in mapSprites:
            if sprite != self and pygame.sprite.collide_rect(self, sprite):
                if y > 0:  # falling down
                    if sprite.decorative:
                        continue

                    self.rect.bottom = sprite.rect.top
                    self.verticalVelocity = 0  # Stop falling
                elif y < 0:  # moving up
                    if sprite.decorative:
                        continue

                    self.rect.top = sprite.rect.bottom
                    self.verticalVelocity = 0  # Stop upward motion

        # update the center position to ensure it is accurate
        self.y = self.rect.center[1]

    def moveHorizontal(self, x, mapSprites, movedSprites=None):
        """
            Description:
            Moves the object horizontally and checks for collisions
            
            args:
                x: int, the amount to move horizontally
                mapSprites: list, the list of sprites to check for collisions
                movedSprites: list, the list of sprites that have already been moved. this was added because physics objects can move other physics objects
            """
        if x == 0:  # no movement so dont run it
            return

        if movedSprites is None:
            movedSprites = []  # initialize the list of already moved sprites aka other physics objects

        if self in movedSprites:
            return  # prevent infinite recursion by skipping already processed sprites

        movedSprites.append(self)  # mark this sprite as moved
        self.rect.left += x  # update the position

        for sprite in mapSprites:
            # if the sprite is not itself and there is a collision
            if sprite != self and pygame.sprite.collide_rect(self, sprite):
                if sprite.decorative:  # decorative objects shouldnt have collision
                    continue

                if x < 0:  # obj moving left
                    if sprite.affectedByGravity:
                        # allow for the sprite to move
                        sprite.moveHorizontal(x, mapSprites, movedSprites)
                    else:  # solid object
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
        """
            Description:
            Updates the object against the base class
        """
        MapObject.update(self)
        
