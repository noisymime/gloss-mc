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
from MenuMgr import MenuMgr
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
        #Load the theme manager
        self.themeMgr = ThemeMgr(self.stage)
        elem = self.themeMgr.get_texture("selector_bar", None)
        #print self.themeMgr.find_attribute_value(elem.childNodes, "position", "type")
        test = "12345"
        print test[:-1]

        self.menuMgr = MenuMgr(self.stage)

        #Update splash status msg
        self.splashScreen.set_msg("Creating menus")
        MainMenu = Menu(self.menuMgr)
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
            title =  mods.Module.title
            image_uri = "ui/"+mods.Module.menu_image
            self.splashScreen.set_msg("Loading "+title)
            tempMod = mods.Module(self.menuMgr, self.dbMgr)
            temp_menu_item = MainMenu.addItem(title, image_uri)
            
            temp_menu_item.setAction(tempMod.action())
        
        self.splashScreen.remove()
        self.stage.connect('key-press-event', self.menuMgr.on_key_press_event)
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
