import clutter

class Transition:
    
    def __init__(self, GlossMgr):
        self.stage = GlossMgr.stage
        self.glossMgr = GlossMgr
    
    def do_transition(self, fromMenu, toMenu):
            
        #oldGroup = fromMenu.getItemGroup()
        #newGroup = toMenu.getItemGroup()
        
        #oldGroup.set_opacity(255)
        
        self.timeline = clutter.Timeline(25, 50)
        self.timeline.connect('completed', self.slide_complete, fromMenu)
        self.alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        #self.exit_behaviour_scale = clutter.BehaviourScale(self.alpha, 1, 0.5, clutter.GRAVITY_CENTER)
        self.exit_behaviour_opacity = clutter.BehaviourOpacity(opacity_start=150, opacity_end=0, alpha=self.alpha)
        
        #Setup some knots
        knots_exiting = (\
                (fromMenu.get_x(), fromMenu.get_y()),\
                #(-oldGroup.get_x(), int(fromMenu.getStage().get_height()/2))
                (-fromMenu.get_x(), fromMenu.get_group_y())\
                )
        self.exit_behaviour_path = clutter.BehaviourPath(knots=knots_exiting, alpha=self.alpha)

        #self.exit_behaviour_scale.apply(oldGroup)
        self.exit_behaviour_opacity.apply(fromMenu.get_current_item().itemTexturesGroup)
        self.exit_behaviour_opacity.apply(fromMenu)
        self.exit_behaviour_path.apply(fromMenu)
        
        
        ##################################################################
        #Start incoming menu
        #self.exit_behaviour_scale = clutter.BehaviourScale(self.alpha, 1, 0.5, clutter.GRAVITY_CENTER)
        self.entrance_behaviour_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=self.alpha)
        
        #Setup some knots
        start_y = fromMenu.get_y()#int(self.stage.get_height()/2 - newGroup.get_height()/2)
        start_x = int(self.stage.get_width())

        (end_x, end_y) = fromMenu.get_position()
        knots_entering = (\
                #(toMenu.get_x(), toMenu.get_y()),\
                (start_x, start_y),\
                (end_x, int(fromMenu.get_y()))
                #(end_x, fromMenu.get_group_y()) \
                #toMenu.get_display_position()
                )
        self.entrance_behaviour_path = clutter.BehaviourPath(self.alpha, knots_entering)
        
        self.entrance_behaviour_opacity.apply(toMenu.get_current_item().itemTexturesGroup)
        self.entrance_behaviour_opacity.apply(toMenu)
        self.entrance_behaviour_path.apply(toMenu)

        #This takes care of adding the new menu to the stage etc
        toMenu.display()
        
        #Finally, move the selector bar
        (bar_x, bar_y) = self.glossMgr.selector_bar.position_0
        self.glossMgr.selector_bar.move_to(bar_x, bar_y, self.timeline)
        toMenu.selectFirst(False)
        
        self.timeline.start()
        self.glossMgr.currentMenu = toMenu
        
    def slide_complete(self, timeline, fromMenu):
        self.stage.remove(fromMenu)
        #self.stage.remove(fromMenu.get_current_item().itemTexturesGroup)
        fromMenu.get_current_item().itemTexturesGroup.get_parent().remove(fromMenu.get_current_item().itemTexturesGroup)