import sys
import random
import time

from constant import HEIGHT, WIDTH, GAMETICK, MODULO_SCREEN, Orientation
from save import Score, addNewScore, loadingGame, saveGame
from menu import Menu


#! Class use to handle Apple behavior
class Apple:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    #? Allow to make respawn a new apple
    def respawn(self, state):
        xApple, yApple = -1, -1
        for c in range(0, 8):
            xApple, yApple = random.randint(0, 39), random.randint(0, 39)
            for el in state:
                if el['x'] == xApple and el['y'] == yApple:
                    xApple, yApple = -1, -1
                    continue
            break
        if xApple == -1 and yApple == -1:
            for xApple in range(0, 39):
                for yApple in range(0, 39):
                    for el in state:
                        if el['x'] == xApple and el['y'] == yApple:
                            continue
                    self.x = xApple
                    self.y = yApple
                    return
        self.x = xApple
        self.y = yApple


#! Class use to handle Player behavior
class Player:
    #!Class Constructor
    #! Size is the snacke lenght (use to calculate the score)
    #! State is a list contain the snake's part (exemple: [{'x': 19, 'y': 19, 'look': 'up'}, {'x': 19, 'y': 18, 'look': 'left'}])
    def __init__(self, size, state):
        self.size = size
        self.state = state

    #! move forward
    def move(self):
        save = self.state[0]['look']
        for i in range(len(self.state)):
            if (self.state[i]['look'] == 'up'):
                self.state[i]['y'] -= 1
            if (self.state[i]['look'] == 'down'):
                self.state[i]['y'] += 1
            if (self.state[i]['look'] == 'left'):
                self.state[i]['x'] -= 1
            if (self.state[i]['look'] == 'right'):
                self.state[i]['x'] += 1
            if i != 0:
                tmp = self.state[i]['look']
                self.state[i]['look'] = save
                save = tmp

    #! Change The direction of the Snacke
    def changeOrientation(self, newOrientation):
        if (newOrientation == 'up' and self.state[0]['look'] != 'down'):
            self.state[0]['look'] = 'up'
        if (newOrientation == 'down' and self.state[0]['look'] != 'up'):
            self.state[0]['look'] = 'down'
        if (newOrientation == 'left' and self.state[0]['look'] != 'right'):
            self.state[0]['look'] = 'left'
        if (newOrientation == 'right' and self.state[0]['look'] != 'left'):
            self.state[0]['look'] = 'right'

    #! Check If the Snacke Head can eat the Apple
    def CheckEatApple(self, apple, lastX, lastY, lastLook):
        if apple.x == self.state[0]['x'] and apple.y == self.state[0]['y']:
            apple.respawn(self.state)
            self.state.append({'x': lastX, 'y': lastY, 'look': lastLook})
            self.size += 1

    #! Check If the Snacke is alive (return True) or Dead (return False)
    def isAlive(self):
        if self.state[0]['x'] < 0 or self.state[0]['y'] < 0 or self.state[0]['x'] > 39 or self.state[0]['y'] > 39:
            return False
        for i in range(len(self.state)):
            for i2 in range(len(self.state)):
                if i != i2 and self.state[i]['x'] == self.state[i2]['x'] and self.state[i]['y'] == self.state[i2]['y']:
                    return False
        return True


#! Handle All Display part (and a little more)
def displayGame(pygame, screen, player, apple):
    lastX, lastY, lastLook = player.state[len(player.state) - 1]['x'], player.state[len(
        player.state) - 1]['y'], player.state[len(player.state) - 1]['look']
    player.move()
    for i in range(len(player.state)):
        z = pygame.image.load("textures/snackeBody.png")
        if i == 0:
            z = pygame.image.load("textures/snackeHead.png")
        if i == len(player.state) - 1 and i != 0:
            z = pygame.image.load("textures/snackeTail.png")
        z = pygame.transform.rotate(z, Orientation[player.state[i]['look']])
        screen.blit(
            z, (player.state[i]['x']*MODULO_SCREEN, player.state[i]['y']*MODULO_SCREEN))
    player.CheckEatApple(apple, lastX, lastY, lastLook)
    a = pygame.image.load("textures/Apple.png")
    screen.blit(a, (apple.x*MODULO_SCREEN, apple.y*MODULO_SCREEN))
    pygame.display.update()
    pass


#! GamePlay function is use to handle the snacke game
#! pygame => lib
#! screen => pygame window
#! loadSave => String Path to a saveFile (default value '')
def gameplay(pygame, screen, start):
    clock = pygame.time.Clock()
    size = 1 #default Value
    xApple, yApple = random.randint(0, 39), random.randint(0, 39) #default Value
    state = [{'x': 19, 'y': 19, 'look': 'up'}] #default Value
    pauseMenu = False; load = False; notDead = False
    
    bg = pygame.image.load("textures/GameBackground.jpg")
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

    #Create Menu
    menu = Menu(pygame, screen)
    
    # Display the Start Menu
    while start:
        menu.displayStartMenu()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    start = False
                if event.key == pygame.K_l:
                    load = True; start = False
                if event.key == pygame.K_r:
                    menu.displayRanking()
                    time.sleep(7)
                if event.key == pygame.K_e:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()  

    # Use saved game data
    if load:
        size, state, xApple, yApple = loadingGame()
    
    # Create Resource
    player = Player(size, state)
    apple = Apple(xApple, yApple)

    while player.isAlive():
        pygame.display.update()
        clock.tick(GAMETICK)
        screen.blit(bg, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.changeOrientation('left')
                if event.key == pygame.K_DOWN:
                    player.changeOrientation('down')
                if event.key == pygame.K_UP:
                    player.changeOrientation('up')
                if event.key == pygame.K_RIGHT:
                    player.changeOrientation('right')
                if event.key == pygame.K_ESCAPE:
                    pauseMenu = True

        if pauseMenu == True:
            while pauseMenu:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_c:
                            pauseMenu = False 
                        # kills the snake but does not show death screen for resume and save
                        if event.key == pygame.K_r:
                            player.state[0]['x'] = 50
                            notDead = True; pauseMenu = False; 
                        if event.key == pygame.K_s:
                            saveGame(player.size, player.state, apple.x, apple.y)
                            player.state[0]['x'] = 50
                            notDead = True; pauseMenu = False
                        if event.key == pygame.K_e:
                            saveGame(0, [{'x': 19, 'y': 19, 'look': 'up'}], random.randint(0, 39), random.randint(0, 39))
                            pygame.display.quit()
                            pygame.quit()
                            sys.exit()    
                menu.displayPauseMenu()                    
        displayGame(pygame, screen, player, apple)
    if notDead:
        start = True
    #End the game and set properties to default
    else:
        menu.displayGameOver(player.size)
        addNewScore(Score("Player One", player.size))
        #Reset last game file
        saveGame(0, [{'x': 19, 'y': 19, 'look': 'up'}], random.randint(0, 39), random.randint(0, 39))
        time.sleep(7)
        start = True

    return player.size, start