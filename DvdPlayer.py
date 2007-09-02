import clutter
from clutter import cluttergst
from VideoController import VideoController

class DvdPlayer:

    def __init__(self, Stage):
        self.stage = Stage
        self.paused = False
        self.isPlaying = False
        self.overlay = None
        
        
        
    def on_key_press_event (self, stage, event):
        if self.isPlaying:
            self.videoController.on_key_press_event(event)
            
        if event.keyval == clutter.keysyms.p:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()

        
    def begin(self, MenuMgr):
        uri = "dvd://1"
        self.videoController = VideoController(self.stage)
        self.video = self.videoController.play_video(uri)
        self.isPlaying = True
        
    def stop(self):
        if self.video.get_playing():
            self.videoController.stop_video()
            
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
        self.videoController.pause_video()
        
        
    def unpause(self):
        self.paused = False
        self.videoController.unpause_video()

