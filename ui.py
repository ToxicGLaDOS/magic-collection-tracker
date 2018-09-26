import pygame as pg


class InputBox(object):
    ALLOWED_KEYS = ["listeners", "font_size", "active_color", "inactive_color"]
    KWARG_DEFAULTS = {
            "listeners": [], 
            "text": '',
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
    

class CardSprite(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path):
        pg.sprite.Sprite.__init__(self)
        
        self.image = pg.image.load(image_path)
        self.rect = pg.rect.Rect(x,y,width,height)

    def update(self):
        pass



