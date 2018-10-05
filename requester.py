import json, mtgsdk, re, requests
from searchparser import SearchParser
from PIL import Image
from io import BytesIO
from cache import save, save_sprite, load, load_sprite, sprite_in_cache

from multiprocessing import Pool, Manager, Process

class Requester(object):
    sets = mtgsdk.Set.all()
    def __init__(self):
        self.page = 1
        self.search_type = None
        self.search_for = None

        #self.async_results = None
        #self.pool = Pool(processes=4)

        self.processes = []
        self.manager = Manager()
        self.async_results = self.manager.list()

    

    # Takes in the raw text from the user and formats a search query to mtgsdk
    def search(self, text):
        kwargs = SearchParser.get_dict(text)
        return mtgsdk.Card.where(**kwargs).all()

    def preforming_async_task(self):
        for process in self.processes:
            if process.is_alive():
                return True
        
        return False

    def has_results_in_list(self):
        return len(self.async_results) > 0
    
    def pop_async_results(self):
        return_list = []
        for result in self.async_results:
            return_list.append(self.async_results.pop(0))
        return return_list
        
    def async_download_images(self, cards_to_download):
        for card in cards_to_download:
            p = Process(target=Requester.async_get_images, args=(card, self.async_results))
            self.processes.append(p)
            p.start()

    @staticmethod
    def get_set_release_date(set_name):
        for magic_set in Requester.sets:
            if magic_set.name == set_name:
                return magic_set.release_date

    @staticmethod
    def load_image_from_server(card):
        print(f"Downloading {card.name} from server.")
        response = requests.get(card.image_url)
        img = Image.open(BytesIO(response.content))
        save_sprite(img, card.multiverse_id)
        data = load_sprite(card.multiverse_id)
        return data
    
    @staticmethod
    def async_get_images(data, return_list):
        """ Takes data and grabs the image from the internet
        :param data: Should be a tuple of format (index, Card)

        :return: (index, img_data, card_data) where data = {img_data:a PIL image, path:path_to_image} """
        index = data[0]
        card_obj = data[1]

        img_data = Requester.load_image_from_server(card_obj)
        
        return_data = (index, img_data, card_obj)
        return_list.append(return_data)

        
    