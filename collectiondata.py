import json,os


class CollectionData(object):
    def __init__(self):
        # For now assume the file is stored in this dir
        self.file_dir = "../collection/"

        
        
        

    # Adds a card to the collection
    def __add__(self, other):
        pass
    
    # Removes a card from the collection
    def __sub__(self, other):
        pass
    
    def save(self):
        try:
            os.makedirs(self.file_dir)
        except OSError as error:
            if error.errno != 17:  # File exists
                raise
        print(os.listdir(self.file_dir))
        # If the file doesn't exist than create it (assuming it's called collection-data.json)
        if "collection-data.json" not in os.listdir(self.file_dir):
            print("created file")
            file = open(os.path.join(self.file_dir,"collection-data.json"), 'w')
            file.close()


    

    


