import sys
from PyQt4 import QtGui, QtCore

class MainWindow(QtGui.QWidget):

	def __init__(self):
		super(MainWindow, self).__init__()

		self.build_and_show_ui()

	def build_and_show_ui(self):
		names = ['Cls', 'Bck', '', 'Close', '7', '8', '9', '/',
				'4', '5', '6', '*', '1', '2', '3', '-',
				'0', '.', '=', '+']

		grid = QtGui.QGridLayout()

		j = 0
		pos = [(0, 0), (0, 1), (0, 2), (0, 3),
				(1, 0), (1, 1), (1, 2), (1, 3),
				(2, 0), (2, 1), (2, 2), (2, 3),
				(3, 0), (3, 1), (3, 2), (3, 3 ),
				(4, 0), (4, 1), (4, 2), (4, 3)]

		for i in names:
			button = QtGui.QPushButton(i)
			button.clicked.connect(self.calcButton)
			if j == 2:
				grid.addWidget(QtGui.QLabel(''), 0, 2)
			else: grid.addWidget(button, pos[j][0], pos[j][1])
			j = j + 1

		self.setLayout(grid)   
		
		self.move(300, 150)
		self.setWindowTitle('Calculator')    
		self.show()

	def calcButton(self):
		sender = self.sender()

	

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	main = MainWindow()

	sys.exit(app.exec_())
