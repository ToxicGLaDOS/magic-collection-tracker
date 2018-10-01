import json, mtgsdk, re, requests
from PIL import Image
from io import BytesIO
from cache import save, save_sprite, load, load_sprite, sprite_in_cache

from multiprocessing import Pool

class Requester(object):
    def __init__(self):
        self.page = 1
        self.cards = []
        self.search_type = None
        self.search_for = None

        self.async_results = None
        self.pool = Pool(processes=4)
    

    # Takes in the raw text from the user and formats a search query to mtgsdk
    def search(self, text):
        pattern = re.compile(r'(name|mc|rarity|text):(.*)',re.IGNORECASE)
        match_obj = re.match(pattern, text)
        if match_obj:
            search_type = match_obj.group(1)
            search_for = match_obj.group(2)
            self.search_type = search_type
            self.search_for = search_for
            self.get_cards()
            return self.cards
        else:
            print('invalid search query')
            return []
        
    
    def get_cards(self):
        print(f"Searched {self.search_for}")
        if self.search_type == 'name':
            self.cards = mtgsdk.Card.where(name=self.search_for, page=self.page).all()
        elif self.search_type == 'mc':
            self.cards = mtgsdk.Card.where(mana_cost=self.search_for, page=self.page).all()
        elif self.search_type == 'rarity':
            self.cards = mtgsdk.Card.where(rarity=self.search_for, page=self.page).all()
        elif self.search_type == 'text':
            self.cards = mtgsdk.Card.where(original_text=self.search_for, page=self.page).all()

    def next_page(self):
        self.page += 1
        self.get_cards()
        return self.cards

    def preforming_async_task(self):
        if self.async_results:
            return not self.async_results.ready()
        else:
            return False
        
    def async_download_images(self, cards_to_download, app):
        self.async_results = self.pool.map_async(Requester.async_get_images, cards_to_download, callback=app.cards_downloaded)

    @staticmethod
    def load_image_from_server(card):
        print(f"Downloading {card.name} from server.")
        response = requests.get(card.image_url)
        img = Image.open(BytesIO(response.content))
        save_sprite(img, card.multiverse_id)
        data = load_sprite(card.multiverse_id)
        return data
    
    @staticmethod
    def async_get_images(data):
        """ Takes data and grabs the image from the internet
        :param data: Should be a tuple of format (index, Card)

        :return: (index, data, card_data) where data = {img_data:a PIL image, path:path_to_image} """
        index = data[0]
        card_data = data[1]

        img_data = Requester.load_image_from_server(card_data)

        return (index, img_data, card_data)

        
    