import clutter
import pygtk
import gtk
import pango
import time
import math
from ReflectionTexture import Texture_Reflection
from interfaces.MenuItem import MenuItem
from InputQueue import InputQueue

class Interface(clutter.Group):
    itemGroup = clutter.Group()
    menu_image_rotation = 0
    
    def __init__ (self, glossMgr):
        clutter.Group.__init__(self)
        self.glossMgr = glossMgr
        self.stage = self.glossMgr.get_stage()
        self.itemGroup = clutter.Group()
        self.setup_ui(self.glossMgr.themeMgr, "main", self)
        
        self.selected = 0
        self.off = 0
        
        #Setup input queue controller
        self.input_queue = InputQueue()
        self.input_queue.set_action(InputQueue.NORTH, self.selectPrevious)
        self.input_queue.set_action(InputQueue.SOUTH, self.selectNext)
        
        self.glossMgr.addMenu(self)
        
    def setup_ui(self, themeMgr, name, menu):
        element = themeMgr.search_docs("menu", name).childNodes
        #Quick check to make sure we found something
        if element is None:
            return None
        
        menu.item_gap = int(themeMgr.find_child_value(element, "item_gap"))
        menu.displayMax = int(themeMgr.find_child_value(element, "num_visible_elements"))
        
        #Grab the font
        font_node = themeMgr.get_subnode(element, "font")
        fontString = themeMgr.get_font("main", font_node)
        menu.font = fontString
        
        #setup the menu_image properties
        menu.useReflection = "True" == (themeMgr.find_child_value(element, "menu_item_texture.use_image_reflections"))
        menu_image_node = themeMgr.get_subnode(element, "menu_item_texture")
        if not menu_image_node is None:
            #Set the position
            (x, y) = themeMgr.get_position(menu_image_node, self.stage)
            menu.menu_image_x = int(x)
            menu.menu_image_y = int(y)
        
        #Setup the menu image transition
        image_transition = themeMgr.find_child_value(element, "menu_item_texture.image_transition.name")
        transition_options = themeMgr.find_child_value(element, "menu_item_texture.image_transition.options")
        transition_path = "transitions/menu_items/" + str(image_transition)
        try:
            menu.menu_item_transition = __import__(transition_path).Transition(self.glossMgr)
            menu.menu_item_transition.set_options(transition_options)
        except ImportError:
            print "Theme Error: No menu_item transition titled '" + str(image_transition) + "'"
            menu.menu_item_transition = None
            
        #Setup the menu transition
        menu_transition = themeMgr.find_child_value(element, "menu_transition.name")
        menu_transition_options = themeMgr.find_child_value(element, "menu_transition.options")
        themeMgr.glossMgr.set_menu_transition(menu_transition)
                
        #Finally set general actor properties (position etc)
        #themeMgr.setup_actor(menu.getItemGroup(), element, themeMgr.stage)
        themeMgr.setup_actor(menu, element, themeMgr.stage)
        
    def addItem(self, itemLabel):
        if self.itemGroup.get_n_children() == 0:
            tempLabel = clutter.Label()
            tempLabel.set_font_name(self.font)
            tempLabel.set_text("S")
            self.label_height = tempLabel.get_height()
            label_width = 0
        
        newItem = WheelListItem(self, itemLabel)
        #self.menuItems.append(newItem)
        self.itemGroup.add(newItem)
        
        return newItem
    
    def display(self):
        self.timeline = clutter.Timeline(20, 60)
        self.input_queue.set_timeline(self.timeline)
        alpha_sine_inc = clutter.Alpha(self.timeline, clutter.sine_inc_func)
        self.step = 360.0 / self.itemGroup.get_n_children()
        self.ang = 0.0
        (stage_width, stage_height) = self.stage.get_size()
        
        for i in range(self.itemGroup.get_n_children()):
            tmpTexturesGroup =self.itemGroup.get_nth_child(i).itemTexturesGroup
            self.add(tmpTexturesGroup)

            tmpTexturesGroup.behaviour_ellipse = clutter.BehaviourEllipse(\
                                                       x = int(stage_width/4),\
                                                       y = int(stage_height-stage_height/3),\
                                                       width = int(stage_width/2),\
                                                       height = int(stage_height-stage_height/4),\
                                                       #clutter.ROTATE_CW,\
                                                       start = self.ang,\
                                                       end = (self.ang+self.step),\
                                                       alpha = alpha_sine_inc\
                                                       )
            tmpTexturesGroup.behaviour_opacity = clutter.BehaviourOpacity(opacity_start=0x66, opacity_end=0x66, alpha=alpha_sine_inc)
            tmpTexturesGroup.behaviour_scale = clutter.BehaviourScale(x_scale_start=0.6, y_scale_start=0.6, x_scale_end=0.6, y_scale_end=0.6, alpha=alpha_sine_inc)
            
            tmpTexturesGroup.behaviour_ellipse.apply(tmpTexturesGroup)
            tmpTexturesGroup.behaviour_opacity.apply(tmpTexturesGroup)
            tmpTexturesGroup.behaviour_scale.apply(tmpTexturesGroup)

            self.ang = self.ang + self.step
            tmpTexturesGroup.show()
            tmpTexturesGroup.show_all()
        
        self.selectFirst(False)
        self.stage.add(self)

        self.itemGroup.show()
        self.show()
        
    def selectFirst(self, moveBar):
        for i in range(self.itemGroup.get_n_children()):
            
            ang_start = -90.0
            ang_end   = (self.step * i)

            tmpTexturesGroup = self.itemGroup.get_nth_child(i).itemTexturesGroup
            
            tmpTexturesGroup.behaviour_ellipse.set_angle_start(ang_start)
            tmpTexturesGroup.behaviour_ellipse.set_angle_end(ang_end)
            
            if i == self.selected:
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_start", 0x66)
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_end", 0xff)

        self.timeline.start()
        
    def selectPrevious(self):
        self.do_selection(-1)
    
    def selectNext(self):
        self.do_selection(1)
    
    def do_selection(self, step):
        from_index = self.selected
        
        self.selected = self.selected + (-1 * step)

        if (self.selected < 0): self.selected = self.itemGroup.get_n_children()-1
        if (self.selected >= self.itemGroup.get_n_children()): self.selected = 0
        
        self.ang = self.off
        for i in range(self.itemGroup.get_n_children()):
            tmpTexturesGroup = self.itemGroup.get_nth_child(i).itemTexturesGroup
            
            ang_start = self.ang
            ang_end   = self.ang + (self.step * step)
            
            #Set the rotation based on the step
            if step > 0:
                direction = clutter.ROTATE_CW
            else:
                direction= clutter.ROTATE_CCW
            tmpTexturesGroup.behaviour_ellipse.set_direction(direction)

            #Set the angles
            tmpTexturesGroup.behaviour_ellipse.set_angle_start(ang_start)
            tmpTexturesGroup.behaviour_ellipse.set_angle_end(ang_end)
            
            if i == from_index:
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_start", 0xff)
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_end", 0x66)
                
                tmpTexturesGroup.behaviour_scale.set_property("x_scale_start", 1)
                tmpTexturesGroup.behaviour_scale.set_property("y_scale_start", 1)
                tmpTexturesGroup.behaviour_scale.set_property("x_scale_end", 0.6)
                tmpTexturesGroup.behaviour_scale.set_property("y_scale_end", 0.6)
            elif i == self.selected:
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_start", 0x66)
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_end", 0xff)
                
                tmpTexturesGroup.behaviour_scale.set_property("x_scale_start", 0.6)
                tmpTexturesGroup.behaviour_scale.set_property("y_scale_start", 0.6)
                tmpTexturesGroup.behaviour_scale.set_property("x_scale_end", 1)
                tmpTexturesGroup.behaviour_scale.set_property("y_scale_end", 1)
            else:
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_start", 0x66)
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_end", 0x66)
                
                tmpTexturesGroup.behaviour_scale.set_property("x_scale_start", 0.6)
                tmpTexturesGroup.behaviour_scale.set_property("y_scale_start", 0.6)
                tmpTexturesGroup.behaviour_scale.set_property("x_scale_end", 0.6)
                tmpTexturesGroup.behaviour_scale.set_property("y_scale_end", 0.6)


            self.ang = self.ang + self.step

        self.timeline.start()
        self.off = self.off + (self.step * step)
        if self.off > 360:
            self.off = self.off - 360
        
    def getItem(self, index):
        return self.itemGroup.get_nth_child(index)
    def get_current_item(self):
        print "Selected: " + str(self.itemGroup.get_nth_child(self.selected))
        return self.itemGroup.get_nth_child(self.selected)
    
class WheelListItem(MenuItem):

    def __init__ (self, menu, itemLabel):
        MenuItem.__init__ (self, menu, itemLabel, 0)
        self.glossMgr = menu.glossMgr