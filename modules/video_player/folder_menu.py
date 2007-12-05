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
    selection_box_src = "ui/vid_folders_select_box.png"
    
    def __init__(self, stage, rows, item_size):
        clutter.Group.__init__(self)
        self.stage = stage
        self.max_rows = rows
        self.item_size = item_size
        self.currentItemNo = None
        
        self.selector_box = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.selection_box_src)
        self.selector_box.set_pixbuf(pixbuf)
        self.selector_box.set_size(item_size, item_size)
        self.add(self.selector_box)
        self.selector_box.show()
        
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
    
    def on_key_press_event (self, event):
        up = clutter.keysyms.Up
        down = clutter.keysyms.Down
        left = clutter.keysyms.Left
        right= clutter.keysyms.Right
        
        if (event.keyval == down):
            #Check if we're already at the end of the line
            if self.currentItemNo >= len(self.viewerLibrary)-1:
                return
            
            newItemNo = self.currentItemNo + 1
            self.switch_viewer(self.viewerLibrary[newItemNo], 1)
            self.currentItemNo = newItemNo
        elif (event.keyval == up):
            #Check if we're already at the end of the line
            if self.currentItemNo == 0:
                return
            
            newItemNo = self.currentItemNo - 1
            self.switch_viewer(self.viewerLibrary[newItemNo], -1)
            self.currentItemNo = newItemNo
    
    # This is called when the folder menu changes the currently selected folder. 
    # It causes the coverViewer that's currently on display to roll out and new one come in
    # Direction is negative for up, positive for down
    def switch_viewer(self, new_viewer, direction):
        timeline = clutter.Timeline(15,35)
        alpha = clutter.Alpha(timeline, clutter.smoothstep_inc_func)
        
        if direction > 0:
            rotation_direction = clutter.ROTATE_CCW
            self.behaviour_rotate_incoming = clutter.BehaviourRotate(alpha, clutter.X_AXIS, rotation_direction, 90, 0)
            self.behaviour_rotate_outgoing = clutter.BehaviourRotate(alpha, clutter.X_AXIS, rotation_direction, 0, 270)
        else:
            rotation_direction = clutter.ROTATE_CW
            self.behaviour_rotate_incoming = clutter.BehaviourRotate(alpha, clutter.X_AXIS, rotation_direction, 270, 0)
            self.behaviour_rotate_outgoing = clutter.BehaviourRotate(alpha, clutter.X_AXIS, rotation_direction, 0, 90)
        
        #Need to set the axis of rotation for the covers
        self.behaviour_rotate_outgoing.set_center(0, self.item_size/2, 0)
        self.behaviour_rotate_incoming.set_center(0, self.item_size/2, 0)
        
        self.behaviour_opacity_incoming = clutter.BehaviourOpacity(alpha, 0, new_viewer.inactiveOpacity)
        
        #Apply the outgong behaviour
        current_viewer = self.viewerLibrary[self.currentItemNo]
        timeline.connect('completed', self.completeSwitch, current_viewer)
        self.behaviour_opacity_outgoing = clutter.BehaviourOpacity(alpha, current_viewer.inactiveOpacity, 0)
        
        self.behaviour_opacity_outgoing.apply(current_viewer)
        for cover in current_viewer.get_item_library():
            self.behaviour_rotate_outgoing.apply(cover)

            
        #Apply the incoming behaviour
        new_viewer.set_opacity(0)
        self.behaviour_opacity_incomingViewer = clutter.BehaviourOpacity(alpha, 0, 255)
        self.behaviour_opacity_incomingViewer.apply(new_viewer)
        for cover in new_viewer.get_item_library():
            cover.set_opacity(0)
            self.behaviour_rotate_incoming.apply(cover)
            self.behaviour_opacity_incoming.apply(cover)
        
        #Make sure the new coverViewer is in the right location
        (x, y) = current_viewer.get_abs_position()
        new_viewer.set_position(x, y)
        self.stage.add(new_viewer)
        new_viewer.show()
        
        #Move the selector box
        self.move_selector_box(alpha, direction)
        
        timeline.start()
        
    def move_selector_box(self, alpha, direction):
        
        currentFolder = self.folderLibrary[self.currentItemNo]
        newFolder = self.folderLibrary[self.currentItemNo+direction]
        knots = (\
            (currentFolder.get_x(), currentFolder.get_y()),\
            (newFolder.get_x(), newFolder.get_y() )\
            )
        
        self.behaviour_selectorBox_path = clutter.BehaviourPath(alpha, knots)
        self.behaviour_selectorBox_path.apply(self.selector_box)
        
    def completeSwitch(self, data, old_viewer):
        #self.viewerLibrary[self.currentItemNo].select_first()
        self.stage.remove(old_viewer)
        
                    
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
        