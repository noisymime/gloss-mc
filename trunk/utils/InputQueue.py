import clutter
import gobject
import pygtk
import gtk

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
    
    accelerating = False
    use_acceleration = True
    current_acceleration_factor = 1
    acceleration_factor_base = 10 #Timelines will run at regular speed times this when accelerated
    acceleration_threshold = 3 #The queue size at which accleration kicks in (Make this higher to increase the delay before acceleration takes place)
    acceleration_time = 1000 #Time (in ms) it takes for the queue to accelerate/decelerate from nothing to full
    acceleration_steps = 5 #The number of steps in the acceleration process
    
    queue_max_size = 10
    release_timeout = 500 #The time (in ms) that the queue waits for key-events before timing out
    
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
        
        self.current_acceleration_step = 0
        #self.stage = clutter.stage_get_default()
        self.poll_time = None
        self.release_timeout_id = None
        self.timeline = None
        #gtk.settings_get_default().set_long_property("gtk-timeout-repeat", 5000, "gloss")
        
    def set_timeline(self, timeline):
        if not self.timeline is None: self.timeline.disconnect(self.flush_id)
        
        self.timeline = timeline
        self.base_fps = self.timeline.get_speed()
        if self.accelerating:
            fps = self.timeline.get_speed() * self.current_acceleration_factor
            if fps < 1: fps = self.base_fps
            self.timeline.set_speed(fps)
        self.flush_id = self.timeline.connect('completed', self.flush_queue)
        
    def input(self, event):
        self.actor = event.source
        if not self.timeline.is_playing():
            if (event.keyval == clutter.keysyms.Left) and (not self.action_west is None): self.action_west()
            if (event.keyval == clutter.keysyms.Right) and (not self.action_east is None): self.action_east()
            if (event.keyval == clutter.keysyms.Up) and (not self.action_north is None): self.action_north()
            if (event.keyval == clutter.keysyms.Down) and (not self.action_south is None): self.action_south()
            
            return True
        
        self.emit("entering-queue")
        
        #Poll for key release
        if self.accelerating:
            if not self.release_timeout_id is None:
                gobject.source_remove(self.release_timeout_id)
            self.release_timeout_id = gobject.timeout_add(self.release_timeout, self.decelerate)
        
        if event.keyval == clutter.keysyms.Left:
            self.queue_west += 1
            return True
        elif event.keyval == clutter.keysyms.Right:
            self.queue_east += 1
            return True
        elif event.keyval == clutter.keysyms.Down:
            self.queue_south += 1
            return True
        elif event.keyval == clutter.keysyms.Up:
            self.queue_north += 1
            return True
        
        #If we get to this point, we haven't handled the input, so return False
        return False
    
    def set_action(self, direction, function):
        if (direction == self.NORTH): self.action_north = function
        if (direction == self.EAST): self.action_east = function
        if (direction == self.SOUTH): self.action_south = function
        if (direction == self.WEST): self.action_west = function
        
    def flush_queue(self, data):
        if self.queue_north > self.queue_max_size: self.queue_north = self.queue_max_size
        if self.queue_east > self.queue_max_size: self.queue_east = self.queue_max_size
        if self.queue_south > self.queue_max_size: self.queue_south = self.queue_max_size
        if self.queue_west > self.queue_max_size: self.queue_west = self.queue_max_size
        
        #Consolodate north/south, east/west volumes
        if self.queue_north > self.queue_south: 
            self.queue_north = self.queue_north - self.queue_south
            self.queue_south = 0
        elif self.queue_south > self.queue_north:
            self.queue_south =  self.queue_south - self.queue_north
            self.queue_north = 0
        if self.queue_east > self.queue_west: 
            self.queue_east =  self.queue_east - self.queue_west
            self.queue_west = 0
        elif self.queue_west > self.queue_east:
            self.queue_west =  self.queue_west - self.queue_east        
            self.queue_east = 0
        
        if (self.queue_north > 0) or (self.queue_east > 0) or (self.queue_south > 0) or (self.queue_west > 0):
            self.timeline.connect('completed', self.flush_queue)
            
            absolute_queue_size = self.queue_north + self.queue_east + self.queue_south + self.queue_west
            if absolute_queue_size > self.acceleration_threshold:
                if not self.accelerating:
                    self.accelerating = True
                    self.accelerate()
            #print "Queue Size: N=%s E=%s S=%s W=%s" % (self.queue_north, self.queue_east, self.queue_south, self.queue_west)
            
            if self.queue_north > 0:
                self.queue_north -= 1
                self.action_north()
            if self.queue_east > 0:
                self.queue_east -= 1
                self.action_east()
            if self.queue_south > 0:
                self.queue_south -= 1
                self.action_south()
            if self.queue_west > 0:
                self.queue_west -= 1
                self.action_west()
    
            return
        else:
            self.queue_east = 0
            self.queue_south = 0
            self.queue_west = 0
            self.queue_north = 0
            
            if not self.accelerating: 
                self.emit("queue-flushed")
            self.accelerating = False

        
    def is_in_queue(self):
        if self.accelerating: return True
        
        if (self.queue_north > 0) or (self.queue_south > 0) or (self.queue_east > 0) or (self.queue_west > 0):
            return True
        else:
            return False
        
    def accelerate(self):
        if not self.accelerating:
            return False
        
        self.accelerating = True
        if self.current_acceleration_step < self.acceleration_steps:
            self.current_acceleration_step +=1
            #print "accelerating: %s" % str(self.current_acceleration_step)
            self.current_acceleration_factor = self.current_acceleration_step * (self.acceleration_factor_base / self.acceleration_steps)
            
            fps = self.base_fps * self.current_acceleration_factor
            if fps < 1: fps = self.base_fps
            self.timeline.set_speed(fps)
            if self.current_acceleration_step == 1: gobject.timeout_add( (self.acceleration_time / self.acceleration_steps), self.accelerate)
            return True
        
        #print "Acceleration finished"
        return False
        
    def decelerate(self, actor=None, event=None):
        #print "Key released: %s" % str(gtk.gdk.keyval_name(event.keyval))
        if self.current_acceleration_step > 0:
            self.current_acceleration_step -= 1
            #print "decelerating: %s" % str(self.current_acceleration_step)
            self.current_acceleration_factor = self.current_acceleration_step * (self.acceleration_factor_base / self.acceleration_steps)
            
            fps = self.base_fps * self.current_acceleration_factor
            if fps < 1: fps = self.base_fps
            self.timeline.set_speed(fps)
            if self.current_acceleration_step == (self.acceleration_steps-1): gobject.timeout_add( (self.acceleration_time / self.acceleration_steps), self.decelerate)
            return True

        self.accelerating = False
        self.emit("queue-flushed")
        #print "Deceleration finished"   
        return False