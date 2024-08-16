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
        self.fps = 60
        self.pfps = min(self.config.getint('default', 'fps'), self.fps/2) 
        self.clock = pygame.time.Clock()
        self.frame = 0
        self.line_color = [50,0,0]
        
        
        # Game vars
        self.gridx, self.gridy = max(self.config.getint('default', 'cols'), 5) , max(self.config.getint('default', 'rows'), 5)
        self.tilew, self.tileh = self.sx/self.gridx, self.sy/self.gridy
        self.grid_ratio = self.gridx/self.gridy
        self.adjacent_tiles = []
        self.use_ai = self.config.getboolean('default', 'useai')
        self.paused = False
        self.accept_pause_input = True

        # Quick move allows for the player to immediately move the Snek head, rather than wait for the next frame
        #   Makes the game feel smoother
        self.quick_move = False   
        self.can_quick_move = True 

        # Calculate the height/width ratio so that non-square grids can be rendered properly 
        if self.grid_ratio >= 1: 
            self.sy /= self.grid_ratio
            self.tileh /= self.grid_ratio
        else: 
            self.sx *= self.grid_ratio
            self.tilew *= self.grid_ratio

        self.bg = pygame.Surface([self.sx, self.sy])

        # Start coords. Index 0 is the Snek's head. Reused on respawn
        self.start = [[2,int(self.gridy/2)], [1,int(self.gridy/2)], [0,int(self.gridy/2)]]
        self.snek = Snek(self.start.copy(), (self.tilew, self.tileh), (self.gridx, self.gridy))
        
        self.apple_pos = self.get_apple_pos()
        self.score = 0
        self.high_score = 0

        pygame.display.set_caption("Snek | High Score: " + str(self.high_score) + " | Score: " + str(self.score))

        self.py = pygame.init()
        self.sc = pygame.display.set_mode((self.sx,self.sy)) # Main Screen

        self.mainloop()

    def ai(self):
        # Chase tail in zigzag pattern to win. Doesn't work on grids with odd area because of how graph circuits work
        #   well, a similar strategy could be 50/50 to win on an odd grid, but I don't care to implement it
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
        # Set high score
        if self.score > self.high_score: 
            self.high_score = self.score 
        pygame.display.set_caption("Snek | High Score: " + str(self.high_score) + " | Score: 0")

        # Respawn Snek
        self.snek = Snek(self.start.copy(), (self.tilew, self.tileh), (self.gridx, self.gridy))

        # Get new apple pos
        self.apple_pos = self.get_apple_pos()
        

    def get_apple_pos(self):
        # Try to return a random coordinate for the next apple. If it's under the Snek, recalculate until a valid position is found
        x = random.randint(0, self.gridx-1)
        y = random.randint(0, self.gridy-1)

        i = 0
        while [x,y] in self.snek.pdata and i < self.gridx*self.gridy*1000:
            # If under Snek, recalculate for awhile
            x = random.randint(0, self.gridx-1)
            y = random.randint(0, self.gridy-1)
            i += 1
        return [x,y]
    
    def apple(self):
        # apple img
        ap = pygame.Surface([int(self.tilew/1.5), int(self.tileh/1.5)])
        ap.fill('red')

        # draw apple
        self.sc.blit(ap, [self.apple_pos[0]*self.tilew + int(self.tilew/4), self.apple_pos[1]*self.tileh + int(self.tileh/4)])

        # check if Snek has eaten apple
        if self.snek.pdata[0] == self.apple_pos: 
            self.apple_pos = self.get_apple_pos()
            self.snek.grow = True
            self.score = len(self.snek.pdata) - 2
            pygame.display.set_caption("Snek | High Score: " + str(self.high_score) + " | Score: " + str(self.score))

    def draw_snek(self):
        self.snekBlock = pygame.Surface([self.tilew, self.tileh])
        for i in range(len(self.snek.pdata)):
            if i <= 40: 
                self.snekBlock.fill([0,255-5*i,0])
            else: self.snekBlock.fill([0,50,0])
            self.sc.blit(self.snekBlock, [self.tilew*self.snek.pdata[i][0], self.tileh*self.snek.pdata[i][1]])
    
    def draw_grid(self):
        for i in range(self.gridx+1):
            pygame.draw.line(self.sc, self.line_color, [i*self.tilew, 0], [i*self.tilew, self.sy])
        
        for i in range(self.gridy+1):
            pygame.draw.line(self.sc, self.line_color, [0, i*self.tileh], [self.sx, i*self.tileh])
        
    def mainloop(self):
        while self.running == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False

            # pause 
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                if self.accept_pause_input == True: self.paused = not self.paused ; self.accept_pause_input = False
            else: self.accept_pause_input = True
            
            if self.paused == False:
                self.frame += 1
                if self.snek.dead == False: 
                    if self.can_quick_move:
                        self.quick_move = self.snek.snek_input()
                    else: self.snek.snek_input() ; self.quick_move = False
                
                    if self.frame % (int(self.fps/self.pfps)) == 0 or (self.quick_move and self.frame): 
                        # if can_quickmove is false, the player has jumped on an off frame, and we don't want to update
                        #  if we did, the play would jump forward whenever they pressed a movement key
                        if self.can_quick_move == True:
                            if self.use_ai == True:
                                self.ai()
                            self.sc.blit(self.bg, [0,0])
                            self.draw_grid()
                            self.snek.update()
                            self.apple()
                            self.draw_snek()

                            if self.quick_move:
                                self.quick_move = False
                                self.can_quick_move = False
                                self.frame = 1 # Reset frame to ensure move timing is consistent
                                
                        else: self.can_quick_move = True
                else: self.reset() # Reset if Snek is dead
                self.clock.tick(self.fps)
            pygame.display.update()

class Snek():
    def __init__(self, pdata:list, blockSize:tuple[int,int], gridSize:tuple[int,int]) -> None:
        self.facing = [1,0]
        self.new_facing = self.facing
        self.blockSize = blockSize
        self.pdata = pdata
        self.gridx, self.gridy = gridSize
        self.grow = False
        self.dead = False
    
    def snek_input(self) -> bool:
        # Return True if move 
        if pygame.key.get_pressed()[pygame.K_UP]:
            if self.facing != [0,1]: self.new_facing = [0,-1] ; return True
        elif pygame.key.get_pressed()[pygame.K_DOWN]:
            if self.facing != [0,-1]: self.new_facing = [0,1] ; return True
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            if self.facing != [-1,0]: self.new_facing = [1,0] ; return True
        elif pygame.key.get_pressed()[pygame.K_LEFT] :
            if self.facing != [1,0]: self.new_facing = [-1,0] ; return True
        return False
    
    def update(self):
        # Movement pops from tail and inserts at new front
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