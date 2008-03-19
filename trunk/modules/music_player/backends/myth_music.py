import time
from modules.music_player.music_objects.song import song
from modules.music_player.music_objects.artist import artist
from modules.music_player.music_objects.album import album

#############################################################
# This is the backend for the regular MythMusic backend.
# Information is pulled from the 'mythconverg' mysql db
#############################################################
class Backend:
    
    def __init__(self, music_player):
        self.music_player = music_player
        self.dbMgr = music_player.dbMgr
    
    #Returns a list of artist objects
    def get_artists(self):
        #Generate some SQL to retrieve videos that were in the final_file_list
        #Load the videos into the cover viewer
        sql = "SELECT * FROM music_artists"
        if self.music_player.glossMgr.debug: print "Music Artist SQL: " + sql
            
        results = self.dbMgr.run_sql(sql)
        
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
        
        return artists
    
    #Given an artistID, returns a list of albums for them
    def get_albums_by_artistID(self, id):
        #Generate some SQL
        sql = "SELECT * FROM music_albums where artist_id='%s'" % (str(id))
        if self.music_player.glossMgr.debug: print "Music Album SQL: " + sql
            
        results = self.dbMgr.run_sql(sql)
        
        #Check for null return
        if results == None:
            print "MusicPlayer: No connection to DB or no albums found with ID %s" % (str(id))
            return None
        
        pixbuf = None
        artists = []
        #Else add the entries in    
        for record in results:
            tempAlbum = album(self.music_player)
            tempAlbum.import_from_mythObject(record)
            artists.append(tempAlbum)
            #self.artistImageRow.add_object(tempArtist)
        return artists
    
    #Given an albumID, returns a list of songs on the album
    def get_songs_by_albumID(self, id):
        #Generate some SQL
        sql = "SELECT * FROM music_songs where album_id='%s'" % (str(id))
        if self.music_player.glossMgr.debug: print "Music Song SQL: " + sql
            
        results = self.dbMgr.run_sql(sql)
        
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
            songs.append(tempSong)
            #self.artistImageRow.add_object(tempArtist)
        return songs
    