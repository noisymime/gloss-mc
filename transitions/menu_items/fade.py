import clutter

class Transition:
    
    def __init__(self, GlossMgr):
        self.stage = GlossMgr.stage
        self.glossMgr = GlossMgr
    
    def forward(self, timeline, oldGroup, newGroup):
        self.do_transition(timeline, oldGroup, newGroup)
        newGroup.show()
        
    def backward(self, timeline, oldGroup, newGroup):
        self.do_transition(timeline, oldGroup, newGroup)
        newGroup.show()
        
    def do_transition(self, timeline, oldGroup, newGroup):
        timeline.connect('completed', self.on_transition_complete, oldGroup)

        newGroup.set_opacity(0)
        (x, y) = oldGroup.get_position()
        newGroup.set_position(x, y)
        
        #self.exit_behaviour_scale = clutter.BehaviourScale(self.alpha, 1, 0.5, clutter.GRAVITY_CENTER)
        self.alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.new_behaviour_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=oldGroup.get_opacity(), alpha=self.alpha)
        self.old_behaviour_opacity = clutter.BehaviourOpacity(opacity_start=oldGroup.get_opacity(), opacity_end=0, alpha=self.alpha)
        
        #self.exit_behaviour_scale.apply(oldGroup)
        self.new_behaviour_opacity.apply(newGroup)
        self.old_behaviour_opacity.apply(oldGroup)

    def on_transition_complete(self, data, oldGroup):
        if not oldGroup.get_parent is None:
            oldGroup.get_parent().remove(oldGroup)
    
    def set_options(self, options):
        pass