import gst
import pygtk
import pygst
import os

from clutter import cluttergst
from myth.MythBackendConn import MythBackendConnection
from Menu import Menu

class TVPlayer:

    def __init__(self, stage, dbMgr):
        self.video = cluttergst.VideoTexture()
        self.stage = stage
        self.dbMgr = dbMgr
        #audio.set_filename('cast1.avi')
        #audio.show()
        
        #test = cluttercairo.Cairo()
        #audio = cluttergst.Audio()
        #audio.set_filename('test.mp3')
        
        #stage.add(audio)
        #audio.set_playing(True)
        
        #self.db_conn = mythVideoDB()
        
    def begin(self, menuMgr):
        (server, port) = self.dbMgr.get_backend_server()
        self.myConn = MythBackendConnection(self, server, port)
        self.myConn.start()
        
    def begin_playback(self, fd):
        #self.video.set_filename("test.mpg")
        #print "File Descriptor: " + str(fd)
        #self.buffer_file = open("test.mpg","r")
        #fd = self.buffer_file.fileno()
        #print os.read(fd, 100)
        """
        self.video.set_uri("fd://"+str(fd))
        self.video.show()
        
        self.stage.add(self.video)
        self.video.set_playing(True)
        
        return None"""
        self.pipeline = gst.Pipeline("mypipeline")
        self.pbin = gst.element_factory_make("playbin", "pbin");
        self.pbin.set_property("uri", "fd://"+str(fd))
  
        # add elements to the pipeline
        self.pipeline.add(self.pbin)
        self.pipeline.set_state(gst.STATE_PLAYING)
    
    def on_key_press_event (self, stage, event):
        #print event.hardware_keycode
        #self.myConn.stop()
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
