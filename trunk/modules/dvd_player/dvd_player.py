import clutter
import cluttergst
from multimedia.VideoController import VideoController

class Module:
    title = "DVD"

    def __init__(self, glossMgr, dbMgr):
        self.stage = glossMgr.get_stage()
        self.glossMgr = glossMgr
        self.setup_ui()
        
        self.paused = False
        self.isPlaying = False
        self.overlay = None
        
    def setup_ui(self):
        self.menu_image = self.glossMgr.themeMgr.get_texture("dvd_menu_image", None, None)
        
    #Action to take when menu item is selected
    def action(self):
        return self
        
    def on_key_press_event (self, stage, event):
        if self.isPlaying:
            self.videoController.on_key_press_event(event)
            
            if event.keyval == clutter.keysyms.Escape:
                self.videoController.stop_video()
            
        if event.keyval == clutter.keysyms.p:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()
        if event.keyval == clutter.keysyms.Escape:
            return True

        
    def begin(self, glossMgr):
        uri = "dvd://1"
        #glossMgr.background.hide()
        self.videoController = VideoController(glossMgr)
        self.video = self.videoController.play_video(uri, self)
        self.isPlaying = True
        
    def stop(self):
        if self.video.get_playing():
            #self.videoController.stop_video()
            
            timeline = clutter.Timeline(15, 25)
            timeline.connect('completed', self.end_video_event)
            alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
            behaviour = clutter.BehaviourOpacity(opacity_start=255, opacity_end=0, alpha=alpha)
            behaviour.apply(self.video)
        
            timeline.start()
            
    def end_video_event(self, data):
        self.stage.remove(self.video) 
        
    def stop_video(self):
        self.stop()
        
    def pause(self):
        self.paused = True
        self.videoController.pause_video()
        
        
    def unpause(self):
        self.paused = False
        self.videoController.unpause_video()

