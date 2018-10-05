import datetime,  PIL.Image
from tkinter import *
from tkinter import ttk
from itertools import groupby
from requester import Requester
from cache import save_sprite, load_sprite, sprite_in_cache
from PIL import ImageTk
from io import BytesIO


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
        self.__update_images(self.images, cards)


    def load_cards(self, search_text):
        cards_to_download = []
        # Get cards that match the search
        cards = self.searchable.search(search_text)

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
        canvas.configure(scrollregion=canvas.bbox("all"), width=self.winfo_width())

    def __load_new_images(self):
        if self.requester.has_results_in_list():
            results = self.requester.pop_async_results()
            for index, img_data, card_obj in results:
                image = self.__make_image_from_path(img_data['path'])
                self.__update_image(index, image, card_obj)

        # I think in theory if the requester finishes it's last process right here
        # we could end up missing some of the cards because preforming_async_task will be false
        # but the data won't have been loaded yet... Maybe?

        # If it's still loading data than try again in 20ms
        if self.requester.preforming_async_task():
            self.after(20, self.__load_new_images)

    def __update_images(self, images, cards):
        """ Destroy all current images and load in new ones """
        for child in self.exterior_frame.winfo_children():
            child.destroy()
        for index, image in enumerate(images):
            self.update_image(index, image, cards[index])
            
    def update_image(self, index, image, card):
        raise NotImplementedError()

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
    def __init__(self, master, searchable, remove_card_callback, collection, height=300, class_='Local Viewer', **kwargs):
        super().__init__(master, searchable, height=height, class_=class_, **kwargs)
        self.remove_card_callback = remove_card_callback
        self.collection = collection
        
    def update_image(self, index, image, card):
        column = index % self.columns
        row = index // self.columns
        
        self.images[index] = image
        print(f'updating image for {card.name}')
        card_frame = OnlineCard(self.exterior_frame, card, image, self.remove_card_callback, width=CardViewer.card_size[0], height=CardViewer.card_size[1], background='purple')
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

        self.canvas.pack()

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
    def __init__(self, master, card, image, **kwargs):
        super().__init__(master, card, image, **kwargs)
        self.popup_menu.add_command(label="Remove from collection",
                                    command=self.remove_from_collection)
    
        self.callback = callback


    def remove_from_collection(self):
        self.callback(self.card_data)