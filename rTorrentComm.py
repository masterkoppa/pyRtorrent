import xmlrpc.client
import threading
import random
import urllib.parse

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
refreshTimer = 5.0

'''
The table model that the GUI will use

Since the table model needs to be instanciated and controlled by
the torrent manager then it's stored here initially where after the init
process gets assigned to the table in the GUI
'''
torrentTable = None

'''
A special model that will store the current torrent's information

This model should be initialized in TorrentManager.__init__
'''
infoPanelModel = None

'''
The Torrent Manager

This class makes the first communication with the server and retrieves
the initial list of torrents. Then sets each torrent in motion.

Aditionally it is a watchdog for changes that happen on the server side
outside of the individual torrent's scope. For example: Adding and Removing
Torrents from the internal model.
'''
class TorrentManager():
	'''
	The current list of hashes from the information we get from the server
	this is used for comparison since we assume no 2 torrents will contain
	the same hash.
	'''
	torrentInfoHash = []

	'''
	The list of torrent objects. Each torrent should co-relate to a 
	info hash in the torrentInfoHash list.
	'''
	torrentList = []

	def __init__(self, tableModel=None):
		print("Getting the list of torrents.")
		self.torrentInfoHash = server.download_list()
		print("Found " + str(len(self.torrentInfoHash)) + " torrents.")

		# If no model is passed in create one
		if tableModel == None:
			tableModel = TorrentTableModel()

		# Iterate through the list of hashes creating new torrent objects.
		# On init, they will gather the required info and spawn off.
		for uuid in self.torrentInfoHash:
			self.torrentList.append(Torrent(uuid, tableModel.layoutChanged))
			

		#Make sure we have the correct object if the model was passed in
		if isinstance(tableModel, TorrentTableModel):
			tableModel.setTorrentList(self.torrentList)

		# Set the reference for table model so the GUI can grab it,
		# it the model was created here
		global torrentTable

		torrentTable = tableModel

		# Set the reference for the information panel model.
		global infoPanelModel

		infoPanelModel = TorrentInformationModel()

		# Start the watchdogss
		self.monitor()

	def monitor(self):
		tmp_list = server.download_list()

		if tmp_list != self.torrentInfoHash:
			#Something changed, lets fix the problem
			self.fixState(tmp_list)
			print("Something changed... Fixing the model")

		# Check if refresh timer is equal to -1, the kill signal
		if(refreshTimer == -1):
			return
		else:
			# Schedule the next check. For performance reasons 
			# make it refreshTimer x 2
			threading.Timer((refreshTimer * 2), self.monitor).start()

	'''
	Fix our internal model to adjust for changes:

	Here is what we care about: Adding or Removing a Torrent

	Adding: 	If a new torrent is added we want to add it to our
				list and start the torrent refresh cycle

	Removing:	If a torrent is removed then we simply want to remove
				the torrent from our model. The Torrent object will
				die on its own to be garbage collected latter.
	'''
	def fixState(self, newList):
		#Adding new torrents
		for infoHash in newList:
			#If the torrent is new
			if self.torrentInfoHash.count(infoHash) == 0:
				self.torrentList.append(Torrent(infoHash))

		#Removing old ones
		for infoHash in self.torrentInfoHash:
			#If the torrent is not in the new list, it was removed
			if newList.count(infoHash) == 0:
				tmpObj = None
				for torrent in self.torrentList:
					if torrent.uuid == infoHash:
						tmpObj = torrent
				self.torrentList.remove(tmpObj)

		self.torrentInfoHash = newList
		torrentTable.setTorrentList(self.torrentList)
		#Refresh the list and resort it with the new data
		torrentTable.resort()
		print("Model has been updated")


class TorrentInformationModel():

	#The selected row will allways start at 0
	currentRow = 0
	torrent = None

	def __init__(self):
		print("Initialing Information Panel Model")
		self.changeActiveRow(0)

	def changeActiveRow(self, newRow):
		self.currentRow = newRow
		self.torrent = torrentTable.torrentList[newRow]

	def getName(self):
		return self.torrent.name

	def getDownloaded(self):
		return self.torrent.sizeof_t(self.torrent.downloaded)

	def getUploaded(self):
		return self.torrent.sizeof_t(self.torrent.uploaded)

	def getRatio(self):
		return "%.3f" % (self.torrent.ratio)
	      
	def getInfoHash(self):
		return str(self.torrent.uuid)






class TorrentTableModel(QtCore.QAbstractTableModel):

	torrentList = None
	nColSort = 0
	orderingSort = 1

	tableHeaders = ["Name", "Size", "Completed", "Downloaded", "Uploaded", "Ratio", "Down Rate", "Up Rate", "Label", "Priority"]

	def __init__(self):
		super(TorrentTableModel, self).__init__()

		# Since we can't guarantee all the data changes all the time
		# we should resort every time we recieve a change in data.
		#self.layoutChanged.connect(self.resort)

	def setTorrentList(self, torrentList):
		self.torrentList = torrentList

	def rowCount(self, parent):
		return len(self.torrentList)

	def columnCount(self, parent):
		return self.torrentList[0].getDataFieldCount()

	def data(self, index, role):
		if(role == 0):
			return self.torrentList[index.row()].getTabularData(index.column())

	def sort(self, nCol, order):
		self.nColSort = nCol
		self.orderingSort = order
		
		if nCol == 0:
			self.torrentList = sorted(self.torrentList, key=lambda torrent: torrent.name.lower())
		elif nCol == 1:
			self.torrentList = sorted(self.torrentList, key=lambda torrent: torrent.size)
		elif nCol == 2:
			self.torrentList = sorted(self.torrentList, key=lambda torrent: torrent.completion)
		elif nCol == 3:
			self.torrentList = sorted(self.torrentList, key=lambda torrent: torrent.downloaded)
		elif nCol == 4:
			self.torrentList = sorted(self.torrentList, key=lambda torrent: torrent.uploaded)
		elif nCol == 5:
			self.torrentList = sorted(self.torrentList, key=lambda torrent: torrent.ratio)
		elif nCol == 6:
			self.torrentList = sorted(self.torrentList, key=lambda torrent: torrent.down_rate)
		elif nCol == 7:
			self.torrentList = sorted(self.torrentList, key=lambda torrent: torrent.up_rate)
		elif nCol == 8:
			self.torrentList = sorted(self.torrentList, key=lambda torrent: torrent.label)
		elif nCol == 9:
			self.torrentList = sorted(self.torrentList, key=lambda torrent: torrent.priority)

		#Order == 1, acending
		#Order == 0, decending
		if order == 0:
			self.torrentList.reverse()

		self.layoutChanged.emit()


	def headerData(self, section, orientation, role):
		#If its the horizontal header and its the display role, send it through
		if orientation == QtCore.Qt.Horizontal and role == 0:
			return self.tableHeaders[section]
		else:
			return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

	def resort(self):
		self.sort(self.nColSort, self.orderingSort)


class Torrent():
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
	#                        Torrent Constants                      #
	#################################################################

	torrentPriority = {1 : "Low", 2: "Normal", 3: "High", 0: "Off"}

	'''
	The number of columns this can be represented as
	'''
	dataFields = 10

	'''
	The initial delay the torrent should take before starting
	the regular update cycle.

	Idealy this should be long enough to allow all the torrents
	to initialize.
	'''
	initialDelay = 2


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
	The number of peers(ppl not 100% done) are available.
	
	MUTABLE
	'''
	peer_count = None

	'''
	The number of peers(ppl not 100% done) are connected.
	
	MUTABLE
	'''
	peer_conn = None
	
	
	seed_count = None
	
	seed_conn = None

	'''
	Calculated Properties

	These properties aren't given to us by the server, instead we do the math
	ourselves.
	'''
	completion = None

	ratio = None
	
	label = None

	priority = None

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
	
	'''
	This gets the number that is to the left of the number in paretheses
	in ruTorrent.
	'''
	def _getPeersConnected(self):
		#Both of these seem to work just fine, needs more investigation
		self.peer_conn = self.server.d.get_peers_accounted(self.uuid)
		#OR
		#self.peer_conn = self.server.d.get_peers_connected(self.uuid)
	
	'''
	Like _getPeersConnected this will give you the number on the seeds column to the
	left of the number in paretheses.
	'''
	def _getSeedsConnected(self):
		self.seed_conn = self.server.d.get_peers_complete(self.uuid)
		
	def _getTrackerCount(self):
		self.tracker_count = self.server.d.tracker_size(self.uuid)
	
	'''
	Retrieve the torrent comment, not sure if it works yet...
	'''
	def _getMessage(self):
		self.comment = self.server.d.get_message(self.uuid)
	
	
	def _getLabel(self):
		self.label = self.server.d.get_custom1(self.uuid)#Might not work everywhere
		self.label = urllib.parse.unquote(self.label)
	
	def _getPriority(self):
		#print("NOT IMPLEMENTED!")
		self.priority = self.server.d.get_priority(self.uuid)
		#Priority = 3 : High Priority
		#Priority = 2 : Normal Priority
		#Priority = 1 : Low Priority
		#Priority = 0 : Off Priority
	
	def _getTorrentLocation(self):
		#Gets the path to the location of the torrent in the server
		self.root_dir = self.server.d.directory(self.uuid)
	
	def _getIsActive(self):
		# If the torrent started or stoped
		# 0 is stopped
		# 1 is active
		self.is_active = self.server.d.is_active(self.uuid)
	
	def _getIsPrivate(self):
		# Finds out if the torrent is from a private tracker or not
		# 0 public
		# 1 private
		self.private = self.server.d.is_private(self.uuid)
	
	def _getNumberOfFiles(self):
		# Gets the number of files for this torrent
		self.numFiles = self.server.d.size_files(self.uuid)

	def _getNumberOfChunks(self):
		self.numChunks = self.server.d.size_chunks(self.uuid)
		
	def _getNumberOfTrackers(self):
		self.numTrackers = self.server.d.tracker_size(self.uuid)
	
	def _getFileName(self, fileIndex):
		# Get the name of the file in this torrent
		self.filenames[fileIndex] = self.server.f.get_path(self.uuid, fileIndex)

	def getUUID(self):
		return uuid

	'''
	Make all the requests for data that are supposed to change over time
	'''
	def refresh(self):
		
		try:
			#TODO: Make grabing changing information smart about what data
			#      to grab. Not all data will change depending on the torrent's
			#      current state.
			self._getDownloaded()
			self._getUploaded()
			self._getDownRate()
			self._getUpRate()
			self._getPeersConnected()
			self._getMessage()
			self._getLabel()
			self._getPriority()
			
			
		except Exception:
			#Die on exception
			print(self.name + " torrent found a exception while refreshing.")
			print("Assuming torrent was removed, moving on...")
			return
		#For Debug Purposes Only
		#self.printInfo()

		#Calculate the completion %
		self.completion = (self.downloaded / self.size) * 100

		#Calculate the ratio
		if self.downloaded != 0:
			self.ratio = self.uploaded / self.downloaded
		else:
			self.ratio = 0

		#If there is a table model associated with this torrent, AKA torrent
		#is being shown, then signal the change.
		if self.tableModelSignal != None:
			#print("Emiting Signal!")
			self.tableModelSignal.emit()

		#global refreshTimer

		#Check if refresh timer is equal to -1, the kill signal
		if(refreshTimer == -1):
			print("Killing off Torrent: " + self.name)
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
			#Return the raw completion value in a nice format
			#return "%3.1f%s" % (self.completion, "%")
			return self.completion
		elif index == 3:
			return self.sizeof_t(self.downloaded)
		elif index == 4:
			return self.sizeof_t(self.uploaded)
		elif index == 5:
			return "%.3f" % (self.ratio)
		elif index == 6:
			return self.speedof_t(self.down_rate)
		elif index == 7:
			return self.speedof_t(self.up_rate)
		elif index == 8:
			return self.label
		elif index == 9:
			return self.torrentPriority[self.priority]
		

	def printInfo(self):
		print(self.name + ' | ' + str(self.comment) )

	#From: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
	def sizeof_t(self, num):
		for x in [' bytes',' KB',' MB',' GB']:
			if num < 1024.0:
				return "%3.2f%s" % (num, x)
			num /= 1024.0
		return "%3.2f%s" % (num, ' TB')

	def speedof_t(self, num):
		for x in [' bytes/s',' KB/s',' MB/s',' GB/s']:
			if num < 1024.0:
				return "%3.1f%s" % (num, x)
			num /= 1024.0
		return "%3.21%s" % (num, ' TB/s')

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

def startServerDEBUG():
	#Initialize the server
	global server
	server = xmlrpc.client.ServerProxy(serverURL)

	#Print a test message, the start the manager
	print('Connected to: ' + server.system.hostname())

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


