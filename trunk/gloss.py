import sys
import clutter
#import gobject
import pygtk
import gtk
import gobject
import os.path
#import threading
from SplashScr import SplashScr
from themeMgr import ThemeMgr

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
from GlossMgr import GlossMgr
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
        #clutter.threads_enter()
        gobject.timeout_add(500, self.loadGloss)
        #clutter.threads_leave()
        #clutter.threads_add_timeout(500, self.loadGloss())
    
    def loadGloss(self):
        
        self.glossMgr = GlossMgr(self.stage)

        #Update splash status msg
        self.splashScreen.set_msg("Creating menus")
        MainMenu = Menu(self.glossMgr)
        #menu1.addItem("nothing", "ui/dvd.png")
        #menu1.addItem("nothing", "ui/dvd.png")
        #menu1.addItem("nothing", "ui/dvd.png")

        #menu1.setListFont('Tahoma 42')
        MainMenu.setMenuPositionByName("center")
        #self.MainMenu = menu


        #Update splash status msg
        self.splashScreen.set_msg("Connecting to MythTV server")        
        #Create a master mySQL connection
        self.dbMgr = mythDB()
        
        #Update splash status msg
        for mods in modules:
            #print "Loading mod..."
            tempMod = mods.Module(self.glossMgr, self.dbMgr)
            title =  tempMod.title
            #print title
            self.splashScreen.set_msg("Loading "+title)
            temp_menu_item = MainMenu.addItem(title)
            temp_menu_item.add_image_from_texture(tempMod.menu_image)
            
            temp_menu_item.setAction(tempMod.action())
        
        self.splashScreen.remove()
        self.stage.connect('key-press-event', self.glossMgr.on_key_press_event)
        MainMenu.display()
        MainMenu.selectFirst(True)
        
       
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
