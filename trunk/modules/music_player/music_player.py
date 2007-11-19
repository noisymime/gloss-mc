import pygtk
import gtk
import clutter
import eyeD3

class Module():
    title = "Music"
    menu_image = "dvd.png"

    def __init__(self, MenuMgr, dbMgr):
        self.stage = MenuMgr.get_stage()
        self.cover_viewer = coverViewer(self.stage) 
        
        self.is_playing = False
        
    #Action to take when menu item is selected
    def action(self):
        return self
        
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
        timeline_backdrop = clutter.Timeline(10,40)
        alpha = clutter.Alpha(timeline_backdrop, clutter.ramp_inc_func)
        backdrop_behaviour = clutter.BehaviourOpacity(alpha, 0, 255)
        backdrop_behaviour.apply(self.backdrop)
        timeline_backdrop.start()
        
    def stop(self):
        pass
        
    def pause(self):
        pass
        
    def unpause(self):
        pass
        
        
class coverViewer(clutter.Group):

    def __init__(self, stage):
        clutter.Group.__init__(self)
        self.stage = stage
        self.covers = []
        self.num_covers = 0
        self.cover_size = 50 #A cover will be cover_size * cover_size (X * Y)
        self.cover_gap = 10
        
        self.num_rows = 2
        self.num_columns = int(self.stage.get_width() / self.cover_size)
        
    def add_image(self, imagePath):
        tempTexture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(imagePath)
        tempTexture.set_pixbuf(pixbuf)
        xy_ratio = tempTexture.get_width() / tempTexture.get_height()
        
        height = int(self.cover_size * xy_ratio)
        tempTexture.set_width(self.cover_size)
        tempTexture.set_height(height)
        
        self.add(tempTexture)
        self.num_covers = self.num_covers +1
        
        #Redo positioning on all textures to add new one :(
        """for i = 0 to self.num_covers:
            tempTexture = self.get_nth_child(i)
            x = (self.cover_gap + self.cover_size) * i
            y = (i % self.num_rows) * self.cover_size 
            tempTexture.set_position(x, y)"""
        

        
        
        
    