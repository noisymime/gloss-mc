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
        self.videoLibrary = []
        
        self.is_playing = False
        
        #This block can be moved to begin() but causes a performance hit when loading the module *shrug*
        results = dbMgr.get_videos()
        
        if results == None:
            print "VideoPlayer: No connection to DB or no videos found in DB"
            return None
        
        for record in results:
            tempVideo = videoItem()
            tempVideo.importFromMythObject(record)
            self.videoLibrary.append(tempVideo)
            self.cover_viewer.add_image(tempVideo.getCoverfile())
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
        
class customBin:

    def __init__(self):
        self.gstInit()
    
    def gstInit(self):
        self.texture = gobject.new(cluttergst.VideoTexture, tiled=False) # , "sync-size=False"

        #self.texture = clutter.Texture() #cluttergst.VideoTexture()
        self.texture.set_property("sync-size", False)
        
        # declare our pipeline and GST elements
        self.pipeline = gst.Pipeline("mypipeline")
        """
        
        self.src = gst.element_factory_make("filesrc", "src");
        self.src.set_property("location", "test.mpg")
        self.demux = gst.element_factory_make("ffdemux_mpegts", "demux")
        self.queue1 = gst.element_factory_make("queue", "queue1")
        self.queue2 = gst.element_factory_make("queue", "queue2")
        self.deinterlace = gst.element_factory_make("ffdeinterlace", "deinterlace")
        self.vdecode = gst.element_factory_make("mpeg2dec", "vdecode")
        self.adecode = gst.element_factory_make("mad", "adecode")
        #self.vsink = gst.element_factory_make("xvimagesink", "vsink")
        self.vsink = cluttergst.VideoSink(self.video_texture)
        self.asink = gst.element_factory_make("alsasink", "asink")
        """
        self.src = gst.element_factory_make("videotestsrc", "src")
        #self.warp = gst.element_factory_make ("warptv", "warp")
        self.colorspace = gst.element_factory_make ("ffmpegcolorspace", "color")
        self.pipeline.add(self.colorspace)
        #self.demux = gst.element_factory_make("ffdemux_mpegts", "demux")
        self.sink = cluttergst.VideoSink (self.texture)
        #self.sink = gst.element_factory_make("autovideosink", "vsink")
        self.sink.set_property("qos", True)
        self.sink.set_property("sync", True)
    
        # add elements to the pipeline
        self.pipeline.add(self.src)
        #self.pipeline.add(self.warp)
        #self.pipeline.add(self.demux)
        #self.pipeline.add(self.colorspace)
        self.pipeline.add(self.sink)
        
        """
        self.pipeline.add(self.demux)
        self.pipeline.add(self.queue1)
        self.pipeline.add(self.queue2)
        self.pipeline.add(self.vdecode)
        self.pipeline.add(self.deinterlace)
        self.pipeline.add(self.adecode)
        self.pipeline.add(self.vsink)
        self.pipeline.add(self.asink)
        
        
        # we can"t link demux until the audio and video pads are added
        # we need to listen for "pad-added" signals
        self.demux.connect("pad-added", self.on_pad_added)
        """
        self.texture.set_width(200)
        self.texture.set_height(200)
        #self.pipeline.add_signal_watch()
        #self.pipeline.add_many(self.pipeline, self.src, self.warp, self.colorspace, self.sink)
        gst.element_link_many(self.src, self.sink) #self.warp, self.colorspace, 
        # link all elements apart from demux
        #gst.element_link_many(self.src, self.demux)
        #gst.element_link_many(self.queue1, self.vsink) #self.vdecode, self.deinterlace, 
        #gst.element_link_many(self.queue2, self.adecode, self.asink)
        
        #self.pipeline.set_state(gst.STATE_PLAYING)
        
    def on_pad_added(self, element, src_pad):
        caps = src_pad.get_caps()
        name = caps[0].get_name()
        # link demux to vdecode when video/mpeg pad added to demux
        if name == "video/mpeg":
            sink_pad = self.queue1.get_pad("sink")
        elif name == "audio/mpeg":
            sink_pad = self.queue2.get_pad("sink")
        else:
            return
        
        if not sink_pad.is_linked():
            src_pad.link(sink_pad)
        
    def startPlayback(self):
        # start playback
        self.pipeline.set_state(gst.STATE_PLAYING)
        
    def get_texture(self):
        return self.texture
        
