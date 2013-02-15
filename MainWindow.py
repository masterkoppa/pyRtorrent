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

	infoPanel = None

	def __init__(self):
		super(MainWindow, self).__init__()
		print("Test")
		self.initUI()

	def initUI(self):
		# Testing hardcoded values
		rTorrentComm.setServerInfo("example", "example", "example", True)
		rTorrentComm.startServer()

		hBox = QtGui.QHBoxLayout()

		#Set up the splitter to hold the window
		splitter = QtGui.QSplitter(QtCore.Qt.Vertical)

		#Set up the information panel
		self.infoPanel = InfoPanelView(rTorrentComm.infoPanelModel, self)
		self.infoPanel.setFrameShape(QtGui.QFrame.StyledPanel)


		#Set up the table
		table = QtGui.QTableView(self)
		tableModel = rTorrentComm.torrentTable

		

		#For Debug Purposes Only
		#tableModel.layoutChanged.connect(self.dataChanged)

		table.setModel(tableModel)
		table.resizeColumnsToContents()
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QTableView.SelectRows)
		table.setItemDelegate(ProgressBarTableViewDelegate())

		table.selectionModel().currentRowChanged.connect(self.selectionChanged)

		#Add items to the splitter
		splitter.addWidget(table)
		splitter.addWidget(self.infoPanel)

		hBox.addWidget(splitter)

		self.setLayout(hBox)

		self.setGeometry(300,300,800,600)
		self.setWindowTitle("Main")
		self.show()
		

	def dataChanged(self):
		print("DATA CHANGED!! REFRESH!")

	def selectionChanged(self, current, previous):
		print("Row changed")
		print("New Row: " + str(current.row()))
		self.infoPanel.update(current.row())


class InfoPanelView(QtGui.QFrame):

	infoPanelModel = None
	
	grid = None

	nameLabel = None
	downloadedLabel = None
	uploadedLabel = None

	def __init__(self, infoPanel, parent=None):
		super(InfoPanelView, self).__init__(parent)
		self.grid = QtGui.QGridLayout()

		self.infoPanelModel = infoPanel

		# Add the labels
		self.grid.addWidget(QtGui.QLabel('Name'), 0, 0)
		self.grid.addWidget(QtGui.QLabel('Downloaded'), 1, 0)
		self.grid.addWidget(QtGui.QLabel('Uploaded'), 1, 3)

		# Add the empy labels for the variable data
		# and store them localy
		self.nameLabel = QtGui.QLabel('')
		self.grid.addWidget(self.nameLabel, 0, 1, 1, 3)

		self.downloadedLabel = QtGui.QLabel('')
		self.grid.addWidget(self.downloadedLabel, 1, 1)

		self.uploadedLabel = QtGui.QLabel('')
		self.grid.addWidget(self.uploadedLabel, 1, 4)


		# Set the variable data label
		self._drawVariableGrids()

		# Set the layout
		self.setLayout(self.grid)

	def update(self, newRow):
		self.infoPanelModel.changeActiveRow(newRow)
		self._drawVariableGrids()

	'''
	Set the text for the QLabel objects that represent the data
	'''
	def _drawVariableGrids(self):

		name = self.infoPanelModel.getName()
		self.nameLabel.setText(name)

		downloaded = self.infoPanelModel.getDownloaded()
		self.downloadedLabel.setText(downloaded)

		uploaded = self.infoPanelModel.getUploaded()
		self.uploadedLabel.setText(uploaded)


'''
The custom painter object for the table to render the progress bar
object correctly. The idea for this was taken from the qt website
examples.
'''
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