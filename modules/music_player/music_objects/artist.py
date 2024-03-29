import pygtk
import gtk
import gobject
import os
import threading
from modules.music_player.music_objects.music_object import MusicObject
from utils.ThumbnailMgr import ThumbnailMgr

class artist(MusicObject):
    
    artistID = None
    name = None
    image = None
    
    def __init__(self, music_player):
        MusicObject.__init__(self)
        self.music_player = music_player
    
    def import_from_mythObject(self, mythObject):
        try:
            #self.artistID = mythObject['artist_id']
            #self.name = mythObject['artist_name']
            #self.image = mythObject['artist_image']
            self.artistID = mythObject[0]
            self.name = mythObject[1]
            self.image = mythObject[2]
            
            if self.image is None: self.image = "unset"

                
        except IndexError, e:
            print "Music_Player: Found difference in DB structure for artists. Attempting to continue."
    
    def update_db(self):
        print "Music_Player: Looks like this is the first time the Music Player has been started. Attempting to upgrade DB"
        sql = "ALTER TABLE music_artists ADD artist_image TEXT AFTER artist_name;"
        self.music_player.dbMgr.run_sql(sql)
        print "Music_Player: DB Upgrade completed"
            
    
    def get_image(self, size = None):
        thumb_mgr = ThumbnailMgr()
        #If image is still equal to None it means that the artist_image column did not exist in the db, we should create it.
        if self.image is None:
            self.update_db()
            self.image = "unset"
        #If there was something in self.image, means we've probably already got a pic
        if not self.image == "unset":
            filename = self.music_player.images_dir + "artists/" + self.image
            try:
                #If a size has been given, we use the thumbnail mgr, else return the full thing
                if not size is None:
                    pixbuf = thumb_mgr.get_pixbuf(filename, size)
                else:
                    pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
            except gobject.GError, e:
                print "Music_Player: Attempted to open file '%s', but it does not exist. Using defualt image." % (filename)
                return self.get_default_image()
            
            return pixbuf
        #If self.image is a eqaul to 'unset', means the column exists but that the image entry is blank, we should try to find one
        else:
            #We send a request off to LastFM to grab an image.
            #This will emit the "image-found" signal when and if it was successful
            #gobject.idle_add(self.get_image_from_lastFM)
            #try:
            thread = self.queue_thread(self.get_image_from_lastFM)
                #thread = threading.Thread(target=self.get_image_from_lastFM)
                #thread.start()
            #except thread.error, e:
                #"Music_Player: Attempted to start too many threads"
                #Returning None forces the default image to be used
            #    return None
            return self.PENDING_DOWNLOAD
        
    def get_image_from_lastFM(self):
        pixbuf = self.music_player.lastFM.get_artist_image(self.name)
        if not pixbuf is None: 
            self.save_image(pixbuf)
            
        self.thread_finished()
        return False
    
    #Saves an image (pixbuf) to file and updates the Myth db
    def save_image(self, pixbuf):
        base_dir = self.music_player.images_dir + "artists/"
        #Check to make sure the above directory exists
        if not os.path.isdir(base_dir):
            try:
                os.makedirs(base_dir, int('777',8))
            except OSError:
                print "Music Player Error: Unable to write to music directory '%s'" % (base_dir)
                return
        
        self.name = self.name.replace("'","")
        self.name = self.name.replace("/","_")
        self.name = self.name.replace("\\","_")
        filename = base_dir + self.name + ".png"
        try:
            pixbuf.save(filename, "png")
        except gobject.GError:
            print "Music_Player: Permission denied trying to save '%s'" % (filename)
            return
        
        #Now insert an entry into the db for this 
        filename_short = self.name + ".png"
        sql = "UPDATE music_artists SET artist_image = '%s' WHERE artist_id = '%s'" % (filename_short, self.artistID)
        self.music_player.dbMgr.run_sql(sql)
        
        self.image = filename_short
        
        #Let off a signal to say the image is ready
        self.emit("image-found")
        
    #Returns the pixbuf of the default artist image
    def get_default_image(self):
        return self.music_player.default_artist_cover