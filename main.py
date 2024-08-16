import pygame
import random
import configparser

class SnekWindow():
    def __init__(self) -> None:
        # Environ vars
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.running = True
        self.sx, self.sy = max(self.config.getint('default', 'winsize'), 200), max(self.config.getint('default', 'winsize'), 200)
        self.fps = 240
        self.pfps = min(self.config.getint('default', 'fps'), self.fps/2) 
        self.clock = pygame.time.Clock()
        self.frame = 0
        self.line_color = [50,0,0]
        
        
        # Game vars
        self.gridx, self.gridy = max(self.config.getint('default', 'cols'), 5) , max(self.config.getint('default', 'rows'), 5)
        self.tilew, self.tileh = self.sx/self.gridx, self.sy/self.gridy
        self.grid_ratio = self.gridx/self.gridy
        self.adjacent_tiles = []
        self.use_ai = True

        if self.grid_ratio >= 1: 
            self.sy /= self.grid_ratio
            self.tileh /= self.grid_ratio
        else: 
            self.sx *= self.grid_ratio
            self.tilew *= self.grid_ratio

        self.bg = pygame.Surface([self.sx, self.sy])
        self.start = [[2,int(self.gridy/2)], [1,int(self.gridy/2)], [0,int(self.gridy/2)]]
        self.snek = Snek(self.start.copy(), (self.tilew, self.tileh), (self.gridx, self.gridy))
        self.apple_pos = self.get_apple_pos()
        self.high_score = 0

        pygame.display.set_caption("Snek | High Score: " + str(self.high_score))

        self.py = pygame.init()
        self.sc = pygame.display.set_mode((self.sx,self.sy))

        self.mainloop()

    def ai(self):
        h = self.snek.pdata[0]
        if self.gridy % 2 == 0:
            if self.start[0][1] % 2 == 0:
                if h[1] == 0: 
                    if h[0] == self.gridx-1: 
                        self.snek.new_facing = [0,1]
                    else: self.snek.new_facing = [1,0]
                elif h[1] == self.gridy-1:
                    if h[0] == 0:
                        self.snek.new_facing = [0,-1]
                    else: self.snek.new_facing = [-1,0]
                else:
                    if h[0] == self.gridx-2:
                        if self.snek.new_facing == [1,0]: self.snek.new_facing = [0,-1]
                        else: self.snek.new_facing = [-1,0]
                    if h[0] == 0:
                        if self.snek.new_facing == [-1,0]: self.snek.new_facing = [0,-1]
                        else: self.snek.new_facing = [1,0]
            else:
                if h[1] == 0: 
                    if h[0] == 0: 
                        self.snek.new_facing = [0,1]
                    else: self.snek.new_facing = [-1,0]
                elif h[1] == self.gridy-1:
                    if h[0] == self.gridx-1:
                        self.snek.new_facing = [0,-1]
                    else: self.snek.new_facing = [1,0]
                else:
                    if h[0] == self.gridx-2:
                        if self.snek.new_facing == [1,0]: self.snek.new_facing = [0,1]
                        else: self.snek.new_facing = [-1,0]
                    if h[0] == 0:
                        if self.snek.new_facing == [-1,0]: self.snek.new_facing = [0,1]
                        else: self.snek.new_facing = [1,0]
        else: pass

        

        
    def reset(self):
        score = len(self.snek.pdata) - 3
        if score > self.high_score: self.high_score = score 
        self.snek = Snek(self.start.copy(), (self.tilew, self.tileh), (self.gridx, self.gridy))
        self.apple_pos = self.get_apple_pos()
        pygame.display.set_caption("Snek | High Score: " + str(self.high_score))

    def get_apple_pos(self):
        x = random.randint(0, self.gridx-1)
        y = random.randint(0, self.gridy-1)

        i = 0
        while [x,y] in self.snek.pdata and i < self.gridx*self.gridy*1000:
            x = random.randint(0, self.gridx-1)
            y = random.randint(0, self.gridy-1)
            i += 1
        return [x,y]
    
    def apple(self):
        ap = pygame.Surface([int(self.tilew/2), int(self.tileh/2)])
        ap.fill('red')
        self.sc.blit(ap, [self.apple_pos[0]*self.tilew + int(self.tilew/4), self.apple_pos[1]*self.tileh + int(self.tileh/4)])

        if self.snek.pdata[0] == self.apple_pos: 
            self.apple_pos = self.get_apple_pos()
            self.snek.grow = True


    def draw_snek(self):
        self.snekBlock = pygame.Surface([self.tilew, self.tileh])
        for i in range(len(self.snek.pdata)):
            if i <= 40: 
                self.snekBlock.fill([0,255-5*i,0])
            else: self.snekBlock.fill([0,50,0])
            self.sc.blit(self.snekBlock, [self.tilew*self.snek.pdata[i][0], self.tileh*self.snek.pdata[i][1]])
        
        # self.snekBlock.fill('blue')
        # for t in self.adjacent_tiles:
        #     self.sc.blit(self.snekBlock, [self.tilew*t[0], self.tileh*t[1]])

    
    def draw_grid(self):
        for i in range(self.gridx+1):
            pygame.draw.line(self.sc, self.line_color, [i*self.tilew, 0], [i*self.tilew, self.sy])
        
        for i in range(self.gridy+1):
            pygame.draw.line(self.sc, self.line_color, [0, i*self.tileh], [self.sx, i*self.tileh])
        
    def mainloop(self):
        while self.running == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
            
            # Logic goes here
            self.frame += 1
            if self.snek.dead == True: 
                self.reset()
            else:
                self.snek.snek_input()
                if self.frame % (int(self.fps/self.pfps)) == True: 
                    if self.use_ai == True:
                        self.ai()
                    self.sc.blit(self.bg, [0,0])
                    self.draw_grid()
                    self.snek.update()
                    self.apple()
                    self.draw_snek()
            

            pygame.display.update()
            self.clock.tick(self.fps)

class Snek():
    def __init__(self, pdata:list, blockSize:tuple[int,int], gridSize:tuple[int,int]) -> None:
        self.facing = [1,0]
        self.new_facing = self.facing
        self.blockSize = blockSize
        self.pdata = pdata
        self.gridx, self.gridy = gridSize
        self.grow = False
        self.dead = False
    
    def snek_input(self):
        if pygame.key.get_pressed()[pygame.K_UP]:
            if self.facing != [0,1]: self.new_facing = [0,-1]
        elif pygame.key.get_pressed()[pygame.K_DOWN]:
            if self.facing != [0,-1]: self.new_facing = [0,1]
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            if self.facing != [-1,0]: self.new_facing = [1,0]
        elif pygame.key.get_pressed()[pygame.K_LEFT] :
            if self.facing != [1,0]: self.new_facing = [-1,0]
    
    def update(self):
        self.facing = self.new_facing
        self.pdata.insert(0, [self.pdata[0][0]+self.facing[0],self.pdata[0][1]+self.facing[+1]])
        
        if self.grow == True:
            self.grow = False
        else: self.pdata.pop()
            
        # Check for overlaps
        if len(self.pdata) != len(set([str(i) for i in self.pdata])): 
            self.dead = True

        # Check bounds
        elif self.pdata[0][0] >= self.gridx or self.pdata[0][0] < 0:
            self.dead = True
        elif self.pdata[0][1] >= self.gridy or self.pdata[0][1] < 0:
            self.dead = True
      
SnekWindow()