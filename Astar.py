import pygame
from noise import pnoise2 as perlin
from random import randint
from time import time
pygame.init()

###Main controls
controls = '''
Left click:   set starting position
Right click:  set target position
Middle click: create wall (with shift: delete walls)
Space:        start search
Escape:       stop search / exit

c: clear screen
r: clear path from previous search
n: new random set of walls
m: enter a seed manually
i: set the wall intensity (between 0 and 1, lower = less walls)
d: set distWeight (weight of the distance from the end node)

More settings (such as screen size) can be found in the Astar class
'''

###Variables
col = {
  'black' : (0, 0, 0),        #wall
  'white' : (255, 255, 255),  #blank square
  'grey' : (160, 160, 160),   #discovered nodes
  'red' : (255, 0, 0),        #current square
  'green' : (0, 240, 0),      #visited nodes
  'blue' : (0, 0, 255),       #current pos
  'purple' : (255, 0, 255)    #target pos
}
screen = None
run = True
clock = pygame.time.Clock()

###Functions
def checkPos(pos, l): #Returns the item with a certain position
    for i in l:
        if i.pos == pos:
            return i

    return None

def newWalls(x, y, seed, intensity): #Uses perlin noise to generate random walls
    walls = []
    base = randint(0,300) if seed==None else seed
    print('\nSeed:', base)
    for i in range(x):
        for j in range(y):
            if perlin(i/5.0, j/5.0, octaves=1, persistence=0.5, lacunarity=8.0, base=base) > intensity:
                walls.append([i, j])
    return walls

def coordToBlock(pos):
    return [int(pos[0]/Astar.blockSize), int(pos[1]/Astar.blockSize)]

def sign(num):
    if num >= 0:
        return 1
    else:
        return -1

def line(posA, posB): #Gets the points between two positions in ordere to form a line
    blocks = []

    dist = [posA[0]-posB[0], posA[1]-posB[1]]
    
    if dist[0] == 0: #verical line
        for x in range(0, abs(dist[1])+1):
            block = coordToBlock([posA[0], posA[1]+x])
            blocks.append([block[0],   block[1]])
            blocks.append([block[0]+1, block[1]])
            blocks.append([block[0]-1, block[1]])
    else:
        gradient = dist[1]/dist[0]
        for x in range(0, abs(dist[0])+1):
            block = coordToBlock([posA[0] + x*sign(-dist[0]), posA[1] + x*sign(-dist[0])*gradient])
            blocks.append([block[0],   block[1]])
            blocks.append([block[0]+1, block[1]])
            blocks.append([block[0]-1, block[1]])
            blocks.append([block[0], block[1]+1])
            blocks.append([block[0], block[1]-1])
    
    return blocks

def euclidean(a, b):
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2) ** .5

###Classes
class Astar:
    gridSize = (300, 200) #Sets numbers of blocks in the x and y axis, respectivley
    blockSize = 5 #Sets the height and width of each block in pixels
    defaultIntensity = 0.75 #Sets the intensity of the walls, number between 0 and 1, lower value = less walls
    distWeight = 1.4 #Sets the weight of the distance from the target node, recommended between 1.25 and 2
    #A higher value of distWeight can mean faster times and less efficient paths
    
    def __init__(self, x = gridSize[0], y = gridSize[1]):
        global screen
        #Set up properties
        self.x = x
        self.y = y
        self.intensity = Astar.defaultIntensity
        self.drawWalls = False
        self.invertWalls = False
        self.prevPos = None

        #Set up the display
        self.screenSize = (x*Astar.blockSize, y*Astar.blockSize)
        screen = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption('A*')

        self.newWalls()

    def newWalls(self, seed=None): #Create walls with a specified seed, if none given a random seed is picked
        self.reset()
        self.seed = randint(0,300) if seed==None else seed
        self.walls = newWalls(self.x, self.y, self.seed, self.intensity)

    def drawNewWalls(self, pos):
        if self.prevPos == None:
            self.prevPos = pos

        if self.drawWalls:
            if self.invertWalls:
                for b in line(self.prevPos, pos):
                    if b in self.walls:
                        self.walls.remove(b)
            else:
                for b in line(self.prevPos, pos):
                    self.walls.append(b)

        self.prevPos = pos

    def click(self, pos, btn):
        block = coordToBlock(pos)
        if btn == 1: #left
            if block in self.walls:
                print('Cannot put start or target position in walls')
            else:
                self.blocks[0] = block
        if btn == 2: #middle
            pathfinder.drawWalls = False
            self.prevPos == None
        elif btn == 3: #right
            if block in self.walls:
                print('Cannot put start or target in walls')
            else:
                self.blocks[1] = block

    def reset(self, completeReset=True):
        if completeReset:
            self.blocks = [None, None]  #left=current,  right=target
            self.walls = []
        self.visitedNodes = []
        self.discoveredNodes = []
        self.path = []

    def update(self):
        screen.fill(col['white'])
        #draw visited and discovered nodes
        for n in self.discoveredNodes:
            self.drawBlock(n.pos, col['grey'])
        for n in self.visitedNodes:
            self.drawBlock(n.pos, col['green'])
        #draw path
        for n in self.path:
            self.drawBlock(n, col['red'])
        #draw user & target squares
        if self.blocks[0] != None:
            self.drawBlock(self.blocks[0], col['blue'])
        if self.blocks[1] != None:
            self.drawBlock(self.blocks[1], col['purple'])
        #draw walls
        for w in self.walls:
            self.drawBlock(w, col['black'])
        #draw grid lines
        if Astar.blockSize > 12:
            for i in range(1, self.x):
                pygame.draw.rect(screen, col['black'], pygame.Rect((i*Astar.blockSize)-1, 0, 2, self.screenSize[1]))
            for i in range(1, self.y):
                pygame.draw.rect(screen, col['black'], pygame.Rect(0, (i*Astar.blockSize)-1, self.screenSize[0], 2))

    def search(self):
        if self.blocks[0] != None and self.blocks[1] != None:
            self.reset(False)
            self.update()
            #Set up variables for searching
            pygame.display.set_caption('A* - searching')
            startTime = time()
            timeTaken = None
            found = False
            currentNode = StartNode(self.blocks[0])
            self.path = []
            self.visitedNodes = [] #Nodes that have been visited and checked
            self.discoveredNodes = [] #Nodes that have been discovered (next to) by visited nodes

            while not found:
                #Get neighbours of the current node
                neighbours = currentNode.getNeighbours(self.discoveredNodes, self.visitedNodes)
                #Add the neighbours at the start of the dicovered nodes
                neighbours.extend(self.discoveredNodes)
                self.discoveredNodes = list(neighbours)
                self.visitedNodes.append(currentNode)
                if currentNode in self.discoveredNodes:
                    self.discoveredNodes.remove(currentNode)

                #Get the next node with the lowest cost
                nextNodes = sorted(self.discoveredNodes, key=lambda x: x.cost)
                if len(nextNodes) == 0:
                    print('No path found!')
                    break
                self.drawBlock(currentNode.pos, col['green'])
                currentNode = nextNodes[0]

                if checkPos(self.blocks[1], self.visitedNodes):
                    timeTaken = round(time()-startTime, 2)
                    found = True

                #Draw to screen
                self.drawBlock(currentNode.pos, col['red'])
                self.drawBlock(self.blocks[0], col['blue'])
                pygame.display.flip()
                for e in pygame.event.get():
                    if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                        found = True

            #Finds the node that found the target
            for i, n in enumerate(self.visitedNodes):
                if n.pos == self.blocks[1]:
                    break
            currentNode = self.visitedNodes[i]

            #Output the oath length and time taken
            if timeTaken:
                print('Found path of length {} in {} seconds'.format(round(currentNode.pathCost, 1), timeTaken))
            else:
                print('Pathfinding cancelled')

            #Finds the path back from the end node to the starting node
            while currentNode != None:
                self.path.append(tuple(currentNode.pos))
                currentNode = currentNode.pre
            pygame.display.set_caption('A*')

    def drawBlock(self, pos, colour):
        block = pygame.Rect(pos[0]*Astar.blockSize, pos[1]*Astar.blockSize, Astar.blockSize, Astar.blockSize)
        pygame.draw.rect(screen, colour, block)

    @property
    def intensity(self):
        return self._intensity

    @intensity.setter
    def intensity(self, i):
        self._intensity = (1-i)**2

class Node:
    def __init__(self, pos, pre):
        self.pos = pos
        self._pre = pre

        #Calculate distance from starting node
        self.pathCost = pre.pathCost + euclidean(pos, pre.pos)
        #Calculate distance from end node
        self.distCost = euclidean(pathfinder.blocks[1], pos)

    def getNeighbours(self, discoveredNodes, visitedNodes): #Return each valid neighbour that has not been visited
        n = []
        for x in (self.pos[0], self.pos[0]+1, self.pos[0]-1):
            for y in (self.pos[1], self.pos[1]+1, self.pos[1]-1):
                pos = [x, y]

                #If the neighbour has been visited before check if it has a more efficient path than the current previous node
                neighbourVisited = checkPos(pos, visitedNodes)
                if neighbourVisited.__class__ == Node:
                    self.pre = neighbourVisited
                    neighbourVisited.pre = self
                    continue
                
                #If the neighbour is valid add it to the array
                notColliding = pos != self.pos and not pos in pathfinder.walls
                inGrid = x >= 0 and x < pathfinder.x and y >= 0 and y < pathfinder.y
                if notColliding and inGrid and checkPos(pos, discoveredNodes) == None and pos != pathfinder.blocks[0]:
                    n.append(Node(pos, self))
        return n #Returns all valid neighbours

    @property
    def cost(self):
        return self.pathCost + self.distCost*Astar.distWeight

    @property
    def pre(self):
        return self._pre

    @pre.setter
    def pre(self, newPre):
        if self._pre.pathCost > newPre.pathCost+euclidean(self.pos, newPre.pos) and newPre.pre != self:
            self._pre = newPre
            self.pathCost = newPre.cost + euclidean(self.pos, newPre.pos)

    def __str__(self): #Used for debugging
        return 'Node {},{}\t pre:{}\t cost:{}\t path cost:{}\t distance from end:{}'.format(
            self.pos[0], self.pos[1],
            None if self.pre == None else self.pre.pos,
            round(self.cost, 1), round(self.pathCost, 1), round(self.distCost, 1)
        )

class StartNode(Node):
    def __init__(self, pos):
        self.pos = pos

        #Calculate costs
        self.pathCost = 0
        self.distCost = euclidean(pathfinder.blocks[1], pos)

    @property
    def pre(self):
        return None

###Init
print('Controls:' + controls)
pathfinder = Astar()

###Main loop
while run:
    #Handle events
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            run = False
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 2:
            pathfinder.drawWalls = True
        elif e.type == pygame.MOUSEBUTTONUP:
            pathfinder.reset(False)
            pathfinder.click(pygame.mouse.get_pos(), e.button)
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_LSHIFT or e.key == pygame.K_RSHIFT:
                pathfinder.invertWalls = True
            if e.key == pygame.K_SPACE:
                pathfinder.search()
            elif e.key == pygame.K_c:
                pathfinder.reset()
            elif e.key == pygame.K_r:
                pathfinder.reset(False)
            elif e.key == pygame.K_n:
                pathfinder.newWalls()
            elif e.key == pygame.K_m:
                pathfinder.newWalls(int(input('What seed would you like to have? ')))
            elif e.key == pygame.K_i:
                pathfinder.intensity = float(input('Set new intensity '))
                pathfinder.newWalls(pathfinder.seed)
            elif e.key == pygame.K_d:
                Astar.distWeight = float(input('Set new distWeight (current: {}) '.format(Astar.distWeight)))
        elif e.type == pygame.KEYUP:
            if e.key == pygame.K_LSHIFT or e.key == pygame.K_RSHIFT:
                pathfinder.invertWalls = False
    pathfinder.drawNewWalls(pygame.mouse.get_pos())
    
    #Update the screen
    pathfinder.update()
    pygame.display.flip()
    clock.tick(150)

###Exit code
print('\nExiting')
pygame.quit()
