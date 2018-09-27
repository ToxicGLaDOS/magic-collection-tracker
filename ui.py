import pygame as pg


class InputBox(object):
    ALLOWED_KEYS = ["listeners", "font_size", "active_color", "inactive_color"]
    KWARG_DEFAULTS = {
            "listeners": [], 
            "text": 'Lightning Bolt',
            "font_size": 32,
            "active_color": pg.Color('dodgerblue2'),
            "inactive_color": pg.Color('lightskyblue3')
        }
        
    def __init__(self, x, y, height, width, **kwargs):
        # Set all the attributes that appear in KWARG_DEFAULTS to this class
        # Example: if font_size=15 is passed in self.font_size will be 15
        # however if foo="abc" is passed in than nothing will be set
        for (arg, default) in [(key, value) for (key, value) in InputBox.KWARG_DEFAULTS.items() if key in InputBox.KWARG_DEFAULTS.keys()]:
            setattr(self, arg, kwargs.get(arg, default))

        self.font = pg.font.Font(None, self.font_size)
        self.rect = pg.Rect(x, y, height, width)
        self.color = self.inactive_color
        self.txt_surface = self.font.render(self.text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.active_color if self.active else self.inactive_color
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    # Call each listener and give it self.text
                    for listener in self.listeners:
                        listener(self.text)
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)
    
    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width
    
    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pg.draw.rect(screen, self.color, self.rect, 2)


class PageLayout(object):
    def __init__(self, x, y, width, height, sprites=[]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sprites = sprites
        self.active_group = pg.sprite.Group()
        self.padding=10
        self.x_fit = None
        self.y_fit = None
        self.first_showing = 0
        self.last_showing = 0
        self.set_images(sprites)

        
    def set_images(self, sprites, start_index=0):
        self.active_group = pg.sprite.Group()
        if len(sprites) - start_index > 0:
            sprite_rect = sprites[0].rect
            self.x_fit = int(self.width / (sprite_rect.width + self.padding * 2))
            self.y_fit = int(self.height / (sprite_rect.height + self.padding * 2))
            self.first_showing = self.last_showing = start_index
            

            x_index = y_index = 0
            for sprite_index in range(min(self.x_fit * self.y_fit, len(sprites) - start_index)):
                cur_sprite = sprites[start_index + sprite_index]
                x_index = sprite_index % self.x_fit
                y_index = sprite_index // self.x_fit

                cur_sprite.rect.x = self.x + self.padding * (x_index+1) + sprite_rect.width * (x_index)
                cur_sprite.rect.y = self.y + self.padding * (y_index+1) + sprite_rect.height * (y_index)
                
                self.active_group.add(cur_sprite)

                
                self.last_showing += 1
            
    def set_sprites(self, sprites):
        self.sprites = sprites

    def next_page(self):
        if self.last_showing != len(self.sprites):
            self.set_images(self.sprites, self.last_showing)

    def prev_page(self):
        if self.first_showing - (self.x_fit * self.y_fit) >= 0:
            self.set_images(self.sprites, self.first_showing - (self.x_fit * self.y_fit))



    def draw(self, surface):
        self.active_group.draw(surface)
        
class Button(object):
    def __init__(self, x, y, width, height, img_path, on_clicks=[], flip=False):
        self.rect = pg.rect.Rect(x, y, width, height)
        self.image = pg.transform.scale(pg.image.load(img_path).convert_alpha(), (width, height))
        if flip:
            self.image = pg.transform.flip(self.image, True, False)
        self.on_clicks = on_clicks
    
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                for on_click in self.on_clicks:
                    on_click()

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        pass

class CardSprite(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path):
        pg.sprite.Sprite.__init__(self)
        
        self.image = pg.image.load(image_path)

        self.rect = self.image.get_rect()
        

    def update(self):
        pass



