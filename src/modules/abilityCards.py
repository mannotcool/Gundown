"""
    Author: Nick S
    Date: January 15th, 2025
    Description: Houses all the ability cards for the player to select, and their modifiers
"""

import pygame
from . import weaponManager

class AbilityCardBase(pygame.sprite.Sprite):
    """
        Description:
        Base class for all ability cards, basically a list of modifiers

        Attributes:
        cardType: Type of card, either "attribute" or "weapon"
        cardName: Name of the card
        cardDescription: Description of the card
        modifierList: List of Modifier objects
    """
    def __init__(self, cardType, cardName, cardDescription, modifierList):
        pygame.sprite.Sprite.__init__(self)
        # cardType is either "attribute" or "weapon"
        self.cardType = cardType
        self.cardName = cardName
        self.cardDescription = cardDescription
        self.modifiers = modifierList
    
class Modifier(pygame.sprite.Sprite):
    """
        Description:
        Applies the modifier (more damage, health, etc) to a player

        Attributes:
        modifierType: Type of modifier
        modifierValue: Value of the modifier
    """
    def __init__(self, modifierType, modifierValue):
        pygame.sprite.Sprite.__init__(self)
        self.modifierType = modifierType
        self.modifierValue = modifierValue
    
    def setModifier(self, player):
        """
            Description:
            Applies the modifier to the player

            Args:
            player: Player object
        """
        if self.modifierType == "speed":
            # ensure to do a check to make sure current speed is not negative, 
            player.walkSpeed = int(player.walkSpeed * self.modifierValue)
        elif self.modifierType == "health":
            player.MaxHealth = int(player.MaxHealth * self.modifierValue)
        elif self.modifierType == "damage":
            player.weapon.damage = int(player.weapon.damage * self.modifierValue)
        elif self.modifierType == "ammo":
            # make sure ammo is never more than 500
            if player.weapon.magazineSize * self.modifierValue > 500:
                player.weapon.magazineSize = 500
            # make sure ammo is never 0
            elif player.weapon.magazineSize * self.modifierValue < 0:
                player.weapon.magazineSize = 1
            else:
                player.weapon.magazineSize = int(player.weapon.magazineSize * self.modifierValue)
        elif self.modifierType == "fireRate":
            # make sure weapon fire rate is at least 2
            if player.weapon.fireRate * self.modifierValue < 2:
                player.weapon.fireRate = 2
            # make sure fire rate is never more than 2000
            elif player.weapon.fireRate * self.modifierValue > 2000:
                player.weapon.fireRate = 2000
            else:
                player.weapon.fireRate = int(player.weapon.fireRate * self.modifierValue)
        elif self.modifierType == "fireRange":
            # make sure weapon fire range is at least 8
            if player.weapon.bulletSpeed * self.modifierValue < 8:
                player.weapon.bulletSpeed = 8
            # make sure fire range is never more than 120
            elif player.weapon.bulletSpeed * self.modifierValue > 120:
                player.weapon.bulletSpeed = 120
            else:
                player.weapon.bulletSpeed = int(player.weapon.bulletSpeed * self.modifierValue)
        elif self.modifierType == "assaultRifle":
            # kill player weapon current weapon and give them an assault rifle
            player.weapon.kill()
            player.weapon = weaponManager.AssaultRifle(player.screen, player)
            player.weapon.update()  # ensure the new weapon's image shows up
        elif self.modifierType == "deagle":
            player.weapon.kill()
            player.weapon = weaponManager.DesertEagle(player.screen, player)
            player.weapon.update()  # ensure the new weapon's image shows up
        elif self.modifierType == "SMG":
            player.weapon.kill()
            player.weapon = weaponManager.SMG(player.screen, player)
            player.weapon.update()  # ensure the new weapon's image shows up
        elif self.modifierType == "explosive":
            player.exploadingBullets = True

AVAILABLECARDS = [
    # Base cards
    AbilityCardBase("attribute", "Speed Boost", "Increases player speed by 50%", [Modifier("speed", 1.5)]),
    AbilityCardBase("attribute", "Health Boost", "Increases player health by 2x", [Modifier("health", 2)]),
    AbilityCardBase("attribute", "Damage Boost", "Increases player damage by 1.5x", [Modifier("damage", 1.5)]),
    AbilityCardBase("attribute", "Ammo Boost", "Increases player ammo by 2x", [Modifier("ammo", 2)]),
    AbilityCardBase("attribute", "Fire Range Boost", "Increases player fire range by 1.5x", [Modifier("fireRange", 1.5)]),
    
    # Other Weapons
    AbilityCardBase("weapon", "Assault Rifle", "Gives player an Assault Rifle", [Modifier("assaultRifle", 0)]),
    AbilityCardBase("weapon", "Desert Eagle", "Gives player a Desert Eagle", [Modifier("deagle", 0)]),
    AbilityCardBase("weapon", "SMG", "Gives player an SMG", [Modifier("SMG", 0)]),
    
    # Medium Strength Cards
    AbilityCardBase("attribute", "Speed Demon", "Increases player speed by 2x", [Modifier("speed", 2)]),
    AbilityCardBase("attribute", "Healthier Boost", "Increases player health by 3x", [Modifier("health", 3)]),
    AbilityCardBase("attribute", "Triple Damage", "Increases player damage by 3x", [Modifier("damage", 3)]),
    AbilityCardBase("attribute", "Fire Rate Boost", "Increases player fire rate by 2x", [Modifier("fireRate", 0.5)]),
    AbilityCardBase("attribute", "Gimmie an SMG", "Increases player fire rate by 3x", [Modifier("fireRate", 0.33)]),
   
    # High Strength Cards, Mixed and Matched
    AbilityCardBase("attribute", "Speedy Gonzales", "4x player speed but horrible Health", [Modifier("speed", 4), Modifier("health", 0.33)]),
    AbilityCardBase("attribute", "Basically a Sniper", "5x damage but horrible Fire rate", [Modifier("damage", 5), Modifier("fireRate", 10)]),
    AbilityCardBase("attribute", "Tank", "5x health but 1/5th speed", [Modifier("health", 5), Modifier("speed", 0.20)]),
    AbilityCardBase("attribute", "Bullet Hell", "5x ammo but 1/5th damage", [Modifier("ammo", 5), Modifier("damage", 0.20)]),

    # exploading bullets
    AbilityCardBase("attribute", "Bullet Shield", "Make a wild guess.", [Modifier("explosive", 0)]),
]