import pickle
import os

class Config():
    config = {
        'protocol': 'IMAP',
        'host': 'imap.gmail.com'
    }
    config_path = ''
    loaded = False
    
    def __init__(self):
        self.config_path = os.path.expanduser('~/.config/kutemail.rc')
        self.config['cache_path'] = os.path.expanduser('~/.local/share/kutemail')
        self.load_config()
    
    def load_config(self):
        if os.path.isfile(self.config_path):
            self.config = pickle.load(open(self.config_path, "rb"))
            self.loaded = True
    
    def save(self):
        pickle.dump(self.config, open(self.config_path, "wb"))
    
    def is_loaded(self):
        return self.loaded

    def as_dict(self):
        return self.config
