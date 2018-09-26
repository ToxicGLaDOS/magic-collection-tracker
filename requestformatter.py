import json, mtgsdk

from cache import load, load_sprite, load_cache


class RequestFormatter(object):
    def __init__(self):
        pass
    
    # Takes in the raw text from the user and formats a search query to mtgsdk
    def search(self, text):

        print(f"Searched {text}")
        # For now we just assume you're looking for a card title
        return mtgsdk.Card.where(name=text).all()