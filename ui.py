import pygame as pg
from preciserect import PreciseRect

class UIElement(object):
    def handle_event(self, event):
        pass
    
    def draw(self, surface):
        pass
    
    def set_rect(self, new_rect):
        pass

class Layout(UIElement):
    pass





class InputBox(UIElement):
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
        self.rect = PreciseRect(x, y, width, height)
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

    def set_rect(self, new_rect):
        self.rect = new_rect


class PageLayout(Layout):
    def __init__(self, x, y, width, height, sprites=[]):
        self.rect = PreciseRect(x, y, width, height)
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
        x,y = self.rect.topleft
        width, height = self.rect.size
        if len(sprites) - start_index > 0:
            sprite_rect = sprites[0].rect
            self.x_fit = int(width / (sprite_rect.width + self.padding * 2))
            self.y_fit = int(height / (sprite_rect.height + self.padding * 2))
            self.first_showing = self.last_showing = start_index
            

            x_index = y_index = 0
            for sprite_index in range(min(self.x_fit * self.y_fit, len(sprites) - start_index)):
                cur_sprite = sprites[start_index + sprite_index]
                x_index = sprite_index % self.x_fit
                y_index = sprite_index // self.x_fit

                cur_sprite.rect.x = x + self.padding * (x_index+1) + sprite_rect.width * (x_index)
                cur_sprite.rect.y = y + self.padding * (y_index+1) + sprite_rect.height * (y_index)
                
                self.active_group.add(cur_sprite)

                
                self.last_showing += 1
            
    def set_sprites(self, sprites):
        self.sprites = sprites

    def next_page(self, button):
        if len(self.sprites) > 0 and self.last_showing != len(self.sprites):
            self.set_images(self.sprites, self.last_showing)

    def prev_page(self, button):
        # len(self.sprites) > 0 shortcircuits the if statements so we don't crash if self.x_fit/self.y_fit are None
        if len(self.sprites) > 0 and self.first_showing - (self.x_fit * self.y_fit) >= 0:
            self.set_images(self.sprites, self.first_showing - (self.x_fit * self.y_fit))

    def draw(self, surface):
        self.active_group.draw(surface)

    def set_rect(self, new_rect):
        self.rect = new_rect
        self.set_images(self.sprites, self.first_showing)




class Text(UIElement):
    def __init__(self, x, y, width, height, text=""):
        self.rect = PreciseRect(x, y, width, height)
        self.text = text
        self.font_size = 32
        self.font = pg.font.Font(None, self.font_size)
        self.color = pg.Color('dodgerblue2')
        self.txt_surface = self.font.render(self.text, True, self.color)        
    
    def draw(self, surface):
        surface.blit(self.txt_surface, (self.rect.x, self.rect.y))

    def set_rect(self, new_rect):
        self.rect = new_rect

class TabLayout(Layout):
    def __init__(self, x, y, width, height, tabs={}):
        self.rect = PreciseRect(x, y, width, height)
        self.tab_height = 30
        self.tab_width = 100
        self.tabs = tabs
        self.tab_buttons = []
        self.active_tab = list(tabs.keys())[0]
        
        self.set_child_rects(pg.rect.Rect(0, self.tab_height, width, height))

        for index,tab in enumerate(self.tabs.keys()):
            self.tab_buttons.append(Button(x + index * self.tab_width, y, self.tab_width, self.tab_height, text=tab, on_clicks=[self.change_tab]))

    def change_tab(self, tab):
        self.active_tab = tab.text.text

    def get_active_tab_elements(self):
        return self.tabs[self.active_tab]

    def draw(self, surface):
        # Draw the data in a tab
        for element in self.tabs[self.active_tab]:
            element.draw(surface)
        # Draw the tab buttons
        for tab_button in self.tab_buttons:
            tab_button.draw(surface)
    
    def handle_event(self, event):
        for element in self.tabs[self.active_tab]:
            element.handle_event(event)
        
        for tab_button in self.tab_buttons:
            tab_button.handle_event(event)

    def set_rect(self, new_rect):
        self.set_child_rects(new_rect)
        self.rect = new_rect

    def set_child_rects(self, new_rect):
        """ Sets the rect of child objects based on new_rect
            :param new_rect_: The new rect that the TabLayout will have. This is not the new rect of the children 
            """
        x_diff = new_rect.x - self.rect.x
        y_diff = new_rect.y - self.rect.y
        
        width,height = self.rect.size
        for elements in self.tabs.values():
            width_diff = (new_rect.width - self.rect.width) / len(elements)
            height_diff = (new_rect.height - self.rect.height) / len(elements)

            x_sorted = sorted(elements, key=lambda e : e.rect.x)
            y_sorted = sorted(elements, key=lambda e : e.rect.y)

            for element in elements:
                # This is the new rect for the child
                # We use the x_sorted/y_sorted stuff to slide over content that would be blocked by something being scaled up
                child_rect = PreciseRect(
                             element.rect.precise_x + x_diff + x_sorted.index(element) * width_diff,
                             element.rect.precise_y + y_diff + y_sorted.index(element) * height_diff,
                             element.rect.precise_width + width_diff,
                             element.rect.precise_height + height_diff)
                element.set_rect(child_rect)

                



class Button(UIElement):
    def __init__(self, x, y, width, height, img_path=None, on_clicks=[], flip=False, text=''):
        self.rect = PreciseRect(x, y, width, height)

        self.flip = flip
        # If there is an image than load it and if the flip flag is set than flip it
        # Otherwise set self.image to None
        
        if img_path:
            self.orig_image = pg.image.load(img_path)
            self.image = pg.transform.scale(self.orig_image.convert_alpha(), (width, height))
            if flip:
                self.image = pg.transform.flip(self.image, True, False)
        else:
            self.orig_image = None
            self.image = None
        
        # If there is text than make a text object
        # otherwise don't
        if text:
            self.text = Text(x, y, width, height, text=text)
        else:
            self.text = None
        
        self.on_clicks = on_clicks
    
    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                print('clicked')
                for on_click in self.on_clicks:
                    on_click(self)
                    

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (self.rect.x, self.rect.y))
        if self.text:
            self.text.draw(surface)
        
        pg.draw.rect(surface, pg.Color('dodgerblue2'), self.rect, 2)


    def update(self):
        pass

    def set_rect(self, new_rect):
        self.rect = new_rect
        if new_rect.width >= 0 and new_rect.height >= 0:
            if self.image:
                self.image = pg.transform.scale(self.orig_image, (self.rect.size))
                if self.flip:
                    self.image = pg.transform.flip(self.image, True, False)

class CardSprite(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path):
        pg.sprite.Sprite.__init__(self)
        
        self.image = pg.image.load(image_path)

        self.rect = self.image.get_rect()
        

    def update(self):
        pass



