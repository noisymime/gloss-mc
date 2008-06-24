import clutter
import gobject
from multimedia.MediaOSD import osd


# This is an abstract class
# It should not be instantiated directly
class MediaController(gobject.GObject):
    
    #Setup signals
    __gsignals__ =  { 
        "playing": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "completed": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "stopped": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
        }
    
    def __init__(self, glossMgr):
        gobject.GObject.__init__(self)
        self.stage = glossMgr.stage
        self.glossMgr = glossMgr
        #self.media_element = clutter.Media()
        
        self.use_osd = True
        self.osd = osd(glossMgr)
        
        
    #Skips the media forward the specified amount
    def skip(self, amount):
        if not self.media_element.get_can_seek():
            return
        
        #current_pos = self.video_texture.get_position()
        current_pos = self.media_element.get_property("position")
        new_pos = int(int(current_pos) + int(amount))
        
        if new_pos >= self.media_element.get_duration():
            new_pos = self.media_element.get_duration()-1
        if new_pos <= 0:
            new_pos = 1
        
        # There's apparently a collision in the python bindings with the following method. Change this when its fixed in the bindings
        #self.media_element.set_position(new_pos)
        #Until then use:
        self.media_element.set_property("position", int(new_pos))
        if self.use_osd: self.osd.shift_media(amount)
        
    def get_position_percent(self):
        length = int(self.media_element.get_duration())
        pos = int(self.media_element.get_property("position"))
        
        #Sanity check
        if length == 0: return 0
        
        percent = float( float(pos) / float(length) )
        
        return percent