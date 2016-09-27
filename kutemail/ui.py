import os
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
import quopri

from .config import Config
from .mail import MailAccount

def ui_path(filename):
    basepath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(basepath, 'ui', filename)

class ComposeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ComposeWindow, self).__init__()
        uic.loadUi(ui_path('composewindow.ui'), self)
    
    def onSend(self):
        print('sending...')
        self.close()

class AccountDialog(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super(AccountDialog, self).__init__(parent)
        uic.loadUi(ui_path('accountdialog.ui'), self)
    
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
    config = None
    folders = []
    emails = []
    
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(ui_path('mainwindow.ui'), self)
        self.config = Config()

    def advanceSlider(self):
        self.ui.progressBar.setValue(self.ui.progressBar.value() + 1)
    
    def onComposeMail(self):
        self.compose = ComposeWindow()
        self.compose.show()
    
    def onRefresh(self):
        self.statusbar.showMessage("Refreshing...")
        self.folders = self.mail_retriever.list_folders(force_refresh=True)
        self.statusbar.showMessage("")
        self.refreshTreeView()
    
    def onFolderSelected(self, folder):
        self.emails = self.mail_retriever.list_mails(folder.text(0))
        subjects = []
        for email in self.emails:
            subjects.append(quopri.decodestring(email[1].get('subject')).decode("utf-8"))
        self.listEmails.clear()
        self.listEmails.addItems(subjects)
    
    def onMailSelected(self, item):
        index = item.listWidget().row(item)
        email = self.emails[index][1]
        document = QtGui.QTextDocument()
        if email.is_multipart():
            html = None
            plain = None
            for payload in email.walk():
                if payload.get_content_type() == 'text/html' and html == None:
                    html = payload.get_payload(decode=True).decode("utf-8")
                if payload.get_content_type() == 'text/plain' and plain == None:
                    plain = payload.get_payload(decode=True).decode("utf-8")
                if plain != None and html != None:
                    break;
            
            if html != None:
                document.setHtml(html)
            if "DOCTYPE" in plain or "doctype" in plain:
                document.setHtml(plain)
            else:
                document.setPlainText(plain)
        else:
            plain = email.get_payload(decode=True).decode("utf-8")
            if "DOCTYPE" in plain or "doctype" in plain:
                document.setHtml(plain)
            else:
                document.setPlainText(plain)
        
        self.emailPreview.setDocument(document)
    
    def refreshTreeView(self):
        items = []
        for folder in self.folders:
            folder_item = QtWidgets.QTreeWidgetItem([folder], 0)
            folder_item.setIcon(0, QtGui.QIcon.fromTheme('folder-mail'))
            items.append(folder_item)
        self.treeMailWidget.insertTopLevelItems(0, items)
    
    def showEvent(self, event):
        if not self.config.is_loaded():
            info = AccountDialog.getAccountDetails()
            
            if not info["accepted"]:
                self.close()
            
            self.config.config['username'] = info['username']
            self.config.config['password'] = info['password']
            self.config.save()
        self.mail_retriever = MailAccount(self.config.as_dict())
        self.onRefresh()
