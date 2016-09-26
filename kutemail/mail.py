from imaplib import IMAP4_SSL
import re
from email import parser as emailparser

class MailRetriever():
    imap_backend = None
    folders = []
    
    def __init__(self, config):
        self.imap_backend = IMAP4_SSL(host="imap.gmail.com")
        self.imap_backend.login(config["username"], config["password"])
    
    def refresh_mail(self):
        imap_folder_reg = re.compile(b'^\(.+\) "(.+)" "(.+)"$')
        self.folders = []
        raw_folders = self.imap_backend.list()
        if raw_folders[0] == 'OK':
            for raw_folder in raw_folders[1]:
                folder_info = imap_folder_reg.match(raw_folder)
                self.folders.append((folder_info.group(1), folder_info.group(2)))
    
    def list_mails(self, folder):
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
