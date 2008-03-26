import clutter
import gobject

#########################################################
# The input queue controls fast user input by queing up
# signals and processing them one by one once any timelines
# are complete
#########################################################

class InputQueue(gobject.GObject):
    NORTH, EAST, SOUTH, WEST = range(4)
    
    #Setup signals
    __gsignals__ =  { 
        "queue-flushed": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "entering-queue": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
        }
    
    def __init__(self):
        gobject.GObject.__init__(self)
        
        self.queue_north = 0
        self.queue_east = 0
        self.queue_south = 0
        self.queue_west = 0
        
        self.action_north = None
        self.action_east = None
        self.action_south = None
        self.action_west = None
        
    def set_timeline(self, timeline):
        self.timeline = timeline
        self.timeline.connect('completed', self.flush_queue)
        
    def input(self, event):
        if not self.timeline.is_playing():
            if (event.keyval == clutter.keysyms.Left) and (not self.action_west is None): self.action_west()
            if (event.keyval == clutter.keysyms.Right) and (not self.action_east is None): self.action_east()
            if (event.keyval == clutter.keysyms.Up) and (not self.action_north is None): self.action_north()
            if (event.keyval == clutter.keysyms.Down) and (not self.action_south is None): self.action_south()
            
            return True
        
        self.emit("entering-queue")
        
        if event.keyval == clutter.keysyms.Left:
            self.queue_west = self.queue_west + 1
            return True
        elif event.keyval == clutter.keysyms.Right:
            self.queue_east = self.queue_east + 1
            return True
        elif event.keyval == clutter.keysyms.Down:
            self.queue_south = self.queue_south + 1
            return True
        elif event.keyval == clutter.keysyms.Up:
            self.queue_north = self.queue_north + 1
            return True
        
        #If we get to this point, we haven't handled the input, so return False
        return False
    
    def set_action(self, direction, function):
        if (direction == self.NORTH): self.action_north = function
        if (direction == self.EAST): self.action_east = function
        if (direction == self.SOUTH): self.action_south = function
        if (direction == self.WEST): self.action_west = function
        
    def flush_queue(self, data):
        #Consolodate north/south, east/west volumes
        self.queue_north =  self.queue_north - self.queue_south
        self.queue_south =  self.queue_south - self.queue_north
        self.queue_east =  self.queue_east - self.queue_west
        self.queue_west =  self.queue_west - self.queue_east        
        
        if self.queue_north > 0:
            self.action_north()    
        if self.queue_east > 0:
            self.action_east()
        if self.queue_south > 0:
            self.action_south()
        if self.queue_west > 0:
            self.action_west()

        self.queue_east = 0
        self.queue_south = 0
        self.queue_west = 0
        self.queue_north = 0
        
        self.emit("queue-flushed")
        
    def is_in_queue(self):
        if (self.queue_north > 0) or (self.queue_south > 0) or (self.queue_east > 0) or (self.queue_west > 0):
            return True
        else:
            return False