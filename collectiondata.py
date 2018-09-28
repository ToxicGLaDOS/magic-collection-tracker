import json,os
from mtgsdk import Card


class CollectionData(object):
    default_collection = {'collection':[]}
    def __init__(self):
        self.file_dir = "../collection"
        # For now assume the file is stored in this dir
        self.file_path = os.path.join(self.file_dir,"collection-data.json")

        self.collection_data = self.open_collection_data()

        
        

    # Adds a card to the collection
    def add_card(self, card):
        if type(card) != Card:
            raise ValueError("You must only add Cards types to your collection.")

        # Grabs the multiverse_id value from all the cards in the collection
        # TODO : This can probably be cache instead of calculated every time we add a card if it becomes too slow to iterate through them all
        cards = [card['card_data']['multiverse_id'] for card in self.collection_data['collection']]

        # If this card appears in the collectoin add one to the owned field
        # otherwise add it to the collection with 1 owned
        if card.multiverse_id in cards:
            index = cards.index(card.multiverse_id)
            self.collection_data['collection'][index]['collection_data']['owned'] += 1
        else:
            # This is a default version of what a card's data is
            default_card_data = {'card_data':card.__dict__, 'collection_data':{'owned':1}}
            self.collection_data['collection'].append(default_card_data)

    # Removes a card from the collection
    def remove_card(self, card):
        if type(card) != Card:
            raise ValueError("You must only remove Cards types from your collection.")

        # Grabs the multiverse_id value from all the cards in the collection
        # TODO : This can probably be cache instead of calculated every time we add a card if it becomes too slow to iterate through them all
        cards = [card['card_data']['multiverse_id'] for card in self.collection_data['collection']]
        print(card.__dict__)
        if card.multiverse_id in cards:
            index = cards.index(card.multiverse_id)
            if self.collection_data['collection'][index]['collection_data']['owned'] >= 0:
                self.collection_data['collection'][index]['collection_data']['owned']-= 1

    def num_owned(self,card):
        if type(card) != Card:
            raise ValueError("You must only remove Cards types from your collection.")

        mid = card.multiverse_id

        cards = [card['card_data']['multiverse_id'] for card in self.collection_data['collection']]

        if mid in cards:
            index = cards.index(mid)
            return self.collection_data['collection'][index]['collection_data']['owned']
        else:
            return '0'

    
    def save(self):
        self.make_path()
        with open(self.file_path, 'w') as f:
            f.write(json.dumps(self.collection_data))
    
    def open_collection_data(self):
        self.make_path()
        # If the file doesn't exist
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        else:
            return CollectionData.default_collection


    def make_path(self):
        try:
            os.makedirs(self.file_dir)
        except OSError as error:
            if error.errno != 17:  # File exists
                raise


    

    


