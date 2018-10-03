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
from tkinter.filedialog import askopenfilename, asksaveasfilename
import ntpath


class Application(object):
    def __init__(self):
        self.requester = Requester()
        self.window = Tk()
        self.window.title("MTG Collection Tracker")
        self.tab_control = ttk.Notebook(self.window)

        # create a toplevel menu
        menubar = Menu(self.window)
        filemenu = Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Save", command=self.save_collection)
        filemenu.add_command(label="Save as", command=self.save_collection_as)
        filemenu.add_command(label="Open", command=self.open_collection)
        filemenu.add_command(label="New", command=self.new_collection)
        # display the menu
        self.window.config(menu=menubar)


       

        self.window.mainloop()
    
    def save_collection(self):
        active_tab_name = self.tab_control.select()
        active_tab = self.tab_control.nametowidget(active_tab_name)

        # If the collection has a file_path we save to that file path
        # otherwise we use the "save as" saving
        if active_tab.collection.file_path:
            active_tab.collection.save()
        else:
            self.save_collection_as()
            
        

    def save_collection_as(self):
        file_path = asksaveasfilename(title='Save as', defaultextension='.json')
        active_tab_name = self.tab_control.select()
        active_tab = self.tab_control.nametowidget(active_tab_name)
        active_tab.collection.save_as(file_path)

        file_name = ntpath.basename(file_path)
        file_name_no_extension = os.path.splitext(file_name)[0]

        self.tab_control.tab(active_tab, text=file_name_no_extension)

    def new_collection(self):
        self.new_card_viewer_tab(CollectionData())
    
    def open_collection(self):
        file_path = askopenfilename(initialdir = "~/",title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
        file_name = ntpath.basename(file_path)
        file_name_no_extension = os.path.splitext(file_name)[0]

        collection = CollectionData(file_path=file_path)

        self.new_card_viewer_tab(collection, file_name_no_extension)
    
        
        
    
    def new_card_viewer_tab(self, collection, title='New Collection'):
        # Main tab
        new_tab = CardViewer(self.tab_control, collection, height=700, background='bisque')
        self.tab_control.add(new_tab, text=title)
        self.tab_control.grid(column=2,row=0,sticky=W+E)
        
        # Label
        checkbox_label = Label(self.window, text='Edit')
        checkbox_label.grid(column=0, row=0)

        # Checkbox
        checkbox = Checkbutton(self.window)
        checkbox.grid(column=1,row=0, sticky=W)

        # Text entry
        self.txt_entry = Entry(self.window, width=100)
        self.txt_entry.grid(column=2,row=1, sticky=S)

        # Search button
        search_button = Button(self.window, text='Search', command=lambda:new_tab.load_cards(self.txt_entry.get()))
        search_button.grid(column=3,row=1)

    

class CardFrame(Frame):
    def __init__(self, master, card, image, collection, **kwargs):
        super().__init__(master, class_='Card Frame', **kwargs)
        self.image = image
        width = self.image.width()
        height = self.image.height()
        self.card_data = card
        self.collection = collection
        self.canvas = Canvas(self, width=width, height=height, background='green')

        self.canvas.create_image(0, 0, image=image, anchor=NW)

        self.canvas.pack()

        self.popup_menu = Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Add to collection",
                                    command=self.add_to_collection)
        self.popup_menu.add_command(label="Remove from collection",
                                    command=self.remove_from_collection)


        self.popup_menu.bind("<Leave>", self.__leave)
        self.canvas.bind("<Button-3>", self.__popup)
    
    def __leave(self, event):
        self.popup_menu.unpost()

    def __popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()
    
    def add_to_collection(self):
        self.collection.add_card(self.card_data)
    
    def remove_from_collection(self):
        self.collection.remove_card(self.card_data)
        
class CardViewer(Frame):
    card_size = (223, 310)
    def __init__(self, master, collection_data, height=300, **kwargs):
        super().__init__(master, class_='Card Viewer', **kwargs)
        self.columns = 3
        self.requester = Requester()
        self.scrollable_canvas = Canvas(self, height=height, background='red')
        self.exterior_frame = Frame(self.scrollable_canvas, background='blue')
        self.scrollbar = Scrollbar(self, orient='vertical', command=self.scrollable_canvas.yview)
        self.scrollable_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.collection = collection_data
        # This is just here to keep references to prevent garbage collection
        self.images = []
        
        # Geometry managment
        self.scrollable_canvas.pack(side=LEFT,anchor=E)
        self.exterior_frame.pack(fill=BOTH)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Put exterior_frame in the canvas
        self.scrollable_canvas.create_window((0,0), window=self.exterior_frame, anchor=NW)

        # Bind on scroll
        self.exterior_frame.bind("<Configure>", self.__on_scroll)

    def set_images_with_path(self, img_paths, cards):
        self.images = self.__make_images_from_path(img_paths)
        self.__update_images(self.images, cards)


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
        self.set_images_with_path(paths, cards)

        # Download the ones that need to be downloaded
        self.requester.async_download_images(cards_to_download)
        # Load the new images
        self.__load_new_images()
        
    def __on_scroll(self, event):
        canvas = self.scrollable_canvas
        # we resize the canvas so that it fits the amount of cards dictated by self.columns
        canvas.configure(scrollregion=canvas.bbox("all"), width=self.exterior_frame.winfo_width())

    def __load_new_images(self):
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
            self.after(20, self.__load_new_images)

    def __update_images(self, images, cards):
        for index, image in enumerate(images):
            self.__update_image(index, image, cards[index])
            
    def __update_image(self, index, image, card):
        column = index % self.columns
        row = index // self.columns
        
        self.images[index] = image

        card_frame = CardFrame(self.exterior_frame, card, image, self.collection, width=CardViewer.card_size[0], height=CardViewer.card_size[1], background='purple')
        #card_frame = Frame(self.exterior_frame, width=CardViewer.card_size[0], height=CardViewer.card_size[1])
        #canvas.create_image(0, 0, image=image, anchor='nw')
        card_frame.grid(column=column, row=row, padx=5, pady=5)

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
    Application()


