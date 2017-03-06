
from random import randrange
from time import sleep
import pygame
import os

height = 25
width = 10
cell_size = 35

hs_file = os.environ['HOME'] + '/.tetris.high'

def read_hs():
    if os.path.isfile(hs_file):
        return int(open(hs_file).read())
    else:
        return 0

def write_hs(n):
    open(hs_file,'w').write(str(n))

# state = (grid,piece,x,y,next-piece)
# piece = list of rotations the piece can be in
# x,y - offset of piece in grid
# grid/piece represented as set of covered positions

def rotateList(xs):
    # rotate(!) 1st element to the back of the list
    return xs[1:len(xs)] + [xs[0]]

def placePiece(piece,x,y):
    currentRot = piece[0]
    return { (a+x,b+y) for (a,b) in currentRot }

squarePiece = [
    { (0,0), (1,0), (1,1), (0,1) }
]
straightPiece = [
    { (0,0), (1,0), (2,0), (3,0) }, 
    # ok for y to be -1, just means can't rotate until it has dropped
    { (1,-1), (1,0), (1,1), (1,2) },
]
Spiece1 = [
    { (0,0), (1,0), (1,1), (2,1) },
    { (2,0), (2,1), (1,1), (1,2) },
]
Spiece2 = [
    { (2,0), (1,0), (1,1), (0,1) },
    { (0,0), (0,1), (1,1), (1,2) },
]
Tpiece = [
    { (0,0), (1,0), (2,0),  (1,1) },
    { (1,1), (1,0), (1,-1), (2,0) },
    { (0,0), (1,0), (1,-1), (2,0) },
    { (0,0), (1,0), (1,-1), (1,1) },
]
Lpiece1 = [
    { (0,0), (0,1), (0,2), (1,2) },
    { (0,0), (1,0), (2,0), (0,1) },
    { (1,0), (2,0), (2,1), (2,2) },
    { (2,1), (0,2), (1,2), (2,2) },
]
Lpiece2 = [
    { (1,0), (1,1), (1,2), (0,2) },
    { (0,1), (2,2), (1,2), (0,2) },
    { (1,0), (0,0), (0,1), (0,2) },
    { (2,0), (1,0), (0,0), (2,1) },
]

allPieces = [ 
    Lpiece1, Lpiece2, squarePiece, 
    straightPiece, #straightPiece, straightPiece,  # cheat with more straight pieces
    Tpiece, Spiece1, Spiece2 
]

def overlap(g1,g2):
    return (g1 & g2) != set([])
    
def merge(g1,g2):
    return g1 | g2

def ongrid(g):
    filtered = [ (x,y) for (x,y) in g 
                if (x<0) | (x>=width) | (y<0) | (y>=height) ]
    return (filtered == [])

def tryClearLine(h,grid):
    if len({ x for x,y in grid if y == h }) == width:
        def drop(y):
            if y >= h:
                return y
            else:
                return y+1
        #print ('clearing line: ' + str(h))
        return { (x,drop(y)) for x,y in grid if y != h }, True
    else:
        return grid, False

def clearAnyCompleteLines(grid):
    lines_cleared = []
    for h in range(height):
        grid,cleared = tryClearLine(h,grid)
        if cleared:
            lines_cleared = lines_cleared + [h]
    return grid, lines_cleared

def testPlace(grid,piece,x,y):
    pgrid = placePiece(piece,x,y)
    if not (ongrid (pgrid)):
        return False # out of bounds
    if overlap (grid,pgrid): # do mean if! (not elif) ## CHECK
        return False # collides
    else:
        return True

initPos = (width/2-2,0) # middle of top row

def randomPiece():
    r = randrange(len(allPieces))
    return allPieces[r]

def state0():
    x,y = initPos
    return ( set([]), randomPiece(), x, y, randomPiece())

def tick(state):
    grid,piece,x,y,nextp = state
    ok = testPlace(grid,piece,x,y+1)
    if ok: # that we can move the piece one step down
        return (grid,piece,x,y+1,nextp), [], False
    else:
        pgrid = placePiece(piece,x,y) # we know we can
        grid = merge (grid,pgrid) # freeze
        grid,lines_cleared = clearAnyCompleteLines(grid)
        x,y = initPos
        ok2 = testPlace(grid,nextp,x,y)
        if ok2: # that the new piece fits at the top of the screen
            new_nextp = randomPiece()
            return (grid,nextp,x,y,new_nextp), lines_cleared, True
        else:
            return 'GameOver', lines_cleared, True

def cheat(state):
    grid,piece,x,y,_ = state
    new_nextp = randomPiece()
    return (grid,piece,x,y,new_nextp)

def interpretKey(key,piece,x):
    if key == "Left":
        return piece, x-1
    elif key == "Right":
        return piece, x+1
    elif key == "Rotate":
        return rotateList(piece), x
    elif key == "Nothing":
        return piece, x
    else:
        return piece, x
        
def move(key,state):
    grid,piece,x,y,np = state
    piece2,x2 = interpretKey(key,piece,x)
    ok = testPlace(grid,piece2,x2,y)
    if ok: # that we can shift/rotate into the new position
        return (grid,piece2,x2,y,np) # move
    else:
        return (grid,piece,x,y,np) # dont move
            
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

xoff = 6
yoff = 1
screen_width = cell_size  * (width + xoff + 1)
screen_height = cell_size * (height + yoff + 1)

def cells_of_state(state):
    grid,piece,x,y,nextp = state
    grid = merge (grid, placePiece(piece,x,y))
    grid = merge (grid, placePiece(nextp,-5,1))
    return grid

key_desc = {
    pygame.K_LEFT   : '*left-arrow*',
    pygame.K_RIGHT  : '*right-arrow*',
    pygame.K_TAB    : '*tab*',
    pygame.K_RETURN : '*enter*',
    pygame.K_SPACE  : '*space*',
    pygame.K_LSHIFT : '*left-shift*',
    pygame.K_RSHIFT : '*right-shift*',
    pygame.K_ESCAPE : '*escape*',
    pygame.K_z      : 'z',
    pygame.K_x      : 'x',
}

def key_name(k):
    if k in key_desc:
        return key_desc[k]
    else:
        return 'key-'+str(k)

def displayState(key,screen,state,cleared,score,high,speed,paused,gameOver):

    def fill_cell (x,y,col):
        x,y = x+xoff, y+yoff
        s = cell_size
        r = pygame.Rect (x * s, y * s, s-1, s-1)
        pygame.draw.rect(screen,col,r,0)

    def draw_border():
        s = cell_size
        r = pygame.Rect (xoff * s, yoff * s, width * s, height * s)
        pygame.draw.rect(screen,white,r,1)

    def messageS(h, col, text, scale):
        font = pygame.font.Font('freesansbold.ttf', cell_size//scale)
        surf = font.render(text, True, col)
        rect = surf.get_rect()
        rect.left = cell_size
        rect.top = h * cell_size
        screen.blit(surf, rect)

    def message(h,col,text):
        messageS(h,col,text,1)

    def message_key(h,tag):
        messageS(h,red, tag + ' : ' + key_name(key[tag]),2)

    screen.fill(black)
    message(1,red,'next')
    message(6,red,'speed')
    message(7,white,str(speed))
    message(9,red,'cleared')
    message(10,white,str(cleared))
    message(12,red,'score')
    message(13,white,str(score))
    message(15,red,'high')
    message(16,white,str(high))

    message_key(height-2.5,'Left')
    message_key(height-2,'Right')
    message_key(height-1.5,'Rotate')
    message_key(height-1,'Drop')
    message_key(height-0.5,'Pause')
    message_key(height,'Keys')

    if gameOver:
        message(19,red,'GAME')
        message(20,red,'OVER')
    elif paused:
        message(19,red,'(paused)')

    draw_border()
    for (x,y) in cells_of_state(state):
        fill_cell (x,y,white)
    pygame.display.update()

clock = pygame.time.Clock()

keyA = {
    'Left'   : pygame.K_LEFT,
    'Right'  : pygame.K_RIGHT,
    'Rotate' : pygame.K_TAB,
    'Drop'   : pygame.K_LSHIFT,
    'Pause'  : pygame.K_SPACE,
    'Keys'   : pygame.K_ESCAPE
}

keyB = {
    'Left'   : pygame.K_z,
    'Right'  : pygame.K_x,
    'Rotate' : pygame.K_RETURN,
    'Drop'   : pygame.K_RSHIFT,
    'Pause'  : pygame.K_SPACE,
    'Keys'   : pygame.K_ESCAPE,
}

fps = 60
max_speed = 20 # reducing max speed has effect of making speed=1 harder!

auto_repeat_period = 5

def init():
    state = state0()
    cleared = 0
    score = 0
    high = read_hs()
    speed = 1
    paused = True
    gameOver = False
    elapsed_frames = 0
    dropping = False
    return state,cleared,score,high,speed,paused,gameOver,elapsed_frames,dropping

def run():

    stop = False

    state,cleared,score,high,speed,paused,gameOver,elapsed_frames,dropping = init()

    left_repeat = False
    right_repeat = False

    keyAlts = [keyA,keyB]
    
    pygame.init()
    pygame.display.set_caption('My Tetris')
    screen = pygame.display.set_mode((screen_width,screen_height))
    while not stop:

        key = keyAlts[0]

        e = "Nothing"
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT: # red-cross clicked
                stop = True
            if event.type == pygame.KEYDOWN:
                if event.key == key['Keys']:
                    keyAlts = rotateList(keyAlts)
                elif event.key == key['Left']:
                    e = "Left"
                    left_repeat = True
                    left_repeat_count = 2 * auto_repeat_period
                elif event.key == key['Right']:
                    e = "Right"
                    right_repeat = True
                    right_repeat_count = 2 * auto_repeat_period
                elif event.key == key['Rotate']:
                    e = "Rotate"
                elif event.key == pygame.K_DELETE:
                    state = cheat(state)
                elif event.key == key['Pause']:
                    if gameOver:
                        if score > high:
                            write_hs(score)
                        state,cleared,score,high,speed,paused,gameOver,elapsed_frames,dropping = init()
                    else:
                        paused = not paused
                elif event.key == key['Drop']:
                    dropping = True

            if event.type == pygame.KEYUP:
                if event.key == key['Drop']:
                    dropping = False
                elif event.key == key['Left']:
                    left_repeat = False
                elif event.key == key['Right']:
                    right_repeat = False

        if left_repeat:
            left_repeat_count = left_repeat_count - 1
            if left_repeat_count == 0:
                left_repeat_count = auto_repeat_period
                e = 'Left'

        if right_repeat:
            right_repeat_count = right_repeat_count - 1
            if right_repeat_count == 0:
                right_repeat_count = auto_repeat_period
                e = 'Right'

        def state_with_frozen_piece(state):
            grid,piece,x,y,nextp = state
            grid = merge (grid, placePiece(piece,x,y))
            return grid,[{}],x,y,nextp  # and remove piece

        def state_without_lines(state,lines):
            g1,piece,x,y,nextp = state
            g2 = { (x,y) for x,y in g1 if not y in lines }
            return g2,piece,x,y,nextp

        def flash_cleared(state,lines):
            s1 = state_with_frozen_piece(state)
            s2 = state_without_lines(s1,lines)
            displayState(key,screen,s2,cleared,score,high,speed,paused,gameOver)
            clock.tick(5)
            displayState(key,screen,s1,cleared,score,high,speed,paused,gameOver)
            clock.tick(5)
            displayState(key,screen,s2,cleared,score,high,speed,paused,gameOver)
            clock.tick(5)

        if not paused:       
            state = move(e,state)
            elapsed_frames = elapsed_frames + 1
            frames_per_tick = 1 + max_speed - speed
            if dropping | (elapsed_frames % frames_per_tick == 0):
                if dropping:
                    score = score + 5
                else:
                    score = score + 1
                nextS,lines_cleared,new_appeared = tick(state)
                if new_appeared:
                    dropping = False
                if lines_cleared != []:
                    n_cleared = len(lines_cleared)
                    cleared = cleared + n_cleared
                    score = score + 50 * n_cleared
                    flash_cleared(state,lines_cleared)
                speed = min (max (speed, 1 + cleared // 10), 20)
                if nextS == 'GameOver':
                    gameOver = True
                    paused = True
                else:
                    state = nextS

        #print("Display: " + str(elapsed_frames))
        displayState(key,screen,state,cleared,score,high,speed,paused,gameOver)
        clock.tick(fps)


run()
