import time
import gobject
from myth.MythMySQL import mythDB
from modules.music_player.music_objects.song import song
from modules.music_player.music_objects.artist import artist
from modules.music_player.music_objects.album import album

#############################################################
# This is the backend for the regular MythMusic backend.
# Information is pulled from the 'mythconverg' mysql db
#############################################################
class Backend(gobject.GObject):
    #Setup signals
    __gsignals__ =  { 
        "query-complete": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "deselected": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
        }
    
    def __init__(self, music_player):
        gobject.GObject.__init__(self)
        
        self.music_player = music_player
        self.dbMgr = music_player.dbMgr
        
        self.directories = {}
        self.cache_artists = {}
        self.cache_albums = {}
        self.cache_albums_by_artistID = {}
        self.cache_songs_by_albumID = {}
        self.cache_songs_by_artistID = {}
        
        self.get_directories()
        
    #Setup a list of directory entries
    def get_directories(self):
        sql = "SELECT * FROM music_directories"
        if self.music_player.glossMgr.debug: print "Music Artist SQL: " + sql
        
        dbMgr = mythDB()
        results = dbMgr.run_sql(sql)
        dbMgr.close_db()

        #self.directories = [len(results)]
        for record in results:
            id = int(record[0])
            directory = record[1]
            self.directories[str(id)] = directory
            
    #Returns a list of artist objects
    def get_artists(self, no_cache = False):
        #Check cache
        if (not no_cache) and (len(self.cache_artists) > 0):
            return self.cache_artists.values()
        
        #Load the sql
        sql = "SELECT * FROM music_artists ORDER BY artist_name"
        if self.music_player.glossMgr.debug: print "Music Artist SQL: " + sql
            
        #results = self.dbMgr.run_sql(sql)
        dbMgr = mythDB()
        results = dbMgr.run_sql(sql)
        dbMgr.close_db()
        
        #Check for null return
        if results == None:
            print "MusicPlayer: No connection to DB or no artists found in DB"
            return None
        
        pixbuf = None
        artists = []
        #Else add the entries in    
        for record in results:
            tempArtist = artist(self.music_player)
            tempArtist.import_from_mythObject(record)
            artists.append(tempArtist)
            #self.artistImageRow.add_object(tempArtist)
            #time.sleep(0.01) #Arbitary sleep time to avoid CPU bound status
            self.cache_artists[tempArtist.artistID] = tempArtist
        
        return artists
    
    def get_artist_by_ID(self, id, no_cache = False):
        #Check cache
        if (not no_cache) and (len(self.cache_artists) > 0):
            return self.cache_artists[id]
        else:
            self.get_artists()
            self.cache_artists[id]
            
    #Returns a list of all album objects
    def get_albums(self, no_cache = False):
        #Check cache
        if (not no_cache) and (len(self.cache_albums) > 0):
            return self.cache_albums.values()
        
        #Load the sql
        sql = "SELECT * FROM music_albums ORDER BY album_name"
        if self.music_player.glossMgr.debug: print "Music Albums SQL: " + sql
            
        #results = self.dbMgr.run_sql(sql)
        dbMgr = mythDB()
        results = dbMgr.run_sql(sql)
        dbMgr.close_db()
        
        #Check for null return
        if results == None:
            print "MusicPlayer: No connection to DB or no albums found in DB"
            return None
        
        albums = []
        #Else add the entries in    
        for record in results:
            tempAlbum = album(self.music_player)
            tempAlbum.import_from_mythObject(record)
            albums.append(tempAlbum)
            #self.artistImageRow.add_object(tempArtist)
            #time.sleep(0.01) #Arbitary sleep time to avoid CPU bound status
            self.cache_albums[tempAlbum.albumID] = tempAlbum
        
        return albums
    
    #Return a specific album based on its ID
    def get_album_by_ID(self, id, no_cache = False):
        #Check cache
        if (not no_cache) and (len(self.cache_albums) > 0):
            return self.cache_albums[id]
        else:
            self.get_albums()
            self.cache_albums[id]
    
    #Given an artistID, returns a list of albums for them
    def get_albums_by_artistID(self, id, no_cache = False):
        #Check cache
        if (not no_cache) and (self.cache_albums_by_artistID.has_key(str(id))):
            self.emit("query-complete")
            return self.cache_albums_by_artistID[str(id)]
        
        #Generate some SQL
        sql = "SELECT * FROM music_albums where artist_id='%s'" % (str(id))
        if self.music_player.glossMgr.debug: print "Music Album SQL: " + sql
            
        #results = self.dbMgr.run_sql(sql)
        dbMgr = mythDB()
        results = dbMgr.run_sql(sql)
        dbMgr.close_db()
        
        #Check for null return
        if results == None:
            print "MusicPlayer: No connection to DB or no albums found with ID %s" % (str(id))
            return None
        
        pixbuf = None
        albums = []
        #Else add the entries in    
        for record in results:
            tempAlbum = album(self.music_player)
            tempAlbum.import_from_mythObject(record)
            albums.append(tempAlbum)
            #self.artistImageRow.add_object(tempArtist)
            
        self.emit("query-complete")
        self.cache_albums_by_artistID[str(id)] = albums
        return albums
    
    #Given an albumID, returns a list of songs on the album
    def get_songs_by_albumID(self, id, no_cache = False):
        #Check cache
        if (not no_cache) and (self.cache_songs_by_albumID.has_key(str(id))):
            self.emit("query-complete")
            return self.cache_songs_by_albumID[str(id)]
        
        
        #Generate some SQL
        sql = "SELECT * FROM music_songs where album_id='%s'" % (str(id))
        if self.music_player.glossMgr.debug: print "Music Song SQL: " + sql
            
        #results = self.dbMgr.run_sql(sql)
        dbMgr = mythDB()
        results = dbMgr.run_sql(sql)
        dbMgr.close_db()
        
        #Check for null return
        if results == None:
            print "MusicPlayer: No connection to DB or no songs found with ID %s" % (str(id))
            return None
        
        pixbuf = None
        songs = []
        #Else add the entries in    
        for record in results:
            tempSong = song(self.music_player)
            self.import_song_from_mythObject(record, tempSong)
            tempSong.directory = self.directories[str(tempSong.directory_id)]
            songs.append(tempSong)
            #self.artistImageRow.add_object(tempArtist)
        self.emit("query-complete")
        self.cache_songs_by_albumID[str(id)] = songs
        return songs
    
    #Given an artistID, returns a list of songs on the album
    def get_songs_by_artistID(self, id, no_cache = False):
        #Check cache
        if (not no_cache) and (self.cache_songs_by_artistID.has_key(str(id))):
            self.emit("query-complete")
            return self.cache_songs_by_artistID[str(id)]
        
        
        #Generate some SQL
        sql = "SELECT * FROM music_songs where artist_id='%s'" % (str(id))
        if self.music_player.glossMgr.debug: print "Music Song SQL: " + sql
            
        #results = self.dbMgr.run_sql(sql)
        dbMgr = mythDB()
        results = dbMgr.run_sql(sql)
        dbMgr.close_db()
        
        #Check for null return
        if results == None:
            print "MusicPlayer: No connection to DB or no songs found with artist ID %s" % (str(id))
            return None
        
        pixbuf = None
        songs = []
        #Else add the entries in    
        for record in results:
            tempSong = song(self.music_player)
            self.import_song_from_mythObject(record, tempSong)
            tempSong.directory = self.directories[str(tempSong.directory_id)]
            songs.append(tempSong)
            #self.artistImageRow.add_object(tempArtist)
        self.emit("query-complete")
        self.cache_songs_by_artistID[str(id)] = songs
        return songs
    
    def import_song_from_mythObject(self, mythObject, song):
        try:
            song.songID = mythObject[0]
            song.filename = mythObject[1]
            song.name = mythObject[2]
            song.track = mythObject[3]
            song.artistID = mythObject[4]
            song.albumID = mythObject[5]
            song.genreID = mythObject[6]
            song.year = mythObject[7]
            song.length = mythObject[8]
            song.numplays = mythObject[9]
            song.rating = mythObject[10]
            song.lastplay = mythObject[11]
            song.date_entered = mythObject[12]
            song.date_modified = mythObject[13]
            song.format = mythObject[14]
            song.mythdigest = mythObject[15]
            song.size = mythObject[16]
            song.description = mythObject[17]
            song.comment = mythObject[18]
            song.disc_count = mythObject[19]
            song.disc_number = mythObject[20]
            song.track_count = mythObject[21]
            song.start_time = mythObject[22]
            song.stop_time = mythObject[23]
            song.eq_preset = mythObject[24]
            song.retrieve_volume = mythObject[25]
            song.sample_rate = mythObject[26]
            song.bitrate = mythObject[27]
            song.bpm = mythObject[28]
            song.directory_id = mythObject[29]
            
        except IndexError, e:
            print "Music_Player: Found difference in DB structure for songs. Attempting to continue."
    