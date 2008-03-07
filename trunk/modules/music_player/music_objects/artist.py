import pygtk
import gtk

class album:
    artistID, name, image = None
    
    def __init__(self, music_player):
        self.music_player = music_player
    
    def import_from_mythObject(self, mythObject):
        try:
            self.artistID = mythObject[0]['artist_id']
            self.name = mythObject[1]
            self.image = mythObject[2]
                
        except IndexError, e:
            print "Music_Player: Found difference in DB structure for artists. Attempting to continue."
    
    def insert_into_db(self):
        if self.image is None:
            sql = "ALTER TABLE music_artists ADD image TEXT AFTER artist_name;"
    
    def get_image(self):
        if not self.image is None:
            return gtk.gdk.pixbuf_new_from_file(self.image)
        else:
            return self.get_image_from_lastFM()
        
    def get_image_from_lastFM(self):
        return self.music_player.lastFM
        