import sys, clutter, clutter.cluttergst, gst, pygst, gtk, pygtk, gobject
import threading
import os
from multimedia.MediaController import MediaController

class VideoController(MediaController):
    
    def __init__(self, glossMgr):
        MediaController.__init__(self, glossMgr)
        self.overlay = None
        self.blackdrop = None
        
        # Primary video texture & sink definition
        self.video_texture = clutter.cluttergst.VideoTexture()
        self.media_element = self.video_texture
        self.video_sink = clutter.cluttergst.VideoSink(self.video_texture)
        self.video_texture.connect('size-change', self.set_fullscreen)
        self.video_texture.set_position(0,0)
        
    def on_key_press_event(self, event):
        if event.keyval == clutter.keysyms.Left:
            self.skip(-20)
        if event.keyval == clutter.keysyms.Right:
            self.skip(20)
            
        #self.osd.enter()
    
    def play_video(self, uri, player):
        #self.customBin(uri)
        #return
    
        self.player = player
        self.video_texture.set_uri(uri)
        

        #We need to connect to the message queue on the playbin to watch for any message (ie codec or file not found errors)
        self.bin = self.video_texture.get_playbin()
        #print "Queue: " + str(self.bin.get_property("queue_size"))
        #print "Queue: " + str(self.bin.get_property("queue_threshold"))
        #print "Queue: " + str(self.bin.get_property("queue_min_threshold"))
        bus = self.video_texture.get_playbin().get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_bus_message)
        
        #Now we can start the video
        self.video_texture.set_playing(True)
        #self.bin.set_state(gst.STATE_PAUSED)
        self.bin.set_state(gst.STATE_PLAYING)
        self.isPlaying = True
        
        #decodebin = self.bin.get_by_name("decodebin0")
        #for element in decodebin.elements():
        #    print "GST Element 1: " + str(element.get_name()) 
        #queue = decodebin.get_by_name("queue0")
        #print queue.get_name()
        #ypefind = decodebin.get_by_name("typefind")
        
        #decodebin.connect("pad-added", self.on_pad_added)
        #vid = demuxer.get_by_name("video_00")
        #self.queue1 = gst.element_factory_make("queue", "queue1")
        #self.queue1.set_property("max-size-time", 50000)
        #self.queue1.set_property("max-size-buffers", 0)
        
        #self.queue2 = gst.element_factory_make("queue", "queue2")
        #self.bin.add(self.queue1)
        #self.bin.add(self.queue2)
        #decodebin.link(self.queue1)  
        #self.queue1.link(decodebin)
        self.video_texture.set_opacity(255)
        self.video_texture.set_position(0, 0)
        self.video_texture.show()
        #if self.video_texture.get_parent() is None:
        self.stage.add(self.video_texture)
        
        self.emit("playing")
        return self.video_texture

    #This handles any messages that are sent accross the playbin
    #Currently this is checking two types of msgs:
    #    1) A "codec not found" warning, at which stage playback is stopped
    #    2) A Buffering msg. This pauses the video until the buffer is at 100%
    def on_bus_message(self, bus, message):
        t = message.type
        #print "message type: " + str(t)
        if t == gst.MESSAGE_ELEMENT:
            #This occurs when an invalid codec is attempted to be played
            #Need to insert some form of message to the user here
            if self.player.glossMgr.debug: print "GStreamer Bus msg: " + message.structure.to_string()
            struc = message.structure
            if struc is None:
                return
            
            if struc.get_name() == "missing-plugin":
                print "GStreamer Error (missing-plugin): " + message.structure.to_string()
                self.isPlaying = False
                self.video_texture.set_playing(False)
                self.player.stop_video()
        elif t == gst.MESSAGE_BUFFERING:
            percent = message.parse_buffering()
            print "Buffer: " + str(percent)
            if percent < 100:
                self.bin.set_state(gst.STATE_PAUSED)
            else:
                if not self.bin.get_state() == gst.STATE_PLAYING:
                    self.bin.set_state(gst.STATE_PLAYING)
        elif t == gst.MESSAGE_STATE_CHANGED:
            prev, current, next = message.parse_state_changed()
            #print "State Changed. Previous state: " + str(prev)
            #print "State Changed. Current state: " + str(current)
        elif t == gst.STREAM_ERROR:
            #print "OHH NOES!"
            print "GST Stream Error: " + message.structure.to_string()
        else:
            if not self.player is None:
                if self.player.glossMgr.debug: print "GST Message: " + str(message)
    
    def stop_video(self):
        if self.video_texture.get_playing():
            self.isPlaying = False
            self.player.stop_video()
            self.player = None
            self.video_texture.set_playing(False)
            
            timeline = clutter.Timeline(15, 25)
            timeline.connect('completed', self.end_video_event)
            alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
            self.behaviour = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=alpha)
            self.behaviour.apply(self.video_texture)
            if not (self.blackdrop is None):
                self.behaviour.apply(self.blackdrop)
        
            timeline.start()
            
    def end_video_event(self, data):
        self.stage.remove(self.video_texture)
        if not (self.blackdrop is None):
            self.stage.remove(self.blackdrop)
        self.blackdrop = None 
        
    def customBin(self, fd):
        self.pipeline = gst.Pipeline("testPipeline")
        #self.src = gst.element_factory_make("filesrc", "src")
        #self.src.set_property("location", "test.mpg")
        self.src = gst.element_factory_make("fdsrc", "src");
        self.src.set_property("fd", int(fd))
        self.demux = gst.element_factory_make("ffdemux_mpegts", "demux")
        #self.demux = gst.element_factory_make("decodebin", "demux")
        self.queue1 = gst.element_factory_make("queue", "queue1")
        self.queue1.set_property("max-size-time", 500000)
        self.queue1.set_property("max-size-buffers", 0)
        self.queue2 = gst.element_factory_make("queue", "queue2")
        #self.deinterlace = gst.element_factory_make("ffdeinterlace", "deinterlace")
        self.vdecode = gst.element_factory_make("mpeg2dec", "vdecode")
        self.adecode = gst.element_factory_make("mad", "adecode")
        self.vsink = gst.element_factory_make("xvimagesink", "vsink")
        #self.vsink = self.video_sink #cluttergst.VideoSink(self.video_texture)
        self.asink = gst.element_factory_make("alsasink", "asink")

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_bus_message)
        
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
        print "linking..."
        gst.element_link_many(self.src, self.demux)
        gst.element_link_many(self.queue1, self.vdecode, self.vsink) #self.deinterlace, self.vsink)
        gst.element_link_many(self.queue2, self.adecode, self.asink)

        self.pipeline.set_state(gst.STATE_PLAYING)

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
        
    def set_fullscreen(self, texture, width, height):
        texture.set_property("sync-size", False)
        texture.set_position(0, 0)
        ratio = float(self.stage.get_width()) / float(width)
        xy_ratio = float(width) / float(height)
        #print "Width: " + str(width)
        #print "Height: " + str(height)
        #print "XY Ratio: " + str(ratio)
        
        width = int(self.stage.get_width())
        height = int ((height * ratio))
        #print "New Width: " + str(width)
        #print "New Height: " + str(height)
        
        if height < self.stage.get_height():
            #Create a black backdrop that the video can sit on
            self.blackdrop = clutter.Rectangle()
            self.blackdrop.set_color(clutter.color_parse('Black'))
            self.blackdrop.set_size(self.stage.get_width(), self.stage.get_height())
            self.stage.remove(self.video_texture)
            self.stage.add(self.blackdrop)
            self.stage.add(self.video_texture)
            self.blackdrop.show()
            
            #And move the video into the vertical center
            pos_y = int((self.stage.get_height() - height) / 2)
            self.video_texture.set_position(0, pos_y)
        
        texture.set_size(width, height)
        
    def pause_video(self, use_backdrop):
        if use_backdrop:
            #Use the overlay to go over show
            if self.overlay == None:
                self.overlay = clutter.Rectangle()
                self.overlay.set_color(clutter.color_parse('Black'))
                self.overlay.set_size(self.stage.get_width(), self.stage.get_height())
                self.stage.add(self.overlay)
            self.overlay.set_opacity(0)
            self.overlay.show()
    
    
            #self.video_texture.lower_actor(self.overlay)
            #self.overlay.raise_actor(self.video_texture)
            #Fade the overlay in
            timeline_overlay = clutter.Timeline(10,30)
            alpha = clutter.Alpha(timeline_overlay, clutter.ramp_inc_func)
            self.overlay_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=200, alpha=alpha)
            self.overlay_behaviour.apply(self.overlay)
            #video_behaviour.apply(self.video_texture)
            timeline_overlay.start()
        
        #Pause the video
        self.video_texture.set_playing(False)
        
    def unpause_video(self):
        if not self.overlay is None:
            #Fade the backdrop in
            timeline_unpause = clutter.Timeline(10,30)
            alpha = clutter.Alpha(timeline_unpause, clutter.ramp_inc_func)
            self.overlay_behaviour = clutter.BehaviourOpacity(opacity_start=200, opacity_end=0, alpha=alpha)
            self.overlay_behaviour.apply(self.overlay)
            #video_behaviour.apply(self.video_texture)
            timeline_unpause.start()
            
        #Resume the video
        self.video_texture.set_playing(True)
        
   

        
        
