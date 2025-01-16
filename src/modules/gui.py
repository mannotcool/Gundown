"""
    Author: Nick S
    Date: January 15th, 2025
    Description: Ammo bar and Health bar for the player, GUI house. Also stores multi-player's score
"""

# I - Import & Initialize
import pygame

# Health percentage bar above the player
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
        """
            Description:
            Updates the health bar based on the player's health
        """
        self.image.fill((0, 255, 0))  # green for full health

        # red overlay width based on lost health
        lostHealthPercentage = 1 - (self.player.Health / self.maxHealth)
        redWidth = int(self.player.rect.width * lostHealthPercentage)

        # drawing it the on the right side
        redRectBar = pygame.Rect(self.player.rect.width - redWidth, 0, redWidth, 6)

        # if is dead, make it grey
        if self.player.isDead:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)
            pygame.draw.rect(self.image, (255, 0, 0), redRectBar)

        # and updating the position to follow the player
        self.rect.center = (self.player.rect.centerx, self.player.rect.top - 10)

# Bullet bar above the player
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
        """
            Description:
            Updates the bullet bar based on the player's ammo
        """
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
            # but first check if player is dead
            if self.player.isDead:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
                if self.player.weapon.isReloading:
                    pygame.draw.rect(self.image, (100, 100, 100), (x, y, self.bulletSize, self.bulletSize))
                else:
                    pygame.draw.rect(self.image, (255, 166, 43), (x, y, self.bulletSize, self.bulletSize)) # orange-ish bullet

        # bullet bar above the health bar
        self.rect.center = (self.player.rect.centerx, self.player.rect.top - 20 - self.imageH // 2)

# Scorekeeper stores player score, and displays in the top left corner as squares
class ScoreKeeper(pygame.sprite.Sprite):
    def __init__(self, screen, player, location):
        pygame.sprite.Sprite.__init__(self)
        self.window = screen
        self.player = player
        self.numSquares = 3
        self.squareSize = 10
        self.largeSize = 30
        self.spacing = 20
        self.color = player.colorScheme
        self.imageWidth = self.numSquares * self.largeSize + (self.numSquares - 1) * self.spacing
        self.imageHeight = self.largeSize
        self.image = pygame.Surface((self.imageWidth, self.imageHeight))
        self.rect = self.image.get_rect()
        self.rect.topleft = location

    def update(self):
        """
            Description:
            Updates the scorekeeper based on the player's score
        """
        # get the player's score
        self.score = self.player.score
        self.image.fill((0, 0, 0))
        self.image.set_alpha(200)

        # draw the squares based on the score
        for i in range(self.numSquares):
            # if the index is less than the score, draw a large square
            size = self.largeSize if i < self.score else self.squareSize

            # calculate the x and y position of the square
            x = i * (self.largeSize + self.spacing)
            y = (self.imageHeight - size) // 2

            # draw the square
            pygame.draw.rect(self.image, self.color, (x, y, size, size))




