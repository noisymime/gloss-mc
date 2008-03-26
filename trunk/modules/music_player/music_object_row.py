import time
import thread
import clutter
from ui_elements.image_row import ImageRow
from ui_elements.image_frame import ImageFrame

class MusicObjectRow(ImageRow):
    
    def __init__(self, glossMgr, width, height, columns, music_player):
        ImageRow.__init__(self, glossMgr, width, height, columns)
        self.music_player = music_player
        self.sleep = False
        
        self.objectLibrary = []
        self.timeline = None
        
    def add_object(self, object):
        self.objectLibrary.append(object)
        
        
    def load_image_range(self, start, end, as_thread = False, thread_data = None):
        #External timeline can be set by other objects as a form of 'lock'. If external timeline is running, thread will be paused
        self.external_timeline = None
        
        for i in range(start, end):
            object = self.objectLibrary[i]
            print "loading: " + object.name
            pixbuf = object.get_image()
            #If there is currently motion, we need to pause this work
            while self.should_sleep():
                time.sleep(0.1)
            #if self.sleep: 
                #self.timeline.connect('completed', self.restart_cb)
                #time.sleep(self.music_player.sleep_time)

            if as_thread: clutter.threads_enter()
            if pixbuf == object.PENDING_DOWNLOAD:
                #Get the temporary image
                pixbuf = object.get_default_image()
                tmpImage = ImageFrame(pixbuf, self.image_size, use_reflection = True, quality = ImageFrame.QUALITY_FAST) #clutter.Texture()
                object.connect("image-found", self.set_image_cb, object, tmpImage)
            elif not pixbuf is None:
                #If we're performing this loading as a seperate thread, we need to lock the Clutter threads

                tmpImage = ImageFrame(pixbuf, self.image_size, use_reflection=True, quality = ImageFrame.QUALITY_FAST)

            else:
                pixbuf = object.get_default_image()
                tmpImage = ImageFrame(pixbuf, self.image_size, use_reflection = True, quality = ImageFrame.QUALITY_FAST) #clutter.Texture()

            if as_thread: clutter.threads_leave()
            self.add_texture_group(tmpImage)

        
        #print "Finished threads"
        
    #Just a callback function to call 'load_image_range()' in a new thread
    def load_image_range_cb(self, timeline):
        thread.start_new_thread(self.load_image_range, (self.num_columns, len(self.objectLibrary)-1, True))
        
    #A simple callback funtion to set the image of an artist/album after it has completed a download
    def set_image_cb(self, data, music_object, tmpImage):
        #if self.glossMgr.debug:
        print "Image for music_object '%s' downloaded" % (music_object.name)
        pixbuf = music_object.get_image()
        if not pixbuf is None:
            clutter.threads_init()
            tmpImage.set_pixbuf(pixbuf)
            clutter.threads_leave()
    
    def restart_cb(self, data):
        self.sleep = True
        
    def should_sleep(self):
        ret_val = False
        #if self.sleep:
        #    return True
        
        if not self.external_timeline is None:
            if self.external_timeline.is_playing():
                ret_val = True
        
        if not self.timeline is None:
            if self.timeline.is_playing():
                ret_val = True
                
        return ret_val
            
    def get_current_object(self):
        return self.objectLibrary[self.currentSelection]