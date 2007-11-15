import sys
import clutter
#import gobject
import pygtk
import gtk
import gobject
import os.path
#import threading
from SplashScr import SplashScr

#Import all the modules
mod_dir = "modules"
module_list = os.listdir(mod_dir)

modules = []
for fs_object in module_list:
    path = mod_dir + "/" + fs_object
    if os.path.isdir(path) and (not fs_object[0] == "."):
        tmp_dir = mod_dir+"/"+fs_object+"/"+fs_object
        print "Found Module: " + fs_object
        modules.append(__import__(tmp_dir))
        
from Menu import Menu
from MenuMgr import MenuMgr
#from Slideshow import Slideshow
#from VideoPlayer import VideoPlayer
#from MusicPlayer import MusicPlayer
#from TVPlayer import TVPlayer
#from DvdPlayer import DvdPlayer

from myth.MythMySQL import mythDB


class MainApp:
    def __init__ (self):
        gtk.gdk.threads_init()
        clutter.threads_init()
    
        self.stage = clutter.stage_get_default()
        self.stage.set_color(clutter.color_parse('Black'))
        #self.stage.set_size(800, 600)
        self.stage.set_property("fullscreen", True)
        self.stage.connect('button-press-event', self.on_button_press_event)
        self.stage.show_all()
        #clutter.main()
        
        #hide the cursor
        self.stage.hide_cursor()
        
        #Display a loading / splash screen
        self.splashScreen = SplashScr(self.stage)
        self.splashScreen.display()
        gobject.timeout_add(500, self.loadGloss)
        #clutter.threads_add_timeout(500,self.loadGloss())
    
    def loadGloss(self):


        self.menuMgr = MenuMgr(self.stage)

        #Update splash status msg
        self.splashScreen.set_msg("Creating menus")
        menu1 = Menu(self.menuMgr)
        menu1.addItem("TV", "ui/dvd.png")
        menu1.addItem("Slideshow", "ui/gallery.png")        
        menu1.addItem("Videos", "ui/videos.png")
        menu1.addItem("Link", "ui/link.png")
        menu1.addItem("DVD", "ui/dvd.png")
        menu1.addItem("nothing", "ui/dvd.png")
        menu1.addItem("nothing", "ui/dvd.png")
        menu1.addItem("nothing", "ui/dvd.png")

        #menu1.setListFont('Tahoma 42')
        menu1.setMenuPositionByName("center")
        self.menu1 = menu1
        
        self.menu2 = Menu(self.menuMgr)
        self.menu2.addItem("Nothing", "ui/dvd.png")
        self.menu2.addItem("Link", "ui/gallery.png")
        self.menu2.addItem("blah3", "ui/game.png")
        self.menu2.addItem("blah4", "ui/music.png")
        self.menu2.addItem("blah", "ui/dvd.png")
        self.menu2.addItem("blah2", "ui/dvd.png")
        self.menu2.addItem("blah3", "ui/dvd.png")
        self.menu2.addItem("blah4", "ui/dvd.png")
        #self.menu2.setListFont('Tahoma 42')
        self.menu2.setMenuPositionByName("center")


        #Update splash status msg
        self.splashScreen.set_msg("Connecting to MythTV server")        
        #Create a master mySQL connection
        self.dbMgr = mythDB()
        
        #Update splash status msg
        self.splashScreen.set_msg("Loading gallery")
        self.mySlideshow = modules[0].Slideshow(self.menuMgr, self.dbMgr)
       
        #Update splash status msg
        self.splashScreen.set_msg("Loading videos")
        self.vidPlayer = modules[2].VideoPlayer(self.stage, self.dbMgr)
        #Update splash status msg
        self.splashScreen.set_msg("Setting up TV player")
        self.tvPlayer = modules[1].TVPlayer(self.stage, self.dbMgr)
        #Update splash status msg
        self.splashScreen.set_msg("Setting up DVD player")
        self.dvdPlayer = modules[3].DvdPlayer(self.stage)
        #Update splash status msg
        self.splashScreen.set_msg("Setting up Music player")
        self.musicPlayer = modules[4].MusicPlayer(self.stage)
        
        menu1.getItem(0).setAction(self.tvPlayer)
        #menu1.getItem(1).setAction(self.mySlideshow)
        menu1.getItem(1).setAction(self.mySlideshow.generateMenu())
        menu1.getItem(2).setAction(self.vidPlayer)
        menu1.getItem(3).setAction(self.menu2)
        menu1.getItem(4).setAction(self.dvdPlayer)
        
        self.menu2.getItem(1).setAction(self.menu1)
        
        self.splashScreen.remove()
        self.stage.connect('key-press-event', self.menuMgr.on_key_press_event)
        self.menu1.display()
        self.menu1.selectFirst(True)
        
        return False
        #print self.menuMgr.get_selector_bar().get_abs_position()
        #self.menuMgr.get_selector_bar().set_spinner(True)


    def on_button_press_event (self, stage, event):
        print "mouse button %d pressed at (%d, %d)" % \
              (event.button, event.x, event.y)
        if event.button == 1:
            pass
        
    
    def run (self):
        self.stage.show()
        #self.timeline.start()
        clutter.main()

def main (args):
    app = MainApp()
    #app.loadGloss()
    app.run()

    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
