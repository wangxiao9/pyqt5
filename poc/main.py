#   Description:
#       main.py : program main entrance


import sys

from PyQt5.QtWidgets import QApplication

from base.NautilusLogic import NautilusUI





if __name__ == '__main__':

    app = QApplication([])
    myWin = NautilusUI()
    myWin.ui.show()
    sys.exit(app.exec_())