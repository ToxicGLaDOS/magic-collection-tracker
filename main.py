#!/usr/bin/env python3

# Main program file.
# Main drawing loop handled in this file.
# Event queue is processed in this file.


import pygame
pygame.init()
import sys,requests,os
from PIL import Image
from io import BytesIO
from collectiondata import CollectionData
from requestformatter import RequestFormatter
from ui import *
from cache import save, save_sprite, load, load_sprite, sprite_in_cache



class Application(object):
    
    def __init__(self, width, height):
        self.cd = CollectionData()
        self.rf = RequestFormatter()
        self.screen = pygame.display.set_mode(size)
        self.sprites = pygame.sprite.Group()
        self.page_layout = PageLayout(100, 10, width-100, height-50-10)
        self.main()

    def main(self):
        ui_elements = self.make_ui_objects(self.screen.get_rect())
        self.cd.save()
        while 1:
            # Events phase
            self.handle_events(ui_elements)
            
            # Update phase
            for element in ui_elements:
                element.update()
            for sprite in self.sprites:
                sprite.update()




            # Draw phase
            self.screen.fill((40,40,40))
            for element in ui_elements:
                element.draw(self.screen)
            
            self.page_layout.draw(self.screen)
            self.sprites.draw(self.screen)
            pygame.display.flip()


    def handle_events(self, ui_elements):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            for element in ui_elements:
                element.handle_event(event)

    def make_ui_objects(self, rect):
        objs = []
        screen_width, screen_height = self.screen.get_size()
        objs.append(InputBox(5, screen_height-50-5, 400, 50, font_size=32, listeners=[self.load_card_page]))
        objs.append(Button(         0,       rect.height // 2, 100, 100, "./scr_images/red_arrow.png", on_clicks=[self.page_layout.prev_page], flip=True))
        objs.append(Button(rect.width - 100, rect.height // 2, 100, 100, "./scr_images/red_arrow.png", on_clicks=[self.page_layout.next_page]))
        return objs
    
    # Bound to return key on text box
    def load_card_page(self, text):
        # Get cards that match the search
        cards = self.rf.search(text)
        # For each card save it to cache
        sprites = []
        for card in cards:
            if card.multiverse_id != None:
                # If the sprite isn't in the cache
                if not sprite_in_cache(card.multiverse_id):
                    print(f"Downloading {card.name} from server.")
                    response = requests.get(card.image_url)
                    img = Image.open(BytesIO(response.content))
                    save_sprite(img, card.multiverse_id)
                    data = load_sprite(card.multiverse_id)
                    sprites.append(CardSprite(0,0,100,100,data["path"]))
                # If the sprite is in the cache
                else:
                    data = load_sprite(card.multiverse_id)
                    sprites.append(CardSprite(0,0,100,100,data["path"]))
        self.page_layout.set_sprites(sprites)
        self.page_layout.set_images(sprites)







if __name__ == "__main__":    
    size = width, height = 1000, 1000
    Application(width, height)


