import sys
from time import sleep
import threading
from PyQt5 import QtWidgets
from PyQt5 import uic

class MailRetriever(threading.Thread):
    onFinish = None
    
    def __init__(self, onFinish):
        super(MailRetriever, self).__init__()
        self.onFinish = onFinish
    
    def run(self):
        sleep(3)
        self.onFinish()

#class ComposeDialog(QtWidgets.QDialog):
    #def __init__(self):
        #super(ComposeDialog, self).__init__()
        #uic.loadUi('composedialog.ui', self)
    
    #def onSend(self):
        #print('sending...')
        #self.close()

class ComposeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ComposeWindow, self).__init__()
        uic.loadUi('composewindow.ui', self)
    
    def onSend(self):
        print('sending...')
        self.close()


class MainWindow(QtWidgets.QMainWindow):
    refreshing = False
    
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)

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
            retriever = MailRetriever(self.onRefreshEnd)
            retriever.run()
            
    def onRefreshEnd(self):
        self.refreshing = False
        self.statusbar.showMessage("")
        
app = QtWidgets.QApplication(sys.argv)

my_mainWindow = MainWindow()
my_mainWindow.show()

sys.exit(app.exec_())
