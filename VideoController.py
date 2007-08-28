import sys, clutter, clutter.cluttergst, gst


class VideoController:

    def __init__(self):
        # Primary video texture & sink definition
        self.video_texture = clutter.cluttergst.VideoTexture()
        video_sink = clutter.cluttergst.VideoSink(self.video_texture)
        self.video_texture.set_position(0,0)
    
        # Gst pipeline def
        self.pipeline = gst.Pipeline()
        src = gst.element_factory_make ("videotestsrc")
        colorspace = gst.element_factory_make ("ffmpegcolorspace")
        bus = self.pipeline.get_bus()
        gst.Bus.add_signal_watch (bus)
        gst.Bin.add (self.pipeline, src, colorspace, video_sink)
        gst.element_link_many (src, colorspace, video_sink)
    
    
    def begin(self, stage):
        stage.add(self.video_texture)
        self.video_texture.show()
        self.pipeline.set_state(gst.STATE_PLAYING)
 
