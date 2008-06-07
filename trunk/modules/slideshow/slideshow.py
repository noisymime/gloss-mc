import clutter
from clutter import cluttergst
from ui_elements.image_preview import image_previewer
import time
import os.path
import pygtk
import gtk
import random
#import thread

class Module:
    title = "Slideshow"
    
    menu_image = None
    MAX_PREVIEW_IMG = 15 #The maximum number of images from each directory that will be used in the preview
    
    image_file_types = ["jpg", "gif", "jpeg", "png", "bmp"]
    sound_file_types = ["mp3", "wav", "ogg"] #possibly more supported by default?
    imageDuration = 7 # In seconds
    effect_FPS = 50
    
    max_percent_of_stage = 0.75 # The maximum percentage of the stage size that images can be

    def __init__(self, glossMgr, dbMgr):
        self.glossMgr = glossMgr
        self.setup_ui()
        self.currentSong = None
        self.paused = False
        self.textures = []
        self.music = []
        self.overlay = clutter.Rectangle()
        self.backdrop = None
        
        #Load the base image directory. This is pulled from the myth db's settings table
        self.baseDir = dbMgr.get_setting('GalleryDir')
        
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
        #Strip out any directory info
        filename_structure = fileName.split("/")
        fileName = filename_structure[ len(filename_structure)-1 ]
        
        extension = fileName[-3:] #Get 3 letter extension
        if not extension in self.image_file_types:
            return False
        elif fileName[0] == ".":
            return False
        else:
            return True
        
    #This filters for image files starting with "."
    def filterPreviewImageFile(self, fileName):
        #Strip out any directory info
        filename_structure = fileName.split("/")
        fileName = filename_structure[ len(filename_structure)-1 ]
        
        extension = fileName[-3:] #Get 3 letter extension
        if not extension in self.image_file_types:
            return False
        elif not fileName[0] == ".":
            return False
        else:
            return True
            
    #This makes sure we only take in sound files
    def filterSoundFile(self, fileName):
        extension = fileName[-3:] #Get 3 letter extension
        if extension in self.sound_file_types:
            return True
        else:
            return False
        
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
        
        self.stage = self.glossMgr.get_stage()
        self.currentTexture = clutter.Texture()
        
        #Set the maximum sizes of the images
        self.max_height = int(self.stage.get_height() * self.max_percent_of_stage)
        self.max_width = int(self.stage.get_width() * self.max_percent_of_stage)
        
        #Check for an empty baseDir, this means there are no slideshows or no db connection. We simply tell the menuMgr to go back a menu level when this occurs
        if self.baseDir is None:
            MenuMgr.go_up_x_levels(1)
            return
        #self.MenuMgr.get_selector_bar().set_spinner(True)
        #self.stage.queue_redraw()
        
        #Clear out music and texture lists
        self.textures = [] 
        self.music = []
        #Then load them back up
        slideName = self.baseDir + "/" + self.menu.get_current_item().get_data() #self.glossMgr.get_current_menu().get_current_item().get_data()
        self.loadDir(slideName, True)
        
        #Check if there actually are any images, quit if there aren't
        if len(self.textures) == 0:
            glossMgr.display_msg("Slideshow", "Directory is empty")
            if glossMgr.currentMenu.get_opacity() > 0:
                self.timeline_stop = clutter.Timeline(10,30)
                alpha = clutter.Alpha(self.timeline_stop, clutter.ramp_inc_func)
                self.stop_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
                self.stop_behaviour.apply(glossMgr.currentMenu)
                glossMgr.currentMenu.show()
                self.timeline_stop.start()
            glossMgr.currentPlugin = None
            return
        
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
        self.backdrop_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
        self.menu_behaviour = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=alpha)
        self.backdrop_behaviour.apply(self.backdrop)
        self.menu_behaviour.apply(self.menu.getItemGroup())
        timeline_backdrop.start()
        
        
        #print "No of children: " + str(self.image_texture_group.get_n_children())
        #Get a random texture
        self.currentFilename = ""
        self.currentTexture = self.get_rand_texture()
        
        (x_pos, y_pos) = self.get_random_coords(self.currentTexture)
        self.currentTexture.set_position(x_pos, y_pos)
        
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
        self.nextTexture = self.get_rand_texture()

            
        #Make sure its not visible initially (Prevents a nasty flicker the first time a photo is shown)
        self.nextTexture.set_opacity(0)
               
        #Zooming stuff
        rand_zoom = random.uniform(1,1.3) # Zoom somewhere between 1 and 1.3 times
        self.behaviour1 = clutter.BehaviourScale(x_scale_start=1, y_scale_start=1, x_scale_end=rand_zoom, y_scale_end=rand_zoom, alpha=self.alpha)
        #self.behaviour1.set_property("scale-gravity", clutter.GRAVITY_CENTER) #As at Clutter r1807 you cannot set the gravity on the line above. 
        
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
        
    #Just gets a random texture
    def get_rand_texture(self): 
        self.nextTexture = None   
        while (self.nextTexture == None):
            self.rand1 = random.randint(0, len(self.textures)-1 )
            self.newFilename = self.textures[self.rand1]
            #Make sure we don't show the same photo twice
            if (self.newFilename == self.currentFilename) and (len(self.textures) > 1):
                self.nextTexture = None
            else:
                self.nextTexture = clutter.Texture()
                pixbuf = gtk.gdk.pixbuf_new_from_file(self.newFilename)
                self.currentFilename = self.newFilename
                
                #Do a check on the size of the image
                if (pixbuf.get_width() > self.max_width) or (pixbuf.get_height() > self.max_height):
                    #Resize as necesary
                    xy_ratio = float(pixbuf.get_width()) / pixbuf.get_height()
                    if pixbuf.get_width() > pixbuf.get_height():
                        width = self.max_width
                        height = int(width / xy_ratio)
                    else:
                        height = self.max_height
                        width = int(xy_ratio * height)
        
                    pixbuf = pixbuf.scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)
                
                self.nextTexture.set_pixbuf(pixbuf)

        return self.nextTexture
        
    def image_timeline_end_event(self, data):
        #Add the timeline for the dissolve at the end
        self.timeline_dissolve = clutter.Timeline(30,30)
        self.timeline_dissolve.connect('completed', self.dissolve_timeline_end_event)
        self.alpha_dissolve = clutter.Alpha(self.timeline_dissolve, clutter.ramp_inc_func)
    
        #Setup the dissolve to the next image
        self.behaviour3 = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=self.alpha_dissolve)
        self.behaviour4 = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=self.alpha_dissolve)
        
        self.behaviour3.apply(self.currentTexture)
        self.behaviour4.apply(self.nextTexture)
        
        #Pick a random spot for the next image
        #x_pos = random.randint(0, abs(self.stage.get_width() - self.nextTexture.get_width()) ) #Somewhere between 0 and (stage_width-image_width)
        #y_pos = random.randint(0, abs(self.stage.get_height() - self.nextTexture.get_height())  )
        #Messy stuff because of damned gravity messup in 0.5
        (x_pos, y_pos) = self.get_random_coords(self.nextTexture)
        #print "pic pos: " + str(x_pos) + ":" + str(y_pos)
        
        
        self.oldTexture = self.currentTexture
        self.currentTexture = self.nextTexture
        self.currentTexture.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
        self.currentFilename = self.newFilename
        self.stage.add(self.currentTexture)
        self.nextTexture.set_position(x_pos, y_pos)
        self.nextTexture.show()
        self.timeline_dissolve.start()
        self.nextImage(self.currentTexture)
        
    def get_random_coords(self, texture):
        x_pos = random.randint(texture.get_width()/2, (self.stage.get_width() - texture.get_width()/2) ) #Somewhere between 0 and (stage_width-image_width)
        y_pos = random.randint(texture.get_height()/2, (self.stage.get_height() - texture.get_height()/2)  )
        
        return (x_pos, y_pos)
        
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
        
        #print self.baseDir
        #This occurs when there are not slideshows or we could not connect to the db to establish baseDir
        if self.baseDir is None:
            tempItem = tempMenu.addItem("No slideshows available")
            tempItem.setAction(self)
            return
        
        try:
            file_list = os.listdir(self.baseDir)
        except os.error, (errno, errstr):
            self.glossMgr.display_msg("File Error", "Could not load Slideshow directory")
            return
        
        for directoryEntry in file_list:
            subdir = self.baseDir + "/" + directoryEntry
            if os.path.isdir(subdir):
                
                tempItem = tempMenu.addItem(directoryEntry)
                
                #Start experimental schtuff (MESSY!!!)
                img_list = os.listdir(subdir)
                img_list_temp = []
                for img in img_list:
                    img = subdir + "/" + img
                    img_list_temp.append(img)
                img_list = img_list_temp
                img_list.extend(self.os_listdir_recursive(subdir, showHidden = False))
                #Attempt to get the thumbnail images
                #print img_list
                
                img_list_preview = filter(self.filterPreviewImageFile, img_list)
                if len(img_list_preview) > 0:
                    img_list = img_list_preview
                #If not, just use the full images
                else:
                    img_list = filter(self.filterImageFile, img_list)
                    
                img_previewer = image_previewer(self.glossMgr.stage)
                #Set the max preview img sizes (These come from the slideshow.xml theme file
                if (not self.preview_width is None) and (not self.preview_height is None):
                    img_previewer.set_max_img_dimensions(self.preview_width, self.preview_height)
                
                preview_count = 0
                for img in img_list:
                    #imgPath = subdir + "/" + img #os.listdir(subdir)[0]
                    imgPath = img
                    #print imgPath
                    
                    #Only add a max of 15 images to the previewer
                    if preview_count < 10:
                        img_previewer.add_texture(imgPath)
                        preview_count += 1
    
                #new_file_list = os.listdir(dirPath)
                if tempMenu.usePreviewEffects:
                    tempItem.itemTexturesGroup = img_previewer
                    img_previewer.set_position(tempItem.menu.menu_image_x, tempItem.menu.menu_image_y)
                else:
                    if not len(img_list) == 0:
                        tempItem.add_image_from_path(imgPath, 0, 0, self.preview_width, self.preview_height)
                
                tempItem.setAction(self)

        return tempMenu
        
