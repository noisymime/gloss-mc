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
from modules.video_player.elements.cover_viewer import coverViewer
from modules.video_player.elements.video_details import video_details
from modules.video_player.elements.folder_menu import folderMenu
from modules.video_player.video_object import videoItem

#===============================================================================
#This module displays a basic cover viewer for videos within myth's Mythvideo table
#It defines the following theme elements:
#video_menu_image (Texture): The graphic used on the menu to represent this module
#video_cover_bg_image (Texture): Graphic that serves as the background for the cover viewer grid
#===============================================================================

class Module():
    title = "Videos"
    STATE_FOLDERS, STATE_COVERS, STATE_VIDEO = range(3)

    #The are just some default values to be used in case of an emergency
    coverViewerWidth = 750
    coverViewerHeight = 600
    coverViewerPosX = 300
    coverViewerPosY = 50
    coverViewerRows = 3
    coverViewerColumns = 4
    coverDetailsWidth = 750
    foldersPosX = 50
    foldersPosX = 50
    cover_size = int(coverViewerWidth / coverViewerColumns)
    
    #Basic UI elements
    currentViewer = None
    backdrop = None
    video_details = None
    covers_background = None

    def __init__(self, glossMgr, dbMgr):
        self.stage = glossMgr.get_stage()
        self.glossMgr = glossMgr
        self.dbMgr = dbMgr
        self.setup_ui()
        self.viewerLibrary = []
        self.folderLibrary = []
        self.videoController = VideoController(glossMgr)
        
        #Setup initial vars
        self.is_playing = False
        self.controlState = self.STATE_FOLDERS

        
        #This block can be moved to begin() but causes a performance hit when loading the module *shrug*
        #All it does is load the initial folders into the viewers
        self.baseDir = dbMgr.get_setting("VideoStartupDir")
        if self.glossMgr.debug: print "VideoPlayer: Base directory=" + str(self.baseDir)
        
        self.cwd = self.baseDir
        self.folder_level = 0
        self.base_folder_menu = folderMenu(glossMgr, self.coverViewerRows, self.folders_cover_size)
        self.base_folder_menu.set_position(self.foldersPosX, self.foldersPosY)
        self.folderLibrary.append(self.base_folder_menu)
        self.load_base_folders(self.baseDir, self.base_folder_menu)
        
        #Set the current viewer
        self.currentViewer = self.base_folder_menu.get_current_viewer()
        #self.currentViewer.set_depth(self.currentViewer.cover_size)
        
        #Create the details group
        self.video_details = video_details(self.coverDetailsWidth)
        self.video_details.set_position(self.coverDetailsPosX, self.coverDetailsPosY)
        
    def setup_ui(self):
        self.menu_image = self.glossMgr.themeMgr.get_texture("video_menu_image", None, None)
        
        #Add the background
        self.covers_background = self.glossMgr.themeMgr.get_texture("video_covers_background", self.stage, None)
        
        #Set the number of rows / cols for the viewer (These come from the MythVideo settings in the backend DB)
        tmp_rows = self.dbMgr.get_setting("VideoGalleryRowsPerPage")
        tmp_cols = self.dbMgr.get_setting("VideoGalleryColsPerPage")
        if not tmp_rows is None: self.coverViewerRows = int(tmp_rows)
        if not tmp_cols is None: self.coverViewerColumns = int(tmp_cols)
        
        #Set the size / position of the cover_viewer
        element = self.glossMgr.themeMgr.search_docs("video_cover_viewer", "main").childNodes
        (self.coverViewerWidth, self.coverViewerHeight) = self.glossMgr.themeMgr.get_dimensions(element, self.stage)
        (self.coverViewerPosX, self.coverViewerPosY) = self.glossMgr.themeMgr.get_position(element, self.stage)
        
        #Set the all important cover size
        self.cover_size = int(self.coverViewerWidth / self.coverViewerColumns)
        
        #set the size / position of the details group
        element = self.glossMgr.themeMgr.search_docs("video_cover_details", "main").childNodes
        (self.coverDetailsWidth, self.coverDetailsHeight) = self.glossMgr.themeMgr.get_dimensions(element, self.stage)
        (self.coverDetailsPosX, self.coverDetailsPosY) = self.glossMgr.themeMgr.get_position(element, self.stage)
        
        #set the size / position of the folder menu
        element = self.glossMgr.themeMgr.search_docs("video_folder_menu", "main").childNodes
        (self.foldersWidth, self.foldersHeight) = self.glossMgr.themeMgr.get_dimensions(element, self.stage)
        (self.foldersPosX, self.foldersPosY) = self.glossMgr.themeMgr.get_position(element, self.stage)
        self.folders_cover_size = self.foldersWidth #int(self.foldersWidth / self.coverViewerColumns)
        

    def load_base_folders(self, dirPath, folder_menu):
        try:
            new_file_list = os.listdir(dirPath)
        except os.error, (errno, errstr):
            self.glossMgr.display_msg("VideoPlayer File Error", "Could not load Video directory")
            return
        
        #Videos and Directories
        for dir_entry in new_file_list:
            tempPath = dirPath + "/" + dir_entry
            if os.path.isdir(tempPath) and not ( dir_entry[0] == "."):
                tempViewer = coverViewer(self.glossMgr, self.coverViewerWidth, self.coverViewerHeight, self.coverViewerRows, self.coverViewerColumns)
                self.loadDir(tempPath, tempViewer)
                folder_menu.add_base_dir(dir_entry, tempViewer)
            
    def loadDir(self, dirPath, cover_viewer):
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
            
        #Generate some SQL to retrieve videos that were in the final_file_list
        #Load the videos into the cover viewer
        sql = "SELECT * FROM videometadata WHERE filename IN ("
        for filename in final_file_list:
            filename = dirPath + filename
            sql = sql + "\"" + filename + "\", "
        sqlLength = int(len(sql) - 2)
        sql = sql[:sqlLength]
        sql = sql + ")"
        
        if self.glossMgr.debug: print "Video SQL: " + sql
            
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
        up = clutter.keysyms.Up
        down = clutter.keysyms.Down
        left = clutter.keysyms.Left
        right= clutter.keysyms.Right
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()
        
        #*****************************************************************
        #"State based input handling
        if self.controlState == self.STATE_FOLDERS:
            if event.keyval == clutter.keysyms.Escape:
                return True
            elif event.keyval == right:
                self.controlState = self.STATE_COVERS
                self.currentViewer = self.folderLibrary[self.folder_level].get_current_viewer()
                self.currentViewer.select_first()
            
            self.folderLibrary[self.folder_level].on_key_press_event(event)
            self.currentViewer = self.folderLibrary[self.folder_level].get_current_viewer()
            
        #**********************************************************        
        elif self.controlState == self.STATE_VIDEO:
            if event.keyval == clutter.keysyms.Escape:
                self.videoController.stop_video()
                self.is_playing = False
                self.controlState = self.STATE_COVERS
            else:
                self.videoController.on_key_press_event(event)
    
            return False
    
            if event.keyval == clutter.keysyms.p:
                if self.paused:
                    self.unpause()
                else:
                    self.pause()
        #**********************************************************
        elif self.controlState == self.STATE_COVERS:
            if (event.keyval == up) or (event.keyval == down) or (event.keyval == left) or (event.keyval == right):
                timeline = self.currentViewer.on_key_press_event(event)
                video = self.currentViewer.get_current_video()
                #Do a check to see if the input queue is currently processing
                #
                if not self.currentViewer.input_queue.is_in_queue():
                    if not video is None:
                        self.video_details.set_video_bare(video)
                        self.currentViewer.set_details_update(False, None)
                    else:
                        self.video_details.set_folder(self.currentViewer.folderLibrary[(self.currentViewer.currentSelection-len(self.currentViewer.folderLibrary))])
                        #self.video_details.clear()
                else:
                    self.currentViewer.set_details_update(True, self.video_details)
            
            if event.keyval == clutter.keysyms.Return:
                #Find whether the current item is a folder or video
                item = self.currentViewer.get_current_item()
                if item.isFolder:
                    self.glossMgr.display_msg("Msg", "Its a folder")
                else:
                    self.play_video()
            
            if event.keyval == clutter.keysyms.Escape:
                self.currentViewer.select_none()
                self.controlState = self.STATE_FOLDERS
        
            
        
        
    def begin(self, glossMgr):
        #Check that the library actually contains something
        #if len(self.currentViewer.textureLibrary) == 0:
        if self.currentViewer is None:
            self.glossMgr.display_msg("Error: No videos", "There are no videos available in the library. This maybe caused by an empty library or a failed connection to the server.")
            self.stop()
            return
       
        #Create a backdrop for the player. In this case we just use the same background as the menus
        self.backdrop = glossMgr.get_themeMgr().get_texture("background", None, None) #clutter.CloneTexture(glossMgr.get_skinMgr().get_Background())
        self.backdrop.set_size(self.stage.get_width(), self.stage.get_height())
        self.backdrop.set_opacity(0)
        self.backdrop.show()
        self.stage.add(self.backdrop)
        
        #Add the covers background
        self.covers_background.set_opacity(0)
        self.covers_background.show()
        self.stage.add(self.covers_background)
        
        #Add the folders menu
        self.folderLibrary[0].set_opacity(0)
        self.folderLibrary[0].show()
        self.stage.add(self.folderLibrary[0])
        
        #Add the cover viewer
        self.currentViewer.set_opacity(0)    
        self.currentViewer.show_all()
        self.currentViewer.show()
        self.currentViewer.set_position(self.coverViewerPosX, self.coverViewerPosY)
        self.stage.add(self.currentViewer)
        
        #Add the video details
        self.video_details.set_opacity(0)
        self.video_details.show_all()
        self.video_details.show()
        self.stage.add(self.video_details)

        
        #Fade everything in
        timeline_begin = clutter.Timeline(10,40)
        alpha = clutter.Alpha(timeline_begin, clutter.ramp_inc_func)
        self.begin_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
        
        
        self.begin_behaviour.apply(self.backdrop)
        self.begin_behaviour.apply(self.folderLibrary[0])
        self.begin_behaviour.apply(self.covers_background)
        self.begin_behaviour.apply(self.currentViewer)
        self.begin_behaviour.apply(self.video_details)
        
        
        #self.viewerLibrary[0].set_position(50, 40)
        #self.currentViewer.toggle_details() #Turns the details group on
        #self.currentViewer.select_first()
        
        
        timeline_begin.start()
        
        #self.folder_menu = folderMenu(self.stage, self.currentViewer.num_visible_rows, self.currentViewer.cover_size)
        #self.folder_menu.set_dir_cover_viewer(self.currentViewer)
        
    def stop(self):
        self.glossMgr.currentPlugin = None
        
        #Fade everything out
        timeline_stop = clutter.Timeline(10,30)
        alpha = clutter.Alpha(timeline_stop, clutter.ramp_inc_func)
        self.stop_behaviour = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=alpha)
        if not self.currentViewer is None: self.stop_behaviour.apply(self.currentViewer)
        if not self.backdrop is None: self.stop_behaviour.apply(self.backdrop)
        if not self.folderLibrary[self.folder_level] is None: self.stop_behaviour.apply(self.folderLibrary[self.folder_level])
        if not self.video_details is None: self.stop_behaviour.apply(self.video_details)
        if not self.covers_background is None: self.stop_behaviour.apply(self.covers_background)
        timeline_stop.connect('completed', self.destroyPlugin)
        timeline_stop.start()
        
    def destroyPlugin(self, data):
        self.stage.remove(self.currentViewer)
        self.stage.remove(self.folderLibrary[self.folder_level])
        self.stage.remove(self.video_details)
        self.stage.remove(self.covers_background)
        self.backdrop.hide()
        #self.stage.remove(self.overlay)
    
    def play_video(self):
        vid = self.currentViewer.get_current_item().video
        uri = "file://" + str(vid.filename)
        self.videoController.play_video(uri, self)
        self.is_playing = True
        self.controlState = self.STATE_VIDEO
        
        self.stage.remove(self.currentViewer)
        self.stage.remove(self.base_folder_menu)
        
    def stop_video(self):
        if not self.is_playing:
            return
        
        self.is_playing = False
        
        timeline = clutter.Timeline(15, 25)
        self.currentViewer.set_opacity(0)
        self.base_folder_menu.set_opacity(0)
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
        self.behaviour.apply(self.currentViewer)
        self.behaviour.apply(self.base_folder_menu)
        
        self.stage.add(self.currentViewer)
        self.stage.add(self.base_folder_menu)
        self.currentViewer.show()
        timeline.start()
        
    def pause(self):
        pass
        
    def unpause(self):
        pass
             
        

