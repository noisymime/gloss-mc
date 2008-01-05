import clutter

class Transition:
    
    def __init__(self, GlossMgr):
        self.stage = GlossMgr.stage
        self.glossMgr = GlossMgr
    
    def do_transition(self, fromMenu, toMenu):
            oldGroup = fromMenu.getItemGroup()
            oldMenuGroup = fromMenu #.getMenuGroup()
            newGroup = toMenu.getItemGroup()
            newMenuGroup = toMenu #.getMenuGroup()
            
            oldGroup.set_opacity(255)
            
            self.timeline = clutter.Timeline(25, 50)
            self.alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
            #self.exit_behaviour_scale = clutter.BehaviourScale(self.alpha, 1, 0.5, clutter.GRAVITY_CENTER)
            self.exit_behaviour_opacity = clutter.BehaviourOpacity(opacity_start=150, opacity_end=0, alpha=self.alpha)
            
            #Setup some knots
            knots_exiting = (\
                    (oldGroup.get_x(), oldGroup.get_y()),\
                    #(-oldGroup.get_x(), int(fromMenu.getStage().get_height()/2))
                    (-oldGroup.get_x(), oldGroup.get_y())\
                    )
            self.exit_behaviour_path = clutter.BehaviourPath(knots=knots_exiting, alpha=self.alpha)
            
            #self.exit_behaviour_scale.apply(oldGroup)
            self.exit_behaviour_opacity.apply(oldGroup)
            self.exit_behaviour_opacity.apply(oldMenuGroup)
            self.exit_behaviour_path.apply(oldGroup)
            
            
            ##################################################################
            #Start incoming menu
            #self.exit_behaviour_scale = clutter.BehaviourScale(self.alpha, 1, 0.5, clutter.GRAVITY_CENTER)
            self.entrance_behaviour_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=self.alpha)
            
            #Setup some knots
            start_y = int(self.stage.get_height()/2 - newGroup.get_height()/2)
            start_x = int(self.stage.get_width())
            newGroup.set_position(start_x, start_y)
            #end_x = int(self.stage.get_width() - newGroup.get_width())/2
            (end_x, end_y) = toMenu.get_display_position()
            end_x = oldGroup.get_x() #int(end_x)
            end_y = oldGroup.get_y() #int(end_y)
            knots_entering = (\
                    (newGroup.get_x(), newGroup.get_y()),\
                    #(-oldGroup.get_x(), int(fromMenu.getStage().get_height()/2))
                    (end_x, end_y) \
                    #toMenu.get_display_position()
                    )
    
            self.entrance_behaviour_path = clutter.BehaviourPath(self.alpha, knots_entering)
            
            self.entrance_behaviour_opacity.apply(newGroup)
            self.entrance_behaviour_opacity.apply(newMenuGroup)
            self.entrance_behaviour_path.apply(newGroup)
            #newGroup.show_all()
            #newMenuGroup.show_all()

            toMenu.display()
            
            
            #Finally, move the selector bar
            self.glossMgr.selector_bar.selectItem(fromMenu.getItem(0), self.timeline)
            #(to_x, to_y) = toMenu.get_display_position() #fromMenu.getItem(0).get_abs_position()
            #self.selector_bar.move_to(int(to_x), int(to_y), self.timeline)
            toMenu.selectFirst(False)
            
            #self.timeline.connect('completed', self.on_transition_complete, fromMenu)
            self.timeline.start()

            self.glossMgr.currentMenu = toMenu
    
    def on_transition_complete(self, data):
        pass