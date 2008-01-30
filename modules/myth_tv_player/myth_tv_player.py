import gst
import pygtk
import pygst
import os
import clutter

from clutter import cluttergst
from modules.myth_tv_player.MythBackendConn import MythBackendConnection
#from Menu import Menu
from VideoController import VideoController

class Module:
    title = "TV"

    def __init__(self, glossMgr, dbMgr):
        self.stage = glossMgr.get_stage()
        self.glossMgr = glossMgr
        self.setup_ui()
        
        self.videoController = VideoController(glossMgr)
        self.dbMgr = dbMgr
        self.isRunning = False
        
    def setup_ui(self):
        self.menu_image = self.glossMgr.themeMgr.get_texture("mythtv_menu_image", None, None)
    
    #Action to take when menu item is selected
    def action(self):
        return self
        
    def begin(self, menuMgr):
        self.menuMgr = menuMgr
        #self.buffer_file_reader = open("test.mpg","r")
        menuMgr.get_selector_bar().set_spinner(True)
        (server, port) = self.dbMgr.get_backend_server()
        self.myConn = MythBackendConnection(self, server, port)
        self.myConn.start()
        #vid.begin(self.stage)
        
        self.isRunning = True
        
    def begin_playback(self, fd):#buffer_file):
        self.menuMgr.get_selector_bar().set_spinner(False)
        #uri = "file://" + os.getcwd() +"/" + buffer_file
        #f = open(os.getcwd() +"/" + buffer_file, 'r')
        uri = "fd://" + str(fd)
        #uri = str(fd)
        #print uri
        self.videoController.play_video(uri, self)
        
    def stop(self):
        self.videoController.stop_video()
        self.myConn.stop() # Stops the backend / frontend streaming
        
    def stop_video(self):
        self.myConn.stop() 
    
    def on_key_press_event (self, stage, event):
        if self.isRunning:
            self.videoController.on_key_press_event(event)
        if event.keyval == clutter.keysyms.Escape:
            return True
        #print event.hardware_keycode

        """if event.keyval == clutter.keysyms.p:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()"""
            
        #The following generates a menu with an option for each of the slideshows in the base menu
    def generateMenu(self):
        
        tempMenu = self.glossMgr.create_menu() #Menu(self.MenuMgr)
        
        self.dbMgr.get_channels()
        file_list = os.listdir(self.baseDir)
        
        for directoryEntry in file_list:
            subdir = self.baseDir + "/" + directoryEntry
            if os.path.isdir(subdir):
                imgPath = subdir + "/" + os.listdir(subdir)[0]
                #print imgPath
                tempItem = tempMenu.addItem(directoryEntry, "/home/josh/.mythtv/MythVideo/0088763.jpg")
                tempItem.setAction(self)
                
                
        return tempMenu
            
            
class channel:
    
    def __init__(self, chanID, channum, name, iconLocation, xmltvid):
        self.chanID = chanID
        self.channum = channum
        self.name = name
        self.iconLocation = iconLocation
        self.xmltvid = xmltvid
        
    def get_name():
        return self.name
