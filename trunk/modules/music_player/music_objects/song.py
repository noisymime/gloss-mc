import eyeD3
import os
import pygtk
import gtk

class song:
    filename = None
    
    def __init__(self, music_player):
        self.music_player = music_player
        self.base_dir = music_player.base_dir
    
    def import_from_mythObject(self, mythObject):
        try:
            self.songID = mythObject[0]
            self.filename = mythObject[1]
            self.name = mythObject[2]
            self.track = mythObject[3]
            self.artistID = mythObject[4]
            self.albumID = mythObject[5]
            self.genreID = mythObject[6]
            self.year = mythObject[7]
            self.length = mythObject[8]
            self.numplays = mythObject[9]
            self.rating = mythObject[10]
            self.lastplay = mythObject[11]
            self.date_entered = mythObject[12]
            self.date_modified = mythObject[13]
            self.format = mythObject[14]
            self.mythdigest = mythObject[15]
            self.size = mythObject[16]
            self.description = mythObject[17]
            self.comment = mythObject[18]
            self.disc_count = mythObject[19]
            self.disc_number = mythObject[20]
            self.track_count = mythObject[21]
            self.start_time = mythObject[22]
            self.stop_time = mythObject[23]
            self.eq_preset = mythObject[24]
            self.retrieve_volume = mythObject[25]
            self.sample_rate = mythObject[26]
            self.bitrate = mythObject[27]
            self.bpm = mythObject[28]
            
        except IndexError, e:
            print "Music_Player: Found difference in DB structure for songs. Attempting to continue."
    
    def get_image(self):
        return self.get_image_from_ID3()
    
    #Tries to retrieve an image (pixbuf) from a song
    #Returns None if nothing found
    def get_image_from_ID3(self):
        #Basic check first up to make sure the filename is set
        if self.filename is None:
            return None
        
        tag = eyeD3.Tag()
        filename = self.base_dir + "/" + self.filename
        print filename
        
        #Make sure the file exists and we can read it
        if not os.access(filename, os.R_OK):
            return None
        
        tag.link(filename)
        """
        print tag.getArtist()
        print tag.getAlbum()
        print tag.getTitle()
        """
        
        images = tag.getImages()
        for img in images:
            #str(img.picTypeToString(img.pictureType) + " Image"), \
            #print "%s: [Size: %d bytes] [Type: %s]" % "test", len(img.imageData), img.mimeType
            #print img.picTypeToString(img.pictureType) + " Image"
                    
            print "Image Mine Type: " + str(img.mimeType)
            data = img.imageData
            loader = gtk.gdk.PixbufLoader()
            loader.write(pixbuf)
            loader.close()
            return loader.get_pixbuf()
            
            
