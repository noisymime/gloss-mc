import gst
import pygtk
import pygst
import os
import clutter
import gobject

from clutter import cluttergst
from modules.myth_tv_player.MythBackendConn import MythBackendConnection
from modules.myth_tv_player.tv_db_controller import tv_db_controller
from SplashScr import SplashScr
#from Menu import Menu
from VideoController import VideoController

class Module:
    title = "TV"

    def __init__(self, glossMgr, dbMgr):
        self.stage = glossMgr.get_stage()
        self.glossMgr = glossMgr
        self.dbMgr = dbMgr
        self.setup_ui()
        
        self.osd = osd()
        self.videoController = VideoController(glossMgr)
        self.dbController = tv_db_controller(dbMgr)
        #self.dbController.get_current_show(1033)
        self.channels = self.dbController.get_channels()
        self.currentChannel = 0

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
        (self.server, self.port) = self.dbMgr.get_backend_server()
        self.myConn = MythBackendConnection(self, self.server, self.port)
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
        if self.myConn:
            self.myConn.stop() # Stops the backend / frontend streaming
        
    def stop_video(self):
        self.myConn.stop() 
    
    def on_key_press_event (self, stage, event):
        if self.isRunning:
            #Handle up/down presses for OSD
            if (event.keyval == clutter.keysyms.Up) or (event.keyval == clutter.keysyms.Down):
                self.osd.on_key_press_event(self.stage, event, self)
            
            self.videoController.on_key_press_event(event)
            
            if (event.keyval == clutter.keysyms.Return):
                if self.osd.on_screen:
                    self.loading_scr = SplashScr(self.stage)
                    self.loading_scr.set_msg("Loading Channel ")
                    self.loading_scr.set_details(self.osd.currentChannel.name)
                    self.loading_scr.backdrop.set_opacity(180)
                    self.loading_scr.display_elegant()
                    self.videoController.pause_video(False)
                    self.myConn.stop()
                    self.myConn = None
                    self.myConn = MythBackendConnection(self, self.server, self.port)
                    self.myConn.chanNum = self.osd.currentChannel.channum
                    self.myConn.start()
                    self.videoController.unpause_video()
                    #self.loading_scr.remove()                   
                    #self.myConn.change_channel(self.currentChannel.name)
                    
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
            
            
class osd:
    
    def __init__(self):
        self.background = clutter.Texture()
        self.text = clutter.Label()
        self.text.set_font_name("Mono 40")
        self.text.show()
        
        self.on_screen = False
        self.channelOffset = 0 
        self.input_count = 0
        
    def on_key_press_event(self, stage, event, tv_player):
        if self.on_screen:
            if (event.keyval == clutter.keysyms.Up):
                self.channelOffset += 1
            elif (event.keyval == clutter.keysyms.Down):
                self.channelOffset -= 1
                
            #Increment the input counter (Only when this reaches 0 will the osd be removed from screen
            self.input_count += 1
        else:
            stage.add(self.text)
            self.channelOffset = 0
            
        self.currentChannel = tv_player.channels[tv_player.currentChannel+self.channelOffset]


        self.text.set_text(self.currentChannel.name)
        self.on_screen = True
        self.timeout_id = gobject.timeout_add(3000, self.exit, stage)
        
    def exit(self, stage):
        #First check the input counter, we only remove the osd from screen if this is 0
        if self.input_count > 0:
            self.input_count -= 1
            return False
        
        if self.on_screen:
            stage.remove(self.text)
            self.on_screen = False
            
        return False