import sys
from time import sleep
import threading
from PyQt5 import QtWidgets
from PyQt5 import uic
from imaplib import IMAP4_SSL
import pickle
import os

from pprint import pprint

class Account():
    config = {}
    
    def __init__(self):
        self.config = pickle.load(open(os.path.expanduser("~/.config/kutemail.rc"), "rb"))
    
    def save(self):
        pickle.dump(self.config, open(os.path.expanduser("~/.config/kutemail.rc"), "wb"))

class MailRetriever(threading.Thread):
    imap_backend = None
    
    def __init__(self):
        super(MailRetriever, self).__init__()
        self.imap_backend = IMAP4_SSL(host="imap.gmail.com")
        self.imap_backend.login()
        pprint(self.imap_backend.list())
        print("\n")
    
    def refresh(self, onFinish):
        sleep(3)
        onFinish()

class ComposeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ComposeWindow, self).__init__()
        uic.loadUi('composewindow.ui', self)
    
    def onSend(self):
        print('sending...')
        self.close()

class AccountDialog(QtWidgets.QDialog):
    def __init__(self):
        super(AccountDialog, self).__init__()
        uic.loadUi('accountdialog.ui', self)
    
    def accept(self):
        pass
    
    def reject(self):
        pass

class MainWindow(QtWidgets.QMainWindow):
    refreshing = False
    mail_retriever = None
    account = None
    
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.mail_retriever = MailRetriever()
        self.account = Account()

    def advanceSlider(self):
        self.ui.progressBar.setValue(self.ui.progressBar.value() + 1)
    
    def onComposeMail(self):
        print('compose')
        self.compose = ComposeWindow()
        self.compose.show()
    
    def onRefresh(self):
        if not self.refreshing:
            self.refreshing = True
            self.statusbar.showMessage("Refreshing...")
            self.mail_retriever.refresh(self.onRefreshEnd())
            
    def onRefreshEnd(self):
        self.refreshing = False
        self.statusbar.showMessage("")
    
    def showEvent(self, event):
        if self.acccount == None:
            diag = AccountDialog()
            diag.show()

app = QtWidgets.QApplication(sys.argv)

my_mainWindow = MainWindow()
my_mainWindow.show()

sys.exit(app.exec_())
