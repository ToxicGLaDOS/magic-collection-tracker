import json,os
from mtgsdk import Card
from searchparser import SearchParser

class CollectionData(object):
    default_collection = {'collection':[]}
    def __init__(self, file_path=''):
        
        self.file_path = file_path

        self.collection_data = self.open_collection_data(file_path)

    def search(self, text):
        """ Gets a list of cards based on the text.
        :param text: The text used to search the collection
        :return: A list of mtgsdk.Card objects that match the search. """
        search_dict = SearchParser.get_dict(text)
        cards = []
        for card_data in self.collection_data['collection']:
            # Pull out the card data
            card_dict = card_data['card_data']
            # If all of the search parameters appear in their respective locations for this card
            # then we need to add it to the cards list
            if all([search_dict[key].lower() in card_dict[key].lower() for key in search_dict.keys()]):
                # Make a card object
                card = Card()
                card.__dict__.update(card_dict)

                cards.append(card)
        print(f'cards found in collection: {[card.name for card in cards]}')
        return cards


    # Adds a card to the collection
    def add_card(self, card):
        """ Adds one card from the collection. If the card already exists in the collection it adds one to owned. 

        `card` Should be a mtgsdk.Card type. Will throw error otherwise

        :param card: The card to add."""
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
        """ Removes one card from the collection. If the card doesn't exist in the collection it does nothing. 

        `card` Should be a mtgsdk.Card type. Will throw error otherwise

        :param card: The card to add."""
        if type(card) != Card:
            raise ValueError("You must only remove Cards types from your collection.")

        # Grabs the multiverse_id value from all the cards in the collection
        # TODO : This can probably be cache instead of calculated every time we add a card if it becomes too slow to iterate through them all
        cards = [card['card_data']['multiverse_id'] for card in self.collection_data['collection']]
        if card.multiverse_id in cards:
            index = cards.index(card.multiverse_id)
            self.collection_data['collection'][index]['collection_data']['owned']-= 1
            
            if self.collection_data['collection'][index]['collection_data']['owned'] <= 0:
                self.collection_data['collection'].pop(index)


    def num_owned(self,card):
        """ Gets the number of owned cards with the same multiverse_id as the given card.
        :param card: The card to check.
        :return: The number of cards of this type that are owned in the collection. """
        if type(card) != Card:
            raise ValueError("You must only remove Cards types from your collection.")

        mid = card.multiverse_id

        cards = [card['card_data']['multiverse_id'] for card in self.collection_data['collection']]

        if mid in cards:
            index = cards.index(mid)
            return self.collection_data['collection'][index]['collection_data']['owned']
        else:
            return '0'

    
    def save_as(self, file_path):
        """ Save the collection data to disk as file_path
        :return: None """
        with open(file_path, 'w') as f:
            f.write(json.dumps(self.collection_data))
        self.file_path = file_path
    
    def save(self):
        """ Save the collection data to disk as the file given to __init__
        :return: None """
        assert(self.file_path != '')
        with open(self.file_path, 'w') as f:
            f.write(json.dumps(self.collection_data))
    
    def open_collection_data(self, file_path):
        """ Get the data from disk.
        :return: The data as a json style set of dicts and list. If no file exists then returns a default value."""
        # If the file doesn't exist
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            return CollectionData.default_collection
    
    def get_collection_data(self):
        return self.collection_data['collection']




    

    


