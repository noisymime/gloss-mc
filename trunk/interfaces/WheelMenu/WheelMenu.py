import clutter
import pygtk
import gtk
import pango
import time
import math
from ui_elements.ReflectionTexture import Texture_Reflection
from interfaces.MenuItem import MenuItem
from utils.InputQueue import InputQueue

class Interface(clutter.Group):
    usePreviewEffects = False # Tells the modules NOT to use any effects on the images
    itemGroup = clutter.Group()
    menu_image_rotation = 0
    
    def __init__ (self, glossMgr):
        clutter.Group.__init__(self)
        self.glossMgr = glossMgr
        self.stage = self.glossMgr.get_stage()
        self.itemGroup = clutter.Group()
        self.image_group = None
        self.setup_ui(self.glossMgr.themeMgr, "main", self)
        
        self.selected = 0
        self.off = 0
        self.is_ready = False
        self.ang = 0.0
        
        #Setup input queue controller
        self.input_queue = InputQueue()
        self.input_queue.set_action(InputQueue.NORTH, self.selectPrevious)
        self.input_queue.set_action(InputQueue.SOUTH, self.selectNext)
        
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
        tmp_frame = themeMgr.get_imageFrame("menu_item_texture")
        self.menu_image_size = int(tmp_frame.img_size)
        self.use_reflection = tmp_frame.use_reflection
        self.menu_image_x = tmp_frame.get_x()
        self.menu_image_y = tmp_frame.get_y()
        
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
        
    def on_key_press_event(self, event):
        self.input_queue.input(event)
        
    def addItem(self, itemLabel):
        if self.itemGroup.get_n_children() == 0:
            tempLabel = clutter.Label()
            tempLabel.set_font_name(self.font)
            tempLabel.set_text("S")
            self.label_height = tempLabel.get_height()
            label_width = 0
        
        newItem = WheelListItem(self, itemLabel)
        self.itemGroup.add(newItem)
        self.step = 360.0 / self.itemGroup.get_n_children()
        
        return newItem
    
    def display(self):
        self.step = 360.0 / self.itemGroup.get_n_children()
        self.add(self.itemGroup)
        
        if not self.is_ready: self.setup_behaviours()
        
        self.displayed = True
        self.selectFirst(False)
        self.stage.add(self)


        self.itemGroup.show()
        self.show()
        
    def setup_behaviours(self):
        self.timeline = clutter.Timeline(20, 60)
        self.input_queue.set_timeline(self.timeline)
        alpha_sine_inc = clutter.Alpha(self.timeline, clutter.sine_inc_func)
        (stage_width, stage_height) = self.stage.get_size()
        
        for i in range(self.itemGroup.get_n_children()):
            tmpTexturesGroup = self.itemGroup.get_nth_child(i).itemTexturesGroup
            tmpTexturesGroup.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
            tmpItem = self.itemGroup.get_nth_child(i)
            tmpItem.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
            self.add(tmpTexturesGroup)


            tmpTexturesGroup.behaviour_ellipse = clutter.BehaviourEllipse(\
                                                       #x = int(stage_width/4),\
                                                       #y = int(stage_height-stage_height/3),\
                                                       x = int(stage_width/2),\
                                                       y = int(3*stage_height/4),\
                                                       width = int(3*stage_width/4),\
                                                       height = int(stage_height-stage_height/4),\
                                                       #clutter.ROTATE_CW,\
                                                       start = self.ang,\
                                                       end = (self.ang+self.step),\
                                                       alpha = alpha_sine_inc\
                                                       )
            tmpItem.behaviour_ellipse = clutter.BehaviourEllipse(\
                                                       x = int(stage_width/2),\
                                                       y = int(3*stage_height/4),\
                                                       #x = int(stage_width*.66),\
                                                       #y = int(stage_height/2),\
                                                       width = int(3*stage_width/4),\
                                                       height = int(0),\
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
            
            tmpItem.behaviour_ellipse.apply(tmpItem)
            tmpTexturesGroup.behaviour_opacity.apply(tmpItem)
            tmpTexturesGroup.behaviour_scale.apply(tmpItem)

            self.ang = self.ang + self.step
            tmpTexturesGroup.show()
            tmpTexturesGroup.show_all()
            
        self.is_ready = True
        
    def selectFirst(self, moveBar=False):
        if not self.is_ready:
            self.setup_behaviours()
        
        for i in range(self.itemGroup.get_n_children()):
            
            ang_start = -90.0
            ang_end   = (self.step * i)

            tmpTexturesGroup = self.itemGroup.get_nth_child(i).itemTexturesGroup
            tmpItem = self.itemGroup.get_nth_child(i)
            
            tmpTexturesGroup.behaviour_ellipse.set_angle_start(ang_start)
            tmpTexturesGroup.behaviour_ellipse.set_angle_end(ang_end)
            
            tmpItem.behaviour_ellipse.set_angle_start(ang_start)
            tmpItem.behaviour_ellipse.set_angle_end(ang_end)
            
            if i == self.selected:
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_start", 0x66)
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_end", 0xff)

                tmpItem.show()
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
            tmpItem = self.itemGroup.get_nth_child(i)
            
            ang_start = self.ang
            ang_end   = self.ang + (self.step * step)
            
            #Set the rotation based on the step
            if step > 0:
                direction = clutter.ROTATE_CW
            else:
                direction= clutter.ROTATE_CCW
            tmpTexturesGroup.behaviour_ellipse.set_direction(direction)
            tmpItem.behaviour_ellipse.set_direction(direction)

            #Set the angles
            tmpTexturesGroup.behaviour_ellipse.set_angle_start(ang_start)
            tmpTexturesGroup.behaviour_ellipse.set_angle_end(ang_end)
            tmpItem.behaviour_ellipse.set_angle_start(ang_start)
            tmpItem.behaviour_ellipse.set_angle_end(ang_end)
            
            if i == from_index:
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_start", 0xff)
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_end", 0x66)
                
                tmpTexturesGroup.behaviour_scale.set_property("x_scale_start", 1)
                tmpTexturesGroup.behaviour_scale.set_property("y_scale_start", 1)
                tmpTexturesGroup.behaviour_scale.set_property("x_scale_end", 0.6)
                tmpTexturesGroup.behaviour_scale.set_property("y_scale_end", 0.6)
                
                tmpItem.hide()
                
                #Pause the image previewer (if in use)
                if tmpTexturesGroup.__class__.__name__ == "image_previewer":
                    tmpTexturesGroup.stop(None)
                    
            elif i == self.selected:
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_start", 0x66)
                tmpTexturesGroup.behaviour_opacity.set_property("opacity_end", 0xff)
                
                tmpTexturesGroup.behaviour_scale.set_property("x_scale_start", 0.6)
                tmpTexturesGroup.behaviour_scale.set_property("y_scale_start", 0.6)
                tmpTexturesGroup.behaviour_scale.set_property("x_scale_end", 1)
                tmpTexturesGroup.behaviour_scale.set_property("y_scale_end", 1)
                
                tmpItem.show()
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
        #print "Selected: " + str(self.itemGroup.get_nth_child(self.selected))
        return self.itemGroup.get_nth_child(self.selected)
    def getItemGroup(self):
        return self.itemGroup
    def get_group_y(self):
        return self.itemGroup.get_y()
        return int(self.get_current_item().get_y())
    def get_selector_bar(self):
        return None
    def undisplay(self):
        pass
    
class WheelListItem(MenuItem):

    def __init__ (self, menu, itemLabel):
        MenuItem.__init__ (self, menu, itemLabel)
        self.glossMgr = menu.glossMgr