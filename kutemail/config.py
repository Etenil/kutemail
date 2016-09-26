import pickle
import os

class Account():
    config = {}
    config_path = ''
    
    def __init__(self):
        self.config_path = os.path.expanduser("~/.config/kutemail.rc")
        self.load_config()
    
    def load_config(self):
        if os.path.isfile(self.config_path):
            self.config = pickle.load(open(self.config_path, "rb"))
    
    def save(self):
        pickle.dump(self.config, open(self.config_path, "wb"))
    
    def is_loaded(self):
        return self.config != {}
