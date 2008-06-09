import clutter

class Transition:
    
    def __init__(self, GlossMgr):
        self.stage = GlossMgr.stage
        self.glossMgr = GlossMgr
    
    def forward(self, timeline, oldGroup, newGroup):
        timeline.connect('completed', self.on_transition_complete, oldGroup)
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        
        
        newGroup.set_position( int(-newGroup.get_width()), int(oldGroup.get_y() * 0.8))
        newGroup.show()
        
        knots_incoming = (\
                  #( int(-newGroup.get_width()), int(oldGroup.get_y() * 0.8) ),\
                  ( int(oldGroup.get_x()/2), int(oldGroup.get_y()*1.5) ),\
                  ( int(oldGroup.get_x()*1.2) , int(oldGroup.get_y()) ),\
                  ( oldGroup.get_x(), oldGroup.get_y() )\
                  )
        
        #self.behaviour_incoming_bspline = clutter.BehaviourBspline(knots=knots_incoming, alpha=alpha)
        self.behaviour_incoming_bspline = clutter.BehaviourPath(knots=knots_incoming, alpha=alpha)
        self.behaviour_incoming_bspline.apply(newGroup)
        
        self.behaviour_incoming_scale = clutter.BehaviourScale(x_scale_start=0, y_scale_start=0, x_scale_end=1, y_scale_end=1, alpha=alpha)
        self.behaviour_incoming_scale.apply(newGroup)
        #self.behaviour_incoming_depth = clutter.BehaviourDepth(depth_start=-1000, depth_end=oldGroup.get_depth(), alpha=alpha)
        #self.behaviour_incoming_depth.apply(newGroup)
        
        self.behaviour_incoming_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=oldGroup.get_opacity(), alpha=alpha)
        self.behaviour_incoming_opacity.apply(newGroup)
        
        #*************************************************************************8
        #Do the outgoing group
        knots_outgoing = (\
                  ( oldGroup.get_x(), oldGroup.get_y() ),\
                  ( int(oldGroup.get_x()/2) , int(oldGroup.get_y() * 0.9) ),\
                  ( int(-oldGroup.get_width()), int(oldGroup.get_y() * 0.8) )\
                  )

        self.behaviour_outgoing_bspline = clutter.BehaviourPath(knots=knots_outgoing, alpha=alpha)
        self.behaviour_outgoing_bspline.apply(oldGroup)
        
        self.behaviour_outgoing_scale = clutter.BehaviourScale(x_scale_start=1, y_scale_start=1, x_scale_end=2, y_scale_end=2, alpha=alpha)
        self.behaviour_outgoing_scale.apply(oldGroup)
        #self.behaviour_outgoing_depth = clutter.BehaviourDepth(depth_start=oldGroup.get_depth(), depth_end=1000, alpha=alpha)
        #self.behaviour_outgoing_depth.apply(oldGroup)
        
        self.behaviour_outgoing_opacity = clutter.BehaviourOpacity(opacity_start=oldGroup.get_opacity(), opacity_end=0, alpha=alpha)
        self.behaviour_outgoing_opacity.apply(oldGroup)
        
        
    def backward(self, timeline, oldGroup, newGroup):
        timeline.connect('completed', self.on_transition_complete, oldGroup)
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        
        
        newGroup.set_position( int(-newGroup.get_width()), int(oldGroup.get_y() * 0.8))
        newGroup.show()
        
        knots_incoming = (\
                  ( int(-newGroup.get_width()), int(oldGroup.get_y() * 0.8) ),\
                  ( int(oldGroup.get_x()/2) , int(oldGroup.get_y() * 0.9) ),\
                  ( oldGroup.get_x(), oldGroup.get_y() )\
                  )
        
        #self.behaviour_incoming_bspline = clutter.BehaviourBspline(knots=knots_incoming, alpha=alpha)
        self.behaviour_incoming_bspline = clutter.BehaviourPath(knots=knots_incoming, alpha=alpha)
        self.behaviour_incoming_bspline.apply(newGroup)
        
        self.behaviour_incoming_scale = clutter.BehaviourScale(x_scale_start=2, y_scale_start=2, x_scale_end=1, y_scale_end=1, alpha=alpha)
        self.behaviour_incoming_scale.apply(newGroup)
        #self.behaviour_incoming_depth = clutter.BehaviourDepth(depth_start=1000, depth_end=oldGroup.get_depth(), alpha=alpha)
        #self.behaviour_incoming_depth.apply(newGroup)
        
        self.behaviour_incoming_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=oldGroup.get_opacity(), alpha=alpha)
        self.behaviour_incoming_opacity.apply(newGroup)
        
        #*****************************************************************
        #Begin outgoing stuff
        knots_outgoing = (\
                  ( oldGroup.get_x(), oldGroup.get_y() ),\
                  ( int(oldGroup.get_x()/2) , int(oldGroup.get_y() * 0.9) ),\
                  (( int(-oldGroup.get_width()), int(oldGroup.get_y() * 0.8) ))\
                  )
        self.behaviour_outgoing_bspline = clutter.BehaviourPath(knots=knots_outgoing, alpha=alpha)
        self.behaviour_outgoing_bspline.apply(oldGroup)
        
        self.behaviour_outgoing_scale = clutter.BehaviourScale(x_scale_start=1, y_scale_start=1, x_scale_end=0, y_scale_end=0, alpha=alpha)
        self.behaviour_outgoing_scale.apply(oldGroup)
        #self.behaviour_outgoing_depth = clutter.BehaviourDepth(depth_start=oldGroup.get_depth(), depth_end=-1000, alpha=alpha)
        #self.behaviour_outgoing_depth.apply(oldGroup)
        
        self.behaviour_outgoing_opacity = clutter.BehaviourOpacity(opacity_start=oldGroup.get_opacity(), opacity_end=0, alpha=alpha)
        self.behaviour_outgoing_opacity.apply(oldGroup)

    def on_transition_complete(self, data, oldGroup):
        oldGroup.get_parent().remove(oldGroup)
        pass
    
    def set_options(self, options):
        pass