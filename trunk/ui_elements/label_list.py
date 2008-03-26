import clutter
import pango
from InputQueue import InputQueue

class LabelList(clutter.Group):
    DIRECTION_UP, DIRECTION_DOWN = range(2)
    
    fps = 35
    frames = 25

    #Default font
    font_string = "Tahoma 30"
    item_gap = 0
    
    def __init__(self, length):
        clutter.Group.__init__(self)
        self.items = []
        
        #Setup input queue controller
        self.input_queue = InputQueue()
        self.input_queue.set_action(InputQueue.NORTH, self.move_up)
        self.input_queue.set_action(InputQueue.SOUTH, self.move_down)
        
        self.selected = 0
        self.displayMin = 0 #The number of menu items that will be shown at a time
        self.displayMax = length
        self.displaySize = self.displayMax - self.displayMin
        
        #Selector bar image, moves with selections to show current item
        self.selector_bar = None
        
    def on_key_press_event (self, event):
        self.input_queue.input(event)
        return self.timeline
    
    def add_item(self, itemLabel):
        if len(self.items) == 0:
            #Perform a cheap hack to figure out the height of a label
            tempLabel = clutter.Label()
            tempLabel.set_font_name(self.font_string)
            tempLabel.set_text("S")

            self.label_height = tempLabel.get_height()
            label_width = 0
        
        label_y = len(self.items) * (self.label_height + self.item_gap)
        
        newItem = ListItem(self.font_string, itemLabel)
        newItem.set_position(0, label_y)
        newItem.show()
        self.items.append(newItem)
        
        self.add(newItem)
        return newItem
    
    #Removes all items from the list
    def clear(self):
        for item in self.items:
            self.remove(item)
            item = None
        self.items = []
        
    
    def display(self):
        if self.displayMax > len(self.items):
            self.displayMax = len(self.items)
            self.displaySize = self.displayMax - self.displayMin
        
        #for i in range(self.displaySize):
        #    self.menuItems[i].show()
        
        self.show()
        
    def move_selection(self, direction):

        if direction == self.DIRECTION_DOWN:
            #Check if we're at the last item in the list
            if (self.selected) == (len(self.items)-1):
                return
            else:
                self.selected = self.selected+1
        elif direction == self.DIRECTION_UP:
            #Check if we're at the first / last item in the list
            if (self.selected) == 0:
                return
            else:
                self.selected = self.selected-1
                
        self.timeline = clutter.Timeline (self.frames, self.fps)
        self.input_queue.set_timeline(self.timeline)

        
        #This horrible loop does all the scaling
        #This includes, the selected item and the ones on either side of it
        for i in range(len(self.items)):
            #print str(i)
            if i == self.selected:
                self.items[i].scaleLabel(ListItem.SCALE_FULL, self.timeline)
            elif (i == self.selected-1) and (i >= self.displayMin):
                self.items[i].scaleLabel(ListItem.SCALE_MEDIUM, self.timeline)
            elif (i == self.selected+1) and (i <= self.displayMax-1):
                self.items[i].scaleLabel(ListItem.SCALE_MEDIUM, self.timeline)
            else:
                self.items[i].scaleLabel(ListItem.SCALE_NONE, self.timeline)
        
        #Check we're at the top of the viewable list
        if self.selected < (self.displayMin):
            #If yes, move the menu, leave the selection bar where is
            #self.menuItems[self.selected].set_opacity(0)
            #self.menuItems[self.selected].show()
            self.rollList( self.menuItems[self.selected], self.menuItems[self.selected+self.displaySize], self.timeline)
        else:
            if not self.selector_bar is None:
                #move the selection bar
                self.selector_bar().selectItem(self.menuItems[self.selected], self.timeline)

        self.timeline.start()
            
    def move_up(self):
        self.move_selection(self.DIRECTION_UP)
        
    def move_down(self):
        self.move_selection(self.DIRECTION_DOWN)
                        
    def select_first(self, frames = 1, fps = 75):
        if self.input_queue.is_in_queue():
            "ERROR: Timeline should NOT be playing here!"
            return
               
        self.timeline = clutter.Timeline(frames, fps)
        self.input_queue.set_timeline(self.timeline)
        self.selected = 0
        for i in range(0,len(self.items)):
            if i == 0:
                self.items[i].scaleLabel(ListItem.SCALE_FULL, self.timeline)
            elif i == 1:
                self.items[i].scaleLabel(ListItem.SCALE_MEDIUM, self.timeline)
            else:
                self.items[i].scaleLabel(ListItem.SCALE_NONE, self.timeline)
                
        self.timeline.start()
        
    #Just calls the above function with different arguements to result in the first item being selected in a 'prettier' manner
    def select_first_elegant(self):
        self.select_first(frames=self.frames, fps=self.fps)
        
    def select_none(self, frames = 1, fps = 75):
        self.timeline = clutter.Timeline(frames, fps)
        self.input_queue.set_timeline(self.timeline)
        self.selected = None
        for i in range(0,len(self.items)):
            self.items[i].scaleLabel(ListItem.SCALE_NONE, self.timeline)
                
        self.timeline.start()
    
    def select_none_elegant(self):
        self.select_none(self.frames, self.fps)
        
    #When the menu needs to display a new item from the top or bottom, it rolls
    # The distance the menu moves is the distance (in pixels) between the incoming item and the selector bar
    def rollList(self, incomingMenuItem, outgoingMenuItem, timeline):  
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
        
import gobject
class ListItem(clutter.Group):
    #Setup signals
    __gsignals__ =  { 
        "selected": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, []),
        "deselected": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
        }
    
    SCALE_NONE, SCALE_MEDIUM, SCALE_FULL = range(3) 
    
    #Default values for zoom and opacity
    opacity_step_full = 255
    opacity_step_medium = 135
    opacity_step_none = 50
    scale_step_full = 1
    scale_step_medium = 0.5
    scale_step_none = 0.4

    def __init__ (self, font, label_left = "", label_right = ""):
        clutter.Group.__init__ (self) #, menu, itemLabel, y)
        
        self.label_left = clutter.Label()
        self.label_right = clutter.Label()
        
        #setup the label/s
        self.add(self.label_left)
        self.label_left.show()
        self.label_left.set_font_name(font)
        self.label_left.set_text(label_left)
        self.color = clutter.Color(0xff, 0xff, 0xff, 0xdd)
        self.label_left.set_color(self.color)
        self.currentOpacity = 255
        self.data = label_left #By default the items data is simply its label
        
        #The width is the length of the selector bar minus its offset
        #width = self.glossMgr.get_selector_bar().get_width() + self.glossMgr.get_selector_bar().get_x_offset()
        #self.set_width(width)
        
        self.label_left.set_ellipsize(pango.ELLIPSIZE_END)
        
        #Text is actually scaled down in 'regular' position so that it doesn't get jaggies when zoomed in
        #self.set_scale(self.zoomLevel, self.zoomLevel)
        self.currentZoom = 0        
        
        """
        #(label_width, label_height) = self.label.get_size()
        label_x = 0 #x #self.stage.get_width() - label_width - 50
        label_y = y #self.stage.get_height() - label_height
        self.set_position(0, y)
        """
        
    def scaleLabel(self, level, timeline):
       
        #Default values (Just in case)
        zoomTo=0
        opacityTo = 255

        
        if level == self.SCALE_FULL:
            zoomTo = self.scale_step_full #self.menu.zoomStep0
            opacityTo = self.opacity_step_full #self.menu.opacityStep0
            self.emit("selected")
        if level == self.SCALE_MEDIUM:
            zoomTo = self.scale_step_medium #self.menu.zoomStep1
            opacityTo = self.opacity_step_medium #self.menu.opacityStep1
            self.emit("deselected")
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
        
    def set_data(self, data):
        self.data = data
        
    def get_data(self):
        return self.data
    
    def get_menu(self):
        return self.menu