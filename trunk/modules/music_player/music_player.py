import pygtk
import gtk
import clutter
import thread
from modules.music_player.music_objects.song import song
from modules.music_player.music_objects.artist import artist
from modules.music_player.music_objects.album import album
from modules.music_player.lastFM_interface import lastFM_interface
from ui_elements.image_row import ImageRow
from ui_elements.image_frame import ImageFrame

class Module():
    title = "Music"
    num_columns = 6

    def __init__(self, glossMgr, dbMgr):
        self.stage = glossMgr.get_stage()
        self.glossMgr = glossMgr
        self.dbMgr = dbMgr
        self.setup_ui()
        self.albums = []
        self.artists = []
        self.songs = []
        
        self.imageRow = ImageRow(self.glossMgr, self.stage.get_width(), 200, self.num_columns)
        
        self.lastFM = lastFM_interface()
        self.base_dir = self.dbMgr.get_setting("MusicLocation")
        self.images_dir = self.get_images_dir()
        #print "Music Base Dir: " + self.base_dir
        
        self.is_playing = False
        #self.load_albums()
        self.load_artists()
        
        
    def setup_ui(self):
        self.menu_image = self.glossMgr.themeMgr.get_texture("music_menu_image", None, None)
    
    #Get the images dir setting our of the DB
    #But also creates the setting if it doesn't already exist
    def get_images_dir(self):
        images_dir = self.dbMgr.get_setting("GlossMusicImgLocation")
        
        if images_dir is None:
            #We need to create the setting
            #Default value is the same as the music base_dir + covers
            images_dir = self.base_dir + "/.images/"
            images_dir = images_dir.replace("//", "/") #Just a silly little check
            self.dbMgr.set_setting("GlossMusicImgLocation", images_dir)
            
        return images_dir
    
    #Action to take when menu item is selected
    def action(self):
        return self
        
    def on_key_press_event (self, stage, event):
        if event.keyval == clutter.keysyms.p:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()
        
    def begin(self, glossMgr):
        
        #Create a backdrop for the player. In this case we just use the same background as the menus
        self.backdrop = glossMgr.get_themeMgr().get_texture("background", None, None)
        self.backdrop.set_size(self.stage.get_width(), self.stage.get_height())
        self.backdrop.set_opacity(0)
        self.backdrop.show()
        self.stage.add(self.backdrop)
        #Fade the backdrop in
        timeline_backdrop = clutter.Timeline(10,40)
        alpha = clutter.Alpha(timeline_backdrop, clutter.ramp_inc_func)
        self.backdrop_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
        self.backdrop_behaviour.apply(self.backdrop)
        timeline_backdrop.start()
        
        #Load in the initial images:
        self.load_image_range(0, self.num_columns)
        
        self.stage.add(self.imageRow)
        self.imageRow.show()
        
        #Load the rest of the images
        thread.start_new_thread(self.load_image_range, (self.num_columns, len(self.artists)-1))
        #self.load_image_range(self.num_columns, len(self.artists)-1)
        
    def load_image_range(self, start, end, thread_data = None):
        for i in range(start, end):
            artist = self.artists[i]
            pixbuf = artist.get_image()
            tmpImage = clutter.Texture()
            if pixbuf == artist.PENDING_DOWNLOAD:
                artist.connect("image-found", self.set_image_cb, artist, tmpImage)
            elif not pixbuf is None:
                #tmpImage.set_pixbuf(pixbuf)
                tmpImage = ImageFrame(pixbuf, self.imageRow.image_size)
                self.imageRow.add_texture_group(tmpImage)
        
    #A simple callback funtion to set the image of an artist/album after it has completed a download
    def set_image_cb(self, data, music_object, tmpImage):
        #if self.glossMgr.debug:
        print "Image for music_obect '%s' downloaded" % (music_object.name)
        pixbuf = music_object.get_image()
        if not pixbuf is None:
                tmpImage.set_pixbuf(pixbuf)
        
    def stop(self):
        pass
        
    def pause(self):
        pass
        
    def unpause(self):
        pass
    
    def load_albums(self):
        #Generate some SQL to retrieve videos that were in the final_file_list
        #Load the videos into the cover viewer
        sql = "SELECT * FROM music_songs" # WHERE filename IN ("
        if self.glossMgr.debug: print "Music SQL: " + sql
            
        results = self.dbMgr.run_sql(sql)
        
        #Check for null return
        if results == None:
            print "MusicPlayer: No connection to DB or no songs found in DB"
            return None
        
        pixbuf = None
        #Else add the entries in    
        for record in results:
            tempSong = song(self)
            tempSong.import_from_mythObject(record)
            self.songs.append(tempSong)
            
            
            if not tempSong.get_image()is None:
                pixbuf = tempSong.get_image()
                break
            #print filename
            #tempSong.set_file(filename)
        
        if not pixbuf is None:
            loader = gtk.gdk.PixbufLoader()
            loader.write(pixbuf)
            loader.close()
            pixbuf = loader.get_pixbuf()
            self.tmpImage = clutter.Texture()
            self.tmpImage.set_pixbuf(pixbuf)
        
    def load_artists(self):
        #Generate some SQL to retrieve videos that were in the final_file_list
        #Load the videos into the cover viewer
        sql = "SELECT * FROM music_artists" # WHERE filename IN ("
        if self.glossMgr.debug: print "Music Artist SQL: " + sql
            
        results = self.dbMgr.run_sql(sql)
        
        #Check for null return
        if results == None:
            print "MusicPlayer: No connection to DB or no artists found in DB"
            return None
        
        pixbuf = None
        #Else add the entries in    
        for record in results:
            tempArtist = artist(self)
            tempArtist.import_from_mythObject(record)
            self.artists.append(tempArtist)
            
            """
            if not tempArtist.get_image()is None:
                pixbuf = tempArtist.get_image()
                break
            """
            #print filename
            #tempSong.set_file(filename)
        """
        if not pixbuf is None:
            self.tmpImage = clutter.Texture()
            self.tmpImage.set_pixbuf(pixbuf)
        """