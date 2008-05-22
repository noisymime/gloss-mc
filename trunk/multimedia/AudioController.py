import sys, clutter, clutter.cluttergst, gst, pygst, gtk, pygtk, gobject
import threading
import os
from multimedia.MediaController import MediaController

class AudioController(MediaController):
    
    def __init__(self, glossMgr):
        MediaController.__init__(self, glossMgr)
        self.isPlaying = False
        
        # Primary audio object
        self.audio = clutter.cluttergst.Audio()
        self.audio.connect("eos", self.stream_complete)
        self.media_element = self.audio    
        
        #self.osd = osd(glossMgr)

        
    def on_key_press_event(self, event):
        if event.keyval == clutter.keysyms.Left:
            self.skip(-20)
        if event.keyval == clutter.keysyms.Right:
            self.skip(20)
            
        #self.osd.enter()
    
    def play_audio(self, uri):
        if self.isPlaying:
            self.audio.set_playing(False)
        
        """
        # Primary audio object
        self.audio = clutter.cluttergst.Audio()
        self.audio.connect("eos", self.stream_complete)
        self.media_element = self.audio 
        """
        
        self.audio.set_uri(uri)
        self.audio.set_playing(True)

        self.isPlaying = True
        #self.stage.add(self.audio)
        
        self.emit("playing")
        return self.audio

    def stream_complete(self, audio):
        
        self.isPlaying = False
        self.audio.set_playing(False)
        self.emit("completed")
        #self.stop_audio

    def stop_audio(self):
        if self.audio.get_playing():
            self.isPlaying = False
            self.audio.set_playing(False)
        self.emit("stopped")
    
        
    def pause_audio(self, use_backdrop):
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
        
    def unpause_audio(self):
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
        
    def skip(self, amount):
        if not self.video_texture.get_can_seek():
            return
        
        #current_pos = self.video_texture.get_position()
        current_pos = self.video_texture.get_property("position")
        new_pos = int(int(current_pos) + int(amount))
        
        if new_pos >= self.video_texture.get_duration():
            new_pos = self.video_texture.get_duration()-1
        if new_pos <= 0:
            new_pos = 1
        
        # There's apparently a collision in the python bindings with the following method. Change this when its fixed in the bindings
        #self.video_texture.set_position(new_pos)
        #Until then use:
        self.video_texture.set_property("position", int(new_pos))
        self.osd.shift_video(self.video_texture, amount)
        