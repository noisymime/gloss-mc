import pygtk
import gobject
import gtk
import clutter
import threading
from modules.music_player.backends.myth_music import Backend
from modules.music_player.lastFM_interface import lastFM_interface
from modules.music_player.music_object_row import MusicObjectRow
from modules.music_player.playlist import Playlist
from modules.music_player.play_screen import PlayScreen
from ui_elements.image_frame import ImageFrame
from ui_elements.image_clone import ImageClone
from ui_elements.label_list import LabelList

class Module:
    CONTEXT_HEADINGS, CONTEXT_ROW, CONTEXT_ALBUM_LIST, CONTEXT_SONG_LIST, CONTEXT_PLAY_SCR = range(5)
    
    title = "Music"
    num_columns = 6
    sleep_time = 0.3
    
    delay = 1

    def __init__(self, glossMgr, dbMgr):
        self.stage = glossMgr.get_stage()
        self.glossMgr = glossMgr
        self.dbMgr = dbMgr
        self.setup_ui()
        self.albums = []
        self.artists = []
        self.songs = []
        
        self.backend = Backend(self)
        self.playlist = Playlist(self)
        
        self.artistImageRow = MusicObjectRow(self.glossMgr, self.stage.get_width(), 200, self.num_columns, self)
        self.play_screen = PlayScreen(self)
        
        #This is the current input context
        self.current_context = self.CONTEXT_ROW
        self.previous_context = None
        
        self.lastFM = lastFM_interface()
        self.base_dir = self.dbMgr.get_setting("MusicLocation")
        self.images_dir = self.get_images_dir()
        print "Music Base Dir: " + self.base_dir
        
        self.is_playing = False
        self.artists = self.backend.get_artists()
        self.timeout_id = 0
        self.queue_id = 0
        
        
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
        
        #React based on the current input context
        if self.current_context == self.CONTEXT_ROW:
            if (event.keyval == clutter.keysyms.Left) or (event.keyval == clutter.keysyms.Right):
                #First check if there's any current timeouts and if there is, clear it
                #if not self.timeout_id == 0: gobject.source_remove(self.timeout_id)
                self.artistImageRow.sleep = True
                self.artistImageRow.input_queue.input(event)
                #self.artistImageRow.input_queue.connect("queue-flushed", self.start_delay, self.load_albums, None)
                #self.artistImageRow.objectLibrary[0].pause_threads()
                if self.queue_id == 0: self.queue_id = self.artistImageRow.input_queue.connect("queue-flushed", self.load_albums)
                self.artistImageRow.sleep = False
                
                
            elif (event.keyval == clutter.keysyms.Down):
                self.list1.select_first_elegant()
                self.list2.show()
                self.current_context = self.CONTEXT_ALBUM_LIST
            
            elif (event.keyval == clutter.keysyms.Return):
                artist = self.artistImageRow.get_current_object()
                songs = self.backend.get_songs_by_artistID(artist.artistID)
                self.playlist.clear_songs()
                self.playlist.add_songs(songs)
                self.playlist.play()
                
                self.play_screen.append_playlist(self.playlist)
                self.play_screen.display(self.artistImageRow.get_current_texture())#.get_texture())
                
                self.current_context = self.CONTEXT_PLAY_SCR
                self.previous_context = self.CONTEXT_ROW
                
        elif self.current_context == self.CONTEXT_ALBUM_LIST:
            
            if (event.keyval == clutter.keysyms.Up):
                self.artistImageRow.external_timeline = self.list1.timeline
                #If we're at the top of the list already, we change focus bar to the image_row
                if self.list1.selected == 0:
                    self.list1.select_none_elegant()
                    self.list2.hide()
                    self.current_context = self.CONTEXT_ROW
                else:
                    self.list1.input_queue.input(event)
                    self.update_main_img()
            elif (event.keyval == clutter.keysyms.Down):
                self.list1.input_queue.input(event)
                #if self.artist_queue_id == 0: self.artist_queue_id = self.list1.input_queue.connect("queue-flushed", self.update_main_img)
                #self.update_main_img()
                
        elif self.current_context == self.CONTEXT_SONG_LIST:
            pass
        
        elif self.current_context == self.CONTEXT_PLAY_SCR:
            if (event.keyval == clutter.keysyms.Escape):
                self.current_context = self.previous_context
                self.play_screen.hide()
    
    #Fills self.list2 with songs from an album
    def process_songlist_from_album(self, list_item, album):
        #print "got album %s" % album.name
        songs = self.backend.get_songs_by_albumID(album.albumID)
        self.list2.clear()
        for song in songs:
            tmpItem = self.list2.add_item(song.name)
        self.list2.display()
    
    #Loads albums into List1
    def load_albums(self, queue):
        if self.artistImageRow.input_queue.handler_is_connected(self.queue_id): 
            self.artistImageRow.input_queue.disconnect(self.queue_id)
            self.queue_id = 0
        #Just a little test code
        self.artistImageRow.objectLibrary[0].unpause_threads()
        artist = self.artistImageRow.get_current_object()
        thread = threading.Thread(target=self.backend.get_albums_by_artistID, args=(artist.artistID,))
        thread.start()
        #thread.start_new_thread(self.backend.get_albums_by_artistID, (artist.artistID,))
        self.conn_id = self.backend.connect("query-complete", self.update_for_albums, artist)
        
    def update_for_albums(self, data, artist = None):
        if not artist == self.artistImageRow.get_current_object(): return
        if not self.backend.handler_is_connected(self.conn_id): 
            return
        self.backend.disconnect(self.conn_id)
        self.current_albums = self.backend.get_albums_by_artistID(artist.artistID)
        
        clutter.threads_enter()
        self.list1.clear()
        for album in self.current_albums:
            tmpItem = self.list1.add_item(album.name)
            tmpItem.connect("selected", self.process_songlist_from_album, album)
        self.list1.display()
        self.update_main_img()
        clutter.threads_leave()
        
    def update_main_img(self, data = None):
        #clutter.threads_enter()
        pixbuf = self.current_albums[self.list1.selected].get_image()
        if not pixbuf is None:
            self.main_img.set_pixbuf(pixbuf)
            #clutter.threads_leave()
            self.main_img.show()
        else:
            #clutter.threads_enter()
            self.main_img.set_pixbuf(None)

            self.main_img.hide()
        #clutter.threads_leave()

        
    def begin(self, glossMgr):
        self.timeline_loading = clutter.Timeline(80,160)
        self.alpha = clutter.Alpha(self.timeline_loading, clutter.ramp_inc_func)
        self.opacity_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=self.alpha)
        
        #Create a backdrop for the player. In this case we just use the same background as the menus
        self.backdrop = glossMgr.get_themeMgr().get_texture("background", None, None)
        self.backdrop.set_size(self.stage.get_width(), self.stage.get_height())
        self.backdrop.set_opacity(0)
        self.backdrop.show()
        self.stage.add(self.backdrop)
        self.opacity_behaviour.apply(self.backdrop)
        
        self.loading_img = ImageClone(glossMgr.get_current_menu().get_current_item().get_main_texture())
        self.loading_img.show()
        self.stage.add(self.loading_img)
        glossMgr.get_current_menu().get_current_item().get_main_texture().hide()
        
        x = int( (self.stage.get_width() - self.loading_img.get_width()) / 2 )
        y = int( (self.stage.get_height() - self.loading_img.get_height()) / 2 )
        knots = (\
                 (int(self.loading_img.get_x()), int(self.loading_img.get_y()) ),\
                 (x, y)\
                 )
        self.path_behaviour = clutter.BehaviourPath(knots = knots, alpha = self.alpha)
        self.path_behaviour.apply(self.loading_img)
        
        self.artistImageRow.objectLibrary = self.artists
        self.artistImageRow.connect("load-complete", self.display, glossMgr)
        #self.timeline_loading.connect("completed", self.artistImageRow.load_image_range_cb, 0, len(self.artists)-1, False)
        self.timeline_loading.connect("completed", self.flush_gobject_queue)
        
        self.timeline_loading.start()
        #thread.start_new_thread(self.artistImageRow.load_image_range, (0, len(self.artists)-1, True))

        #gobject.idle_add(self.artistImageRow.load_image_range, 0, len(self.artists)-1, True)
        
    def flush_gobject_queue(self, data=None):
        """
        mc = gobject.main_context_default()
        while mc.pending():
            print "Iteration: " + str(mc.iteration(False))
        
        print "finiahed loop"
        """
        self.artistImageRow.load_image_range(0, len(self.artists)-1, False)
        
    def display(self, data, glossMgr):
        self.timeline_display = clutter.Timeline(10,40)
        self.alpha = clutter.Alpha(self.timeline_display, clutter.ramp_inc_func)
        self.opacity_behaviour_incoming = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=self.alpha)
        self.opacity_behaviour_outgoing = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=self.alpha)
        #Fade the backdrop in
        
        self.opacity_behaviour_outgoing.apply(self.loading_img)
        
        self.stage.add(self.artistImageRow)
        self.artistImageRow.set_opacity(0)
        self.artistImageRow.select_first()
        self.artistImageRow.show()
        self.opacity_behaviour_incoming.apply(self.artistImageRow)
        
        #Just a nasty temp label for outputting stuff
        self.list1 = LabelList(5)
        self.list1.setup_from_theme_id(self.glossMgr.themeMgr, "music_albums")
        self.list1.input_queue.connect("queue-flushed", self.update_main_img)
        #self.list1.set_position(self.stage.get_width()/3, 350)
        self.stage.add(self.list1)
        
        self.list2 = LabelList(5)
        self.list2.setup_from_theme_id(self.glossMgr.themeMgr, "music_songs")
        #self.list2.set_position( (600), 350)
        self.stage.add(self.list2)
        
        #The preview img
        self.main_img = ImageFrame(None, 300, True) #clutter.Texture()
        self.main_img.set_position(50, 300)
        self.main_img.set_rotation(clutter.Y_AXIS, 45, self.main_img.get_width(), 0, 0)
        self.main_img.show()
        self.stage.add(self.main_img)
        
        self.timeline_display.start()
    
        
    def stop(self):
        pass
        
    def pause(self):
        pass
        
    def unpause(self):
        pass
    """
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
            
    """