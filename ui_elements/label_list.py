import clutter
import pango
import pygtk
import gtk
from utils.InputQueue import InputQueue

class LabelList(clutter.Group):
    DIRECTION_UP, DIRECTION_DOWN = range(2)
    
    fps = 35
    frames = 25

    #Default font
    font_string = "Tahoma 30"
    item_height_percent = 1.00
    width = 0
    item_height = 0
    
    def __init__(self):
        clutter.Group.__init__(self)
        self.items = []
        
        #Setup input queue controller
        self.input_queue = InputQueue()
        self.input_queue.set_action(InputQueue.NORTH, self.move_up)
        self.input_queue.set_action(InputQueue.SOUTH, self.move_down)
        
        self.selected = 0
        self.displayMin = 0 #The number of menu items that will be shown at a time
        self.displayMax = 5 # default value
        self.displaySize = self.displayMax - self.displayMin
        self.roll_point_min = 1 #The item number at which point the list will roll down
        self.roll_point_max = self.displaySize -1 #The item number at which point the list will roll up
        
        #There are 3 subgroups:
        # 1) item_group: Contains the labels themselves
        # 2) background_group: Contains the background images
        # 3) display_group: Contains groups 1 & 2
        # Group 3 is then added to self 
        self.item_group = clutter.Group()
        self.item_group.show()
        self.background_group = clutter.Group()
        self.background_group.show()
        self.display_group = clutter.Group()
        self.display_group.show()
        
        self.display_group.add(self.background_group)
        self.display_group.add(self.item_group)
        
        self.inactive_item_background = None

        
        self.image_down = None
        self.image_up = None
        
        #Selector bar image, moves with selections to show current item
        self.selector_bar = None
    
    def setup_from_theme_id(self, themeMgr, id):
        element = themeMgr.search_docs("label_list", id).childNodes
        img_element = themeMgr.search_docs("label_list", id).getElementsByTagName("texture")
        #Quick check to make sure we found something
        if element is None:
            return None
        
        self.item_height_percent = float(themeMgr.find_child_value(element, "item_height_percent"))
        
        #Grab the font
        font_node = themeMgr.get_subnode(element, "font")
        fontString = themeMgr.get_font("main", font_node)
        self.font_string = fontString
        
        #Set the selection effect steps
        self.zoomStep0 = float(themeMgr.find_child_value(element, "scale_step0"))
        self.zoomStep1 = float(themeMgr.find_child_value(element, "scale_step1"))
        self.zoomStep2 = float(themeMgr.find_child_value(element, "scale_step2"))
        self.opacityStep0 = int(themeMgr.find_child_value(element, "opacity_step0"))
        self.opacityStep1 = int(themeMgr.find_child_value(element, "opacity_step1"))
        self.opacityStep2 = int(themeMgr.find_child_value(element, "opacity_step2"))
        
        self.fps = int(themeMgr.find_child_value(element, "transition_fps"))
        self.frames = int(themeMgr.find_child_value(element, "transition_frames"))
        
        themeMgr.setup_actor(self, element, themeMgr.stage)
        (self.width, self.height) = themeMgr.get_dimensions(element, themeMgr.stage)
        
        #Set the up/down images
        #This assumes images go in the bottom right corner, will add flexibility later
        img_element_up = themeMgr.find_element(img_element, "id", "image_up")
        img_element_down = themeMgr.find_element(img_element, "id", "image_down")
        if not img_element_up is None:
            img_element_up = img_element_up.childNodes
            self.image_up = themeMgr.get_texture("image_up", self, element = img_element_up)
            self.image_up.set_opacity(180)
            self.image_up.set_position( self.width-self.image_up.get_width(), self.height+1)
            self.image_up.show()
            self.add(self.image_up)
        if not img_element_down is None:
            img_element_down = img_element_down.childNodes
            self.image_down = themeMgr.get_texture("image_up", self, element = img_element_down)
            self.image_down.set_opacity(180)
            self.image_down.set_position( self.width-self.image_down.get_width()-self.image_up.get_width(), self.height+1)
            self.image_down.show()
            self.add(self.image_down)
            
        
        self.display_group.set_clip(0, 0, self.width, self.height)
        #self.background_group.set_clip(0, 0, self.width, self.height)
        
        #Get the item background img
        img_element_item = themeMgr.find_element(img_element, "id", "inactive_background")
        if not img_element_item is None:
            img_element_item = img_element_item.childNodes
            self.inactive_item_background = themeMgr.get_texture("inactive_background", self, element = img_element_item)
        
        #Update the displayMax and roll_point
        height = self.get_item_height()
        self.displayMax = (self.height / height) - 1
        #For the moment, the roll_point_x is just the ends of the list
        self.roll_point_min = 1
        self.roll_point_max = self.displayMax
        
    def on_key_press_event (self, event):
        self.input_queue.input(event)
        return self.timeline
    
    def get_item_height(self):
        if not self.item_height == 0:
            return self.item_height
        
        #Perform a cheap hack to figure out the height of a label
        tempLabel = clutter.Label()            
        tempLabel.set_font_name(self.font_string)
        tempLabel.set_text("S")

        self.label_height = tempLabel.get_height()
        self.item_height = int(self.label_height * self.item_height_percent)
        
        return self.item_height
    
    def add_item(self, itemLabel):
        if len(self.items) == 0:
            self.displayMax = self.height / self.label_height
            label_width = 0
    
            #This has to go hear for layering purposes
            if self.display_group.get_parent() is None:
                self.add(self.display_group)
        
        item_y = len(self.items) * self.item_height
        label_y = item_y + ((self.item_height - self.label_height)/2)
        label_y = int(label_y)
        
        #If a background pic is specified in the theme, clone it and add
        if not self.inactive_item_background is None:
            bg_img = clutter.CloneTexture(self.inactive_item_background)
            bg_img.set_height(self.item_height)
            bg_img.set_width(self.width)
            bg_img.set_position(0, item_y)
            self.background_group.add(bg_img)
            
        
        newItem = ListItem(self.font_string, itemLabel, label_list = self, max_width = self.width)
        newItem.set_position(0, label_y)
        """
        if len(self.items) < self.displaySize:
            newItem.show()            
            if not self.image_down is None: self.image_down.set_opacity(255)
            if not self.inactive_item_background is None: bg_img.show()
        """
        newItem.show()            
        if not self.image_down is None: self.image_down.set_opacity(255)
        if not self.inactive_item_background is None: bg_img.show()
        self.items.append(newItem)
        
        self.item_group.add(newItem)
        return newItem
    
    #Removes all items from the list
    def clear(self):
        for item in self.items:
            self.item_group.remove(item)
            item = None
        self.items = []
        self.selected = 0
        
    
    def display(self):
        if self.displayMax > len(self.items):
            self.displayMax = len(self.items)
            #self.displaySize = self.displayMax - self.displayMin
        
        #for i in range(self.displaySize):
        #    self.menuItems[i].show()
        
        self.show()
        
    def move_selection(self, direction):

        if direction == self.DIRECTION_DOWN:
            #Check if we're at the last item in the list
            if (self.selected) == (len(self.items)-1):
                return
            else:
                self.selected += 1
        elif direction == self.DIRECTION_UP:
            #Check if we're at the first / last item in the list
            if (self.selected) == 0:
                return
            else:
                self.selected -= 1
                
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
        if (self.selected < self.roll_point_min) and (self.displayMin > 0):
            #If yes, move the menu, leave the selection bar where is
            #self.rollList( self.items[self.displayMin-1], self.items[self.displayMax+1], self.DIRECTION_UP, self.timeline)
            self.rollList( self.DIRECTION_UP, self.timeline)
        #Check if we're at the bottom of the viewable list
        elif (self.selected > self.roll_point_max) and (self.displayMax < (len(self.items)-1)):
            #self.rollList( self.items[self.displayMax+1], self.items[self.displayMin-1], self.DIRECTION_DOWN, self.timeline)
            self.rollList( self.DIRECTION_DOWN, self.timeline)
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
        
        self.selected = 0
        self.timeline.start()
    
    def select_none_elegant(self):
        self.select_none(self.frames, self.fps)
        
    #When the menu needs to display a new item from the top or bottom, it rolls
    # The distance the menu moves is the distance (in pixels) between the incoming item and the selector bar
    def rollList(self, direction, timeline):  
        #print "Rolling: " + incomingMenuItem.data + "<------" + outgoingMenuItem.data  
        (group_x, group_y) = self.item_group.get_position()
        #(bar_x, bar_y) = self.glossMgr.get_selector_bar().get_abs_position() # incomingMenuItem.get_menu().getMenuMgr().
        #(incoming_x, incoming_y) = self.glossMgr.get_selector_bar().get_true_abs_position(incomingMenuItem) #incomingMenuItem.get_abs_position()
        #incoming_y = incomingMenuItem.get_y()
        #outgoing_y = outgoingMenuItem.get_y()
        
        #print "Selected: %s  Roll_min: %s  Roll_max: %s" % (self.selected, self.roll_point_min, self.roll_point_max)
        
        if direction == self.DIRECTION_DOWN:  
            #Then the incoming item is below the selector bar
            #height_diff = int(self.glossMgr.get_selector_bar().get_height() - incomingMenuItem.get_height()) #self.glossMgr.get_selector_bar().get_height())
            #print "height diff: " + str(height_diff)
            #gap = ((incoming_y - bar_y) - math.floor(height_diff/2)) * -1
            #gap = int(gap)
            #gap = -65
            gap = self.item_height * -1
            self.displayMin += 1
            self.displayMax += 1
            self.roll_point_min += 1
            self.roll_point_max += 1
        else:
            #Then the incoming item is above the selector bar
            """
            height_diff = int(self.glossMgr.get_selector_bar().get_height() - incomingMenuItem.get_height()) #self.glossMgr.get_selector_bar().get_height())
            gap = bar_y - incoming_y + math.ceil(height_diff/2)
            gap = int(gap)
            #gap = 65
            """
            gap = self.item_height
            self.displayMin -= 1
            self.displayMax -= 1
            self.roll_point_min -=1
            self.roll_point_max -=1
        
        
        
        #print "Gap: " + str(gap)
        new_y = (group_y + gap)
        knots = (\
            (group_x, group_y),\
            (group_x, new_y )\
            )
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.behaviour_path = clutter.BehaviourPath(alpha, knots)
        #self.behaviour_opacity_outgoing = clutter.BehaviourOpacity(opacity_start=outgoingMenuItem.get_opacity(), opacity_end=0, alpha=alpha)
        #self.behaviour_opacity_incoming = clutter.BehaviourOpacity(opacity_start=0, opacity_end=outgoingMenuItem.get_opacity(), alpha=alpha)
        
        self.behaviour_path.apply(self.item_group)
        self.behaviour_path.apply(self.background_group)
        """
        self.behaviour_opacity_outgoing.apply(outgoingMenuItem)
        #The incoming opacity behaviour is only used if the incomingItem is NOT the currently selected one
        if not self.items[self.selected] == incomingMenuItem: 
            self.behaviour_opacity_incoming.apply(incomingMenuItem)
            #self.behaviour_opacity_incoming.apply(incomingMenutem)
        """
        
    def get_current_item(self):
        return self.items[self.selected]
        
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

    def __init__ (self, font, label_left = "", label_right = "", label_list = None, max_width = None):
        clutter.Group.__init__ (self) #, menu, itemLabel, y)
        self.set_anchor_point_from_gravity(clutter.GRAVITY_WEST)
        
        self.label_left = clutter.Label()
        self.label_right = clutter.Label()
        
        #Takes the scale and opacity values from a label list, if given
        if not label_list is None:
            self.opacity_step_full = label_list.opacityStep0
            self.opacity_step_medium = label_list.opacityStep1
            self.opacity_step_none = label_list.opacityStep2
            self.scale_step_full = label_list.zoomStep0
            self.scale_step_medium = label_list.zoomStep1
            self.scale_step_none = label_list.zoomStep2
            
            self.set_width(label_list.get_width())
            
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
        self.currentZoom = self.scale_step_medium
        self.currentOpacity = self.opacity_step_medium
        self.set_scale(self.currentZoom, self.currentZoom)
        self.set_opacity(self.currentOpacity)
        
        #Set ellipses
        if not max_width is None:
            self.label_left.set_width( max_width - self.label_right.get_width() )
            self.label_left.set_ellipsize(pango.ELLIPSIZE_END)
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