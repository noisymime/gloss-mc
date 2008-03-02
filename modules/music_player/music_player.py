import pygtk
import gtk
import clutter
from modules.music_player.music_objects.song import song
from ui_elements.image_row import ImageRow

class Module():
    title = "Music"

    def __init__(self, glossMgr, dbMgr):
        self.stage = glossMgr.get_stage()
        self.glossMgr = glossMgr
        self.dbMgr = dbMgr
        self.setup_ui()
        self.albums = []
        self.songs = []
        
        self.base_dir = self.dbMgr.get_setting("MusicLocation")
        print "Music Base Dir: " + self.base_dir
        
        self.is_playing = False
        #self.load_albums()
        
    def setup_ui(self):
        self.menu_image = self.glossMgr.themeMgr.get_texture("music_menu_image", None, None)
        
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
        
    def begin(self, MenuMgr):
        
        #Create a backdrop for the player. In this case we just use the same background as the menus
        self.backdrop = clutter.CloneTexture(MenuMgr.get_skinMgr().get_Background())
        self.backdrop.set_size(self.stage.get_width(), self.stage.get_height())
        self.backdrop.set_opacity(0)
        self.backdrop.show()
        self.stage.add(self.backdrop)
        #Fade the backdrop in
        timeline_backdrop = clutter.Timeline(10,40)
        alpha = clutter.Alpha(timeline_backdrop, clutter.ramp_inc_func)
        backdrop_behaviour = clutter.BehaviourOpacity(alpha, 0, 255)
        backdrop_behaviour.apply(self.backdrop)
        timeline_backdrop.start()
        
    def stop(self):
        pass
        
    def pause(self):
        pass
        
    def unpause(self):
        pass
    
    def load_albums(self):
        """
        if not os.path.isdir(dirPath):
            print "ERROR VideoPlayer: Invalid video path"
            return None
        
        final_file_list = []
        new_file_list = os.listdir(dirPath)

        #Videos and Directories
        for dir_entry in new_file_list:
            if os.path.isdir(dirPath + "/" + dir_entry) and not ( dir_entry[0] == "."):
                cover_viewer.add_folder(dir_entry)
                #print dir_entry
            else:
                final_file_list.append(dir_entry)
                
        #Check if we're empty
        if len(final_file_list) == 0:
            return
                
        #Make sure the dirPath ends in "/"
        if not dirPath[-1] == "/":
            dirPath = dirPath + "/"
        """
        #Generate some SQL to retrieve videos that were in the final_file_list
        #Load the videos into the cover viewer
        sql = "SELECT * FROM music_songs" # WHERE filename IN ("
        """
        for filename in final_file_list:
            filename = dirPath + filename
            sql = sql + "\"" + filename + "\", "
        sqlLength = int(len(sql) - 2)
        sql = sql[:sqlLength]
        sql = sql + ")"
        """
        if self.glossMgr.debug: print "Music SQL: " + sql
            
        results = self.dbMgr.run_sql(sql)
        
        #Check for null return
        if results == None:
            print "MusicPlayer: No connection to DB or no songs found in DB"
            return None
        
        #Else add the entries in    
        for record in results:
            tempSong = song()
            tempSong.import_from_mythObject(record)
            self.songs.append(tempSong)
            filename = self.base_dir + "/" + tempSong.filename
            #print filename
            #tempSong.set_file(filename)
        
        
        
    