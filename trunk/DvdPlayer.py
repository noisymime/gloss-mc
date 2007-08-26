import clutter
from clutter import cluttergst

class DvdPlayer:

    def __init__(self, Stage):
        self.stage = Stage
        self.video = cluttergst.VideoTexture()
        self.paused = False
        self.overlay = None
        
        self.video.set_uri("dvd://1")
        
    def on_key_press_event (self, stage, event):
        if event.keyval == clutter.keysyms.p:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()

        
    def begin(self, MenuMgr):
        self.stage.add(self.video)
        
        self.video.set_playing(True)
        
        #Resize for fullscreen
        #while self.video.get_buffer_percent() < 5:
        print self.video.get_position()

        #xy_ratio = self.video.get_width() / self.video.get_height()
        self.video.set_width( int(self.stage.get_width()) )
        #self.video.set_height(self.video.get_width() * xy_ratio)
        
        self.video.show()
        
        
    def stop(self):
        if self.video.get_playing():
            self.video.set_playing(False)
            #self.myConn.stop()
            
            timeline = clutter.Timeline(15, 25)
            timeline.connect('completed', self.end_video_event)
            alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
            behaviour = clutter.BehaviourOpacity(alpha, 255,0)
            behaviour.apply(self.video)
        
            timeline.start()
    def end_video_event(self, data):
        self.stage.remove(self.video) 
        
    def pause(self):
        self.paused = True
        
    
        #Use the overlay to go over show
        if self.overlay == None:
            self.overlay = clutter.Rectangle()
            self.overlay.set_color(clutter.color_parse('Black'))
            self.overlay.set_width(self.stage.get_width())
            self.overlay.set_height(self.stage.get_height())
        self.overlay.set_opacity(0)
        self.overlay.show()

        self.stage.add(self.overlay)
        #Fade the overlay in
        timeline_overlay = clutter.Timeline(10,30)
        alpha = clutter.Alpha(timeline_overlay, clutter.ramp_inc_func)
        overlay_behaviour = clutter.BehaviourOpacity(alpha, 0, 100)
        overlay_behaviour2 = clutter.BehaviourOpacity(alpha, 255, 100) #Used on the backdrop
        overlay_behaviour.apply(self.overlay)
        overlay_behaviour2.apply(self.video)
        timeline_overlay.start()
        
        #Pause the main slideshow
        self.video.set_playing(False)
        
    def unpause(self):
        self.paused = False
        
        #Fade the backdrop in
        timeline_overlay = clutter.Timeline(10,30)
        alpha = clutter.Alpha(timeline_overlay, clutter.ramp_inc_func)
        overlay_behaviour = clutter.BehaviourOpacity(alpha, 100, 0)
        overlay_behaviour2 = clutter.BehaviourOpacity(alpha, 100, 255) #Used on the backdrop
        overlay_behaviour.apply(self.overlay)
        overlay_behaviour2.apply(self.video)
        timeline_overlay.start()
        
        #Resume the video
        self.video.set_playing(True)
