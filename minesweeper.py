import pygame
import os, sys
import random

# create config or setting for this bullshit
SCREEN_WIDTH:int = 260
SCREEN_HEIGHT:int = 260

# COLORS
COLOR_WHITE:tuple = (255,255,255)
COLOR_BLACK:tuple = (20, 20, 40)

# SPRITES
SPRITE_SIZE:int = 16


class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert()


    def image_at(self, rectangle, colorkey = None):
        """Load a specific image from a specific rectangle."""
        # Loads image from x, y, x+offset, y+offset.
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if (colorkey != None):
            if (colorkey == -1):
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey = None):
        """Load a whole bunch of images and return them as a list."""
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, colorkey = None):
        """Load a whole strip of images, and return them as a list."""
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)
  

class Cell:
    def __init__(self, starting_image, start_x=0, start_y=0) -> None:
        self.image = starting_image
        self.x = start_x
        self.y = start_y
        self.is_bomb = False
        self.is_flagged = False
        self.is_revealed = True
        

class MineField:
    def __init__(self, field_width, field_height, bomb_limit, sprite_number_imgs):
        self.width = field_width
        self.height = field_height
        self.bomb_limit = bomb_limit
        self.sn_imgs = sprite_number_imgs
        
        self.cells = self.create_cell_2d_array()
        self.create_random_bombs()
        self.create_number_cells()


    def create_cell_2d_array(self) -> list:
        cell_2d_array = [[Cell(self.sn_imgs[1], col, row) for row in range(self.width)] for col in range(self.height)]
        return cell_2d_array

    def create_random_bombs(self) -> None:
        for i in range(self.bomb_limit):
            rand_x = random.randrange(self.width)
            rand_y = random.randrange(self.height)            
            rand_cell = self.cells[rand_x][rand_y]
            rand_cell.is_bomb = True
            rand_cell.image = self.sn_imgs[5]
    
    def create_number_cells(self) -> None:
        ##top mid: (x,y-1)
        ##top left: (x-1, y-1)
        ##top right: (x+1, y-1)
        ##mid left: (x-1, y)
        ##mid right: (x+1, y)
        ##bot left: (x-1, y+1)
        #bot mid: (x, y+1)
        #bot right: (x+1, y+1)
        sprite_size_number_offset = 6
        for r in range(self.width):
            for c in range(self.height):
                number = 0
                if (self.cells[r][c].is_bomb == False):
                    try:
                        if (self.cells[r][c-1].is_bomb):
                            number += 1
                        if (self.cells[r-1][c-1].is_bomb):
                            number += 1
                        if (self.cells[r+1][c-1].is_bomb):
                            number += 1
                        if (self.cells[r-1][c].is_bomb):
                            number += 1
                        if (self.cells[r+1][c].is_bomb):
                            number += 1
                        if (self.cells[r-1][c].is_bomb):
                            number += 1
                        if (self.cells[r-1][c+1].is_bomb):
                            number += 1
                        if (self.cells[r][c+1].is_bomb):
                            number += 1
                        if (self.cells[r+1][c+1].is_bomb):
                            number += 1
                    except IndexError:
                        pass

                if number < 0 or number > 15: 
                    print(f"Number too small or too big --> {number}")
                    
                if (number > 0):
                    self.cells[r][c].image = self.sn_imgs[7+number]
                    #self.cells[r][c].image = self.sn_imgs[7+sprite_size_number_offset]

    
    
        
class Game:
    def __init__(self) -> None:
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('* Mine-Sweeper! *')
        self.clock = pygame.time.Clock()    
        self.FPS:int = 60
        pygame.init()
        self.spritesheet = SpriteSheet("assets/2000.png")
        self.sprite_imgs = self.spritesheet.load_strip(pygame.Rect(0, 0, SPRITE_SIZE, SPRITE_SIZE), 8)
        self.number_imgs = self.spritesheet.load_strip(pygame.Rect(0, SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE), 8)
        self.sprites = self.sprite_imgs + self.number_imgs
        self.grid = MineField(SPRITE_SIZE, SPRITE_SIZE, 40, self.sprites)
         
    def start(self) -> None:
        self.running = True
        while (self.running):
            self.clock.tick(self.FPS)
            self.update()
            self.events()
        
                
        
    def update(self) -> None:
        self.window.fill(COLOR_BLACK)
        
        for r in range(len(self.grid.cells)):
            for c in range(len(self.grid.cells[r])):
                cell = self.grid.cells[r][c]
                self.window.blit(cell.image, (cell.x*SPRITE_SIZE, cell.y*SPRITE_SIZE))
        
        pygame.display.update()
    
    def events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.click_pos = pygame.mouse.get_pos()
                print(self.click_pos)
        


game = Game()
game.start()

pygame.quit()
sys.exit()