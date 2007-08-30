import sys, clutter, clutter.cluttergst, gst, pygst, gtk, pygtk
import threading


class VideoController:

    def __init__(self):
        # Primary video texture & sink definition
        self.video_texture = clutter.cluttergst.VideoTexture()
        self.video_sink = clutter.cluttergst.VideoSink(self.video_texture)
        self.video_texture.set_position(0,0)
        
        self.pipeline = gst.Pipeline()
        #self.tester()
        """
        src = gst.element_factory_make ("videotestsrc")
        
        gst.Bin.add (self.pipeline, filesrc, colorspace, deinterlace, video_sink)
        gst.element_link_many (filesrc, colorspace, deinterlace, video_sink)
        """
    
    
    def begin(self, stage):
        self.osd = osd(stage)
        self.osd.enter()
        
        return None
        stage.add(self.video_texture)
        self.video_texture.show()
        self.pipeline.set_state(gst.STATE_PLAYING)
        
    def tester(self):
        self.src = gst.element_factory_make("filesrc", "src");
        self.src.set_property("location", "/home/josh/clutter/toys/gloss/test.mpg")
        self.demux = gst.element_factory_make("ffdemux_mpegts", "demux")
        self.queue1 = gst.element_factory_make("queue", "queue1")
        self.queue2 = gst.element_factory_make("queue", "queue2")
        #self.deinterlace = gst.element_factory_make("ffdeinterlace", "deinterlace")
        self.vdecode = gst.element_factory_make("mpeg2dec", "vdecode")
        self.adecode = gst.element_factory_make("mad", "adecode")
        #self.vsink = gst.element_factory_make("xvimagesink", "vsink")
        self.vsink = self.video_sink #cluttergst.VideoSink(self.video_texture)
        self.asink = gst.element_factory_make("alsasink", "asink")

        
        # add elements to the pipeline
        self.pipeline.add(self.src)
        self.pipeline.add(self.demux)
        self.pipeline.add(self.queue1)
        self.pipeline.add(self.queue2)
        self.pipeline.add(self.vdecode)
        #self.pipeline.add(self.deinterlace)
        self.pipeline.add(self.adecode)
        self.pipeline.add(self.vsink)
        self.pipeline.add(self.asink)

        bus = self.pipeline.get_bus()
        gst.Bus.add_signal_watch (bus) 
       
        # we can't link demux until the audio and video pads are added
        # we need to listen for "pad-added" signals
        self.demux.connect("pad-added", self.on_pad_added)
        
        # link all elements apart from demux
        gst.element_link_many(self.src, self.demux)
        gst.element_link_many(self.queue1, self.vdecode, self.vsink) #self.deinterlace, self.vsink)
        gst.element_link_many(self.queue2, self.adecode, self.asink)

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

class osd:

    def __init__(self, stage):
        self.stage = stage
        
        self.bar_group = clutter.Group()
    
        self.background = clutter.Texture()
        self.background.set_pixbuf( gtk.gdk.pixbuf_new_from_file("ui/osd_bar3.png") )
        self.background.set_opacity(255)
        self.background.set_width(stage.get_width())
        self.bar_group.add(self.background)
        self.bar_group.show_all()
        
    def enter(self):
        self.stage.add(self.bar_group)
        self.bar_group.show()
        
        self.bar_group.set_position(0, self.stage.get_height())
        bar_position_y = int(self.stage.get_height() - self.background.get_height())
        
        knots = (\
                (self.bar_group.get_x(), self.bar_group.get_y()),\
                (self.bar_group.get_x(), bar_position_y) \
                )
                
        self.timeline = clutter.Timeline(25, 50)
        self.alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.enter_behaviour_path = clutter.BehaviourPath(self.alpha, knots)
        
        self.enter_behaviour_path.apply(self.bar_group)
        
        self.timeline.start()
        
        self.timer = threading.Timer(3.0, self.exit)
        self.timer.start()
        
    def exit(self):
        
        knots = (\
                (self.bar_group.get_x(), self.bar_group.get_y()),\
                (self.bar_group.get_x(), int(self.stage.get_height())) \
                )
                
        self.timeline = clutter.Timeline(25, 50)
        self.timeline.connect('completed', self.exit_end_event)
        self.alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.exit_behaviour_path = clutter.BehaviourPath(self.alpha, knots)
        
        self.exit_behaviour_path.apply(self.bar_group)
        self.timeline.start()
    def exit_end_event(self, data):
        self.stage.remove(self.bar_group)
        
    def on_key_press_event(self, event):
        self.enter()
        
    def set_fullscreen(self, texture, width, height):
        texture.set_property("sync-size", False)
        texture.set_position(0, 0)
        xy_ratio = float(width / height)
        #print "XY Ratio: " + str(xy_ratio)
        
        width = int(self.stage.get_width())
        height = int (width / xy_ratio)
        height = 768
        
        texture.set_size(width, height)
        
        