import xmlrpc.client
import threading
import random

from PyQt4 import QtGui, QtCore

serverURL = None

'''
The rTorrent xmlrpc server connection, only the manager should use this
'''
server = None

'''
The time that each individual torrent should wait to update its data

Possible Values:

> 0 : The time in seconds to wait
-1  : Kill the timers, exit out
'''
refreshTimer = 20.0

torrentTable = None


class TorrentManager():
	torrentInfoHash = []
	torrentList = []

	def __init__(self, tableModel=None):
		print("Getting the list of torrents.")
		self.torrentInfoHash = server.download_list()
		print("Found " + str(len(self.torrentInfoHash)) + " torrents.")

		if tableModel == None:
			tableModel = TorrentTableModel()

		for uuid in self.torrentInfoHash:
			if tableModel != None:
				self.torrentList.append(Torrent(uuid, tableModel.layoutChanged))
			else:
				self.torrentList.append(Torrent(uuid))

		
		if isinstance(tableModel, TorrentTableModel):
			tableModel.setTorrentList(self.torrentList)

		global torrentTable

		torrentTable = tableModel


class TorrentTableModel(QtCore.QAbstractTableModel):

	torrentList = None

	tableHeaders = ["Name", "Size", "Downloaded"]

	def __init__(self):
		super(TorrentTableModel, self).__init__()

	def setTorrentList(self, torrentList):
		self.torrentList = torrentList

	def rowCount(self, parent):
		return len(self.torrentList)

	def columnCount(self, parent):
		return self.torrentList[0].getDataFieldCount()

	def data(self, index, role):
		if(role == 0):
			return self.torrentList[index.row()].getTabularData(index.column())

	'''
	#TODO This needs to be fixed. Can't get the text I want to actually
	#     display. But everything else is sound.
	def headerData(self, section, orientation, role):
		if orientation == QtCore.Qt.Horizontal:
			print(self.tableHeaders[section])
			return QtCore.QVariant('Test')
		else:
			return QtCore.QVariant(section)
	'''

class Torrent():

	'''
	The initial delay the torrent should take before starting
	the regular update cycle.

	Idealy this should be long enough to allow all the torrents
	to initialize.
	'''
	initialDelay = 2

	'''
	UUID is the info hash used by rTorrent to identify each torrent

	This hash shall be final once it is initialized ans should never
	change.
	'''
	uuid = ''

	'''
	This torrents unique server connection.

	Each Torrent Object must keep its own connection to avoid any
	concurrency issues and to speed up the process by being multi-threaded
	without the use of locks.
	'''
	server = None

	'''
	The number of columns this can be represented as
	'''
	dataFields = 7

	tableModelSignal = None


	#################################################################
	#                        Torrent Properties                     #
	#################################################################

	'''
	Name of the torrent

	INMUTABLE
	'''
	name = None

	'''
	Size of the torrent

	INMUTABLE
	'''
	size = None

	'''
	The number of bytes downloaded

	MUTABLE
	'''
	downloaded = None

	uploaded = None

	down_rate = None

	up_rate = None

	'''
	Initializes the torrent object with the specified info hash as a
	UUID. The torrent is self sufficient and independent.
	'''
	def __init__(self, tUUID, tableModelSignal=None):
		self.uuid = tUUID
		self.server = xmlrpc.client.ServerProxy(serverURL)
		print('Generated Torrent Object with UUID: ' + tUUID)

		#Make the server request for basic information
		self._getName()
		self._getSize()


		if tableModelSignal != None:
			self.tableModelSignal = tableModelSignal

		#Get the information that is constantly changing
		#with a initial delay of 5 seconds
		threading.Timer(self.initialDelay, self.refresh).start()





	'''
	Request the server for this torrents name.
	This should only be called by the constructor, a one time call.
	'''
	def _getName(self):
		self.name = self.server.d.name(self.uuid)

	def _getSize(self):
		self.size = self.server.d.size_bytes(self.uuid)

	def _getDownloaded(self):
		#d.down.total gives you the amount downloaded in this session,
		#including the amount wasted
		#self.downloaded = self.server.d.down.total(self.uuid)
		#d.completed_bytes gives you a usable number of what we have, no
		#wasted included
		self.downloaded = self.server.d.completed_bytes(self.uuid)

	def _getUploaded(self):
		self.uploaded = self.server.d.up.total(self.uuid)

	def _getDownRate(self):
		self.down_rate = self.server.d.down.rate(self.uuid)

	def _getUpRate(self):
		self.up_rate = self.server.d.up.rate(self.uuid)

	def getUUID(self):
		return uuid

	'''
	Make all the requests for data that are supposed to change over time
	'''
	def refresh(self):

		#TODO: Make grabing changing information smart about what data
		#      to grab. Not all data will change depending on the torrent's
		#      current state.
		self._getDownloaded()
		self._getUploaded()
		self._getDownRate()
		self._getUpRate()

		#self.printInfo()

		#If there is a table model associated with this torrent, AKA torrent
		#is being shown, then signal the change.
		if self.tableModelSignal != None:
			print("Emiting Signal!")
			self.tableModelSignal.emit()

		global refreshTimer

		#Check if refresh timer is equal to -1, the kill signal
		if(refreshTimer == -1):
			return
		else:
			threading.Timer(refreshTimer, self.refresh).start()


	def getDataFieldCount(self):
		return self.dataFields

	'''
	Returns a array of data that will be shown on the table view
	'''
	def getTabularData(self, index):
		if index == 0:
			return self.name
		elif index == 1:
			return self.sizeof_t(self.size)
		elif index == 2:
			#Calculate the completion %
			ret = (self.downloaded / self.size) * 100
			return "%3.1f%s" % (ret, "%")
		elif index == 3:
			return self.sizeof_t(self.downloaded)
		elif index == 4:
			return self.sizeof_t(self.uploaded)
		elif index == 5:
			return self.speedof_t(self.down_rate)
		elif index == 6:
			return self.speedof_t(self.up_rate)
		

	def printInfo(self):
		print(self.name + ' | ' + str(self.size) + ' | ' + str(self.downloaded) + ' | ' + str(self.uploaded))

	#From: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
	def sizeof_t(self, num):
		for x in ['bytes','KB','MB','GB']:
			if num < 1024.0:
				return "%3.2f%s" % (num, x)
			num /= 1024.0
		return "%3.2f%s" % (num, 'TB')

	def speedof_t(self, num):
		for x in ['bytes/s','KB/s','MB/s','GB/s']:
			if num < 1024.0:
				return "%3.2f%s" % (num, x)
			num /= 1024.0
		return "%3.2f%s" % (num, 'TB')

def refreshTimerChanged(newValue):
	print(newValue)
	global refreshTimer
	refreshTimer = newValue

def startServer(tableModel=None):
	#Initialize the server
	global server
	server = xmlrpc.client.ServerProxy(serverURL)

	#Print a test message, the start the manager
	print('Connected to: ' + server.system.hostname())
	manager = TorrentManager(tableModel)

'''
Set the server url in the format that the python library expects it.

flag : Set to true if you want to use https:// instead of plain http://
'''
def setServerInfo(url, username, password, flag = False):
	global serverURL

	if flag:
		serverURL = "https://"
	else:
		serverURL = "http://"

	serverURL += username + ":" + password + "@" + url
	print(serverURL)


