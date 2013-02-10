import xmlrpc.client
import threading

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
refreshTimer = 30.0


class TorrentManager():
	torrentInfoHash = []
	torrentList = []

	def __init__(self, tableModel=None):
		print("Getting the list of torrents.")
		self.torrentInfoHash = server.download_list()
		print("Found " + str(len(self.torrentInfoHash)) + " torrents.")

		for uuid in self.torrentInfoHash:
			if tableModel != None:
				self.torrentList.append(Torrent(uuid, tableModel.layoutChanged))
			else:
				self.torrentList.append(Torrent(uuid))

		for t in self.torrentList:
			t.printInfo()


class Torrent():

	'''
	The initial delay the torrent should take before starting
	the regular update cycle.

	Idealy this should be long enough to allow all the torrents
	to initialize.
	'''
	initialDelay = 20

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
		self.downloaded = self.server.d.down.total(self.uuid)

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

		self.printInfo()

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



	def printInfo(self):
		print(self.name + '|' + str(self.size))

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
