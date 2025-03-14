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
            'numbers': load_images("numbers"),
            'coin' : load_image("addons/coin_0.png"),
            'star': load_image("addons/star.png")
        }

        self.sfx = {
            'coin' : pygame.mixer.Sound('data/sfx/coin_3.mp3'),
            'thruster': pygame.mixer.Sound(r'data\sfx\thruster\thruster_3.mp3'),
            'background': pygame.mixer.Sound(r'data\sfx\backgroud\background_1.mp3')
        }

        self.sfx['coin'].set_volume(0.5)
        self.sfx['thruster'].set_volume(0.4)
        
        self.map = []
        self.player_pos = [50, 50]
        self.player = pygame.Rect(self.player_pos, (9, 16))
        self.offset = 1
        self.scroll = [0, 0]
        self.floor_depth = 192
        self.gravity = 4
        self.player_up = True
        f = open("log.txt", "r+")
        text = f.read()
        if(text==""):
            f.write("Highscore: 0")
        
        f.seek(0)
        text = f.read().strip()
        self.highscore = int(text.split(":")[1])
        

    def run(self):
        count = 0
        num = 0
        snow = []
        decor = []
        enemies = []
        coins = []
        self.map = tilemap.fill_map(self.floor_depth, self.assets['ground_tile'], self.map)

        
        pygame.mixer.music.load(r'data\sfx\backgroud\background_8.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        running  = True
        while True:
            self.display.fill((0, 0, 0))

            #player running animation
            if self.player_up == False:
                self.display.blit(self.assets['player_running'][(count//5)%3], self.player_pos)
            else:
                if self.movement[1] == True:
                    self.display.blit(self.assets['player_jump'][(count//5)%3], self.player_pos)
                else:
                    self.display.blit(self.assets['player_jump'][0], self.player_pos)

            #Score system
            score = str(count//6 + num*30)
            for i in range(len(score)):
                self.display.blit(self.assets['numbers'][int(score[i])], (10 + 8*i, 10))

            money = str(num)
            self.display.blit(self.assets['coin'], (10, 30))
            for i in range(len(money)):
                self.display.blit(self.assets['numbers'][int(money[i])], (20 + 8*i, 32))

            if int(score)>int(self.highscore):
                self.highscore = score

            self.display.blit(self.assets['star'], (10, 50))
            for i in range(len(str(self.highscore))):
                self.display.blit(self.assets['numbers'][int(str(self.highscore)[i])], (30 + 8*i, 54))

            #Coin system
            if(count%random.randint(30, 40)==0):
                    pos = random.randint(0, self.floor_depth-16)
                    coins.append([pygame.Rect(352+int(self.scroll[0]), pos, 8, 12), True])

            coins[:] = [coin for coin in coins if coin[0].x - int(self.scroll[0]) > -16]

            for coin in coins:
                if coin[1] == True: 
                    self.display.blit(self.assets['coin'], (coin[0].x-int(self.scroll[0]), coin[0].y))
                rect = pygame.Rect(coin[0].x-int(self.scroll[0]), coin[0].y, 8, 12)
                if self.player.colliderect(rect):
                    if(coin[1]==True):
                        num+=1
                        pygame.mixer.Channel(0).play(self.sfx['coin'])
                    coin[1] = False

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

            #setting enemy positions at random
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
                        count = 0
                        num = 0
                        self.map = []
                        snow = []
                        decor = []
                        enemies = []
                        coins = []
                        self.player = pygame.Rect(self.player_pos, (9, 16))
                        self.player_pos = [50, 50]
                        self.offset = 1
                        self.scroll = [0, 0]
                        self.clock = pygame.time.Clock()
                        self.movement = [False, False]
                        self.player_up = False
                        self.map = tilemap.fill_map(self.floor_depth, self.assets['ground_tile'], self.map)
                        self.sfx['background'].stop()
                        self.sfx['thruster'].stop()
                        pygame.mixer.music.stop()

                        # updating highscore
                        f = open("log.txt", "r+")
                        f.seek(11)
                        f.write(str(self.highscore))

                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_p:
                                    pause = False
                                    pygame.mixer.music.play(-1)


            if self.movement[1] == False:
                self.player_pos[1] += self.gravity
                self.sfx['thruster'].stop()
            else:
                self.player_pos[1] -= 2
                self.sfx['thruster'].play()
            self.player.x = self.player_pos[0]
            self.player.y = self.player_pos[1]
            if count%300==0 and self.offset < 2.5:
                self.offset += 0.5
            
            
            self.scroll[0] += self.offset
            count+=1
            if(self.player_pos[1]+16>=self.floor_depth):
                self.player_pos[1] = self.floor_depth-16
                self.player_up = False
            
            #ensring player does not go above seal
            if self.player_pos[1]<=-2:
                self.player_pos[1] = -2

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.movement[1] = True
                        self.player_up = True

                    #Pause system if escape is pressed
                    if event.key == pygame.K_ESCAPE:
                        if running == True:
                            running = False
                        while not running:
                            self.movement[1] = False
                            # menu = pygame.Surface()
                            pygame.mixer.music.stop()
                            self.sfx['thruster'].stop()
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_ESCAPE:
                                        running = True
                                        pygame.mixer.music.play(-1)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[1] = False

            self.display_2.blit(self.display, (0, 0))
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)



Game().run()