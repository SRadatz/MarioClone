##Final Project
##ITCS 1950
##Platformer: Not your average plummer / Mario clone
##Developer: Sean Radatz

import pygame, sys
from pygame import *

pygame.init()

#Constants
WIN_WIDTH = 800
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)
FONT = pygame.font.SysFont(None, 48)
TEXTCOLOR = (255, 255, 255)
BACKGROUNDCOLOR = ( 255, 165, 125)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0

score = 0
topScore = 0

grabCoin = pygame.mixer.Sound('Coin Sound.wav')
pygame.mixer.music.load('THEMEFX.mid')

screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
pygame.display.set_caption("Platformer!")
timer = pygame.time.Clock()

def terminate():
    pygame.quit()
    sys.exit()

def intro():
    drawtext('Not Your Average Plummer', FONT, screen, (WIN_WIDTH / 4), (WIN_HEIGHT / 3))
    drawtext('Press a key to start.', FONT, screen, (WIN_WIDTH / 3) - 30, (WIN_HEIGHT / 3) + 50)
    pygame.display.update()
    PressKey()

def gameOver(platforms, entities):
    pygame.mixer.music.stop()
    global score
    score = 0
    for p in platforms:
        del p
    for e in entities:
        del e
    drawtext('Game Over !!', FONT, screen, (WIN_WIDTH / 3), (WIN_HEIGHT / 3))
    drawtext('Press a key to start over.', FONT, screen, (WIN_WIDTH / 3) - 30, (WIN_HEIGHT / 3) + 50)
    drawtext('To quit press ESC.', FONT, screen, (WIN_WIDTH  / 3) - 30, (WIN_HEIGHT / 3) + 100)
    pygame.display.update()
    PressKey()
    screen.fill(BACKGROUNDCOLOR)
    pygame.display.update()
    main()
    

def drawtext(text, font, surface, x, y):
    textobj = font.render(text, 1, TEXTCOLOR) #draws text on a new surface
    textrect = textobj.get_rect()             #returns new rectangle
    textrect.topleft = (x, y)                 #designates to start topleft @ x,y
    surface.blit(textobj, textrect)           #draws both objects on the surface that is designated by input

def PressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return

class Camera():
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func                  #defines camera function as an attribute
        self.state = Rect(0, 0, width, height)          #declares self as a rectangle starting at 0,0 with height and width of level 

    def apply(self, target):                            
        return target.rect.move(self.state.topleft)     #apply self x,y to x,y coordinates of target(player) 

    def update(self, target):                           #used to blit everything in entities group
        self.state = self.camera_func(self.state, target.rect) #sends self x,y and player x,y to scrolling camera 

def scrolling_camera(camera, target_rect):
    l, t, _, _ = target_rect                         #player x,y
    _, _, w, h = camera                              #camera x,y
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h #centers player x,y in the middle

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-WIN_WIDTH), l)   # stop scrolling at the right edge
    t = max(-(camera.height-WIN_HEIGHT), t) # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top
    return Rect(l, t, w, h)                 # return all camera and target (x,y) location

class Sprite(pygame.sprite.Sprite):   #Blank sprite class
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Player(Sprite):
    def __init__(self, x, y):
        Sprite.__init__(self)
        self.xvel = 0                 #initial X velocity
        self.yvel = 0                 #initial Y velocity
        self.onGround = False         #Gravity on
        self.rect = Rect(x, y, 19, 26)#rect location, rect size

    def update(self, moveUp, moveDown, moveLeft, moveRight, running, platforms, entities):
        if moveUp:
            if self.onGround:
                self.yvel -= 10                        #jump
        if moveDown:
            pass                                       #null could be used in future
        if running:
            self.xvel = 12                             #running velocity if running was used
        if moveLeft:
            self.xvel = -8                             #Left velocity
            rightwalk = 'ML1.png'
            self.image = pygame.image.load(rightwalk)  #change self image if going left
        if moveRight:
            self.xvel = 8                              #right velocity
            rightwalk = 'MR1.png'
            self.image = pygame.image.load(rightwalk)  #change self image if going left
                    
        if not self.onGround:
            self.yvel += 0.3                           #Gravity velocity
            if self.yvel > 100: self.yvel = 100        #max fall speed
            
        if not(moveLeft or moveRight):                 #stand still
            self.xvel = 0
            sit = 'Msit.png'
            self.image = pygame.image.load(sit)        #change self image if not moving
        
        self.rect.left += self.xvel                    #increment player left or right
        self.collide(self.xvel, 0, platforms, entities)#X collision
        self.rect.top += self.yvel                     #increment player rect up for jump
        self.onGround = False;                         #turns gravity back on if on ground
        self.collide(0, self.yvel, platforms, entities)#Y collision

    def collide(self, xvel, yvel, platforms, entities):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):    #pygames collision with solid objects
                if isinstance(p, ExitBlock):           
                    gameOver(platforms, entities)      #end game
                if xvel > 0:                           #move right
                    self.rect.right = p.rect.left
                    #print("collide right")
                if xvel < 0:                           #move left
                    self.rect.left = p.rect.right
                    #print("collide left")
                if yvel > 0:                           #move down
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                    #print("collide bottom")
                if yvel < 0:                           #move up
                    self.rect.top = p.rect.bottom
                    #print("collide top")
        for e in entities:
            if pygame.sprite.collide_rect(self, e):    #Pygames collision with items
                if isinstance(e, Spikes):
                    gameOver(platforms, entities)      #end game
                if isinstance(e, Coin):
                    global score
                    score += 100
                    grabCoin.play()
                    entities.remove(e)
                if isinstance(e, Mushroom):
                    global score
                    score += 1000
                    grabCoin.play()
                    entities.remove(e)
                if isinstance(e, superStar):
                    global score
                    score += 10000
                    grabCoin.play()
                    entities.remove(e)
                    


class Platform(Sprite):
    def __init__(self, x, y):
        Sprite.__init__(self)
        plat = 'blueblock32.png'
        self.image = pygame.image.load(plat)
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)

class Block(Sprite):
    def __init__(self, x, y):
        Sprite.__init__(self)
        plat = 'Blueplatform.png'
        self.image = pygame.image.load(plat)
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)


class ExitBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        plat = 'Exitblock.png'
        self.image = pygame.image.load(plat)

class Coin(Sprite):
    def __init__(self, x, y):
        Sprite.__init__(self)
        plat = 'Coin.png'
        self.image = pygame.image.load(plat)
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)

class superStar(Sprite):
    def __init__(self, x, y):
        Sprite.__init__(self)
        plat = 'SuperStar.png'
        self.image = pygame.image.load(plat)
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)

class Mushroom(Sprite):
    def __init__(self, x, y):
        Sprite.__init__(self)
        plat = 'Mush.png'
        self.image = pygame.image.load(plat)
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)

class Spikes(Sprite):
    def __init__(self, x, y):
        Sprite.__init__(self)
        plat = 'Spikes.png'
        self.image = pygame.image.load(plat)
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)


def main():
    intro()
    score = 0
    pygame.mixer.music.play(-1, 0.0) #(loops, start point)
    
    moveUp = moveDown = moveLeft = moveRight = running = False
    entities = pygame.sprite.Group()
    player = Player(32, 32)
    platforms = []

    x = y = 0
    level = [
        "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
        "P          SMC          BC               BM    M                                                  M                                P",
        "P         CCCCC        BC                C    CCC                     M                                                            P",
        "P    B     CCC        BC      CCCCCCC    B                                                     C  C  C                         C   P",
        "P     B              BBBBBBBBBBB         B                                SGS                                 CCCCCCCC         C   P",
        "P      B                            B    B   BBB                           B                  BBBBBBBBBB                       C   P",
        "P                                        B     B         BBBBBBBBBB                            B C              CCCC           C   P",
        "P            BBBBBBBBB                   B B  BBBBBBB               CCC                         B C                            C   P",
        "P        B                   C C C       BB  BMMMMMGB                                            B C      BBBBBBBB             C   P",
        "P        B                               B      S  SB             BBBBBBBB              B         B C                          C   P",
        "P        B                  BBBBBBB    SSBBBBBBBBBBBB               CC             C C  S          B C          BBBBBBBBB      C   P",
        "P        B       C                                  B      C C                                      B C         B             C C  P",
        "P        BCCB        C                       BBBB   BC   C     C          BBBBBBB               BBBBBB        CB             C S C P",
        "P         BCB                C     BB               B                                                        CB            BBBBBBBBP",
        "P         BCB                                       B   CCCCCCCCCCCC            B B                         CB                     P",
        "P         BCB           BBBBBB                      B                                                      CB                      P",
        "P         BMB                BS                     B C C BBBBBBBBBBBB          C  C   C                  CB                       P",
        "P         BBB               B                       B  C        M                                        CB                        P",
        "P                 CCCCC    B                        B C C  CCCCCCCCCCC        BBBBBBBBBBBBB                          C             P",
        "P          BBBBBBBBBBBB   B                         BCCCCBBBBBBBBBBBB              S      C  C  C                   CCC            P",
        "P         B       CCC    B             BBBBB        BCCCBS     S                                                   CCCCC           P",
        "P        BC             B       CCCC                BCCB S  S  S                         BBBBBBBBBB               CCCCCCC          P",
        "P       BSC            B                 CCCCC      BMBM S  S  S                B     B                          CCCCMCCCC         P",
        "P      BMCC           B                             BBMM    S                 BCBCBMBCBCB                  CCCCCCCCCMEMCCCC        P",
        "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",]
    # build the level
    for row in level:
        for col in row:
            if col == "P":
                p = Platform(x, y)
                platforms.append(p)
                entities.add(p)
            if col == "B":
                b = Block(x, y)
                platforms.append(b)
                entities.add(b)
            if col == "E":
                e = ExitBlock(x, y)
                platforms.append(e)
                entities.add(e)
            if col == "C":
                c = Coin(x, y)
                entities.add(c)
            if col == "M":
                m = Mushroom(x, y)
                entities.add(m)
            if col == "S":
                s = Spikes(x, y)
                entities.add(s)
            if col == "G":
                g = superStar(x, y)
                entities.add(g)
            x += 32 #adds size to each platform created
        y += 32
        x = 0 # allows more than one level to be created

    total_level_width  = len(level[0])*32 #size of level in pixels
    total_level_height = len(level)*32
    camera = Camera(scrolling_camera, total_level_width, total_level_height)
    entities.add(player)

    while True:
        timer.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                    terminate()
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == ord('a'):
                    moveLeft = True
                if event.key == K_RIGHT or event.key == ord('d'):
                    moveRight = True
                if event.key == K_UP or event.key == ord('w'):
                    moveUp = True
                if event.key == K_DOWN or event.key == ord('s'):
                    moveDown = True
                if event.key == K_SPACE:
                    running = True

            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    terminate()

                if event.key == K_LEFT or event.key == ord('a'):
                    moveLeft = False
                if event.key == K_RIGHT or event.key == ord('d'):
                    moveRight = False
                if event.key == K_UP or event.key == ord('w'):
                    moveUp = False
                if event.key == K_DOWN or event.key == ord('s'):
                    moveDown = False

        # draw background
        screen.fill(BACKGROUNDCOLOR)

        #set top score
        global score
        global topScore
        if score > topScore:
            topScore = score
        drawtext('Score: %s' % (score), FONT, screen, 32, 32)
        drawtext('Top Score: %s' % (topScore), FONT, screen, 32, 64)

        #update camera location
        camera.update(player)

        # update player, draw everything else
        player.update(moveUp, moveDown, moveLeft, moveRight, running, platforms, entities)
        for e in entities:
            screen.blit(e.image, camera.apply(e))

        pygame.display.update()

main()
