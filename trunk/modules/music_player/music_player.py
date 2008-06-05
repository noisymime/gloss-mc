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
from ui_elements.image_clone import ImageClone
from ui_elements.label_list import LabelList
from ui_elements.option_dialog import OptionDialog

class Module:
    CONTEXT_HEADINGS, CONTEXT_ROW, CONTEXT_ALBUM_LIST, CONTEXT_SONG_LIST, CONTEXT_PLAY_SCR = range(5)
    DIRECTION_LEFT, DIRECTION_RIGHT = range(2)
    
    title = "Music"
    num_columns = 6
    sleep_time = 0.3
    required_schema_version = 1013
    version_check = True #Gets set to false if the version check fails
    
    delay = 1

    def __init__(self, glossMgr, dbMgr):
        self.stage = glossMgr.get_stage()
        self.glossMgr = glossMgr
        self.dbMgr = dbMgr
        self.albums = []
        self.artists = []
        self.songs = []
        
        self.backend = Backend(self)
        self.playlist = Playlist(self)
        
        #Do a check of the DB schema version
        dbSchema = self.dbMgr.get_setting("MusicDBSchemaVer")
        if not dbSchema is None:
            dbSchema = int(dbSchema)
            if not dbSchema == self.required_schema_version:
                print "Music DB Version error: Expected version %s, found version %s" % (self.required_schema_version, dbSchema)
                print "Music Player will not be available"
                self.version_check = False
                return
        
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
        
        self.heading = None
        
        self.setup_ui()
        
    def setup_ui(self):
        self.menu_image = self.glossMgr.themeMgr.get_texture("music_menu_image", None, None)
        
        self.default_artist_cover = self.glossMgr.themeMgr.get_texture("music_default_artist_image", None, None).get_pixbuf()
        self.default_album_cover = self.glossMgr.themeMgr.get_texture("music_default_album_image", None, None).get_pixbuf()
        self.main_img = self.glossMgr.themeMgr.get_imageFrame("music_main_image")
        
        colour = clutter.color_parse('White')
        font_string = "Tahoma 30"
        self.heading = musicHeading(colour, font_string)
        self.heading.set_position(400, 250)
        """
        self.artist_label_1.set_position(200, 200)
        self.artist_label_2.set_position(200, 200)
        self.artist_label_3.set_position(200, 200)
        self.artist_label_1.set_color(clutter.color_parse('White'))
        self.artist_label_2.set_color(clutter.color_parse('White'))
        self.artist_label_3.set_color(clutter.color_parse('White'))
        """
    
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
                self.previous_music_object = self.artistImageRow.get_current_object()
                #First check if there's any current timeouts and if there is, clear it
                #if not self.timeout_id == 0: gobject.source_remove(self.timeout_id)
                self.artistImageRow.sleep = True
                self.artistImageRow.input_queue.input(event)
                #self.artistImageRow.input_queue.connect("queue-flushed", self.start_delay, self.load_albums, None)
                #self.artistImageRow.objectLibrary[0].pause_threads()
                if self.queue_id == 0: self.queue_id = self.artistImageRow.input_queue.connect("queue-flushed", self.load_albums)
                self.artistImageRow.sleep = False
                

                if (event.keyval == clutter.keysyms.Left): self.direction = self.DIRECTION_LEFT
                if (event.keyval == clutter.keysyms.Right): self.direction = self.DIRECTION_RIGHT
                
                
            elif (event.keyval == clutter.keysyms.Down):
                self.list1.select_first_elegant()
                self.list2.show()
                self.current_context = self.CONTEXT_ALBUM_LIST
            
            elif (event.keyval == clutter.keysyms.Return):
                artist = self.artistImageRow.get_current_object()
                songs = self.backend.get_songs_by_artistID(artist.artistID)
                self.query_playlist_add(songs)

                self.previous_context = self.CONTEXT_ROW
            elif (event.keyval == clutter.keysyms.Escape):
                return True
                #self.stop()   
            
                
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
                self.play_screen.undisplay()
            else:
                self.play_screen.on_key_press_event(stage, event)
    
    #When the user has selected some songs, this function is called to decide what to do with them
    #Options:
    #1) Append to current playlist
    #2) Append to current playlist and play next
    #3) Replace the current playlist
    def query_playlist_add(self, songs):
        #If the current playlist is empty, its a no brainer:
        if self.playlist.num_songs() == 0:
            self.playlist.append_songs(songs)
            self.playlist.play()
            self.current_context = self.CONTEXT_PLAY_SCR
            self.play_screen.display(self.artistImageRow.get_current_texture())
            return
        
        option_dialog = OptionDialog(self.glossMgr)
        self.query_options = []
        self.query_options.append(option_dialog.add_item("Append to current playlist"))
        self.query_options.append(option_dialog.add_item("Append to current playlist and play next"))
        self.query_options.append(option_dialog.add_item("Replace the current playlist"))
        
        option_dialog.connect("option-selected", self.option_dialog_cb, songs)
        option_dialog.display("What would you like to do with these songs?")
        

            
    def option_dialog_cb(self, data, result, songs):
        print "result: %s" % result
        #Handle options
        if result == self.query_options[0]:
            self.playlist.append_songs(songs)
        if result == self.query_options[1]:
            self.playlist.insert_songs(self.playlist.position, songs)
        if result == self.query_options[2]:
            self.playlist.stop()
            self.playlist.clear()
            self.paylist.append_songs(songs)
        
        self.playlist.play()
        
        #self.play_screen.append_playlist(self.playlist)
        self.current_context = self.CONTEXT_PLAY_SCR
        self.play_screen.display(self.artistImageRow.get_current_texture())#.get_texture())
        
    
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
        self.conn_id = self.backend.connect("query-complete", self.update_for_albums, artist)
        self.backend.get_albums_by_artistID(artist.artistID)
        
        self.heading.transition_heading(self.direction, self.previous_music_object, artist, None)
        #thread = threading.Thread(target=self.backend.get_albums_by_artistID, args=(artist.artistID,))
        #thread.start()
        
        
    def update_for_albums(self, data, artist = None):
        if not artist == self.artistImageRow.get_current_object(): return
        if not self.backend.handler_is_connected(self.conn_id): 
            return
        self.backend.disconnect(self.conn_id)
        self.current_albums = self.backend.get_albums_by_artistID(artist.artistID)
        
        #clutter.threads_enter()
        self.list1.clear()
        for album in self.current_albums:
            tmpItem = self.list1.add_item(album.name)
            tmpItem.connect("selected", self.process_songlist_from_album, album)
        self.list1.display()
        self.update_main_img()
        #clutter.threads_leave()
        
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
        #If the schema version check failed, we quit
        if not self.version_check:
            self.glossMgr.display_msg("Error: MythMusic", "MythMusic version check failed. Please check you are running the correct version.")
            self.stop()
            return
        
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
        self.list1 = LabelList()
        self.list1.setup_from_theme_id(self.glossMgr.themeMgr, "music_albums")
        self.list1.input_queue.connect("queue-flushed", self.update_main_img)
        #self.list1.set_position(self.stage.get_width()/3, 350)
        self.stage.add(self.list1)
        
        self.list2 = LabelList()
        self.list2.setup_from_theme_id(self.glossMgr.themeMgr, "music_songs")
        #self.list2.set_position( (600), 350)
        self.stage.add(self.list2)
        
        #The preview img
        #self.main_img = ImageFrame(None, 300, True) #clutter.Texture()
        #self.main_img.set_position(50, 300)
        self.main_img.set_rotation(clutter.Y_AXIS, 45, self.main_img.get_width(), 0, 0)
        self.main_img.show()
        self.stage.add(self.main_img)
        
        self.stage.add(self.heading)
        self.heading.show()
        
        self.timeline_display.start()
                          
        
    def stop(self):
        #We hid it, we must unhid it
        self.glossMgr.get_current_menu().get_current_item().get_main_texture().show()
        self.loading_img.hide()
        
        self.timeline_remove = clutter.Timeline(20,40)
        self.alpha = clutter.Alpha(self.timeline_remove, clutter.ramp_inc_func)
        self.opacity_behaviour = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=self.alpha)
        
        self.remove_list = []
        self.opacity_behaviour.apply(self.backdrop)
        self.remove_list.append(self.backdrop)
        self.opacity_behaviour.apply(self.artistImageRow)
        self.remove_list.append(self.artistImageRow)
        self.opacity_behaviour.apply(self.list1)
        self.remove_list.append(self.list1)
        self.opacity_behaviour.apply(self.list2)
        self.remove_list.append(self.list2)
        self.opacity_behaviour.apply(self.main_img)
        self.remove_list.append(self.main_img)
        self.opacity_behaviour.apply(self.heading)
        self.remove_list.append(self.heading)
        self.opacity_behaviour.apply(self.loading_img)
        self.remove_list.append(self.loading_img)
        
        
        self.timeline_remove.connect("completed", self.destroy)
        self.timeline_remove.start()
        
        
    def destroy(self, data):
        self.glossMgr.currentPlugin = None
        
        for actor in self.remove_list:
            self.stage.remove(actor)
        
    def pause(self):
        pass
        
    def unpause(self):
        pass
    
class musicHeading(clutter.Group):
    DIRECTION_LEFT, DIRECTION_RIGHT = range(2)
    
    def __init__(self, colour = None, font_string = None):
        clutter.Group.__init__(self)
        
        if colour is None: colour = clutter.color_parse('White')
        if font_string is None: font_string = "Tahoma 30"
        
        #There has be 3 of these labels, one left, center and right
        self.label_1 = clutter.Label()
        self.label_2 = clutter.Label()
        self.label_3 = clutter.Label()
        
        self.label_1.set_font_name(font_string)
        self.label_2.set_font_name(font_string)
        self.label_3.set_font_name(font_string)
        
        self.label_1.set_color(colour)
        self.label_2.set_color(colour)
        self.label_3.set_color(colour)
        
        self.label_current = self.label_1
        
        self.add(self.label_1)
        self.add(self.label_2)
        self.add(self.label_3)
        
        self.label_1.show()
        self.label_2.show()
        self.label_3.show()
        
    def transition_heading(self, direction, old_music_item, new_music_item, timeline = None):
        start_timeline = False
        if timeline is None:
            #Completely generic timeline definition
            timeline = clutter.Timeline(20, 30)
            start_timeline = True
            
        self.alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)

        if direction == self.DIRECTION_LEFT:
            if self.label_current == self.label_1: next_label = self.label_2
            elif self.label_current == self.label_2: next_label = self.label_3
            elif self.label_current == self.label_3: next_label = self.label_1
        else:
            if self.label_current == self.label_1: next_label = self.label_3
            elif self.label_current == self.label_2: next_label = self.label_1
            elif self.label_current == self.label_3: next_label = self.label_2
        
        next_label.set_opacity(0)
        next_label.set_scale(0.5, 0.5)
        next_label.set_text(new_music_item.name)
        
        if direction == self.DIRECTION_RIGHT:
            next_label.set_x( self.label_current.get_x() + (self.label_current.get_width()))
            outgoing_x = self.label_current.get_x() - int(self.label_current.get_width()/2)
        else:
            next_label.set_x( self.label_current.get_x() - (next_label.get_width()))
            outgoing_x = self.label_current.get_x() + int(self.label_current.get_width())
            
        incoming_x = self.label_current.get_x() + int(self.label_current.get_width()/2) - int(next_label.get_width()/2)
        knots_incoming =(\
                         (next_label.get_x(), next_label.get_y()),
                         (incoming_x, next_label.get_y())
                         )
    
        knots_outgoing =(\
                         (self.label_current.get_x(), self.label_current.get_y()),
                         (outgoing_x, next_label.get_y())
                         )
        
        self.behaviourIncomingPath = clutter.BehaviourPath(knots = knots_incoming, alpha = self.alpha)
        self.behaviourOutgoingPath = clutter.BehaviourPath(knots = knots_outgoing, alpha = self.alpha)
        self.behaviourIncomingOpacity = clutter.BehaviourOpacity(opacity_start = 0, opacity_end = 255, alpha = self.alpha)
        self.behaviourOutgoingOpacity = clutter.BehaviourOpacity(opacity_start = 255, opacity_end = 0, alpha = self.alpha)
        self.behaviourIncomingScale = clutter.BehaviourScale(x_scale_start = 0.5, y_scale_start = 0.5, x_scale_end = 1, y_scale_end = 1, alpha = self.alpha)
        self.behaviourOutgoingScale = clutter.BehaviourScale(x_scale_start = 1, y_scale_start = 1, x_scale_end = 0.5, y_scale_end = 0.5, alpha = self.alpha)
        
        self.behaviourIncomingPath.apply(next_label)
        self.behaviourIncomingOpacity.apply(next_label)
        self.behaviourIncomingScale.apply(next_label)
        self.behaviourOutgoingPath.apply(self.label_current)
        self.behaviourOutgoingOpacity.apply(self.label_current)
        self.behaviourOutgoingScale.apply(self.label_current)
        
        timeline.connect("completed", self.set_next_heading, next_label)
        
        if start_timeline:
            timeline.start()
        
    def set_next_heading(self, data, new_heading):
        self.label_current = new_heading