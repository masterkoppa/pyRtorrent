import xmlrpc.client
import threading


'''
The rTorrent xmlrpc server
'''
server = xmlrpc.client.ServerProxy('EXAMPLE SERVER')

'''
Global lock access to the xmlrpc server
'''
lock = threading.Lock()

refreshTimer = 5.0


class TorrentManager():
	torrentInfoHash = []
	torrentList = []

	def __init__(self):
		print("Getting the list of torrents.")
		self.torrentInfoHash = server.download_list()
		print("Found " + str(len(self.torrentInfoHash)) + " torrents.")

		for uuid in self.torrentInfoHash:
			self.torrentList.append(Torrent(uuid))

		for t in self.torrentList:
			t.printInfo()
			threading.Timer(refreshTimer, t.refresh).start()


class Torrent():
	'''
	UUID is the info hash used by rTorrent to identify each torrent

	This hash shall be final once it is initialized ans should never
	change.
	'''
	uuid = ''


	#################################################################
	#                        Torrent Properties                     #
	#################################################################

	'''
	Name of the torrent

	INMUTABLE
	'''
	name = ''
	size = ''
	def __init__(self, tUUID):
		self.uuid = tUUID
		print('Generated Torrent Object with UUID: ' + tUUID)

		#Make the server request for basic information
		self._getName()
		self._getSize()

		#Get the information that is constantly changing
		#self.refresh()





	'''
	Request the server for this torrents name.
	This should only be called by the constructor, a one time call.
	'''
	def _getName(self):
		self.name = server.d.name(self.uuid)

	def _getSize(self):
		self.size = server.d.size_bytes(self.uuid)

	def _getDownloaded(self):
		self.downloaded = server.d.down.total(self.uuid)

	def getUUID(self):
		return uuid

	'''
	Make all the requests for data that are supposed to change over time
	'''
	def refresh(self):
		lock.acquire(True)
		self._getDownloaded()
		lock.release()

		self.printInfo()
		global refreshTimer
		threading.Timer(refreshTimer, self.refresh).start()

	def printInfo(self):
		print(self.name + '|' + str(self.size))

def refreshTimerChanged(newValue):
	print(newValue)
	global refreshTimer
	refreshTimer = newValue

def main():
	#print(server.system.listMethods())
	print('Connected to: ' + server.system.hostname())
	manager = TorrentManager()

if __name__ == '__main__':
	main()