from clutter import cluttergst
from myth.MythMySQL import mythVideoDB
from myth.MythBackendConn import MythBackendConnection

class TVPlayer:

    def __init__(self, stage):
        self.video = cluttergst.VideoTexture()
        self.stage = stage
        #audio.set_filename('cast1.avi')
        #audio.show()
        
        #test = cluttercairo.Cairo()
        #audio = cluttergst.Audio()
        #audio.set_filename('test.mp3')
        
        #stage.add(audio)
        #audio.set_playing(True)
        
        #self.db_conn = mythVideoDB()
        
    def begin(self, menuMgr):
        self.myConn = MythBackendConnection(self)
        self.myConn.start()
        #self.begin_playback()

    
    def begin_playback(self, fd):
        #self.video.set_filename("test.mpg")
        print "File Descriptor: " + str(fd)
        self.video.set_uri("fd://"+str(fd))
        self.video.show()
        
        self.stage.add(self.video)
        self.video.set_playing(True)
    
    def on_key_press_event (self, stage, event):
        #print event.hardware_keycode
        pass
        """if event.keyval == clutter.keysyms.p:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()"""