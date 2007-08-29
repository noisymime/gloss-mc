import pygtk
import gtk
import pygst
import gst
import gobject
import clutter
from clutter import cluttergst

class VideoPlayer():

    def __init__(self, stage, dbMgr):
        self.stage = stage
        self.cover_viewer = coverViewer(self.stage)
        
        self.is_playing = False
        
        #This block can be moved to begin() but causes a performance hit when loading the module *shrug*
        results = dbMgr.get_videos()
        
        if results == None:
            print "VideoPlayer: No connection to DB or no videos found in DB"
            return None
        
        for record in results:
            tempVideo = videoItem()
            tempVideo.importFromMythObject(record)
            self.cover_viewer.add_video(tempVideo)
            #self.cover_viewer.add_image(tempVideo.getCoverfile())
        #dbMgr.close_db()
        ################################################################################
        
    def on_key_press_event (self, stage, event):
        if event.keyval == clutter.keysyms.p:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()
            
        up = clutter.keysyms.Up
        down = clutter.keysyms.Down
        left = clutter.keysyms.Left
        right= clutter.keysyms.Right
        if (event.keyval == up) or (event.keyval == down) or (event.keyval == left) or (event.keyval == right):
            self.cover_viewer.on_cursor_press_event(event)
        
            
        
        
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
        
        """
        video = customBin()

        video.get_texture().show()
        video.get_texture().set_opacity(255)
        self.stage.add(video.get_texture())
        video.startPlayback()
        
        self.video_texture = clutter.Texture() #cluttergst.VideoTexture()
        self.pipeline = gst.Pipeline("mypipeline")
        self.filesrc = gst.element_factory_make("filesrc", "file")
        self.filesrc.set_property("location", "/home/josh/clutter/toys/gloss/cast1.avi")
        #self.pbin.set_property("uri", "file://cast1.avi")
        self.pbin = gst.element_factory_make("decodebin", "pbin")

        #self.pbin = gst.element_factory_make("videotestsrc", "video")
        self.sink = gst.element_factory_make("xvimagesink", "sink")
        #self.sink = cluttergst.video_sink_new(self.video_texture)
        #self.sink = cluttergst.VideoSink(self.video_texture)


        # add elements to the pipeline
        self.pipeline.add(self.pbin)
        self.pipeline.add(self.sink)
        self.pipeline.add(self.filesrc)
        self.pbin.link(self.sink)
        self.pbin.link(self.filesrc)
        self.pipeline.set_state(gst.STATE_PLAYING)
        
        self.stage.add(self.video_texture)
        #self.stage.add(self.sink)
        """
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
        pass
        
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
    scaleFactor = 1.4

    def __init__(self, stage):
        clutter.Group.__init__(self)
        self.stage = stage
        self.videoLibrary = []
        self.num_covers = 0
        self.cover_size = 200 #A cover will be cover_size * cover_size (X * Y)
        self.cover_gap = 1
        
        self.num_rows = 3
        self.num_columns = 4 #int(self.stage.get_width() / self.cover_size)
        
        self.currentSelection = 0
        
    def add_video(self, video):
        self.videoLibrary.append(video)
        imagePath = video.getCoverfile()
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
        
    def select_item(self, incomingItem, outgoingItem):
        outgoingTexture = self.get_nth_child(outgoingItem)
        incomingTexture = self.get_nth_child(incomingItem)
        
        #Make sure the new texture is on the top
        #incomingTexture.raise_top()
        
        self.timeline = clutter.Timeline(20,80)
        alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        behaviourNew = clutter.BehaviourScale(alpha, 1, self.scaleFactor, clutter.GRAVITY_CENTER)
        behaviourOld = clutter.BehaviourScale(alpha, self.scaleFactor, 1, clutter.GRAVITY_CENTER)
        
        behaviourNew.apply(incomingTexture)
        behaviourOld.apply(outgoingTexture)
        
        self.currentSelection = incomingItem
        
        self.timeline.start()
        
    def on_cursor_press_event(self, event):
        newItem = None
        if event.keyval == clutter.keysyms.Left:
            newItem = self.currentSelection - self.num_rows
        if event.keyval == clutter.keysyms.Right:
            newItem = self.currentSelection + self.num_rows
        if event.keyval == clutter.keysyms.Down:
            #Check if we're already on the bottom row
            if not ((self.currentSelection % self.num_rows) == (self.num_rows-1)):
                newItem = self.currentSelection + 1
        if event.keyval == clutter.keysyms.Up:
            #Check if we're already on the top row
            if not (self.currentSelection % self.num_rows) == 0:
                newItem = self.currentSelection - 1
        
        if (newItem < 0) and (not newItem == None):
            newItem = self.currentSelection

        #If there is movement, make the scale happen
        if not newItem == None:
            self.select_item(newItem, self.currentSelection)
            
        

