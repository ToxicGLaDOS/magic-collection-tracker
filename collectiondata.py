import json,os


class CollectionData(object):
    def __init__(self):
        # For now assume the file is stored in this dir
        self.file_dir = "./"
        # If the file doesn't exist than create it (assuming it's called collection-data.json)
        if "collection-data.json" not in os.listdir(self.file_dir):
            open("collection-data.json", 'w')

    # Adds a card to the collection
    def __add__(self, other):
        pass
    
    # Removes a card from the collection
    def __sub__(self, other):
        pass


    

    


