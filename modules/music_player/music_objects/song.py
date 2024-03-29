import eyeD3
import os
import pygtk
import gtk
import gobject

class song:
    filename = None
    
    def __init__(self, music_player):
        self.music_player = music_player
        self.base_dir = music_player.base_dir
    
        self.songID = None
        self.filename = None
        self.directory = None
        self.name = None
        self.track = None
        self.artistID = None
        self.albumID = None
        self.genreID = None
        self.year = None
        self.length = None
        self.numplays = None
        self.rating = None
        self.lastplay = None
        self.date_entered = None
        self.date_modified = None
        self.format = None
        self.mythdigest = None
        self.size = None
        self.description = None
        self.comment = None
        self.disc_count = None
        self.disc_number = None
        self.track_count = None
        self.start_time = None
        self.stop_time = None
        self.eq_preset = None
        self.retrieve_volume = None
        self.sample_rate = None
        self.bitrate = None
        self.bpm = None
    
    def get_image(self):
        return self.get_image_from_ID3()
    
    #Tries to retrieve an image (pixbuf) from a song
    #Returns None if nothing found
    def get_image_from_ID3(self):
        #Basic check first up to make sure the filename is set
        if self.filename is None:
            if self.music_player.glossMgr.debug: print "Music_Player: Attempting to load ID3 image from song '%s', but have no filename to look up" % self.name
            return None
        
        tag = eyeD3.Tag()
        filename = self.base_dir + "/" + self.directory + "/" + self.filename
        #print filename
        
        #Make sure the file exists and we can read it
        if not os.access(filename, os.R_OK):
            if self.music_player.glossMgr.debug: print "Music_Player: Attempting to read ID3 image on file '%s', however do not appear to have read permission" % filename
            return None
        
        tag.link(filename)
        if self.music_player.glossMgr.debug: print "Music_Player: eyeD3 tag linked to file '%s'" % filename
        
        images = tag.getImages()
        if self.music_player.glossMgr.debug: print "Music_Player: found %i images in file '%s'" % (len(images), filename)
        
        for img in images:   
            try:                 
                if self.music_player.glossMgr.debug: print "Music_Player: Image Mine Type: " + str(img.mimeType)
                
                data = img.imageData
                loader = gtk.gdk.PixbufLoader()
                loader.write(data)
                loader.close()
                if self.music_player.glossMgr.debug: print "Music_Player:Image successfully written to pixbuf loader: " + str(img.mimeType)
                return loader.get_pixbuf()
            except gobject.GError:
                if self.music_player.glossMgr.debug:
                    print "Music_Player: Found image in ID3 for song '%s' but could not load it" % (self.filename)
            
