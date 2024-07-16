import pygame
import os, sys
import random
import ctypes

# create config or setting for this bullshit
SCREEN_WIDTH:int = 513
SCREEN_HEIGHT:int = 513

# COLORS
COLOR_WHITE:tuple = (255,255,255)
COLOR_BLACK:tuple = (20, 20, 40)

# SPRITES
SPRITE_SIZE:int = 32
BOMB_AMOUNT:int = 40

def MessageBox(title, text, style):
    style_num = 0
    style = style.lower()
    if style == 'ok':
        style_num = 0
    elif style == 'ok_cancel':
        style_num = 1
    elif style == 'retry_abort':
        style_num = 2
    elif style == 'yes_no_cancel':
        style_num = 3
    elif style == 'yes_no':
        style_num = 4
    elif style == 'retry_cancel':
        style_num = 5
    elif style == 'continue':
        style_num = 6

    return ctypes.windll.user32.MessageBoxW(0, text, title, style_num)


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
    def __init__(self, sprite_images, start_x=0, start_y=0) -> None:
        self.x = start_x
        self.y = start_y
        self.sprites = sprite_images
        self.image = self.sprites[0]
        self.rect = self.create_collide_box()
        self.is_bomb = False
        self.is_flagged = False
        self.is_revealed = False
        self.state = '0'
        self.left_handled = False
        self.right_handled = False

    def create_collide_box(self) -> object:
        box_x = self.x*SPRITE_SIZE 
        box_y = self.y*SPRITE_SIZE
        return pygame.Rect(box_x, box_y, SPRITE_SIZE, SPRITE_SIZE)


    def get_mouse(self, pos):
        left_action = False
        right_action = False

        if self.rect.collidepoint(pos):
            if (pygame.mouse.get_pressed()[0] == True) and (self.is_flagged == False) and (self.left_handled == False):
                self.left_handled = True
                left_action = True

            if (pygame.mouse.get_pressed()[2] == True) and (self.is_revealed == False) and (self.right_handled == False):
                self.right_handled = True
                right_action = True

        if pygame.mouse.get_pressed()[0] == False:
            self.left_handled = False

        if pygame.mouse.get_pressed()[2] == False:
            self.right_handled = False

        return left_action, right_action

    

class MineField:
    def __init__(self, field_width, field_height, bomb_limit, sprite_imgs):
        self.width = field_width
        self.height = field_height
        self.bomb_limit = bomb_limit
        self.sn_imgs = sprite_imgs
        
        self.cells = self.create_cell_2d_array()
        self.bombs = self.create_random_bombs()
        self.flags = []
        self.update()


    def create_cell_2d_array(self) -> list:
        cell_2d_array = [[Cell(self.sn_imgs, row, col) for row in range(self.width)] for col in range(self.height)]
        return cell_2d_array

    def create_random_bombs(self) -> list:
        bomb_list = []
        for i in range(self.bomb_limit):
            rand_x = random.randrange(self.width)
            rand_y = random.randrange(self.height)            
            rand_cell = self.cells[rand_x][rand_y]
            rand_cell.is_bomb = True
            rand_cell.state = 'x'
            bomb_list.append(rand_cell)
        return bomb_list


    def reveal_bombs(self, sprite_index=5):
        for bomb_cell in self.bombs:
            bomb_cell.is_revealed = True
            bomb_cell.image = self.sn_imgs[sprite_index]
            


    def check_neighbor_states(self, row, col) -> None:
        neighbor_bomb_count = 0
        cell = self.cells[row][col]
        if (cell.is_bomb == True):
            return

        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                i = row + x_offset
                j = col + y_offset
                if (i > -1 and i < self.width and j > -1 and j < self.height):
                    neighbor = self.cells[i][j]
                    if (neighbor.is_bomb):
                        neighbor_bomb_count += 1
                    if (cell.is_revealed and not neighbor.is_bomb):
                        if (cell.state == '0'):
                            neighbor.is_revealed = True

                if (neighbor_bomb_count > 0):
                    cell.state = str(neighbor_bomb_count)


    def handle_mouse(self, cell):
        pos = pygame.mouse.get_pos()
        LB_clicked, RB_clicked = cell.get_mouse(pos)
        if LB_clicked:
            cell.is_revealed = True
        elif RB_clicked:
            if cell.is_flagged == True:
                cell.is_flagged = False
            elif cell.is_flagged == False:
                cell.is_flagged = True



    def update_sprite(self, cell):
        sprite_index = 0
        if cell.is_revealed:
            if cell.is_bomb:
                sprite_index = 6
            else:
                if cell.state == '0':
                    sprite_index = 1
                else:
                    sprite_index = 7+int(cell.state)
        else:
            if cell.is_flagged == True:
                sprite_index = 2
                if cell not in self.flags:
                    self.flags.append(cell)

            elif cell.is_flagged == False:
                if cell in self.flags:
                    self.flags.remove(cell)

        cell.image = self.sn_imgs[sprite_index]



    def update(self) -> None:
        sprite_size_number_offset = 6
        for row in range(self.width):
            for col in range(self.height):
                cell = self.cells[row][col]
                self.check_neighbor_states(row, col)
                self.update_sprite(cell)
                self.handle_mouse(cell)
 


        
class Game:
    def __init__(self) -> None:
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Mine-Sweeper!')
        self.clock = pygame.time.Clock()    
        self.FPS:int = 60
        pygame.init()
        self.spritesheet = SpriteSheet("assets/fiorito-2000.png")
        self.sprite_imgs = self.spritesheet.load_strip(pygame.Rect(0, 0, 16, 16), 8)
        self.number_imgs = self.spritesheet.load_strip(pygame.Rect(0, 16, 16, 16), 8)
        self.sprites = self.sprite_imgs + self.number_imgs
        self.grid = MineField(16, 16, BOMB_AMOUNT, self.sprites)
         

    def start(self) -> None:
        self.running = True
        while (self.running):
            self.clock.tick(self.FPS)
            self.grid.update()
            self.update()
            self.events()
            win_check = self.check_bombs()
            if win_check == 1:
                self.grid.reveal_bombs(7)
                self.update()
                MessageBox('Minesweeper', 'You Win!', 'ok')
                while self.running: 
                    self.events()
            elif win_check == -1:
                self.grid.reveal_bombs(6)
                self.update()
                MessageBox('Minesweeper', 'You Lose!', 'ok')
                while self.running: 
                    self.events()

        

    def check_bombs(self):
        flag_count = 0
        for i in range(len(self.grid.bombs)):
            cell = self.grid.bombs[i]
            if (cell.is_revealed):
                return -1

            if (cell.is_flagged):
                flag_count += 1

        if (len(self.grid.bombs) == flag_count):
            return True

        return False

    def update(self) -> None:
        self.window.fill(COLOR_BLACK)
        for r in range(self.grid.width):
            for c in range(self.grid.height):
                cell = self.grid.cells[r][c]
                scaled_img = pygame.transform.scale(cell.image, (SPRITE_SIZE, SPRITE_SIZE))
                self.window.blit(scaled_img, (cell.x*SPRITE_SIZE, cell.y*SPRITE_SIZE))
                #pygame.draw.rect(self.window, (255, 0, 0), cell.create_collide_box(), 1)
        pygame.display.update()

        


    def events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        


game = Game()
game.start()
pygame.quit()
sys.exit()