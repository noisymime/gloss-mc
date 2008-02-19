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
        
#from Menu import Menu
from GlossMgr import GlossMgr
from myth.MythMySQL import mythDB

class MainApp:
    def __init__ (self, args):
        gtk.gdk.threads_init()
        clutter.threads_init()
    
        self.args = args
    
        self.stage = clutter.stage_get_default()
        self.stage.set_color(clutter.color_parse('Black'))
        self.stage.connect('button-press-event', self.on_button_press_event)
        #hide the cursor
        self.stage.hide_cursor()
        
        #clutter.threads_enter()
        gobject.timeout_add(500, self.loadGloss)
        #clutter.threads_leave()
        #clutter.threads_add_timeout(500, self.loadGloss())
    
    def loadGloss(self):
        #Create a master mySQL connection
        self.dbMgr = mythDB()
        if not self.dbMgr.connected:
            return
        
        #Do an initial lookup for GUI size
        width = int(self.dbMgr.get_setting("GuiWidth"))
        height = int(self.dbMgr.get_setting("GuiHeight"))
        #Set stage size
        if width == 0 and height == 0:
            self.stage.fullscreen()
            self.stage.set_property("fullscreen", True)
        else:
            self.stage.set_size(width, height)
        
        #now that the size is set, we can show the stage
        self.stage.show()
        #Display a loading / splash screen
        self.splashScreen = SplashScr(self.stage)
        self.splashScreen.display()
        #And create the Gloss Manager
        self.glossMgr = GlossMgr(self.stage)

        
        #loop through the args
        for arg in self.args:
            if arg == "--debug":
                print "Using debug mode"
                self.glossMgr.debug = True

        #Update splash status msg
        self.splashScreen.set_msg("Creating menus")
        MainMenu = self.glossMgr.create_menu() 
        #Update splash status msg
        self.splashScreen.set_msg("Connecting to MythTV server")        
        

        #Load all modules
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


    def on_button_press_event (self, stage, event):
        print "mouse button %d pressed at (%d, %d)" % \
              (event.button, event.x, event.y)
        if event.button == 1:
            pass
        
    
    def run (self):
        #self.timeline.start()
        clutter.main()

def main (args):
    app = MainApp(args)
    #app.loadGloss()
    app.run()

    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
