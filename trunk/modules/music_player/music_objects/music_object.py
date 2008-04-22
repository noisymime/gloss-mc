import gobject
import threading

# An abstract class that simply serves to help emit a common signal
class MusicObject(gobject.GObject):
    PENDING_DOWNLOAD = range(1)
    MAX_THREADS = 3
    
    queued_threads = []
    running_threads = []
    
    #Setup signals
    __gsignals__ =  { 
        "image-found": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
        }
    
    def __init__(self):
        gobject.GObject.__init__(self)
        #self.queued_threads = []
        #self.running_threads = []
        
    def queue_thread(self, target):
        thread = threading.Thread(target=target)
        
        if len(self.running_threads) > self.MAX_THREADS:
            self.queued_threads.append(thread)
        else:
            self.running_threads.append(thread)
            thread.start()
            
        return thread
            
    def thread_finished(self):
        self.running_threads.pop(0)
        
        if len(self.queued_threads) > 0:
            thread = self.queued_threads.pop(0)
            self.running_threads.append(thread)
            thread.start()