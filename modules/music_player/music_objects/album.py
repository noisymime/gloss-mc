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
        