import os
from imaplib import IMAP4_SSL
import re
import pickle
import time
from email import parser as emailparser

from pprint import pprint

class ImapMailRetriever():
    """
    Retrieve emails through IMAP
    """
    imap_backend = None
    
    def __init__(self, host, username, password):
        self.imap_backend = IMAP4_SSL(host=host)
        self.imap_backend.login(username, password)
    
    def refresh_mail(self):
        imap_folder_reg = re.compile(b'^\(.+\) "(.+)" "(.+)"$')
        folders = []
        raw_folders = self.imap_backend.list()
        if raw_folders[0] == 'OK':
            for raw_folder in raw_folders[1]:
                folder_info = imap_folder_reg.match(raw_folder)
                folders.append((folder_info.group(1), folder_info.group(2)))
        
        return folders
    
    def list_mail(self, folder):
        self.imap_backend.select(folder)
        result, data = self.imap_backend.uid("search", None, "ALL")
        mailparser = emailparser.Parser()
        mails = []
        uid_block = data[0].split()
        #for uid_block in data:
        for uid in uid_block[0:20]:
            result, mail_data = self.imap_backend.fetch(uid, "(RFC822)")
            if result == "OK":
                try:
                    parsed_mail = mailparser.parsestr(mail_data[0][1].decode("utf-8"))
                    mails.append((uid, parsed_mail))
                except UnicodeDecodeError:
                    pass
        return mails

class MailCache():
    """
    Emails cache. Is totally independent from the back-end
    """
    retriever = None
    cache_path = ''
    state_path = ''
    cache_state = {}
    MAX_AGE = 3600
    
    def __init__(self, cache_path, retriever):
        self.retriever = retriever
        self.cache_path = cache_path
        self.state_path = os.path.join(cache_path, 'cache.state')
        
        if not os.path.isdir(self.cache_path):
            os.makedirs(self.cache_path)
        
        self._load_state()
    
    def list_folders(self, force_refresh):
        if force_refresh or self._is_stale('/'):
            folders = self.retriever.refresh_mail()
            for folder in folders:
                folder_name = new_folder[1].decode('utf-8').replace('/', '%')
                if not folder_name in folders:
                    cached_folders.append(folder_name)
                self._cache_folder(folder_name)
            self._renew_state('/')
            self._commit_state()
        
        return self._get_cached_folders(self.cache_path)
    
    def list_mail(self, folder, force_refresh):
        folder_path = os.path.join(self.cache_path, folder)
        mails = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if self._is_stale(folder) or force_refresh == True:
            mails = self.retriever.list_mail(folder)
        # TODO Implementation
        return []
    
    def _get_cached_folders(self, path):
        folders = []
        for folder in os.listdir(path):
            folder_path = os.path.join(path, folder)
            if os.path.isdir(folder_path):
                folders.append((folder, self._get_cached_folders(folder_path)))
        return folders
    
    def _is_stale(self, folder):
        if folder in self.cache_state:
            return self.cache_state[folder] > self.MAX_AGE
        else:
            return True
    
    def _cache_folder(self, folder):
        folder_path = os.path.join(self.cache_path, folder)
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
            self._renew_state(folder)
    
    def _renew_state(self, folder):
        self.cache_state[folder] = time.time()
    
    def _load_state(self):
        if os.path.isfile(self.state_path):
            with open(self.state_path, 'rb') as cache:
                self.cache_state = pickle.load(cache)
    
    def _commit_state(self):
        with open(self.state_path, 'wb') as cache:
            pickle.dump(self.cache_state, cache)

class MailAccount():
    """
    Abstracts fetching / sending and caching to an email account
    """
    cache = None
    
    def __init__(self, config):
        retriever = None
        if config['protocol'] == "IMAP":
            retriever = ImapMailRetriever(config['host'], config['username'], config['password'])
        else:
            raise "ARGH! Unknown protocol!"
        
        self.cache = MailCache(config['cache_path'], retriever)
    
    def list_folders(self, force_refresh=False):
        """Lists the available IMAP folders"""
        return self.cache.list_folders(force_refresh)
    
    def list_mail(self, folder, force_refresh=False):
        """Lists emails in a folder, from cache if available"""
        return self.cache.list_mail(folder, force_refresh)
