import sys
from PyQt4 import QtGui


class MainWindow(QtGui.QWidget):
	
	url = None
	username = None
	password = None

	urlEdit = None
	usernameEdit = None
	passwordEdit = None

	def __init__(self):
		super(MainWindow, self).__init__()
		self.initUI()
		
	def initUI(self):
		
		self.url = QtGui.QLabel('RPC URL')
		self.username = QtGui.QLabel('Username')
		self.password = QtGui.QLabel('Password')

		self.urlEdit = QtGui.QLineEdit()
		self.usernameEdit = QtGui.QLineEdit()
		self.passwordEdit = QtGui.QLineEdit()

		self.passwordEdit.setEchoMode(QtGui.QLineEdit.Password)

		submit = QtGui.QPushButton('OK')

		grid = QtGui.QGridLayout()
		grid.setSpacing(5)

		grid.addWidget(self.url, 1, 0)
		grid.addWidget(self.urlEdit, 1, 1)

		grid.addWidget(self.username, 2, 0)
		grid.addWidget(self.usernameEdit, 2, 1)

		grid.addWidget(self.password, 3, 0)
		grid.addWidget(self.passwordEdit, 3, 1)

		#Add the submit button
		grid.addWidget(submit, 4,1)
		
		self.setLayout(grid)

		submit.clicked.connect(self.submitLogin)
		
		self.setGeometry(300, 300, 350, 300)
		self.setWindowTitle('pyRtorrent')
		self.show()

	def submitLogin(self):
		print("Pressed OK!")
		print(self.urlEdit.text())
		print(self.usernameEdit.text())
		print(self.passwordEdit.text())
		
def main():
	
	app = QtGui.QApplication(sys.argv)
	main = MainWindow()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()