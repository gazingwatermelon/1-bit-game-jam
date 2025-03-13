import pygame
import sys
import random
import tilemap
import math

from utils import load_image, load_images, Animation

class Game:
    def __init__(self):
        pygame.init()

        #setting screen
        pygame.display.set_caption('Winter Run')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        self.movement = [False, False]

        self.assets = {
            'ground_tile': load_image("tiles/0.png"),
            'player_running' : load_images("player/running"),
            'player_standing' : load_images("player/standing"),
            'player_jump' : load_images("player/jump"),
            'small_snow' : load_image("decor/small_snow.png"),
            'large_snow': load_image("decor/large_snow.png"),
            'tree':  load_image("decor/tree.png"),
            'animal' : load_image("animals/jumper/jumper_1.png"),
            'numbers': load_images("numbers")
        }
        
        self.map = []
        self.player_pos = [50, 50]
        self.player = pygame.Rect(self.player_pos, (9, 16))
        self.offset = 1
        self.scroll = [0, 0]
        self.floor_depth = 192
        self.gravity = 4
        self.player_up = False
        
        

    def run(self):
        count = 0

        snow = []
        decor = []
        enemies = []
        self.map = tilemap.fill_map(self.floor_depth, self.assets['ground_tile'], self.map)
        while True:

            self.display.fill((0, 0, 0))

            #player running animation
            self.display.blit(self.assets['player_running'][(count//5)%3], self.player_pos)

            #Score_system
            score = str(count//6)
            for i in range(len(score)):
                self.display.blit(self.assets['numbers'][int(score[i])], (10 + 8*i, 10))

            #setting ground tiles
            
            for tile in self.map:
                left = tile[0].left - int(self.scroll[0])
                if(left>-16):
                    self.display.blit(tile[1], (tile[0].left - int(self.scroll[0]), tile[0].top))
                else:
                    tile[0].left += 352
                    self.display.blit(tile[1], (tile[0].left - int(self.scroll[0]), tile[0].top))

            if(count%random.randint(30, 40)==0):
                for i in range(5):
                    pos = random.randint(int(self.scroll[0]),500+int(self.scroll[0]))
                    type = random.randint(0,1)
                    snow.append([[pos, -5], type])

            snow = [part for part in snow if part[0][1] < self.floor_depth]

            #display snow
            for part in snow:
                
                if part[0][1]<self.floor_depth:
                    part[0][1] += 1
                    if part[1] == 0:
                        self.display.blit(self.assets['small_snow'], (part[0][0]-int(self.scroll[0])+math.cos(count)*0.01, part[0][1]-0.5))
                    else:
                        self.display.blit(self.assets['large_snow'], (part[0][0]-int(self.scroll[0])+math.cos(count)*0.01, part[0][1]-0.5))
            
            #set position of decor
            if random.random() * 100 > 80 and count%16==0:
                decor.append([(352+self.scroll[0]), self.floor_depth-16])
            
            decor[:] = [d for d in decor if d[0] - int(self.scroll[0]) > -16]

            #display decor
            for dec in decor:
                if(dec[0]-int(self.scroll[0])>-16):
                    self.display.blit(self.assets['tree'], (dec[0]-int(self.scroll[0]), dec[1]))

            if(count%random.randint(30, 40)==0):
                    pos = random.randint(0, self.floor_depth-16)
                    enemies.append(pygame.Rect(352+int(self.scroll[0]*1.5), pos, 9, 16))

            enemies[:] = [animal for animal in enemies if animal.x - int(self.scroll[0] * 1.5) > -16]

            for animal in enemies:        
                self.display.blit(self.assets['animal'], (animal.x-int(self.scroll[0]*1.5), animal.y+math.cos(count//10)*3))
                rect = pygame.Rect(animal.x-int(self.scroll[0]*1.5), animal.y+math.cos(count//10)*3, 9, 16)
                if self.player.colliderect(rect):
                    pause = True
                    while pause:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_P:
                                    pause = False


            if self.player_up == False:
                self.player_pos[1] += self.gravity
            else:
                self.player_pos[1] -= 2
            self.player.x = self.player_pos[0]
            self.player.y = self.player_pos[1]
            if count%300==0 and self.offset < 2.5:
                self.offset += 0.5
            
            
            self.scroll[0] += self.offset
            count+=1
            if(self.player_pos[1]+16>=self.floor_depth):
                self.player_pos[1] = self.floor_depth-16

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.player_up = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.player_up = False

            self.display_2.blit(self.display, (0, 0))
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)



Game().run()