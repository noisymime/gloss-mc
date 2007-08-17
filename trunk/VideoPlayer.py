import pygtk
import gtk
import clutter
from myth.MythMySQL import mythVideoDB

class VideoPlayer():

    def __init__(self, stage):
        self.stage = stage
        self.cover_viewer = coverViewer(self.stage)
        self.videoLibrary = []
        
        self.is_playing = False
        
        #This block can be moved to begin() but causes a performance hit when loading the module *shrug*
        dbMgr = mythVideoDB()
        results = dbMgr.get_videos()
        
        for record in results:
            tempVideo = videoItem()
            tempVideo.importFromMythObject(record)
            self.videoLibrary.append(tempVideo)
            self.cover_viewer.add_image(tempVideo.getCoverfile())
        dbMgr.close_db()
        ################################################################################
        
    def on_key_press_event (self, stage, event):
        if event.keyval == clutter.keysyms.p:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()
        
    def begin(self, MenuMgr):
        
        #Create a backdrop for the player. In this case we just use the same background as the menus
        self.backdrop = clutter.CloneTexture(MenuMgr.get_skinMgr().get_Background())
        self.backdrop.set_size(self.stage.get_width(), self.stage.get_height())
        self.backdrop.set_opacity(0)
        self.backdrop.show()
        self.stage.add(self.backdrop)
        #Fade the backdrop in
        timeline_begin = clutter.Timeline(10,40)
        alpha = clutter.Alpha(timeline_begin, clutter.ramp_inc_func)
        begin_behaviour = clutter.BehaviourOpacity(alpha, 0, 255)
        begin_behaviour.apply(self.backdrop)

        self.cover_viewer.set_opacity(0)    
        self.cover_viewer.show_all()
        self.cover_viewer.show()
        self.stage.add(self.cover_viewer)
        begin_behaviour.apply(self.cover_viewer)
        
        timeline_begin.start()
            
        
    def stop(self):
           
        #Fade everything out
        timeline_stop = clutter.Timeline(10,30)
        alpha = clutter.Alpha(timeline_stop, clutter.ramp_inc_func)
        stop_behaviour = clutter.BehaviourOpacity(alpha, 255, 0)
        stop_behaviour.apply(self.cover_viewer)
        stop_behaviour.apply(self.backdrop)
        timeline_stop.connect('completed', self.destroyPlugin)
        timeline_stop.start()
    
    def destroyPlugin(self, data):
        self.stage.remove(self.cover_viewer)
        self.backdrop.hide()
        #self.stage.remove(self.overlay)
        
        
    def pause(self):
        pass
        
    def unpause(self):
        passnews/page2
        
class videoItem():
    def __init(self):
        self.mythID = None
        
    def importFromMythObject(self, mythObject):
        self.mythID = mythObject[0]
        self.title = mythObject[1]
        self.director = mythObject[2]
        self.plot = mythObject[3]
        self.rating = mythObject[4]
        self.inetRef = mythObject[5]
        self.year = mythObject[6]
        self.userRating = mythObject[7]
        self.length = mythObject[8]
        self.showLevel = mythObject[9]
        self.filename = mythObject[10]
        self.coverfile = mythObject[11]
        self.childID = mythObject[12]
        self.browse = mythObject[13]
        self.playCommand = mythObject[14]
        self.category = mythObject[15]
        
    def getTitle(self):
        return self.title
    def getCoverfile(self):
        return self.coverfile        
        
class coverViewer(clutter.Group):

    def __init__(self, stage):
        clutter.Group.__init__(self)
        self.stage = stage
        self.covers = []
        self.num_covers = 0
        self.cover_size = 200 #A cover will be cover_size * cover_size (X * Y)
        self.cover_gap = 10
        
        self.num_rows = 2
        self.num_columns = int(self.stage.get_width() / self.cover_size)
        
    def add_image(self, imagePath):
        tempTexture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(imagePath)
        tempTexture.set_pixbuf(pixbuf)
        xy_ratio = float(tempTexture.get_width()) / tempTexture.get_height()
        
        width = int(self.cover_size * xy_ratio)
        tempTexture.set_width(width)
        tempTexture.set_height(self.cover_size)
        
        tempTexture.set_position( (self.num_covers * self.cover_size), 0)

        x = (self.cover_gap + self.cover_size) * (self.num_covers/self.num_rows)
        y = (self.num_covers % self.num_rows) * self.cover_size + ( (self.num_covers % self.num_rows) * self.cover_gap)
        tempTexture.set_position(x, y)
        
        self.add(tempTexture)
        self.num_covers = self.num_covers +1
        

        
        #Redo positioning on all textures to add new one :(
        """for i in range(self.num_covers):
            tempTexture = self.get_nth_child(i)
            x = (self.cover_gap + self.cover_size) * i
            y = (i % self.num_rows) * self.cover_size 
            tempTexture.set_position(x, y)"""
        

        
        
        
    
