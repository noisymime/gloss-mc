#########################################################
# The input queue controls fast user input by queing up
# signals and processing them one by one once any timelines
# are complete
#########################################################

class InputQueue:
    NORTH, EAST, SOUTH, WEST = range(4)
    
    def __init__(self, timeline):
        self.queue_north = 0
        self.queue_east = 0
        self.queue_south = 0
        self.queue_west = 0
        
        self.action_north = None
        self.action_east = None
        self.action_south = None
        self.action_west = None
        
        
        self.timeline = timeline
        self.timeline.connect('completed', self.flush_queue)
        
    def flush_queue(self):
        if self.queue_north > 0:
            self.selectNext()
        elif self.moveQueue < 0:
            self.selectPrevious()

        self.moveQueue = 0