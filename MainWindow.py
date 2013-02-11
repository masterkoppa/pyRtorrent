import sys
import rTorrentComm
import random
from PyQt4 import QtGui, QtCore


class LoginWindow(QtGui.QWidget):
	
	url = None
	username = None
	password = None

	urlEdit = None
	usernameEdit = None
	passwordEdit = None

	def __init__(self):
		super(LoginWindow, self).__init__()
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

class MainWindow(QtGui.QWidget):

	def __init__(self):
		super(MainWindow, self).__init__()
		print("Test")
		self.initUI()

	def initUI(self):
		# Testing hardcoded values
		rTorrentComm.setServerInfo("example", "example", "example", True)
		rTorrentComm.startServer()

		hBox = QtGui.QHBoxLayout()

		table = QtGui.QTableView(self)
		tableModel = rTorrentComm.torrentTable

		tableModel.layoutChanged.connect(self.dataChanged)

		table.setModel(tableModel)
		table.resizeColumnsToContents()
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QTableView.SelectRows)
		table.setItemDelegate(ProgressBarTableViewDelegate())

		hBox.addWidget(table)

		self.setLayout(hBox)

		self.setGeometry(300,300,800,600)
		self.setWindowTitle("Main")
		self.show()
		

	def dataChanged(self):
		print("DATA CHANGED!! REFRESH!")


class ProgressBarTableViewDelegate(QtGui.QStyledItemDelegate):

	def paint(self, painter, option, index):
		self.initStyleOption(option, index)
		if index.column() == 2:
			progressBar = QtGui.QStyleOptionProgressBar()
			progressBar.state = QtGui.QStyle.State_Enabled
			progressBar.direction = QtGui.QApplication.layoutDirection()
			progressBar.rect = option.rect
			progressBar.fontMetrics = QtGui.QApplication.fontMetrics()
			progressBar.minimum = 0
			progressBar.maximum = 100
			progressBar.textAlignment = QtCore.Qt.AlignCenter
			progressBar.textVisible = True

			progressBar.progress = index.data()
			progressBar.text = "%3.1f%s" % (index.data(), "%")

			QtGui.QApplication.style().drawControl(QtGui.QStyle.CE_ProgressBar, progressBar, painter)

		else:
			super(ProgressBarTableViewDelegate, self).paint(painter, option, index)

class ExampleTableModel(QtCore.QAbstractTableModel):

	def __init__(self):
		super(ExampleTableModel, self).__init__()

	def rowCount(self, parent):
		return 4

	def columnCount(self, parent):
		return 4

	def data(self, index, role):
		return str(random.randint(0,100))


def login():
	app = QtGui.QApplication(sys.argv)
	login = LoginWindow()
	app.exec_()

def main():
	#login()
	app = QtGui.QApplication(sys.argv)
	app.aboutToQuit.connect(closeEvent)
	main = MainWindow()
	sys.exit(app.exec_())

def closeEvent():
	print("Exiting Application, waiting on all threads to finish execution")
	rTorrentComm.refreshTimer = -1

if __name__ == '__main__':
	main()