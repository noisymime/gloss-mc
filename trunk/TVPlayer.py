import gst
import pygtk
import pygst
import os
import clutter

from clutter import cluttergst
from myth.MythBackendConn import MythBackendConnection
from Menu import Menu
from VideoController import VideoController

class TVPlayer:

    def __init__(self, stage, dbMgr):
        self.videoController = VideoController(stage)
        self.stage = stage
        self.dbMgr = dbMgr
        self.isRunning = False

        
    def begin(self, menuMgr):
        self.menuMgr = menuMgr
        #self.buffer_file_reader = open("test.mpg","r")
        menuMgr.get_selector_bar().set_spinner(True)
        (server, port) = self.dbMgr.get_backend_server()
        self.myConn = MythBackendConnection(self, server, port)
        self.myConn.start()
        #vid.begin(self.stage)
        
        self.isRunning = True
        
    def begin_playback(self, buffer_file):
        self.menuMgr.get_selector_bar().set_spinner(False)
        uri = "file://" + os.getcwd() +"/" + buffer_file
        self.videoController.play_video(uri)
        
        """
        timeline = clutter.Timeline(15, 25)
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        behaviour = clutter.BehaviourOpacity(alpha, 0,255)
        behaviour.apply(self.video)
        
        self.stage.add(self.video)
        self.video.set_playing(True)
        timeline.start()
        #return None
        """
        
    def video_size_change(self, texture, width, height):
        self.video.set_property("sync-size", False)
        self.video.set_position(0, 0)
        xy_ratio = float(width / height)
        print "XY Ratio: " + str(xy_ratio)
        
        width = int(self.stage.get_width())
        height = int (width / xy_ratio)
        height = 768
        
        self.video.set_size(width, height)
        
    def stop(self):
        self.videoController.stop_video()
        self.myConn.stop() # Stops the backend / frontend streaming
            
    
    def on_key_press_event (self, stage, event):
        if self.isRunning:
            self.videoController.on_key_press_event(event)
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
        
        tempMenu = Menu(self.MenuMgr)
        
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
