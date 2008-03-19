import time
import thread
import clutter
from ui_elements.image_row import ImageRow
from ui_elements.image_frame import ImageFrame

class MusicObjectRow(ImageRow):
    
    def __init__(self, glossMgr, width, height, columns, music_player):
        ImageRow.__init__(self, glossMgr, width, height, columns)
        self.music_player = music_player
        
        self.objectLibrary = []
        
    def add_object(self, object):
        self.objectLibrary.append(object)
        
        
    def load_image_range(self, start, end, thread_data = None):

        for i in range(start, end):
            object = self.objectLibrary[i]
            print "loading: " + object.name
            pixbuf = object.get_image()
            time.sleep(self.music_player.sleep_time)
            tmpImage = clutter.Texture()
            if pixbuf == object.PENDING_DOWNLOAD:
                object.connect("image-found", self.set_image_cb, object, tmpImage)
            elif not pixbuf is None:
                #tmpImage.set_pixbuf(pixbuf)
                tmpImage = ImageFrame(pixbuf, self.image_size)
                
            
            self.add_texture_group(tmpImage)

        #clutter.threads_leave()
        print "Finished threads"
        
    #Just a callback function to call 'load_image_range()' in a new thread
    def load_image_range_cb(self, timeline):
        thread.start_new_thread(self.load_image_range, (self.num_columns, len(self.objectLibrary)-1))
        
    #A simple callback funtion to set the image of an artist/album after it has completed a download
    def set_image_cb(self, data, music_object, tmpImage):
        #if self.glossMgr.debug:
        print "Image for music_object '%s' downloaded" % (music_object.name)
        pixbuf = music_object.get_image()
        if not pixbuf is None:
            clutter.threads_init()
            tmpImage.set_pixbuf(pixbuf)
            clutter.threads_leave()