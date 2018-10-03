import re

class SearchParser(object):

    @staticmethod    
    def get_dict(text):
        d = {}

        # Looks for one of the things to search for then colon then a non-greedy anything and then either comma or end of string
        pattern = re.compile(r'(name|cmc|rarity|text):(.*?)(,|$)',re.IGNORECASE)
        matches = re.findall(pattern, text)
        for search_for, data, _ in matches:
            # Remove leading and trailing white space that might have gotten picked up in the wildcard
            data = data.strip()
            # For some reason the API calls mythic cards "special" for rarity
            if search_for == 'rarity' and data == 'mythic':
                data = 'special'
            d[search_for] = data
        
        return d


if __name__ == "__main__":
    text = input("Input some text to search: ")
    print(SearchParser.get_dict(text))

        
    
