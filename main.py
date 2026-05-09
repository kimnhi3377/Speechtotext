import sys
from PyQt5.QtWidgets import QApplication
from ui import MyApp

app = QApplication(sys.argv)

window = MyApp()
window.show()

sys.exit(app.exec_())