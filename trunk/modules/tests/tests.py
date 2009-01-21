import clutter
import cluttergst
from ui_elements.image_preview import image_previewer
import time
import os.path
import pygtk
import gtk
import random

class Module:
    title = "Tests"
    
    max_percent_of_stage = 0.75 # The maximum percentage of the stage size that images can be

    def __init__(self, glossMgr, dbMgr):
        self.glossMgr = glossMgr
        self.dbMgr = dbMgr
        self.setup_ui()
        self.currentSong = None
        self.paused = False
        self.textures = []
        self.music = []
        self.overlay = clutter.Rectangle()
        self.backdrop = None
        
        
    def setup_ui(self):
        self.menu_image = self.glossMgr.themeMgr.get_texture("slideshow_menu_image", None, None)
        
        #Need to get/set the size of the preview images
        element = self.glossMgr.themeMgr.search_docs("preview_image", "main").childNodes
        (self.preview_width, self.preview_height) = self.glossMgr.themeMgr.get_dimensions(element, self.glossMgr.stage)
        
        
    def action(self):
        return self.generateMenu()
        
    def on_key_press_event (self, stage, event):
        #print event.hardware_keycode
        if event.keyval == clutter.keysyms.p:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()
        if event.keyval == clutter.keysyms.Escape:
            return True
        
    
        
    #A simple function to add recursive nature to os.listdir
    def os_listdir_recursive(self, dirPath, file_list = None, showHidden = True):
        if file_list is None: file_list = []
        new_file_list = os.listdir(dirPath)
        for fs_object in new_file_list:
                if not showHidden and fs_object[0] == ".": break
                path = dirPath + "/" + fs_object
                if os.path.isdir(path):
                    self.os_listdir_recursive(path, file_list)
                else: file_list.append(path)

        return file_list
    
    def begin(self, glossMgr):
        pass        
    def end(self):
        pass

    
    
    def pause(self):
        self.paused = True
    
        #Use the overlay to go over show
        self.overlay.set_color(clutter.color_parse('Black'))
        self.overlay.set_width(self.stage.get_width())
        self.overlay.set_height(self.stage.get_height())
        self.overlay.set_opacity(0)
        self.overlay.show()
        #self.overlay.raise_top()
        #self.image_texture_group.lower(self.overlay)
        self.stage.add(self.overlay)
        #Fade the backdrop in
        timeline_overlay = clutter.Timeline(10,30)
        alpha = clutter.Alpha(timeline_overlay, clutter.ramp_inc_func)
        overlay_behaviour = clutter.BehaviourOpacity(alpha, 0, 100)
        overlay_behaviour2 = clutter.BehaviourOpacity(alpha, 255, 100) #Used on the backdrop
        overlay_behaviour3 = clutter.BehaviourOpacity(alpha, 255, 0) #Used on the current texture
        overlay_behaviour.apply(self.overlay)
        overlay_behaviour2.apply(self.backdrop)
        overlay_behaviour3.apply(self.currentTexture)
        timeline_overlay.start()
        
        #Pause the main slideshow
        self.timeline_main.pause()
        
        #Pause any music
        if not self.currentSong == None:
            if self.currentSong.get_playing():
                self.currentSong.set_playing(False)
        
    def unpause(self):
        self.paused = False
        
        #Fade the backdrop in
        timeline_overlay = clutter.Timeline(10,30)
        alpha = clutter.Alpha(timeline_overlay, clutter.ramp_inc_func)
        overlay_behaviour = clutter.BehaviourOpacity(alpha, 100, 0)
        overlay_behaviour2 = clutter.BehaviourOpacity(alpha, 100, 255) #Used on the backdrop
        overlay_behaviour3 = clutter.BehaviourOpacity(alpha, 0, 255) #Used on the current texture
        overlay_behaviour.apply(self.overlay)
        overlay_behaviour2.apply(self.backdrop)
        overlay_behaviour3.apply(self.currentTexture)
        timeline_overlay.start()
        
        #Resume the main slideshow
        self.timeline_main.start()
        
        #Resume any music
        if not self.currentSong == None:
            self.currentSong.set_playing(True)
        
    def stop(self):
        #Stop any running timelines
        self.timeline_main.stop()
            
        #Fade everything out
        timeline_stop = clutter.Timeline(10,30)
        alpha = clutter.Alpha(timeline_stop, clutter.ramp_inc_func)
        self.stop_behaviour = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=alpha)
        self.menu_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
        self.stop_behaviour.apply(self.currentTexture)
        self.stop_behaviour.apply(self.backdrop)
        self.stop_behaviour.apply(self.overlay)
        self.menu_behaviour.apply(self.menu.getItemGroup())
        timeline_stop.connect('completed', self.destroySlideshow)
        timeline_stop.start()
        
        #Stop any music
        if not self.currentSong == None:
            if self.currentSong.get_playing():
                self.currentSong.set_playing(False)
                self.currentSong.set_position(0)
        
        
    def destroySlideshow(self, data):
        self.stage.remove(self.currentTexture)
        #self.stage.remove(self.nextTexture)
        self.backdrop.hide()
        #self.stage.remove(self.overlay)
        
        self.currentTexture = None
        self.nextTexture = None
        self.currentSong = None
        self.nexttSong = None
        
    #The following generates a menu with an option for each of the slideshows in the base menu
    def generateMenu(self):        
        tempMenu = self.glossMgr.create_menu() #Menu(self.glossMgr)

        self.menu = tempMenu
        self.tests = []
        tests_dir = "modules/tests"
        module_list = os.listdir(tests_dir)

        for fs_object in module_list:
            file = tests_dir + "/" + fs_object
            if (file[-3:] == ".py") and (not file[-8:] == "tests.py"):
                file = file.rstrip(".py")
                test = __import__(file).Module(self.glossMgr, self.dbMgr)
                self.tests.append(test)
                tempItem = tempMenu.addItem(fs_object)
                tempItem.setAction(test)
        
        tempMenu.selectFirst()        
        return tempMenu
        
