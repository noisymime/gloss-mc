import time
import clutter
import gobject
from ui_elements.image_row import ImageRow
from ui_elements.image_frame import ImageFrame

class MusicObjectRow(ImageRow):
        #Setup signals
    __gsignals__ =  { 
        "load-complete": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "load-begin": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
        }
    
    fps = 75
    frames = 45
    
    def __init__(self, glossMgr, width, height, columns, music_player):
        ImageRow.__init__(self, glossMgr, width, height, columns)
        self.music_player = music_player
        self.sleep = False
        self.glossMgr = glossMgr
        
        self.objectLibrary = []
        self.timeline = None
        self.loaded_max = 0
        
    def add_object(self, object):
        self.objectLibrary.append(object)
        
    def load_image_range_cb(self, timeline, start, end, as_thread = False, thread_data = None):
        self.load_image_range(start, end, as_thread, thread_data)
        
    def load_image_range(self, start, end, as_thread = False, thread_data = None):
        #External timeline can be set by other objects as a form of 'lock'. If external timeline is running, thread will be paused
        self.external_timeline = None
        self.buffer = 5
        
        self.emit("load-begin")
        #Do a check so we don't reload anything that's already been done
        if start < self.loaded_max:
            start = self.loaded_objects
        for i in range(start, end):
            object = self.objectLibrary[i]
            if self.glossMgr.debug: print "Music_Player: loading: " + object.name
            if i > (self.num_columns + self.buffer):
                pixbuf = object.get_default_image()
            else:
                pixbuf = object.get_image(size = self.image_size)

            self.process_pixbuf(pixbuf, object)

        self.loaded_max = (self.num_columns + self.buffer)
        self.emit("load-complete")
        return False
     
    def process_pixbuf(self, pixbuf, object):
        if pixbuf == object.PENDING_DOWNLOAD:
            #Get the temporary image
            #if as_thread: clutter.threads_enter()
            pixbuf = object.get_default_image()
            tmpImage = ImageFrame(pixbuf, self.image_size, use_reflection = True, quality = ImageFrame.QUALITY_FAST) #clutter.Texture()
            object.connect("image-found", self.set_image_cb, object, tmpImage)
            #if as_thread: clutter.threads_leave()
        elif not pixbuf is None:
            #If we're performing this loading as a seperate thread, we need to lock the Clutter threads
            #if as_thread: clutter.threads_enter()
            tmpImage = ImageFrame(pixbuf, self.image_size, use_reflection=True, quality = ImageFrame.QUALITY_FAST)
            #if as_thread: clutter.threads_leave()
        else:
            #if as_thread: clutter.threads_enter()
            pixbuf = object.get_default_image()
            tmpImage = ImageFrame(pixbuf, self.image_size, use_reflection = True, quality = ImageFrame.QUALITY_FAST) #clutter.Texture()
            #if as_thread: clutter.threads_leave()

        self.add_texture_group(tmpImage)
        
    #A simple callback funtion to set the image of an artist/album after it has completed a download
    def set_image_cb(self, data, music_object, tmpImage):
        #if self.glossMgr.debug:
        print "Image for music_object '%s' downloaded" % (music_object.name)
        pixbuf = music_object.get_image()
        if not pixbuf is None:
            clutter.threads_enter()
            tmpImage.set_pixbuf(pixbuf)
            clutter.threads_leave()
            
    def get_current_object(self):
        return self.objectLibrary[self.currentSelection]
    
    def move_common(self, newItem):
        if (newItem + self.buffer) > self.loaded_max:
            max_load = newItem + int(self.num_columns / 2 + 1)
            for i in range(self.loaded_max, max_load):
                object = self.objectLibrary[i]
                img_frame = self.textureLibrary[i]
                print "loading: " + object.name
                pixbuf = object.get_image(size = self.image_size)
                
                if pixbuf == object.PENDING_DOWNLOAD:
                    #Get the temporary image
                    pixbuf = object.get_default_image()
                    object.connect("image-found", self.set_image_cb, object, img_frame)
                
                img_frame.set_pixbuf(pixbuf)
                
            self.loaded_max = max_load
                
        ImageRow.move_common(self, newItem)