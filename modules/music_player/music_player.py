import pygtk
import gtk
import clutter
#import thread, time
from modules.music_player.backends.myth_music import Backend
from modules.music_player.lastFM_interface import lastFM_interface
from modules.music_player.music_object_row import MusicObjectRow
from ui_elements.image_frame import ImageFrame
from ui_elements.label_list import LabelList

class Module:
    title = "Music"
    num_columns = 6
    sleep_time = 0.2

    def __init__(self, glossMgr, dbMgr):
        self.stage = glossMgr.get_stage()
        self.glossMgr = glossMgr
        self.dbMgr = dbMgr
        self.setup_ui()
        self.albums = []
        self.artists = []
        self.songs = []
        
        self.backend = Backend(self)
        
        self.artistImageRow = MusicObjectRow(self.glossMgr, self.stage.get_width(), 200, self.num_columns, self)
        
        self.lastFM = lastFM_interface()
        self.base_dir = self.dbMgr.get_setting("MusicLocation")
        self.images_dir = self.get_images_dir()
        print "Music Base Dir: " + self.base_dir
        
        self.is_playing = False
        #self.load_albums()
        self.artists = self.backend.get_artists()
        #thread.start_new_thread(self.load_artists, ())
        
        
    def setup_ui(self):
        self.menu_image = self.glossMgr.themeMgr.get_texture("music_menu_image", None, None)
        
        self.default_artist_cover = self.glossMgr.themeMgr.get_texture("music_default_artist_image", None, None).get_pixbuf()
        
    
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
        
        if (event.keyval == clutter.keysyms.Left) or (event.keyval == clutter.keysyms.Right):
            #calculate a period of time the loading threads should sleep for when a timline is in progress
            #self.sleep_time = float(MusicObjectRow.frames) / float(MusicObjectRow.fps)
            duration = float(MusicObjectRow.frames) / float(MusicObjectRow.fps)
            self.artistImageRow.input_queue.input(event)
            self.artistImageRow.sleep = True
            
            #Just a little test code
            artist = self.artistImageRow.get_current_object()
            albums = self.backend.get_albums_by_artistID(artist.artistID)
            self.list1.clear()
            for album in albums:
                self.list1.add_item(album.name)
                #name_string += album.name
            self.list1.display()
            #self.tmpLabel.set_text(name_string)
            pixbuf = albums[0].get_image()
            if not pixbuf is None:
                self.main_img.set_pixbuf(pixbuf)
        
    def begin(self, glossMgr):
        
        #Create a backdrop for the player. In this case we just use the same background as the menus
        self.backdrop = glossMgr.get_themeMgr().get_texture("background", None, None)
        self.backdrop.set_size(self.stage.get_width(), self.stage.get_height())
        self.backdrop.set_opacity(0)
        self.backdrop.show()
        self.stage.add(self.backdrop)
        #Fade the backdrop in
        self.timeline_backdrop = clutter.Timeline(10,40)
        self.alpha = clutter.Alpha(self.timeline_backdrop, clutter.ramp_inc_func)
        self.backdrop_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=self.alpha)
        self.backdrop_behaviour.apply(self.backdrop)
        
        #Load in the initial images:
        self.artistImageRow.objectLibrary = self.artists
        self.artistImageRow.load_image_range(0, self.num_columns)
        
        self.stage.add(self.artistImageRow)
        self.artistImageRow.set_opacity(0)
        self.artistImageRow.select_first()
        self.artistImageRow.show()
        self.backdrop_behaviour.apply(self.artistImageRow)
        
        #Just a nasty temp label for outputting stuff
        self.list1 = LabelList(5)
        self.list1.set_position(self.stage.get_width()/2, 350)
        self.stage.add(self.list1)
        """
        self.tmpLabel = clutter.Label()
        self.tmpLabel.set_color(clutter.color_parse('White'))
        self.tmpLabel.set_position(0, 350)
        self.tmpLabel.set_text("Test")
        self.tmpLabel.show()
        self.stage.add(self.tmpLabel)
        """
        
        #The preview img
        self.main_img = ImageFrame(None, 300, True) #clutter.Texture()
        self.main_img.set_position(30, 400)
        self.main_img.set_rotation(clutter.Y_AXIS, 45, self.main_img.get_width(), 0, 0)
        self.main_img.show()
        self.stage.add(self.main_img)
        
        self.timeline_backdrop.start()
        
        #Load the rest of the images
        #thread.start_new_thread(self.load_image_range, (self.num_columns, len(self.artists)-1))
        self.timeline_backdrop.connect("completed", self.artistImageRow.load_image_range_cb)
        #self.load_image_range(self.num_columns, len(self.artists)-1)
        
        
    
        
    def stop(self):
        pass
        
    def pause(self):
        pass
        
    def unpause(self):
        pass
    
    def load_songs(self):
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
            
