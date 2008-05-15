class album:
    
    def __init__(self, music_player):
        self.music_player = music_player
    
    def import_from_mythObject(self, mythObject):
        try:
            self.albumID = mythObject[0]
            self.artistID = mythObject[1]
            self.name = mythObject[2]
            self.year = mythObject[3]
            self.compilation = mythObject[4]
            
        except IndexError, e:
            print "Music_Player: Found difference in DB structure for albums. Attempting to continue."
        
    def get_image(self):
        #First way to get an image is via the songs on this album
        songs = self.music_player.backend.get_songs_by_albumID(self.albumID)
        
        for song in songs:
            pixbuf = song.get_image_from_ID3()
            if not pixbuf is None:
                return pixbuf
        
        #If nothing has been found return the default
        return self.get_default_image()
    
    #Returns the pixbuf of the default artist image
    def get_default_image(self):
        return self.music_player.default_artist_cover