#!/usr/bin/env python3

# Main program file.
# Main drawing loop handled in this file.
# Event queue is processed in this file.


import sys,requests,os
from PIL import ImageTk
import PIL.Image
from io import BytesIO
from collectiondata import CollectionData
from requester import Requester
import datetime
from cache import save, save_sprite, load, load_sprite, sprite_in_cache
import mtgsdk
from itertools import groupby
import multiprocessing
from tkinter import *
from tkinter import ttk



class Application(object):
    def __init__(self):
        self.requester = Requester()
        window = Tk()
        window.title("MTG Collection Tracker")
        tab_control = ttk.Notebook(window)

        self.tab_explore = CardViewer(tab_control, background='bisque')
        tab_control.add(self.tab_explore, text='Explore')
        tab_control.grid(sticky=W+E)
        
        self.txt_entry = Entry(window, width=100)
        self.txt_entry.grid(column=0,row=1, sticky=S)

        search_button = Button(window, text='Search', command=lambda:self.tab_explore.load_cards(self.txt_entry.get()))
        search_button.grid(column=1,row=1)
        window.mainloop()
    

    

    

class CardViewer(Frame):
    card_size = (223, 310)
    def __init__(self, master, **kwargs):
        super().__init__(master, class_='Scroll Layout', **kwargs)
        self.columns = 3
        self.requester = Requester()
        self.scrollable_canvas = Canvas(self, background='red')
        self.exterior_frame = Frame(self.scrollable_canvas, background='blue')
        self.scrollbar = Scrollbar(self, orient='vertical', command=self.scrollable_canvas.yview)
        self.scrollable_canvas.configure(yscrollcommand=self.scrollbar.set)

        # This is just here to keep references to prevent garbage collection
        self.images = []
        
        self.scrollable_canvas.grid(column=0, row=0, sticky=N+E+S+W)
        self.exterior_frame.grid(sticky=N+E+S+W)
        self.scrollbar.grid(column=1, row=0, sticky=N+S)
        self.scrollable_canvas.create_window((0,0), window=self.exterior_frame, anchor='nw')
        self.exterior_frame.bind("<Configure>", self.on_scroll)

    def on_scroll(self, event):
        canvas = self.scrollable_canvas
        # we resize the canvas so that it fits the amount of cards dictated by self.columns
        canvas.configure(scrollregion=canvas.bbox("all"), width=self.exterior_frame.winfo_width())

    def set_images_with_path(self, img_paths):
        self.images = self.__make_images_from_path(img_paths)
        self.__update_images(self.images)

    def load_cards(self, search_text):
        cards_to_download = []
        # Get cards that match the search
        cards = self.requester.search(search_text)

        # Sort the results
        cards = sorted(cards, key=lambda card: card.name)
        temp_cards = []
        for key, group in groupby(cards, key=lambda x: x.name):
            temp_cards.extend(sorted(list(group), key=lambda card: datetime.datetime.strptime(Requester.get_set_release_date(card.set_name), '%Y-%m-%d')))
        cards = temp_cards

        paths = []
        for card in cards:
            print(f'loading card {card.name}')
            # For some reason some cards don't have multiverse ids?
            if card.multiverse_id != None:
                data = None
                if not sprite_in_cache(card.multiverse_id):
                    cards_to_download.append((len(paths), card))
                    data = dict(img_data=None, path='')
                else:
                    data = load_sprite(card.multiverse_id)
                
                if data['path']:
                    # Card with image
                    paths.append(data['path'])
                else:
                    # Blank card
                    paths.append('./scr_images/blank_card.png')

        # Update images
        self.set_images_with_path(paths)

        # Download the ones that need to be downloaded
        self.requester.async_download_images(cards_to_download)
        # Load the new images
        self.load_new_images()
        
    def load_new_images(self):
        if self.requester.has_results_in_list():
            results = self.requester.pop_async_results()
            for index, img_data, card_obj in results:
                image = self.__make_image_from_path(img_data['path'])
                self.__update_image(index, image)

        # I think in theory if the requester finishes it's last process right here
        # we could end up missing some of the cards because preforming_async_task will be false
        # but the data won't have been loaded yet... Maybe?

        # If it's still loading data than try again in 20ms
        if self.requester.preforming_async_task():
            self.after(20, self.load_new_images)

    def __update_images(self, images):
        for index, image in enumerate(images):
            self.__update_image(index, image)
            
    def __update_image(self, index, image):
        column = index % self.columns
        row = index // self.columns
        
        self.images[index] = image

        canvas = Canvas(self.exterior_frame, width=CardViewer.card_size[0], height=CardViewer.card_size[1])
        canvas.create_image(0, 0, image=image, anchor='nw')
        canvas.grid(column=column, row=row, padx=5, pady=5)

    def __make_image_from_path(self, path):
        pil_img = PIL.Image.open(path)
        pil_img = pil_img.resize(CardViewer.card_size, PIL.Image.ANTIALIAS)
        img = ImageTk.PhotoImage(pil_img)

        return img

    def __make_images_from_path(self, img_paths):
        images = []
        for path in img_paths:
            pil_img = PIL.Image.open(path)
            pil_img = pil_img.resize(CardViewer.card_size, PIL.Image.ANTIALIAS)
            images.append(ImageTk.PhotoImage(pil_img))
        
        return images


        

        
        




if __name__ == "__main__":    
    
    size = width, height = 1000, 1000
    Application()


