import pygtk
import gtk
import pygst
import gst
import gobject
import pango
import clutter
import os
from clutter import cluttergst
from VideoController import VideoController
from modules.video_player.cover_viewer import coverViewer
from modules.video_player.folder_menu import folderMenu

class Module():
    title = "Videos"
    menu_image= "videos.png"
    coverViewerWidth = 800
    coverViewerHeight = 600
    coverViewerRows = 3
    coverViewerColumns = 4
    cover_size = int(coverViewerWidth / coverViewerColumns)

    def __init__(self, MenuMgr, dbMgr):
        self.stage = MenuMgr.get_stage()
        self.MenuMgr = MenuMgr
        self.dbMgr = dbMgr
        self.viewerLibrary = []
        self.folderLibrary = []
        self.videoController = VideoController(self.stage)
        self.is_playing = False
        
        #This block can be moved to begin() but causes a performance hit when loading the module *shrug*
        #base_cover_viewer = coverViewer(self.stage, self.coverViewerWidth, self.coverViewerHeight)
        #self.viewerLibrary.append(base_cover_viewer)
        #self.currentViewer = base_cover_viewer
        self.baseDir = dbMgr.get_setting("VideoStartupDir")
        self.cwd = self.baseDir
        self.folder_level = 0
        base_folder_menu = folderMenu(self.stage, self.coverViewerRows, self.cover_size)
        self.folderLibrary.append(base_folder_menu)
        self.load_base_folders(self.baseDir, base_folder_menu)
        self.currentViewer = base_folder_menu.get_current_viewer()
        self.stage.add(base_folder_menu)
        base_folder_menu.show()
        #self.loadDir(self.baseDir, base_cover_viewer)
        #results = dbMgr.get_videos()

    def load_base_folders(self, dirPath, folder_menu):
        new_file_list = os.listdir(dirPath)
        
        #Images and Directories
        for dir_entry in new_file_list:
            tempPath = dirPath + "/" + dir_entry
            if os.path.isdir(tempPath) and not ( dir_entry[0] == "."):
                tempViewer = coverViewer(self.stage, self.coverViewerWidth, self.coverViewerHeight, self.coverViewerRows, self.coverViewerColumns)
                self.loadDir(tempPath, tempViewer)
                folder_menu.add_base_dir(dir_entry, tempViewer)
            
    def loadDir(self, dirPath, cover_viewer):
        if not os.path.isdir(dirPath):
            print "ERROR: Invalid path"
            return None
        
        final_file_list = []
        new_file_list = os.listdir(dirPath)
        
        #Images and Directories
        for dir_entry in new_file_list:
            if os.path.isdir(dirPath + "/" + dir_entry) and not ( dir_entry[0] == "."):
                cover_viewer.add_folder(dir_entry)
                print dir_entry
            else:
                final_file_list.append(dir_entry)
                
        #Check if we're empty
        if len(final_file_list) == 0:
            return
                
        #Make sure the dirPath ends in "/"
        if not dirPath[-1] == "/":
            dirPath = dirPath + "/"
            
        #Generate some SQL to retrieve videos that were in the final_file_list
        #Load the videos into the cover viewer
        sql = "SELECT * FROM videometadata WHERE filename IN ("
        for filename in final_file_list:
            filename = dirPath + filename
            sql = sql + "\"" + filename + "\", "
        sqlLength = int(len(sql) - 2)
        print "SQL Length: " + str(sqlLength)
        sql = sql[:sqlLength]
        sql = sql + ")"
        print sql
        results = self.dbMgr.run_sql(sql)
        
        #Check for null return
        if results == None:
            print "VideoPlayer: No connection to DB or no videos found in DB"
            return None
        
        #Else add the entries in    
        for record in results:
            tempVideo = videoItem()
            tempVideo.importFromMythObject(record)
            cover_viewer.add_video(tempVideo)
            
    #Action to take when menu item is selected
    def action(self):
        return self        
            
    def on_key_press_event (self, stage, event):
        if self.is_playing:
            if event.keyval == clutter.keysyms.Escape:
                self.videoController.stop_video()
                self.is_playing = False
            else:
                self.videoController.on_key_press_event(event)
            
            return False
    
        if event.keyval == clutter.keysyms.p:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()
            
        up = clutter.keysyms.Up
        down = clutter.keysyms.Down
        left = clutter.keysyms.Left
        right= clutter.keysyms.Right
        if (event.keyval == up) or (event.keyval == down) or (event.keyval == left) or (event.keyval == right):
            self.currentViewer.on_key_press_event(event)
        
        if event.keyval == clutter.keysyms.Return:
            #Find whether the current item is a folder or video
            item = self.currentViewer.get_current_item()
            if item.isFolder:
                self.MenuMgr.display_msg("Msg", "Its a folder")
            else:
                self.play_video()
            
        if event.keyval == clutter.keysyms.Escape:
            return True
        
            
        
        
    def begin(self, MenuMgr):
        #Check that the library actually contains something
        if self.currentViewer.num_covers == 0:
            self.MenuMgr.display_msg("Error: No videos", "There are no videos available in the library. This maybe caused by an empty library or a failed connection to the server.")
            self.stop()
            return
       
        #Create a backdrop for the player. In this case we just use the same background as the menus
        self.backdrop = clutter.CloneTexture(MenuMgr.get_skinMgr().get_Background())
        self.backdrop.set_size(self.stage.get_width(), self.stage.get_height())
        self.backdrop.set_opacity(0)
        self.backdrop.show()
        self.stage.add(self.backdrop)
        #Fade the backdrop in
        timeline_begin = clutter.Timeline(10,40)
        alpha = clutter.Alpha(timeline_begin, clutter.ramp_inc_func)
        self.begin_behaviour = clutter.BehaviourOpacity(alpha, 0, 255)
        self.begin_behaviour.apply(self.backdrop)

        
        self.currentViewer.set_opacity(0)    
        self.currentViewer.show_all()
        self.currentViewer.show()
        self.stage.add(self.currentViewer)
        cover_x = self.stage.get_width() - int(self.currentViewer.get_width() * 1.1)
        self.currentViewer.set_position(cover_x, 40)
        #self.viewerLibrary[0].set_position(50, 40)
        self.currentViewer.toggle_details() #Turns the details group on
        self.currentViewer.select_first()
        self.begin_behaviour.apply(self.currentViewer)
        
        timeline_begin.start()
        
        self.folder_menu = folderMenu(self.stage, self.currentViewer.num_visible_rows, self.currentViewer.cover_size)
        self.folder_menu.set_dir_cover_viewer(self.currentViewer)
        
    def stop(self):
        self.MenuMgr.currentPlugin = None
        
        #Fade everything out
        timeline_stop = clutter.Timeline(10,30)
        alpha = clutter.Alpha(timeline_stop, clutter.ramp_inc_func)
        self.stop_behaviour = clutter.BehaviourOpacity(alpha, 255, 0)
        self.stop_behaviour.apply(self.currentViewer)
        self.stop_behaviour.apply(self.backdrop)
        timeline_stop.connect('completed', self.destroyPlugin)
        timeline_stop.start()
        
        
    
    def destroyPlugin(self, data):
        self.stage.remove(self.currentViewer)
        self.backdrop.hide()
        #self.stage.remove(self.overlay)
    
    def play_video(self):
        vid = self.currentViewer.get_current_item().video
        uri = "file://" + str(vid.filename)
        self.videoController.play_video(uri, self)
        self.is_playing = True
        
        self.stage.remove(self.currentViewer)
        
    def stop_video(self):
        if not self.is_playing:
            return
        
        self.is_playing = False
        
        timeline = clutter.Timeline(15, 25)
        self.currentViewer.set_opacity(0)
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.behaviour = clutter.BehaviourOpacity(alpha, 0,255)
        self.behaviour.apply(self.currentViewer)
        
        self.stage.add(self.currentViewer)
        self.currentViewer.show()
        timeline.start()
        
    def pause(self):
        pass
        
    def unpause(self):
        pass
        
class videoItem():
    def __init(self):
        self.mythID = None
        
    def importFromMythObject(self, mythObject):
        self.mythID = mythObject[0]
        self.title = mythObject[1]
        self.director = mythObject[2]
        self.plot = mythObject[3]
        self.rating = mythObject[4]
        self.inetRef = mythObject[5]
        self.year = mythObject[6]
        self.userRating = mythObject[7]
        self.length = mythObject[8]
        self.showLevel = mythObject[9]
        self.filename = mythObject[10]
        self.coverfile = mythObject[11]
        self.childID = mythObject[12]
        self.browse = mythObject[13]
        self.playCommand = mythObject[14]
        self.category = mythObject[15]
        
    def getTitle(self):
        return self.title
    def getCoverfile(self):
        return self.coverfile        
        

