import clutter
from clutter import cluttergst
from Menu import Menu
import time
import os.path
import pygtk
import gtk
import random
#import thread

class Slideshow:
    image_file_types = ["jpg", "gif", "jpeg", "png", "bmp"]
    sound_file_types = ["mp3", "wav", "ogg"] #possibly more supported by default?
    imageDuration = 7 # In seconds
    effect_FPS = 50

    def __init__(self, MenuMgr, dbMgr):
        self.MenuMgr = MenuMgr
        self.currentTexture = clutter.Texture()
        self.currentSong = None
        self.paused = False
        self.textures = []
        self.music = []
        self.overlay = clutter.Rectangle()
        self.backdrop = None
        
        #Load the base image directory. This is pulled from the myth db's settings table
        self.baseDir = dbMgr.get_setting('GalleryDir')
        
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
        
    def loadDir(self, dirPath, recurse):
        if not os.path.isdir(dirPath):
            print "ERROR: Invalid path"
            return None
        
        new_file_list = os.listdir(dirPath)
        
        #If recursive sub-dirs is on, loop through any directories
        if recurse:
            for fs_object in new_file_list:
                path = dirPath + "/" + fs_object
                if os.path.isdir(path):
                    self.loadDir(path, True)
        
        new_image_list = filter(self.filterImageFile, new_file_list)
        new_sound_list = filter(self.filterSoundFile, new_file_list)
        
        #Load pictures into textures array
        for pic in new_image_list:
            imgName = dirPath + "/" + pic
            self.textures.append(imgName)
            
            
        #Load sound into music array
        i = len(self.music)
        for sound in new_sound_list:
            self.music.append(cluttergst.Audio())
            sndName = dirPath + "/" + sound
            self.music[i].set_filename(sndName)
            i = i+1
        
    #This makes sure we only take in image files
    def filterImageFile(self, fileName):
        extension = fileName[-3:] #Get 3 letter extension
        if extension in self.image_file_types:
            return True
        else:
            return False
            
    #This makes sure we only take in sound files
    def filterSoundFile(self, fileName):
        extension = fileName[-3:] #Get 3 letter extension
        if extension in self.sound_file_types:
            return True
        else:
            return False
    
    def begin(self, MenuMgr):
        self.stage = self.MenuMgr.get_stage()
        
        #self.MenuMgr.get_selector_bar().set_spinner(True)
        #self.stage.queue_redraw()
        
        #Clear out music and texture lists
        self.textures = [] 
        self.music = []
        #Then load them back up
        slideName = self.baseDir + "/" + self.MenuMgr.get_current_menu().get_current_item().get_data()
        self.loadDir(slideName, True)
        #self.MenuMgr.get_selector_bar().set_spinner(False)
        
        if self.backdrop == None:
            #Create a rectangle that serves as the backdrop for the slideshow
            self.backdrop = clutter.Rectangle()
            self.backdrop.set_color(clutter.color_parse('Black'))
            self.backdrop.set_width(self.stage.get_width())
            self.backdrop.set_height(self.stage.get_height())
            self.stage.add(self.backdrop)
        #Fade the backdrop in
        #self.image_texture_group.set_opacity(255)
        self.backdrop.set_opacity(0)
        self.backdrop.show()
        timeline_backdrop = clutter.Timeline(10,30)
        alpha = clutter.Alpha(timeline_backdrop, clutter.ramp_inc_func)
        self.backdrop_behaviour = clutter.BehaviourOpacity(alpha, 0, 255)
        self.backdrop_behaviour.apply(self.backdrop)
        timeline_backdrop.start()
        
        
        #print "No of children: " + str(self.image_texture_group.get_n_children())
        #Get a random texture
        self.rand1 = random.randint(0, len(self.textures)-1)
        self.currentFilename = self.textures[self.rand1]
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.currentFilename)
        self.currentTexture.set_pixbuf(pixbuf)
        self.stage.add(self.currentTexture)
        #Make sure its visible
        self.currentTexture.set_opacity(255)
        
        #Get a random song (if there's songs available)
        if not len(self.music) == 0:
            self.rand1 = random.randint(0, len(self.music)-1)
            self.currentSong = self.music[self.rand1]
            self.playNextSong(None)
        
        #Housekeeping
        self.nextSong = None
        
        #Begin the show
        self.currentTexture.show()
        self.nextImage(self.currentTexture)
        
    def end(self):
        pass

    
    def nextImage(self, currentTexture):
        #Setup stuff for KEN BURNS EFFECT!!
        self.timeline_main = clutter.Timeline((self.effect_FPS * self.imageDuration), self.effect_FPS)
        self.timeline_main.connect('completed', self.image_timeline_end_event)
        self.alpha = clutter.Alpha(self.timeline_main, clutter.ramp_inc_func)
        
        #Decide on the next texture to use
        self.nextTexture = None
        while (self.nextTexture == None):
            self.rand1 = random.randint(0, len(self.textures)-1 )
            self.nextTexture = clutter.Texture()
            self.newFilename = self.textures[self.rand1]
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.newFilename)
            self.nextTexture.set_pixbuf(pixbuf)
            #Make sure we don't show the same photo twice
            if (self.newFilename == self.currentFilename) and (len(self.textures) > 1):
                self.nextTexture = None
            
        #Make sure its not visible initially (Prevents a nasty flicker the first time a photo is shown)
        self.nextTexture.set_opacity(0)
               
        #Zooming stuff
        rand_zoom = random.uniform(1,1.3) # Zoom somewhere between 1 and 1.3 times
        self.behaviour1 = clutter.BehaviourScale(self.alpha, 1, rand_zoom, clutter.GRAVITY_CENTER)
        
        #panning stuff
        x_pos = self.currentTexture.get_x() + random.randint(-100, 100)
        y_pos = self.currentTexture.get_y() + random.randint(-100, 100)
        self.alpha = clutter.Alpha(self.timeline_main, clutter.ramp_inc_func)
        
        knots = (\
                (self.currentTexture.get_x(), self.currentTexture.get_y()),\
                (x_pos, y_pos)\
                )
        self.behaviour2 = clutter.BehaviourPath(self.alpha, knots)
            
        
        #Start and run the Ken Burns effect
        self.behaviour1.apply(self.currentTexture)
        self.behaviour2.apply(self.currentTexture)
        self.timeline_main.start()       

        
    def image_timeline_end_event(self, data):
        #Add the timeline for the dissolve at the end
        self.timeline_dissolve = clutter.Timeline(30,30)
        self.timeline_dissolve.connect('completed', self.dissolve_timeline_end_event)
        self.alpha_dissolve = clutter.Alpha(self.timeline_dissolve, clutter.ramp_inc_func)
    
        #Setup the dissolve to the next image
        self.behaviour3 = clutter.BehaviourOpacity(self.alpha_dissolve, 255, 0)
        self.behaviour4 = clutter.BehaviourOpacity(self.alpha_dissolve, 0, 255)
        
        self.behaviour3.apply(self.currentTexture)
        self.behaviour4.apply(self.nextTexture)
        
        #Pick a random spot for the next image
        x_pos = random.randint(0, abs(self.stage.get_width() - self.nextTexture.get_width()) ) #Somewhere between 0 and (stage_width-image_width)
        y_pos = random.randint(0, abs(self.stage.get_height() - self.nextTexture.get_height())  )
        self.nextTexture.set_position(x_pos, y_pos)
        
        self.oldTexture = self.currentTexture
        self.currentTexture = self.nextTexture
        self.currentFilename = self.newFilename
        self.stage.add(self.currentTexture)
        self.nextTexture.show()
        self.timeline_dissolve.start()
        self.nextImage(self.currentTexture)
        
    def dissolve_timeline_end_event(self, data):
        self.stage.remove(self.oldTexture)
        
    #Begins playing a new song
    def playNextSong(self, data):
        self.nextSong = None
        #Check first that there actually is music
        if len(self.music) == 0:
            return None
            
        #Decide on the next song to play
        while self.nextSong == None:
            self.rand1 = random.randint(0, len(self.music)-1)
            self.nextSong = self.music[self.rand1]
            #Make sure we don't play the same song twice
            if (self.nextSong == self.currentSong) and (len(self.music) > 1):
                self.nextSong = None
        
        self.currentSong = self.nextSong
        self.currentSong.set_playing(True)
        self.currentSong.connect('eos', self.playNextSong)
        
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
        self.stop_behaviour = clutter.BehaviourOpacity(alpha, 255, 0)
        self.stop_behaviour.apply(self.currentTexture)
        self.stop_behaviour.apply(self.backdrop)
        self.stop_behaviour.apply(self.overlay)
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
        
        tempMenu = Menu(self.MenuMgr)
        #print self.baseDir
        file_list = os.listdir(self.baseDir)
        
        for directoryEntry in file_list:
            subdir = self.baseDir + "/" + directoryEntry
            if os.path.isdir(subdir):
                if not (len(os.listdir(subdir)) == 0):
                    imgPath = subdir + "/" + os.listdir(subdir)[0]
                    #print imgPath
                tempItem = tempMenu.addItem(directoryEntry, "/home/josh/.mythtv/MythVideo/0088763.jpg")
                tempItem.setAction(self)
                
                
        return tempMenu
        
