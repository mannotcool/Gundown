import pygame

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