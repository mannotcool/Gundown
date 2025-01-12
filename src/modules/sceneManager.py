import pygame

def showStartScreen(screen):
    pygame.font.init()

    # load ThaleahFat.ttf for the title text
    font = pygame.font.Font("src/fonts/ThaleahFat.ttf", 96)
    smallFont = pygame.font.SysFont("Arial", 24)
    
    titleText = font.render("Welcome to Gundown!", True, (255, 255, 255))
    subtitleText = smallFont.render("Press SPACE to start", True, (255, 255, 255))
    errorText = smallFont.render("At least two players must select colors!", True, (255, 100, 100))
    footerText = smallFont.render("Change colors by clicking (A), or using Mouse Left Click.", True, (255, 255, 255))
    
    screenWidth, screenHeight = screen.get_size()
    bg = pygame.image.load("src/art/dark_abs_bg.gif")
    bg = pygame.transform.scale(bg, (screenWidth, screenHeight))

    boxWidth = 150
    boxHeight = 150
    boxSpacing = 50
    colors = [(255, 179, 186), (255, 223, 186), (186, 255, 201), (186, 225, 255), (227, 218, 255)]
    boxes = [
        pygame.Rect((screenWidth - (3 * boxWidth + 2 * boxSpacing)) // 2, screenHeight // 3, boxWidth, boxHeight),
        pygame.Rect((screenWidth - (3 * boxWidth + 2 * boxSpacing)) // 2 + (boxWidth + boxSpacing), screenHeight // 3, boxWidth, boxHeight),
        pygame.Rect((screenWidth - (3 * boxWidth + 2 * boxSpacing)) // 2 + 2 * (boxWidth + boxSpacing), screenHeight // 3, boxWidth, boxHeight),
    ]

    playerColorIndices = [0, 0, 0]
    playerActive = [True, False, False]

    boxieImages = []
    for color in colors:
        image = pygame.image.load("src/art/character/boxie-white/default-340.png").convert_alpha()
        image = pygame.transform.scale(image, (boxWidth, boxHeight))
        image.fill(color, special_flags=pygame.BLEND_RGB_MULT)
        boxieImages.append(image)

    mouseIcon = pygame.image.load("src/art/icons/mouse.gif")
    mouseIcon = pygame.transform.scale(mouseIcon, (64, 64))  # Larger mouse GIF for visibility
    
    controllerIcon = pygame.image.load("src/art/icons/controller.gif").convert_alpha()
    controllerIcon = pygame.transform.scale(controllerIcon, (32, 32))

    clock = pygame.time.Clock()

    # Initialize joysticks and button states
    joysticks = []
    playerActive = [True, False, False]  # Mouse is always active

    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
        if i + 1 < len(playerActive):
            playerActive[i + 1] = True

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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    activePlayers = sum(playerActive)
                    if activePlayers > 1:
                        keepGoing = False
                    else:
                        showError = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if playerActive[0]:  # mouse always controls Player 1
                    playerColorIndices[0] = (playerColorIndices[0] + 1) % len(colors)

        currentJoystickCount = pygame.joystick.get_count()

        if currentJoystickCount != len(joysticks):  # Joystick count has changed
            joysticks = []
            playerActive = [True, False, False]  # Reset playerActive (Mouse remains active)

            for i in range(currentJoystickCount):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                joysticks.append(joystick)
                if i + 1 < len(playerActive):
                    playerActive[i + 1] = True

        for i in range(len(joysticks)):
            if playerActive[i + 1]:  # ensure the player is active
                joystick = joysticks[i]
                
                # if they click the A button, change the color
                if joystick.get_button(0):
                    playerColorIndices[i + 1] = (playerColorIndices[i + 1] + 1) % len(colors)
                    # pause for a bit to prevent rapid color changes
                    pygame.time.wait(200)

        screen.blit(bg, (0, 0))
        screen.blit(titleText, (screenWidth // 2 - titleText.get_width() // 2, screenHeight // 8))

        # add up the number of active players
        activePlayers = sum(playerActive)

        if activePlayers > 1:
            screen.blit(subtitleText, (screenWidth // 2 - subtitleText.get_width() // 2, screenHeight // 2 + 100))
        elif showError:
            screen.blit(errorText, (screenWidth // 2 - errorText.get_width() // 2, screenHeight // 2 + 140))
        
        # blit the footer text
        screen.blit(footerText, (screenWidth // 2 - footerText.get_width() // 2, screenHeight - 50))

        
        screen.blit(mouseIcon, (boxes[0].centerx - mouseIcon.get_width() // 2 - 15, boxes[0].bottom + 5))
        
        for i in range(len(boxes)):
            # if its first box skip
            
            if playerActive[i]:
                screen.blit(boxieImages[playerColorIndices[i]], boxes[i].topleft)
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

            iconX = boxes[i].centerx - controllerIcon.get_width() // 2
            iconY = boxes[i].bottom + 20  # Adjusted position for better visibility
            screen.blit(controllerIcon, (iconX, iconY))

        pygame.display.flip()
        clock.tick(60)

    resultColors = []
    for i in range(len(playerActive)):
        if playerActive[i]:
            resultColors.append(colors[playerColorIndices[i]])

    return resultColors
