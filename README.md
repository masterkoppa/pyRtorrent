pyRtorrent
==========

A rtorrent client built using py and pyQT

Features
========

*     Connect to a rTorrent server using XMLRPC (http / https)
*     View all torrents in the server
*     Completion % of each torrent
*     Downloaded, Uploaded data and its current rate

To Come
=======

*     A GUI interface for putting the setitngs in instead of hard coded value
*     More data about each torrent
*     Other nice to have things

Plans
=====
The current plans is to make this a fully working rTorrent VIEWER. Once all
the read only things are handled then the interaction with the server will be
dealt with. But for now getting all the READ-ONLY functionality has priority.

Commands to NOT Run
===================

XMLRPC Commands that seem to crash rTorrent in my test enviorment,
needs further investigation.

*    f.path(uuid, file_index)
*    f.path_components(uuid, file_index)

rTorrent XMLRPC Notes
=====================

It seems like the documentaiton available is incomplete and old. Basing
most of my calls now from [here](http://code.google.com/p/rutorrent/source/browse/trunk/rutorrent/js/rtorrent.js).

*    d commands take just the torrent uuid
*    f commands take the torrent uuid and file index

