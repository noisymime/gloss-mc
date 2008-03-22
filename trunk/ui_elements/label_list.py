import clutter

class LabelList(clutter.Group):
    DIRECTION_UP, DIRECTION_DOWN = range(2)
    
    def __init__(self):
        clutter.Group.__init__(self)
        
    def move_selection(self, direction):
                
        #Check if we're at the first item in the list
        if (self.selected) != 0:        
            self.timeline = clutter.Timeline (15,85)
            self.input_queue.set_timeline(self.timeline)
            #self.timeline.connect('completed', self.completeMove)
                
            if not self.moveQueue == 0:
                self.selected = self.selected -1 #+ self.moveQueue
                self.moveQueue = self.moveQueue + 1 # 0
                if self.selected < 0:
                    self.selected = 0
            else:
                self.selected = self.selected-1
            
            #This horrible loop does all the scaling
            #This includes, the selected item and the ones on either side of it
            for i in range(len(self.menuItems)):
                #print str(i)
                if i == self.selected:
                    self.menuItems[i].scaleLabel(0, self.timeline)
                elif (i == self.selected-1) and (i >= self.displayMin):
                    self.menuItems[i].scaleLabel(1, self.timeline)
                elif (i == self.selected+1) and (i <= self.displayMax-1):
                    self.menuItems[i].scaleLabel(1, self.timeline)
                else:
                    self.menuItems[i].scaleLabel(2, self.timeline)
                    
            #Do the transition of the menu graphic
            #If there's no transition set (Would have been set in the theme) then the item is simply show
            if not self.menu_item_transition is None:
                self.menu_item_transition.backward(self.timeline, self.menuItems[self.selected+1].itemTexturesGroup, self.menuItems[self.selected].itemTexturesGroup)
            else:
                self.menuItems[self.selected].itemTexturesGroup.show()
            
            #Check we're at the top of the viewable list
            if self.selected < (self.displayMin):
                #If yes, move the menu, leave the selection bar where is
                #self.menuItems[self.selected].set_opacity(0)
                #self.menuItems[self.selected].show()
                self.rollMenu( self.menuItems[self.selected], self.menuItems[self.selected+self.displaySize], self.timeline)
            else:
                #move the selection bar
                self.glossMgr.get_selector_bar().selectItem(self.menuItems[self.selected], self.timeline)

            self.timeline.start()
                        
    def selectFirst(self, moveBar):
        if self.timeline.is_playing:
            "ERROR: Timeline should NOT be playing here!"
               
        self.timeline = clutter.Timeline(1, 75)
        self.selected = 0
        for i in range(0,len(self.menuItems)):
            if i == 0:
                self.menuItems[i].scaleLabel(0, self.timeline)
            elif i == 1:
                self.menuItems[i].scaleLabel(1, self.timeline)
            else:
                self.menuItems[i].scaleLabel(2, self.timeline)
                
        #Show the current menu item's graphic
        self.menuItems[self.selected].itemTexturesGroup.show()
        
        if moveBar:    
            self.glossMgr.get_selector_bar().selectItem(self.menuItems[self.selected], self.timeline)
        
        self.timeline.start()
        
    #When the menu needs to display a new item from the top or bottom, it rolls
    # The distance the menu moves is the distance (in pixels) between the incoming item and the selector bar
    def rollMenu(self, incomingMenuItem, outgoingMenuItem, timeline):  
        print "Rolling: " + incomingMenuItem.data + "<------" + outgoingMenuItem.data  
        (group_x, group_y) = self.itemGroup.get_abs_position()
        (bar_x, bar_y) = self.glossMgr.get_selector_bar().get_abs_position() # incomingMenuItem.get_menu().getMenuMgr().
        (incoming_x, incoming_y) = self.glossMgr.get_selector_bar().get_true_abs_position(incomingMenuItem) #incomingMenuItem.get_abs_position()
        
        print "Starting group position: " + str(self.itemGroup.get_abs_position())
        
        if incoming_y > bar_y:  
            #Then the incoming item is below the selector bar
            height_diff = int(self.glossMgr.get_selector_bar().get_height() - incomingMenuItem.get_height()) #self.glossMgr.get_selector_bar().get_height())
            #print "height diff: " + str(height_diff)
            gap = ((incoming_y - bar_y) - math.floor(height_diff/2)) * -1
            gap = int(gap)
            #gap = -65
            self.displayMin = self.displayMin+1
            self.displayMax = self.displayMax+1
        else:
            #Then the incoming item is above the selector bar
            height_diff = int(self.glossMgr.get_selector_bar().get_height() - incomingMenuItem.get_height()) #self.glossMgr.get_selector_bar().get_height())
            gap = bar_y - incoming_y + math.ceil(height_diff/2)
            gap = int(gap)
            #gap = 65
            self.displayMin = self.displayMin-1
            self.displayMax = self.displayMax-1
        
        #print "Gap: " + str(gap)
        new_y = (group_y + gap)
        knots = (\
            (group_x, group_y),\
            (group_x, new_y )\
            )
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.behaviour1 = clutter.BehaviourPath(alpha, knots)
        self.behaviour2 = clutter.BehaviourOpacity(opacity_start=outgoingMenuItem.get_opacity(), opacity_end=0, alpha=alpha)
        
        #print "Going to: "+ str(new_y)
        #print behaviour1.get_knots()
        
        self.behaviour1.apply(self)
        self.behaviour2.apply(outgoingMenuItem)
        
        
class SimpleListItem(clutter.group):
    SCALE_NONE, SCALE_MEDIUM, SCALE_FULL = range(3) 
    
    #Default values for zoom and opacity
    opacity_step_full = 255
    opacity_step_medium = 135
    opacity_step_none = 50
    scale_step_full = 1
    scale_step_medium = 0.5
    scale_step_none = 0.4
    
    #Default font
    font_string = "Tahoma 30"
    
    label_left = clutter.Label()
    label_right = clutter.Label()

    def __init__ (self, font, label_left = "", label_right = "", y):
        clutter.Group.__init__ (self) #, menu, itemLabel, y)
        self.glossMgr = menu.getGlossMgr()
        #self.menu = menu
        #self.stage = glossMgr.get_stage()
        
        #ItemTexturesGroup is what shows any images / reflections associated with the item
        #self.itemTexturesGroup = clutter.Group()
        #self.itemTexturesGroup.set_position(menu.menu_image_x, menu.menu_image_y)
        
        
        #setup the label
        """
        font = menu.font
        self.set_font_name(font)
        self.set_text(itemLabel)
        self.color = clutter.Color(0xff, 0xff, 0xff, 0xdd)
        self.set_color(self.color)
        self.currentOpacity = 255
        self.data = itemLabel #By default the items data is simply its label
        
        #The width is the length of the selector bar minus its offset
        width = self.glossMgr.get_selector_bar().get_width() + self.glossMgr.get_selector_bar().get_x_offset()
        self.set_width(width)
        
        self.set_ellipsize(pango.ELLIPSIZE_END)
        """
        #Text is actually scaled down in 'regular' position so that it doesn't get jaggies when zoomed in
        self.set_scale(self.zoomLevel, self.zoomLevel)
        self.currentZoom = 0        
        
        """
        #(label_width, label_height) = self.label.get_size()
        label_x = 0 #x #self.stage.get_width() - label_width - 50
        label_y = y #self.stage.get_height() - label_height
        self.set_position(0, y)
        
        #Add textures group and mark whether or not the textures are currently on the stage
        self.itemTexturesGroup.show_all()
        self.onStage = False
        """
        
    def scaleLabel(self, level, timeline):
       
        #Default values (Just in case)
        zoomTo=0
        opacityTo = 255

        
        if level == self.SCALE_FULL:
            zoomTo = self.scale_step_full #self.menu.zoomStep0
            opacityTo = self.opacity_step_full #self.menu.opacityStep0
        if level == self.SCALE_MEDIUM:
            zoomTo = self.scale_step_medium #self.menu.zoomStep1
            opacityTo = self.opacity_step_medium #self.menu.opacityStep1
            #self.itemTexturesGroup.hide_all()
        if level == self.SCALE_NONE:
            zoomTo = self.scale_step_none #self.menu.zoomStep2
            opacityTo = self.opacity_step_none #self.menu.opacityStep2
            
        if (zoomTo == self.currentZoom) and (opacityTo == self.currentOpacity):
            return None
    
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.behaviourScale = clutter.BehaviourScale(x_scale_start=self.currentZoom, y_scale_start=self.currentZoom, x_scale_end=zoomTo, y_scale_end=zoomTo, alpha=alpha) #scale_gravity=clutter.GRAVITY_WEST, 
        self.set_anchor_point_from_gravity(clutter.GRAVITY_WEST)
        self.behaviourOpacity = clutter.BehaviourOpacity(opacity_start=self.currentOpacity, opacity_end=opacityTo, alpha=alpha)
        self.behaviourScale.apply(self)
        self.behaviourOpacity.apply(self)
        
        #timeline.connect('completed', self.scale_end_event, zoomTo, opacityTo)
        self.currentZoom = zoomTo
        self.currentOpacity = opacityTo

    def scale_end_event(self, data, zoomTo, opacityTo):
        pass
        
    def get_zoom_level(self):
        return self.zoomLevel

        
    def add_image_from_path(self, path, x, y):
        self.tempTexture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        tempTexture.set_pixbuf(pixbuf)
        
        self.add_image_from_texture(tempTexture, x, y)
        
    def set_data(self, data):
        self.data = data
        
    def get_data(self):
        return self.data
    
    def get_menu(self):
        return self.menu