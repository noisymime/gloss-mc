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
        self.video = cluttergst.VideoTexture()
        self.video.connect('size-change', self.video_size_change)
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
        self.menuMgr = menuMgr
        #self.buffer_file_reader = open("test.mpg","r")
        menuMgr.get_selector_bar().set_spinner(True)
        (server, port) = self.dbMgr.get_backend_server()
        self.myConn = MythBackendConnection(self, server, port)
        self.myConn.start()
        #vid = VideoController()
        #vid.begin(self.stage)
        #self.begin_playback(self.buffer_file_reader.fileno())
        
    def begin_playback(self, fd):
        #self.video.set_filename("test.mpg")
        #print "File Descriptor: " + str(fd)
        #self.buffer_file = open("test.mpg","r")
        #fd = self.buffer_file.fileno()
        #print os.read(fd, 100)
        stage = self.menuMgr.get_stage()
        self.menuMgr.get_selector_bar().set_spinner(False)
        self.video.set_uri("fd://"+str(fd))
        #self.video.set_property("fullscreen", True)
        self.video.set_opacity(0)  
        self.video.show()
        
        timeline = clutter.Timeline(15, 25)
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        behaviour = clutter.BehaviourOpacity(alpha, 0,255)
        behaviour.apply(self.video)
        
        self.stage.add(self.video)
        self.video.set_playing(True)
        self.video.set_size(400, 300)
        timeline.start()
        #return None
        
    def video_size_change(self, texture, width, height):
        self.video.set_property("sync-size", False)
        self.video.set_position(0, 0)
        xy_ratio = float(width / height)
        print "XY Ratio: " + str(xy_ratio)
        
        width = int(self.stage.get_width())
        height = int (width / xy_ratio)
        height = 768
        
        print "Width: " + str(width)
        print "Height: " + str(height)
        
       
        self.video.set_size(width, height)
        
        
        
        """
        playbin = self.video.get_playbin() .get_by_name("decodebin0")
        for element in playbin.elements():
            print element.get_name()
        
        sink = playbin.elements().next()
        deinterlace = gst.element_factory_make("ffdeinterlace", "deinterlace")
        playbin.add(deinterlace)
        #gst.element_link_many(sink, deinterlace)
        self.video.set_size(stage.get_width(), stage.get_height())

        #self.video.set_height(stage.get_height())
        
        
        
        self.video_texture = clutter.Texture()
        self.pipeline = gst.Pipeline("mypipeline")
        self.pbin = gst.element_factory_make("playbin", "pbin");
        self.sink = cluttergst.video_sink_new(self.video_texture)
        self.pbin.set_property("uri", "fd://"+str(fd))

        # add elements to the pipeline
        self.pipeline.add(self.pbin)
        self.pipeline.set_state(gst.STATE_PLAYING)
        """
    def stop(self):
        if self.video.get_playing():
            self.video.set_playing(False)
            self.myConn.stop()
            
            timeline = clutter.Timeline(15, 25)
            timeline.connect('completed', self.end_video_event)
            alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
            behaviour = clutter.BehaviourOpacity(alpha, 255,0)
            behaviour.apply(self.video)
        
            timeline.start()
            
            
    def end_video_event(self, data):
        self.stage.remove(self.video) 
    
    def on_key_press_event (self, stage, event):
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
