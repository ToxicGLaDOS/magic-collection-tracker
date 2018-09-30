import json, mtgsdk, re


class RequestFormatter(object):
    def __init__(self):
        self.page = 1
        self.cards = []
        self.search_type = None
        self.search_for = None

    

    # Takes in the raw text from the user and formats a search query to mtgsdk
    def search(self, text):
        pattern = re.compile(r'(name|mc|rarity|text):(.*)',re.IGNORECASE)
        match_obj = re.match(pattern, text)
        search_type = match_obj.group(1)
        search_for = match_obj.group(2)
        self.search_type = search_type
        self.search_for = search_for
        self.get_cards()
        return self.cards
        
    
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

    @staticmethod
    def load_image_from_server(self, card):
        print(f"Downloading {card.name} from server.")
        response = requests.get(card.image_url)
        img = Image.open(BytesIO(response.content))
        save_sprite(img, card.multiverse_id)
        data = load_sprite(card.multiverse_id)
        return data
        
    