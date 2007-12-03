import pygtk
import gtk
import pygst
import gst
import gobject
import pango
import clutter
import os
from modules.video_player.CoverItem import cover_item

class folderMenu(clutter.Group):
    scaleFactor = 1.4
    inactiveOpacity = 150
    
    def __init__(self, stage, rows, item_size):
        clutter.Group.__init__(self)
        self.max_rows = rows
        self.item_size = item_size
        self.currentItemNo = None
        
        self.folderLibrary = []
        self.viewerLibrary = []
        
    def add_base_dir(self, folderName, cover_viewer):
        tempItem = cover_item(None, folderName, self.item_size)
        rows = len(self.folderLibrary)
        x = 0 #Change this later to center it
        y = rows * self.item_size
        tempItem.set_position(x, y)
        tempItem.show()
        self.add(tempItem)
        
        #Check if this is the first folder
        if len(self.folderLibrary) == 0:
            self.currentItemNo = 0
        
        self.folderLibrary.append(tempItem)
        self.viewerLibrary.append(cover_viewer)
        
    def get_current_viewer(self):
        return self.viewerLibrary[self.currentItemNo]
        
    def set_dir_cover_viewer(self, cover_view):
        timeline = clutter.Timeline(10,35)
        alpha = clutter.Alpha(timeline, clutter.smoothstep_inc_func)# clutter.ramp_inc_func)
        self.behaviour_opacity_outgoing = clutter.BehaviourOpacity(alpha, 255, 0)
        
        num_folders = len(cover_view.folderLibrary)
        count = 0
        for item in cover_view.textureLibrary:
            if count < num_folders:
                self.add_folder(item, timeline)
            else:
                self.behaviour_opacity_outgoing.apply(item)
                
        timeline.start()
        
    def add_folder(self, cover_viewer_item, timeline):
        #First we clone the textures pixbuf
        #tempFolderTexture = clutter.CloneTexture(cover_viewer_texture)
        #tempFolderTexture.set_pixbuf(cover_viewer_texture.get_pixbuf())
        #tempFolderTexture.set_parent_texture(cover_viewer_texture)
        
        """
        knots = (\
            (group_x, group_y),\
            (group_x, new_y )\
            )
        """
        self.add(cover_viewer_item)
        