import sys
import PyQt5
from PyQt5.QtWidgets import QMainWindow
from untitled import Ui_Form


class MyGui(QMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


app = PyQt5.QtWidgets.QApplication(sys.argv)
MyUiStart = MyGui()
MyUiStart.show()
sys.exit(app.exec_())
