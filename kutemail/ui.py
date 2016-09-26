from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
import quopri

from . import config
import mail

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
    emails = []
    
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.account = config.Account()

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
        self.mail_retriever = mail.MailRetriever(self.account.config)
        self.onRefresh()
