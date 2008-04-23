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
        self.cache_artists = []
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
            return self.cache_artists
        
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
            time.sleep(0.01) #Arbitary sleep time to avoid CPU bound status
        
        self.cache_artists = artists
        return artists
    
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
            tempSong.import_from_mythObject(record)
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
            tempSong.import_from_mythObject(record)
            tempSong.directory = self.directories[str(tempSong.directory_id)]
            songs.append(tempSong)
            #self.artistImageRow.add_object(tempArtist)
        self.emit("query-complete")
        self.cache_songs_by_artistID[str(id)] = songs
        return songs
    