import gobject

# An abstract class that simply serves to help emit a common signal
class MusicObject(gobject.GObject):
    PENDING_DOWNLOAD = range(1)
    
    #Setup signals
    __gsignals__ =  { 
        "image-found": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
        }
    
    def __init__(self):
        gobject.GObject.__init__(self)