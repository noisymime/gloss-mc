import pygtk
import gtk
import pygst
import gst
import gobject
import pango
import clutter
import os
from modules.video_player.elements.CoverItem import cover_item
from ui_elements.image_grid import ImageGrid
from utils.InputQueue import InputQueue

class coverViewer(ImageGrid):
    scaleFactor = 1.4
    inactiveOpacity = 150
    covers_size_percent = 0.90 #This is the percentage of the total group size that the covers will take
    detailBox_height = 160 #Needs a percent
    update_details = False
    

    def __init__(self, glossMgr, width, height, rows, columns):
        ImageGrid.__init__(self, glossMgr, width, height, rows, columns)
        self.cover_size = self.image_size
        self.videoLibrary = []
        self.folderLibrary = []
        
    def add_video(self, video):      
        self.videoLibrary.append(video)
        tempTexture = cover_item(self.glossMgr, video, None, self.cover_size)
        self.add_texture_group(tempTexture)
    
    def add_folder(self, folder_name):
        tempTexture = cover_item(self.glossMgr, None, folder_name, self.cover_size)
        self.folderLibrary.append(folder_name)
        self.add_texture_group(tempTexture)            
        
    def select_item(self, incomingItem, outgoingItem):
        numFolders = len(self.folderLibrary)
        if incomingItem >= numFolders:
            incomingItemVideo = incomingItem - numFolders
        
        ImageGrid.select_item(self, incomingItem, outgoingItem)
            
     
    def get_current_video(self):
        if self.textureLibrary[self.currentSelection].isFolder:
            return None #self.folderLibrary[(self.currentSelection-len(self.folderLibrary))]
        else:
            return self.videoLibrary[(self.currentSelection-len(self.folderLibrary))]
        
    def get_item_x(self, itemNo):
        return self.textureLibrary[itemNo]
    
    def get_item_library(self):
        return self.textureLibrary
    
    def get_current_item(self):
        if self.textureLibrary[self.currentSelection].isFolder:
            return None #self.folderLibrary[(self.currentSelection-len(self.folderLibrary))]
        else:
            return self.textureLibrary[(self.currentSelection-len(self.folderLibrary))+1]
    
    def set_details_update(self, on_off, details):
        self.update_details = on_off
        self.details_group = details
        
    def on_key_press_event(self, event):
        self.input_queue.input(event)
        return self.timeline
        
            
    def move_common(self, newItem):
        ImageGrid.move_common(self, newItem)        
          
        if self.update_details:
            if not self.textureLibrary[self.currentSelection].isFolder:
                self.details_group.set_video_bare(self.videoLibrary[self.currentSelection])
                self.update_details = False
            else:
                self.details_group.set_folder(self.folderLibrary[(self.currentSelection-len(self.folderLibrary))])
                #self.details_group.clear()
        
