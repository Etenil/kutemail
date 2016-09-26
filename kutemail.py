import sys

from kutemail import ui

app = QtWidgets.QApplication(sys.argv)

my_mainWindow = ui.MainWindow()
my_mainWindow.show()

sys.exit(app.exec_())
