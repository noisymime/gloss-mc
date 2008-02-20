import gst
import pygtk, gtk
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
    myConn = None

    def __init__(self, glossMgr, dbMgr):
        self.stage = glossMgr.get_stage()
        self.glossMgr = glossMgr
        self.dbMgr = dbMgr
        self.setup_ui()
        
        self.osd = osd_channel(self.stage)
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
                self.osd.on_key_press_event(event, self)
            
            self.videoController.on_key_press_event(event)
            
            if (event.keyval == clutter.keysyms.Return):
                if self.osd.on_screen:
                    chanNum = self.osd.currentChannel.channum
                    self.set_channel(chanNum)
                    
                    
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
    
    def set_channel(self, channum):
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
        self.videoController.connect("playing", self.complete_change)
        self.myConn.start()

    def complete_change(self, data):
        self.videoController.unpause_video()
        self.loading_scr.remove_elegant()                   
            
class osd_channel(clutter.Group):
    font = "Lucida Grande "
    name_font_size = 30
    prog_title_font_size = 22
    detail_font_size = 18
    
    
    def __init__(self, stage):
        clutter.Group.__init__(self)
        self.stage = stage
        
        pixbuf = gtk.gdk.pixbuf_new_from_file("ui/splash_box.png")
        self.box = clutter.Texture()
        self.box.set_pixbuf(pixbuf)
        self.box.set_opacity(int(255 * 0.75))
        self.box.set_height(int(self.stage.get_height()* 0.15))
        self.add(self.box)
       
        self.logo = clutter.Texture()
        height = int(self.box.get_height() * 0.90)
        height = height + (height % 2) # Make sure that the dimension is even
        self.logo.set_height(height)
        self.logo.set_width(height)
        self.logo.set_position(5, int(self.box.get_height() * 0.05 ) )
        self.add(self.logo)

        self.name = clutter.Label()
        self.name.set_font_name(self.font + str(self.name_font_size))
        self.name.set_color(clutter.color_parse('White'))
        pos_x = self.logo.get_x() + int (self.logo.get_width() * 1.1)
        pos_x = pos_x 
        self.name.set_position(pos_x, 0)
        self.name.set_text(" ")
        self.add(self.name)
        
        self.prog_title = clutter.Label()
        self.prog_title.set_font_name(self.font + str(self.prog_title_font_size))
        self.prog_title.set_color(clutter.color_parse('White'))
        self.prog_title.set_position(\
                                 self.name.get_x(),\
                                 self.name.get_y() + self.name.get_height()\
                                 )
        self.add(self.prog_title)
        
        self.detail = clutter.Label()
        self.detail.set_font_name(self.font + str(self.detail_font_size))
        self.detail.set_color(clutter.color_parse('White'))
        self.detail.set_position(\
                                 self.prog_title.get_x(),\
                                 self.prog_title.get_y() + self.prog_title.get_height()\
                                 )
        self.add(self.detail)
        
        pos_x = (self.stage.get_width() - self.box.get_width()) / 2
        pos_y = int(self.stage.get_height() * 0.66)
        self.set_position(pos_x, pos_y)
        
        self.on_screen = False
        self.channelOffset = 0 
        self.input_count = 0
        
    def on_key_press_event(self, event, tv_player):
        if self.on_screen:
            if (event.keyval == clutter.keysyms.Up):
                self.channelOffset += 1
            elif (event.keyval == clutter.keysyms.Down):
                self.channelOffset -= 1
                
            #Increment the input counter (Only when this reaches 0 will the osd be removed from screen
            self.input_count += 1
        else:
            self.stage.add(self)
            self.channelOffset = 0
            
        self.currentChannel = tv_player.channels[tv_player.currentChannel+self.channelOffset]
        self.currentShow = tv_player.dbController.get_current_show(self.currentChannel.chanID)

        self.name.set_text(self.currentChannel.name)
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.currentChannel.icon)
            self.logo.set_pixbuf(pixbuf)
        except gobject.GError, e:
            print "Channel Icon not found: " + self.currentChannel.icon
        if not self.currentShow is None:
            self.prog_title.set_text(self.currentShow.title)
            self.detail.set_text(self.currentShow.description)
        else:
            self.prog_title.set_text("")
            self.detail.set_text("")
        
        self.show_all()
        self.show()
        self.on_screen = True
        self.timeout_id = gobject.timeout_add(3000, self.exit)
        
    def exit(self):
        #First check the input counter, we only remove the osd from screen if this is 0
        if self.input_count > 0:
            self.input_count -= 1
            return False
        
        if self.on_screen:
            self.stage.remove(self)
            self.on_screen = False
            
        return False