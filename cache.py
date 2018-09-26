# Thanks to pokebase for a lot of the ideas behind this cacheing code
import shelve, os

API_CACHE = None
IMAGE_CACHE = None

def get_default_cache():
    xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or \
                        os.path.join(os.path.expanduser('~'), '.cache')

    return os.path.join(xdg_cache_home,'magic-collection-tracker')


# I dont' think this is going to work but i'll keep it around for now
def save(data, multiverse_id):
    """ Function to save data to cache
    `data` Should be a Card object
    `multiverse_id` Is the multiverse_id of the card
    
    :param data: Card object from mtgsdk
    :multiverse_id: Multiverse ID of the card"""

    cache_path = get_default_cache()

    try:
        with shelve.open(API_CACHE) as cache:
            cache[str(multiverse_id)] = data
    except OSError as error:
        if error.errno == 11:   # Cache open by something else
            pass
        else:
            raise error

# I dont' think this is going to work but i'll keep it around for now
def load(multiverse_id):
    cache_path = get_default_cache()

    try:
        with shelve.open(API_CACHE) as cache:
            return cache[multiverse_id]
    except OSError:
        if error.errno == 11:   # Cache open by something else
            pass
        else:
            raise error

def save_sprite(data, multiverse_id):
    """ Function to save sprites to cache
    
    `data` Is expect to be an Image() object
    `multiverse_id` Is the multiverse_id of the card and is what the file name will be
    
    :param data: Image() object of the card
    :multiverse_id: Multiverse ID of the card """
    path = os.path.join(IMAGE_CACHE, str(multiverse_id) + '.png')

    data.save(path)


def load_cache():
    with shelve.open(API_CACHE) as cache:
        return cache

def sprite_in_cache(multiverse_id):
    return os.path.isfile(os.path.join(IMAGE_CACHE, str(multiverse_id) + '.png'))

def load_sprite(multiverse_id):
    path = os.path.join(IMAGE_CACHE, str(multiverse_id) + '.png')
    with open(path, 'rb') as img_file:
        img_data = img_file.read()

    return dict(img_data=img_data, path=path)

def build_cache_path(path):
    try:
        os.makedirs(path)
    except OSError as error:
        if error.errno != 17:  # File exists
            raise

    return path

build_cache_path(os.path.join(get_default_cache(), 'images'))
API_CACHE = os.path.join(get_default_cache(),'api.cache')
IMAGE_CACHE = os.path.join(get_default_cache(), 'images')





