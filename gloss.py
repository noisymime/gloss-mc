"""
This file is part of the Gloss Mythtv Frontend.

    Gloss is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Gloss is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Gloss.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import clutter 
import pygtk
import gtk
import gobject
import os.path
from SplashScr import SplashScr
from utils.themeMgr import ThemeMgr
from GlossMgr import GlossMgr
from myth.MythMySQL import mythDB

modules = []
def find_modules():
        #Import all the modules
        mod_dir = "modules"
        module_list = os.listdir(mod_dir)

        for fs_object in module_list:
            path = mod_dir + "/" + fs_object
            if os.path.isdir(path) and (not fs_object[0] == "."):
                tmp_dir = mod_dir+"/"+fs_object+"/"+fs_object
                #Only print the module if its not the tests one
                if not fs_object == "tests": print "Found Module: " + fs_object
                modules.append(__import__(tmp_dir))

class MainApp:
    def __init__ (self, args):
        gtk.gdk.threads_init()
        clutter.threads_init()
    
        self.args = args
    
        self.stage = clutter.Stage()
        self.stage.set_color(clutter.color_parse('Black'))
        self.stage.connect('button-press-event', self.on_button_press_event)
        #hide the cursor
        self.stage.hide_cursor()
        
        self.show_tests = False
        
        #Create a master mySQL connection
        self.dbMgr = mythDB()
        if not self.dbMgr.connected:
            self.connected = False
            return
        self.connected = True
        
        #Do an initial lookup for GUI size
        (width, height) = (self.dbMgr.get_setting("GuiWidth"), self.dbMgr.get_setting("GuiHeight"))
        if not width is None:
            width = int(width)
        else:
            width = 0
        if not height is None:
            height = int(height)
        else:
            height = 0
        #Set stage size
        if width == 0 and height == 0:
            self.stage.fullscreen()
            self.stage.set_property("fullscreen", True)
        else:
            self.stage.set_size(width, height)
        
        #now that the size is set, we can fade in the stage
        self.stage.set_opacity(0)
        self.stage.show()
        timeline = clutter.Timeline(20,40)
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.behaviour_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
        self.behaviour_opacity.apply(self.stage)
        timeline.start()
        
        theme = None
        debug = False
        #loop through the args
        for i in range(0, len(self.args)):
            arg = self.args[i]
            if arg == "--debug":
                print "Using debug mode"
                debug = True
            elif arg == "--tests":
                self.show_tests = True
                print "Showing tests"
            elif arg == "--theme":
                theme = self.args[i+1]
                print "Using theme %s" % theme
        
        #Create the Gloss Manager
        self.glossMgr = GlossMgr(self.stage, self.dbMgr, theme=theme)
        self.glossMgr.debug = debug
        
        #Display a loading / splash screen
        self.splashScreen = SplashScr(self.glossMgr)
        self.splashScreen.display()
        
        #clutter.threads_enter()
        gobject.timeout_add(500, self.loadGloss)
        #clutter.threads_leave()
        #clutter.threads_add_timeout(500, self.loadGloss())
    
    def loadGloss(self):


        #Update splash status msg
        self.splashScreen.set_msg("Creating menus")
        MainMenu = self.glossMgr.create_menu()
        self.glossMgr.addMenu(MainMenu)
        #Update splash status msg
        self.splashScreen.set_msg("Connecting to MythTV server")

        #Load all modules
        for mods in modules:
            
            tempMod = mods.Module(self.glossMgr, self.dbMgr)
            title =  tempMod.title
            if title == "Tests" and not (self.show_tests): continue
            if self.glossMgr.debug: print "Loading module: %s" % title
            
            self.splashScreen.set_msg("Loading "+title)
            #while gtk.events_pending():
            #    gtk.main_iteration(0)
            temp_menu_item = MainMenu.addItem(title)
            temp_menu_item.add_image_from_texture(tempMod.menu_image)
            temp_menu_item.setAction(tempMod.action())
         
        timeline_remove = self.splashScreen.remove_elegant()
        timeline_remove.connect("completed", self.finish_load, MainMenu)
        self.stage.connect('key-press-event', self.glossMgr.on_key_press_event)
        
    def finish_load(self, data, MainMenu):
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
    path = os.path.dirname(sys.argv[0])
    abs_path = os.path.abspath(path)
    os.chdir(abs_path)
    find_modules()
 
    app = MainApp(args)
    #app.loadGloss()
    if app.connected: app.run()

    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
