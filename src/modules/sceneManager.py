import pygame
import random
from . import utils
pygame.font.init()
pygame.mixer.init()


def showStartScreen(screen):
    # load ThaleahFat.ttf for the title text
    font = pygame.font.Font("src/fonts/ThaleahFat.ttf", 96)
    smallFont = pygame.font.SysFont("Arial", 24)
    
    titleText = font.render("Welcome to Gundown!", True, (255, 255, 255))
    subtitleText = smallFont.render("Press SPACE to start", True, (255, 255, 255))
    errorText = smallFont.render("At least two players must select colors!", True, (255, 100, 100))
    footerText = smallFont.render("Change colors by clicking (A), or using Mouse Left Click.", True, (255, 255, 255))
    
    screenWidth, screenHeight = screen.get_size()
    bg = pygame.image.load("src/art/backgrounds/dark_abs_bg.gif")
    bg = pygame.transform.scale(bg, (screenWidth, screenHeight))

    colors = [utils.Colors.red, utils.Colors.blue, utils.Colors.orange, utils.Colors.purple, utils.Colors.green]

    # box used to draw the players preview
    boxWidth = 150
    boxHeight = 150
    boxSpacing = 50
    boxes = [
        pygame.Rect((screenWidth - (3 * boxWidth + 2 * boxSpacing)) // 2, screenHeight // 3, boxWidth, boxHeight),
        pygame.Rect((screenWidth - (3 * boxWidth + 2 * boxSpacing)) // 2 + (boxWidth + boxSpacing), screenHeight // 3, boxWidth, boxHeight),
        pygame.Rect((screenWidth - (3 * boxWidth + 2 * boxSpacing)) // 2 + 2 * (boxWidth + boxSpacing), screenHeight // 3, boxWidth, boxHeight),
    ]

    # the selected player colors. 
    playerColorSelected = [0, 0, 0]

    # General Note:
    # All boxie images are colorized, and when the player sees them they scroll through the index of these boxies images
    # The playerColorSelected index is the index of the colors array, and the boxieImages index is the index of the boxie images

    # are ticked whenever a player connects or disconnects
    playerActive = [True, False, False]

    # to colorize the boxie character, that we will put in the boxes after
    boxieImages = []
    for color in colors:
        image = pygame.image.load("src/art/character/boxie-white/default-340.png").convert_alpha()
        image = pygame.transform.scale(image, (boxWidth, boxHeight))
        image.fill(color, special_flags=pygame.BLEND_RGB_MULT)
        boxieImages.append(image)

    # gui icons
    mouseIcon = pygame.image.load("src/art/icons/mouse.gif")
    mouseIcon = pygame.transform.scale(mouseIcon, (64, 64))  # Larger mouse GIF for visibility
    
    controllerIcon = pygame.image.load("src/art/icons/controller.gif").convert_alpha()
    controllerIcon = pygame.transform.scale(controllerIcon, (32, 32))

    # initialize joysticks currently active, they may change
    joysticks = []

    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
        if i + 1 < len(playerActive):
            playerActive[i + 1] = True

    # A - Action (broken into ALTER steps)
 
    # A - Assign values to key variables
    clock = pygame.time.Clock()
    keepGoing = True
    showError = False

    # L - Loop
    while keepGoing:
        # T - Timer to set frame rate
        clock.tick(60) 

        # E - Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False

            # game start event
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # check if at least 2 players are in the game
                    activePlayers = sum(playerActive)
                    if activePlayers > 1:
                        # will start the game
                        keepGoing = False
                    else:
                        # display a text error telling you to find friends
                        showError = True

            # change the color of  player 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if playerActive[0]:  # mouse always controls Player 1
                    playerColorSelected[0] = (playerColorSelected[0] + 1) % len(colors)

        currentJoystickCount = pygame.joystick.get_count()

        if currentJoystickCount != len(joysticks):  # if joystick count changed from the og one
            joysticks = []
            playerActive = [True, False, False]  # Reset playerActive (Mouse remains active)

            # reinitialize joysticks
            for i in range(currentJoystickCount):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                joysticks.append(joystick)
                if i + 1 < len(playerActive):
                    playerActive[i + 1] = True

        # color changing script
        for i in range(len(joysticks)):
            if playerActive[i + 1]:  # ensure the player is active
                # pull the specific joystick to not change other user colors
                joystick = joysticks[i]
                
                # if they click the A button, change the color
                if joystick.get_button(0):
                    # change the color index that is selected
                    playerColorSelected[i + 1] = (playerColorSelected[i + 1] + 1) % len(colors)
                    # pause for a bit to prevent rapid color changes
                    pygame.time.wait(200)

        screen.blit(bg, (0, 0))
        screen.blit(titleText, (screenWidth // 2 - titleText.get_width() // 2, screenHeight // 8))

        # add up the number of active players
        activePlayers = sum(playerActive)

        # either show the "start game with enter text" or if there is the error show that one
        if activePlayers > 1:
            screen.blit(subtitleText, (screenWidth // 2 - subtitleText.get_width() // 2, screenHeight // 2 + 100))
        elif showError:
            screen.blit(errorText, (screenWidth // 2 - errorText.get_width() // 2, screenHeight // 2 + 140))
        
        # blit the footer text
        screen.blit(footerText, (screenWidth // 2 - footerText.get_width() // 2, screenHeight - 50))
        screen.blit(mouseIcon, (boxes[0].centerx - mouseIcon.get_width() // 2 - 15, boxes[0].bottom + 5))
        
        # draw the boxies
        for i in range(len(boxes)):
            # grey out the boxes space for non connected players
            if playerActive[i]:
                # using the index of the color, draw the boxie image from the top left of the image/rect
                screen.blit(boxieImages[playerColorSelected[i]], boxes[i].topleft)
                controllerIcon.set_alpha(255)
            else:
                greyImage = pygame.Surface((boxWidth, boxHeight))
                greyImage.fill((100, 100, 100, 200))
                greyImage.set_alpha(80)
                controllerIcon.set_alpha(40)
                screen.blit(greyImage, boxes[i].topleft)

            # mnk get lost lmao
            if i == 0:
                continue

            # place controller icons below the boxies
            iconX = boxes[i].centerx - controllerIcon.get_width() // 2
            iconY = boxes[i].bottom + 20  # adjusted position for better visibility
            screen.blit(controllerIcon, (iconX, iconY))

        pygame.display.flip()
        clock.tick(60)

    # outside of the loop
    resultColors = []

    # for each player that is active, append the color to the resultColors list
    for i in range(len(playerActive)):
        if playerActive[i]:
            # remeber that the playerColorSelected index is the index of the colors array too :D
            resultColors.append(colors[playerColorSelected[i]])

    return resultColors

def showAbilityCardScreen(screen, players, availableCards, selectFx):
    font = pygame.font.Font("src/fonts/ThaleahFat.ttf", 48)
    smallFont = pygame.font.SysFont("Arial", 24)

    titleText = font.render("New Ability Cards!", True, (255, 255, 255))
    instructionText = smallFont.render("Click on an ability card, or select using (A) or (B)", True, (255, 255, 255))

    screenWidth, screenHeight = screen.get_size()

    # same bg as the start screen
    bg = pygame.image.load("src/art/backgrounds/dark_abs_bg.gif")
    bg = pygame.transform.scale(bg, (screenWidth, screenHeight))

    selectFx.play()

    cardWidth, cardHeight = 400, 150
    cardSpacing = 50
    playerCards = []

    # player selections will be filled with the selected cards, playerSelectionsConfirmed ticks off keepGoing when players have all selected their cards
    playerSelections = [None] * len(players)
    playerSelectionsConfirmed = 0

    # Assign random cards to each player and initialize their selections
    for _ in players:
        playerCards.append([
            availableCards[random.randint(0, len(availableCards) - 1)],
            availableCards[random.randint(0, len(availableCards) - 1)],
        ])

    # A - Action (broken into ALTER steps)
 
    # A - Assign values to key variables
    clock = pygame.time.Clock()
    keepGoing = True
    
    # L - Loop
    while keepGoing:

        # T - Timer to set frame rate
        clock.tick(60)
    
        # E - Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False

            # if the player is mouse, they can select the card by clicking on it
            if event.type == pygame.MOUSEBUTTONDOWN:
                # pull as tuple
                cursorX, cursorY = pygame.mouse.get_pos()
                
                # check if the cursor is in the card
                if len(playerCards[0]) > 1:
                    for j in range(2):
                        # calc the X position for the cards based on the number of cards
                        cardX = screenWidth // 2 - (2 * cardWidth + cardSpacing) // 2 + j * (cardWidth + cardSpacing)
                        
                        # see if the cursor is in X of the card
                        if cardX <= cursorX <= cardX + cardWidth:
                            playerY = 200  # fixed Y position for Player 1
                            
                            # check if the cursor is within the Y bounds of the card
                            if playerY <= cursorY <= playerY + cardHeight:
                                # add the selected card to Player 1 and remove it from the list
                                playerSelections[0] = playerCards[0][j]
                                # play the select sound
                                # remove the card from the list
                                playerCards[0].pop(1 - j)
                                playerSelectionsConfirmed += 1
                                selectFx.play()

            # if the player is controller, they can select a card by pressing the A or B button
            for i in range(len(players)):
                if len(playerCards[i]) > 1 and playerSelections[i] is None:
                    if players.sprites()[i].controlScheme == "controller":
                        joystick = players.sprites()[i].joyStick
                        
                        # check for A or B button press
                        if joystick.get_button(0):
                            selectFx.play()
                            playerSelections[i] = playerCards[i][0]

                            # same logic as mnk but i know which card to remove
                            playerCards[i].pop(1)
                            playerSelectionsConfirmed += 1

                            # play the select sound
                            

                        elif joystick.get_button(1):
                            selectFx.play()
                            playerSelections[i] = playerCards[i][1]
                            playerCards[i].pop(0)
                            playerSelectionsConfirmed += 1

                            # play the select sound
                            

        if playerSelectionsConfirmed == len(players):
            # kill the loop if all cards that need to be selected are selected
            keepGoing = False

        screen.blit(bg, (0, 0))
        screen.blit(titleText, (screenWidth // 2 - titleText.get_width() // 2, 50))
        screen.blit(instructionText, (screenWidth // 2 - instructionText.get_width() // 2, 120))

        # draw the cards on the screen!
        for playerIndex in range(len(players)):
            # calculate the Y position for each player's card row
            playerY = 160 + playerIndex * (cardHeight + cardSpacing // 2)

            # draw the card for each player
            for cardIndex in range(len(playerCards[playerIndex])):
                card = playerCards[playerIndex][cardIndex]
                
                # calc the X position for the cards 
                cardX = screenWidth // 2 - (2 * cardWidth + cardSpacing) // 2 + cardIndex * (cardWidth + cardSpacing)
                
                # draw the card rectangle with the player's color scheme
                pygame.draw.rect(screen, players.sprites()[playerIndex].colorScheme, (cardX, playerY, cardWidth, cardHeight - 20), 2)

                # render and put it on screen
                cardTitle = smallFont.render(card.cardName, True, (255, 255, 255))
                cardDescription = smallFont.render(card.cardDescription, True, (200, 200, 200))
                screen.blit(cardTitle, (cardX + 10, playerY + 10))
                screen.blit(cardDescription, (cardX + 10, playerY + 50))
                
                # display button icons for controller players, imagine being first player
                if playerIndex != 0:

                    # display the button icons, card 1 is A, card 2 is B
                    if cardIndex == 0:
                        # if player has seleted a card, dont show the button
                        if playerSelections[playerIndex] is None:
                            aButtonImage = pygame.image.load("src/art/icons/AButtonIddle.png").convert_alpha()
                            aButtonImage = pygame.transform.scale(aButtonImage, (32, 32))

                            # put it in the top right
                            screen.blit(aButtonImage, (cardX + cardWidth - 42, playerY + 10))
                    elif cardIndex == 1:
                        if playerSelections[playerIndex] is None:
                            bButtonImage = pygame.image.load("src/art/icons/BButtonIddle.png").convert_alpha()
                            bButtonImage = pygame.transform.scale(bButtonImage, (32, 32))
                            
                            # put it in the top right
                            screen.blit(bButtonImage, (cardX + cardWidth - 42, playerY + 10))

        pygame.display.flip()
    
    # outside of the loop
    changedWeapons = []

    # apply the cards to the players
    for i in range(len(players)):

        # there are 3 or 2 possible player selections based on the number of players, 0 is always mnk 
        selectedCard = playerSelections[i]
        if selectedCard is not None:
            if selectedCard.cardName in ["Assault Rifle", "Desert Eagle", "SMG"]:
                changedWeapons.append(players.sprites()[i])
            for modifier in selectedCard.modifiers:
                modifier.applyModifier(players.sprites()[i])

    # slight buffer
    pygame.time.wait(400)

    # return the players whose weapons were changed, so that i can properally refresh and add to all sprites
    return changedWeapons
