import pygame
import random
import time
import copy

class game:
    
    def __init__(self, size, colors):
        self.size = size
        self.colors = colors
        self.reset()

    def reset(self):
        self.score = 0
        self.grid = []
        for i in range(self.size):
            self.grid.append([])
            for j in range(self.size):
                self.grid[i].append(-1)
        self.cur = (int(self.size/2), int(self.size/2))
        self.grid[self.cur[0]][self.cur[1]] = random.randint(0, len(self.colors)-1)
        self.upcoming = [random.randint(0, len(self.colors)-1) for i in range(3)]
        return self

    def draw(self, screen, loc):
        screen.fill((0,0,0))
        pygame.draw.rect(screen, (255, 255, 255), loc)
        ssize = loc[2]/self.size
        for i in range(self.size):
            for j in range(self.size):
                if(self.grid[i][j] >= 0):
                    pygame.draw.rect(screen, colors[self.grid[i][j]], (loc[0]+ssize*i, loc[1]+ssize*j, ssize, ssize))
                    if (i,j) == self.cur:
                        pygame.draw.ellipse(screen, (255, 255, 255), (loc[0]+ssize*i+ssize/3, loc[1]+ssize*j+ssize/3, ssize/3, ssize/3))
        for i in range(3):
            pygame.draw.rect(screen, self.colors[self.upcoming[i]], (620, 20 + 160*i, 140, 140))
        line1 = font.render("Score:", True, (255, 255, 255))
        line2 = font.render(str(self.score), True, (255, 255, 255))
        screen.blit(line1, (690-line1.get_width()//2, 500))
        screen.blit(line2, (690-line2.get_width()//2, 550))

    def inGrid(self, pos):
        return pos[0]>=0 and pos[0]<self.size and pos[1]>=0 and pos[1]<self.size

    def canPlace(self, square):
        if not self.inGrid(square):
            return False
        if self.grid[square[0]][square[1]] != -1:
            return False
        return True

    def place(self, square):
        if self.canPlace(square):
            self.cur = square
            self.grid[self.cur[0]][self.cur[1]] = self.upcoming[0]
            self.upcoming = self.upcoming[1:]+[random.randint(0, len(self.colors)-1)]
        self.checkScore()
        return self

    def matching(self, square):
        c = self.grid[square[0]][square[1]]
        matches = []
        newm = [square]
        while newm != []:
            matches += newm
            newm = []
            for d in [(-1,0),(1,0),(0,-1),(0,1)]:
                for s in matches:
                    new = (s[0]+d[0], s[1]+d[1])
                    if self.inGrid(new) and self.grid[new[0]][new[1]] == c and not new in matches + newm:
                        newm.append(new)
        return matches

    def checkScore(self):
        c = self.grid[self.cur[0]][self.cur[1]]
        matches = []
        newm = [self.cur]
        while newm != []:
            matches += newm
            newm = []
            for d in [(-1,0),(1,0),(0,-1),(0,1)]:
                for s in matches:
                    new = (s[0]+d[0], s[1]+d[1])
                    if self.inGrid(new) and self.grid[new[0]][new[1]] == c and not new in matches + newm:
                        newm.append(new)
        self.grid[self.cur[0]][self.cur[1]]
        matches = self.matching(self.cur)
        if len(matches)>=3:
            self.score += len(matches)**2//3
            for s in matches:
                if s!=self.cur:
                    self.grid[s[0]][s[1]] = -1

    def evaluate(self):
        return self.score

    def makeMove(self, agent, future = -1):
        if future == -1:
            future = len(self.upcoming)
        moves = [(-1,0),(1,0),(0,-1),(0,1)]
        if agent == 1:
            m = random.choice(moves)
            self.place((self.cur[0]+m[0], self.cur[1]+m[1]))
        if agent == 2:
            paths = [[]]
            for i in range(future):
                newpaths = []
                for m in moves:
                    newpaths += [p + [m] for p in paths]
                paths = newpaths
            bestscore = 0
            bestmoves = []
            for path in paths:
                x = copy.deepcopy(self)
                good = True
                for move in path:
                    if not x.canPlace((x.cur[0] + move[0], x.cur[1] + move[1])):
                        good = False
                    x = x.place((x.cur[0] + move[0], x.cur[1] + move[1]))
                if good:
                    movescore = x.evaluate()
                    if movescore == bestscore:
                        bestmoves.append(path[0])
                    elif movescore > bestscore:
                        bestscore = movescore
                        bestmoves = [path[0]]
            if len(bestmoves) == 0:
                self.makeMove(2, future-1)
            else:
                move = random.choice(bestmoves)
                self.place((self.cur[0] + move[0], self.cur[1] + move[1]))

    def gameover(self):
        moves = [(-1,0),(1,0),(0,-1),(0,1)]
        for m in moves:
            if self.canPlace((self.cur[0]+m[0], self.cur[1]+m[1])):
                return False
        return True
        
pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 48)
screen = pygame.display.set_mode((800, 600))
done = False

colors = [(70,70,70),(80,140,250),(255,50,50),(0,255,50)]
g = game(7, colors)

agent = 2
games = 0
totalscore = 0

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if agent == 0:
                if event.key == pygame.K_LEFT:
                    g = g.place((g.cur[0]-1,g.cur[1]))
                if event.key == pygame.K_RIGHT:
                    g = g.place((g.cur[0]+1,g.cur[1]))
                if event.key == pygame.K_UP:
                    g = g.place((g.cur[0],g.cur[1]-1))
                if event.key == pygame.K_DOWN:
                    g = g.place((g.cur[0],g.cur[1]+1))
            if event.key == pygame.K_SPACE:
                g = g.reset()
    if agent > 0:
        g.makeMove(agent)
    g.draw(screen, (20, 20, 560, 560))
    pygame.display.flip()
    if g.gameover():
        games += 1
        totalscore += g.score
        print(g.score, totalscore/games)
        if agent != 0:
            g.reset()

pygame.quit()
