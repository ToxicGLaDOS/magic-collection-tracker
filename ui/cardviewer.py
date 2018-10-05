import datetime,  PIL.Image, mtgsdk
from tkinter import *
from tkinter import ttk
from itertools import groupby
from requester import Requester
from cache import save_sprite, load_sprite, sprite_in_cache
from PIL import ImageTk
from io import BytesIO

from random import choice
from string import ascii_letters

class CollectionManager(ttk.Notebook):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def add_card(self, card):
        
        active_tab_name = self.select()
        local_viewer = self.nametowidget(active_tab_name)
        print(f'add card {card.name} to tab {active_tab_name}')
        local_viewer.add_card(card)
    
    def remove_card(self, card):
        active_tab_name = self.select()
        local_viewer = self.nametowidget(active_tab_name)

        local_viewer.remove_card(card)

    def new_local_viewer_tab(self, collection, title='New collection'):
        # Main tab
        new_tab = LocalViewer(self, collection, self.remove_card, height=700, background='bisque')
        self.add(new_tab, text=title)

        new_tab.rowconfigure(0, weight=1)


        # Text entry
        txt_entry = Entry(new_tab, width=100)
        txt_entry.grid(column=0,row=1, sticky=S)

        # Search button
        search_button = Button(new_tab, text='Search', command=lambda:new_tab.search_cards(txt_entry.get()))
        search_button.grid(column=1,row=1)


class CardViewer(Frame):
    card_size = (223, 310)
    def __init__(self, master, searchable, height=300, class_='Card Viewer', **kwargs):
        super().__init__(master, class_=class_, **kwargs)
        self.columns = 3
        self.scrollable_canvas = Canvas(self, height=height, background='red')
        self.exterior_frame = Frame(self.scrollable_canvas, background='blue')
        self.scrollbar = Scrollbar(self, orient='vertical', command=self.scrollable_canvas.yview)
        self.scrollable_canvas.configure(yscrollcommand=self.scrollbar.set)

        # This is an instance of the requester class that is used to get sprites only
        self.requester = Requester()

        # This is an object with a search function. The search function should return a list of mtgsdk.Card objects
        self.searchable = searchable

        # This is just here to keep references to prevent garbage collection
        self.images = []
        
        self.columnconfigure(0, weight=1)

        # Geometry managment
        self.scrollable_canvas.grid(column=0, row=0, sticky=N+E+S+W)
        self.exterior_frame.pack(fill=BOTH, expand=True)
        self.scrollbar.grid(column=1,row=0, sticky=N+S+E)

        # Put exterior_frame in the canvas
        self.scrollable_canvas.create_window((0,0), window=self.exterior_frame, anchor=NW)

        # Bind on scroll
        self.exterior_frame.bind("<Configure>", self.__on_scroll)

    def set_images_with_path(self, img_paths, cards):
        self.images = self.__make_images_from_path(img_paths)
        self.update_images(self.images, cards)

    def search_cards(self, search_text):
        cards = self.searchable.search(search_text)
        self.load_cards(cards)

    def load_cards(self, cards):
        cards_to_download = []
        # Get cards that match the search

        cards = [card for card in cards if card.multiverse_id != None]

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
        assert(len(paths) == len(cards))
        # Update images
        self.set_images_with_path(paths, cards)

        # Download the ones that need to be downloaded
        self.requester.async_download_images(cards_to_download)
        # Load the new images
        self.__load_new_images()



    def update_image(self, index, image, card):
        raise NotImplementedError()
        
    def update_images(self, images, cards):
        """ Destroy all current images and load in new ones """
        for child in self.exterior_frame.winfo_children():
            child.destroy()
        for index, image in enumerate(images):
            self.update_image(index, image, cards[index])

    def __on_scroll(self, event):
        canvas = self.scrollable_canvas
        # we resize the canvas so that it fits the amount of cards dictated by self.columns
        canvas.configure(scrollregion=canvas.bbox("all"))

    def __load_new_images(self):
        if self.requester.has_results_in_list():
            results = self.requester.pop_async_results()
            for index, img_data, card_obj in results:
                image = self.__make_image_from_path(img_data['path'])
                self.update_image(index, image, card_obj)

        # I think in theory if the requester finishes it's last process right here
        # we could end up missing some of the cards because preforming_async_task will be false
        # but the data won't have been loaded yet... Maybe?

        # If it's still loading data than try again in 20ms
        if self.requester.preforming_async_task():
            self.after(20, self.__load_new_images)



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

class OnlineViewer(CardViewer):
    card_size = (223, 310)
    def __init__(self, master, searchable, add_card_callback, height=300, class_='Online Viewer', **kwargs):
        super().__init__(master, searchable, height=height, class_=class_, **kwargs)
        self.add_card_callback = add_card_callback
    
    def update_image(self, index, image, card):
        column = index % self.columns
        row = index // self.columns
        
        self.images[index] = image
        print(f'updating image for {card.name}')
        card_frame = OnlineCard(self.exterior_frame, card, image, self.add_card_callback, width=CardViewer.card_size[0], height=CardViewer.card_size[1], background='purple')
        card_frame.grid(column=column, row=row, padx=5, pady=5)

class LocalViewer(CardViewer):
    card_size = (223, 310)
    def __init__(self, master, collection, remove_card_callback, height=300, class_='Local Viewer', **kwargs):
        super().__init__(master, collection, height=height, class_=class_, **kwargs)
        self.remove_card_callback = remove_card_callback
        self.collection = collection
        self.update_from_collection()
        
    def add_card(self, card):
        self.collection.add_card(card)
        self.update_from_collection()
    
    def remove_card(self, card):
        self.collection.remove_card(card)
        self.update_from_collection()
    
    def update_from_collection(self):
        print(self.collection)
        collection_data = self.collection.get_collection_data()
        card_data = [card['card_data'] for card in collection_data]
        cards = []
        for card in card_data:
            c = mtgsdk.Card()
            c.__dict__.update(card)
            cards.append(c)
        print([card.name for card in cards])
        self.load_cards(cards)

    def update_image(self, index, image, card):
        column = index % self.columns
        row = index // self.columns
        
        self.images[index] = image
        print(f'updating image for {card.name}')
        num_owned = self.collection.num_owned(card)
        card_frame = LocalCard(self.exterior_frame, card, image, self.remove_card_callback, num_owned, width=CardViewer.card_size[0], height=CardViewer.card_size[1], background='purple')
        card_frame.grid(column=column, row=row, padx=5, pady=5)


class CardFrame(Frame):
    def __init__(self, master, card, image, **kwargs):
        super().__init__(master, class_='Card Frame', **kwargs)
        self.image = image
        width = self.image.width()
        height = self.image.height()
        self.card_data = card
        self.canvas = Canvas(self, width=width, height=height, background='green')

        self.canvas.create_image(0, 0, image=image, anchor=NW)

        self.canvas.pack(side=BOTTOM)

        self.popup_menu = Menu(self, tearoff=0)

        self.popup_menu.bind("<Leave>", self.__leave)
        self.canvas.bind("<Button-3>", self.__popup)
    
    def __leave(self, event):
        self.popup_menu.unpost()

    def __popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()


class OnlineCard(CardFrame):
    def __init__(self, master, card, image, callback, **kwargs):
        super().__init__(master, card, image, **kwargs)
        self.popup_menu.add_command(label="Add to collection",
                                    command=self.add_to_collection)
        
        self.callback = callback
                        
    
    def add_to_collection(self):
        self.callback(self.card_data)


class LocalCard(CardFrame):
    def __init__(self, master, card, image, callback, num_owned, **kwargs):
        super().__init__(master, card, image, **kwargs)
        self.popup_menu.add_command(label="Remove from collection",
                                    command=self.remove_from_collection)
        self.card = card
    
        self.callback = callback
        self.label = Label(self, text=f'In collection: {num_owned}')
        self.label.pack(side=TOP)

    def remove_from_collection(self):
        self.callback(self.card_data)