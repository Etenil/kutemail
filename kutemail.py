import sys
from time import sleep
import threading
from PyQt5 import QtWidgets
from PyQt5 import uic
from imaplib import IMAP4_SSL
import pickle
import os
import re
from email import parser as emailparser

from pprint import pprint

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
        for uid in uid_block[0:3]:
            result, mail_data = self.imap_backend.fetch(uid, "(RFC822)")
            if result == "OK":
                try:
                    parsed_mail = mailparser.parsestr(mail_data[0][1].decode("utf-8"))
                    mails.append((uid, parsed_mail))
                except UnicodeDecodeError:
                    pass
        return mails

class ComposeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ComposeWindow, self).__init__()
        uic.loadUi('composewindow.ui', self)
    
    def onSend(self):
        print('sending...')
        self.close()

class AccountDialog(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super(AccountDialog, self).__init__(parent)
        uic.loadUi('accountdialog.ui', self)
    
    @staticmethod
    def getAccountDetails(username='', password='', parent=None):
        dialog = AccountDialog(parent)
        dialog.txtUserName.setText(username)
        result = dialog.exec_()
        return {
            "accepted": result == QtWidgets.QDialog.Accepted,
            "username": dialog.txtUserName.text(),
            "password": dialog.txtPassword.text()
        }

class MainWindow(QtWidgets.QMainWindow):
    mail_retriever = None
    account = None
    
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.account = Account()

    def advanceSlider(self):
        self.ui.progressBar.setValue(self.ui.progressBar.value() + 1)
    
    def onComposeMail(self):
        self.compose = ComposeWindow()
        self.compose.show()
    
    def onRefresh(self):
        self.statusbar.showMessage("Refreshing...")
        self.mail_retriever.refresh_mail()
        self.statusbar.showMessage("")
        self.refreshTreeView()
    
    def onFolderSelected(self, folder):
        emails = self.mail_retriever.list_mails(folder.text(0))
        subjects = []
        for email in emails:
            subjects.append(email[1].get('subject'))
        self.listEmails.clear()
        self.listEmails.addItems(subjects)
    
    def onMailSelected(self):
        pass
    
    def refreshTreeView(self):
        items = []
        for folder in self.mail_retriever.folders:
            items.append(QtWidgets.QTreeWidgetItem([folder[1].decode("utf-8")], 0))
        self.treeMailWidget.insertTopLevelItems(0, items)
    
    def showEvent(self, event):
        if not self.account.is_loaded():
            info = AccountDialog.getAccountDetails()
            
            if not info["accepted"]:
                self.close()
            
            self.account.config = {
                "username": info["username"],
                "password": info["password"]
            }
            self.account.save()
        self.mail_retriever = MailRetriever(self.account.config)
        self.onRefresh()

app = QtWidgets.QApplication(sys.argv)

my_mainWindow = MainWindow()
my_mainWindow.show()

sys.exit(app.exec_())
