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
from requester import Requester
from ui import *
import datetime
from cache import save, save_sprite, load, load_sprite, sprite_in_cache
import mtgsdk
from itertools import groupby
import multiprocessing


class Application(object):
    
    def __init__(self, width, height):
        self.cd = CollectionData()
        self.rf = Requester()
        self.sets = mtgsdk.Set.all()
        self.screen = pygame.display.set_mode(size,pygame.RESIZABLE)
        self.sprites = pygame.sprite.Group()
        self.pool = multiprocessing.Pool(processes=4)
        page_layout = PageLayout(100, 10, width-100, height-50-10)
        left_button = Button(         0,       height // 2, 100, 100, img_path="./scr_images/red_arrow.png", on_clicks=[page_layout.prev_page], flip=True)
        right_button = Button(width - 100, height // 2, 100, 100, img_path="./scr_images/red_arrow.png", on_clicks=[page_layout.next_page])
        self.tab_layout = TabLayout(0,0,width,height-50, 
                            tabs={"explore":[page_layout, left_button, right_button], 
                            "collection":[PageLayout(100, 10, width-100, height-50-10)],
                            })
        self.main()

    def main(self):
        ui_elements = self.make_ui_objects(self.screen.get_rect())
        while 1:
            # Events phase
            self.handle_events(ui_elements)
            
            # Update phase
            for element in ui_elements:
                element.update()
            for sprite in self.sprites:
                sprite.update()

            # If there are results in the requester then we pop them out and load em up in the pagelayout
            if self.rf.has_results_in_list():
                self.change_page_layout_sprites(self.rf.pop_async_results())


            # Draw phase
            self.screen.fill((40,40,40))
            for element in ui_elements:
                element.draw(self.screen)
            
            self.tab_layout.draw(self.screen)
            #self.page_layout.draw(self.screen)
            #self.sprites.draw(self.screen)
            pygame.display.flip()


    def handle_events(self, ui_elements):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.cleanup()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.cleanup()
            if event.type == pygame.VIDEORESIZE:
                width,height = event.size
                self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                self.tab_layout.set_rect(pygame.rect.Rect(0, 0, width, height-50))

            for element in ui_elements:
                element.handle_event(event)

            
            
            self.tab_layout.handle_event(event)

    def cleanup(self):
        self.cd.save()
        sys.exit()

    def make_ui_objects(self, rect):
        objs = []
        screen_width, screen_height = self.screen.get_size()
        objs.append(InputBox(5, screen_height-50-5, 400, 50, font_size=32, listeners=[self.load_card_page]))
        return objs
    
    def get_set_release_date(self, set_name):
        for magic_set in self.sets:
            if magic_set.name == set_name:
                return magic_set.release_date

    def create_card_layout(self, sprite):
        # On click methods will be added after layout is made
        left_button = Button(0, 0, 100, 100, img_path='./scr_images/minus.png', on_clicks=[])
        right_button = Button(0, 0, 100, 100, img_path='./scr_images/plus.png', on_clicks=[])

        layout = CardLayout(0, 0, sprite, left_button, right_button, self.cd)

        left_button.add_on_click(layout.remove_card)
        right_button.add_on_click(layout.add_card)
        return layout



    def change_page_layout_sprites(self, layout_data):
        """ Takes the results of an asyncronous download and swaps layouts in the page layout
        :param layouts: A list of the information to create new layouts with elements of this form: (index, img_data, card_data)
        :return: None """
        # This will fail if we change tabs inbetween calls to this function
        tab_children = self.tab_layout.get_active_tab_elements()
        for child in tab_children:
            if type(child) == PageLayout:
                for l_data in layout_data:
                    index = l_data[0]
                    data = l_data[1]
                    card_data = l_data[2]
                    sprite = CardSprite(card_data, data["path"])
                    layout = self.create_card_layout(sprite)
                    child.swap_layout(index, layout)
        
                child.set_layouts(start_index=child.first_showing)
            

    # Bound to return key on text box
    def load_card_page(self, text):
        cards_to_download = []
        # Get cards that match the search
        cards = self.rf.search(text)
        cards = sorted(cards, key=lambda card: card.name)
        temp_cards = []
        for key, group in groupby(cards, key=lambda x: x.name):
            temp_cards.extend(sorted(list(group), key=lambda card: datetime.datetime.strptime(self.get_set_release_date(card.set_name), '%Y-%m-%d')))
        cards = temp_cards

        # For each card save it to cache
        layouts = []
        for card in cards:
            print(f'loading card {card.name}')
            # For some reason some cards don't have multiverse ids?
            if card.multiverse_id != None:
                data = None
                if not sprite_in_cache(card.multiverse_id):
                    cards_to_download.append((len(layouts), card))
                    data = dict(img_data=None, path='')
                else:
                    data = load_sprite(card.multiverse_id)
                
                if data['path']:
                    # Card with image
                    sprite = CardSprite(card, data["path"])
                else:
                    # Blank card
                    sprite = CardSprite(card)

                layout = self.create_card_layout(sprite)

                layouts.append(layout)

        active_tab_elements = self.tab_layout.get_active_tab_elements()
        
        # If any of the elements are PageLayouts than set there images up with what we found
        for element in active_tab_elements:
            if type(element) == PageLayout:

                element.layouts = layouts
                element.set_layouts()


        self.rf.async_download_images(cards_to_download, self)






if __name__ == "__main__":    
    size = width, height = 1000, 1000
    Application(width, height)


