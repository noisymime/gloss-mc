import pygtk
import gtk
import pygst
import gst
import gobject
import pango
import clutter
import os
from modules.video_player.elements.CoverItem import cover_item
from InputQueue import InputQueue

class ImageRow(clutter.Group):
    DIRECTION_LEFT, DIRECTION_RIGHT = range(2)
    
    scaleFactor = 1.4
    inactiveOpacity = 150
    images_size_percent = 0.90 #This is the percentage of the total group size that the covers will take
    

    def __init__(self, glossMgr, width, height, columns):
        clutter.Group.__init__(self)
        self.glossMgr = glossMgr
        self.stage = glossMgr.stage
        self.textureLibrary = []
        
        self.images_group = clutter.Group()
        self.images_width = int(width * self.images_size_percent)
        self.images_height = int(height * self.images_size_percent)
        
        self.num_columns = columns
        self.image_size = int(self.images_width / self.num_columns) #A cover will be cover_size * cover_size (X * Y)
        
        
        #The viewer actually sits within another group that clips its size
        self.images_group_clip = clutter.Group()
        self.images_group_clip.add(self.images_group)
        #Nasty hack to get around centering problem
        self.images_group.set_position(int(self.image_size/2), int(self.image_size/2))
        #And setup the clip size and position
        scale_amount = int(self.image_size * self.scaleFactor - self.image_size)
        clip_width = (self.image_size*columns) + scale_amount #Width is the cover size by the number of colums, plus the additional amount required for scaling
        clip_height = (height) + scale_amount
        self.images_group_clip.set_clip(-(scale_amount/2), -(scale_amount/2), clip_width, clip_height)
        
        
        #self.current_video_details = video_details_group(self.covers_width)
        self.num_images = 0
        self.image_gap = 1
        
        
        #Setup input queue controller
        self.input_queue = InputQueue()
        self.input_queue.set_action(InputQueue.EAST, self.move_right)
        self.input_queue.set_action(InputQueue.WEST, self.move_left)
        
        
        #Setup the current min and max viewable rows
        self.min_visible_columns = 0
        self.max_visible_columns = columns
        
        self.currentSelection = 0
        
        self.add(self.images_group_clip)
        covers_x = int(width * (1-self.images_size_percent)/2)
        covers_y = int(height * (1-self.images_size_percent)/2)
        #self.images_group.set_position(covers_x, covers_y)
        #self.images_group.set_depth(1) #self.image_size)
        self.images_group.show()
        self.images_group_clip.show()
        
        
    def add_texture_group(self, tempGroup):
        tempGroup.set_opacity(self.inactiveOpacity)
        
        #tempGroup.set_position( (self.num_covers * self.image_size), 0)
        tempGroup.set_depth(1)
        
        self.textureLibrary.append(tempGroup)

        x = self.num_images * self.image_size + ( self.num_images * self.image_gap)
        y = 0#(self.cover_gap + self.image_size) * (self.num_covers/self.num_columns)
        
        tempGroup.set_position(x, y)
        
        #If we're past the maximum rows, make the pics invistible
        if self.num_images > (self.num_columns-1):
            tempGroup.set_opacity(0)
        else:
            self.images_group.add(tempGroup)
        
        tempGroup.show()
        self.num_images += 1
            
        
    def select_item(self, incomingItem, outgoingItem):
        self.timeline = clutter.Timeline(10,35)
        self.input_queue.set_timeline(self.timeline)
        
        #Check if the cover is currently not visible
        rolling = False
        if incomingItem > (self.max_visible_columns-1):
            self.rollViewer(self.DIRECTION_LEFT, self.timeline)
            rolling = True
        if incomingItem < (self.min_visible_columns):
            self.rollViewer(self.DIRECTION_RIGHT, self.timeline)
            rolling = True
    
        outgoingTexture = self.textureLibrary[outgoingItem]
        incomingTexture = self.textureLibrary[incomingItem]
        
        alpha = clutter.Alpha(self.timeline, clutter.smoothstep_inc_func)# clutter.ramp_inc_func)
        self.behaviourNew_scale = clutter.BehaviourScale(x_scale_start=1, y_scale_start=1, x_scale_end=self.scaleFactor, y_scale_end=self.scaleFactor, alpha=alpha) #clutter.GRAVITY_CENTER)
        self.behaviourNew_z = clutter.BehaviourDepth(depth_start=1, depth_end=2, alpha=alpha)
        #If we're performing a roll (See above) then the incoming opacity should start at 0 rather than the normal inactive opacity
        if rolling:
            self.behaviourNew_opacity = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=alpha)
        else:
            self.behaviourNew_opacity = clutter.BehaviourOpacity(opacity_start=self.inactiveOpacity, opacity_end=255, alpha=alpha)
        
        self.behaviourOld_scale = clutter.BehaviourScale(x_scale_start=self.scaleFactor, y_scale_start=self.scaleFactor, x_scale_end=1, y_scale_end=1, alpha=alpha)
        self.behaviourOld_z = clutter.BehaviourDepth(depth_start=2, depth_end=1, alpha=alpha)
        self.behaviourOld_opacity = clutter.BehaviourOpacity(opacity_start=255, opacity_end=self.inactiveOpacity, alpha=alpha)
        
        (x, y) = incomingTexture.get_position()
        (x, y) = self.images_group.get_position()
        anchor_x = incomingTexture.get_width()/2
        anchor_y = incomingTexture.get_height()/2
        #self.images_group.set_anchor_point(anchor_x, anchor_y)
        #incomingTexture.set_anchor_point(anchor_x, anchor_y)
        
        self.behaviourNew_scale.apply(incomingTexture)
        self.behaviourNew_z.apply(incomingTexture)
        self.behaviourNew_opacity.apply(incomingTexture)
        self.behaviourOld_scale.apply(outgoingTexture)
        self.behaviourOld_z.apply(outgoingTexture)
        self.behaviourOld_opacity.apply(outgoingTexture)
        
        #Set gravities
        
        
        (x, y) = outgoingTexture.get_position()
        anchor_x = outgoingTexture.get_width()/2
        anchor_y = outgoingTexture.get_height()/2
        #outgoingTexture.set_anchor_point(anchor_x, anchor_y)
        #incomingTexture.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
        #outgoingTexture.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
        
        
        self.currentSelection = incomingItem
        
        self.timeline.start()
        
    def select_first(self):      
        self.timeline = clutter.Timeline(20,80)
        self.input_queue.set_timeline(self.timeline)
        """
        if not len(self.folderLibrary) == 0:
            pass
        else:
            self.current_video_details.set_video(self.videoLibrary[0], self.timeline)
        """
    
        incomingItem = 0
        incomingTexture = self.textureLibrary[incomingItem]
        
        alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        #self.behaviourNew_scale = clutter.BehaviourScale(scale_start=1, scale_end=self.scaleFactor, alpha=alpha)
        self.behaviourNew_scale = clutter.BehaviourScale(x_scale_start=1, y_scale_start=1, x_scale_end=self.scaleFactor, y_scale_end=self.scaleFactor, alpha=alpha)
        self.behaviourNew_z = clutter.BehaviourDepth(depth_start=1, depth_end=2, alpha=alpha)
        self.behaviourNew_opacity = clutter.BehaviourOpacity(opacity_start=self.inactiveOpacity, opacity_end=255, alpha=alpha)
        
        self.behaviourNew_scale.apply(incomingTexture)
        self.behaviourNew_z.apply(incomingTexture)
        self.behaviourNew_opacity.apply(incomingTexture)
        
        self.currentSelection = incomingItem
        self.timeline.start()
        
    def select_none(self):
        if self.currentSelection is None:
            return
        
        self.timeline = clutter.Timeline(10,35)
        alpha = clutter.Alpha(self.timeline, clutter.smoothstep_inc_func)        
                
        self.behaviourOld_scale = clutter.BehaviourScale(x_scale_start=self.scaleFactor, y_scale_start=self.scaleFactor, x_scale_end=1, y_scale_end=1, alpha=alpha)
        self.behaviourOld_z = clutter.BehaviourDepth(depth_start=2, depth_end=1, alpha=alpha)
        self.behaviourOld_opacity = clutter.BehaviourOpacity(opacity_start=255, opacity_end=self.inactiveOpacity, alpha=alpha)
        
        current_cover = self.textureLibrary[self.currentSelection]
        self.behaviourOld_scale.apply(current_cover)
        self.behaviourOld_z.apply(current_cover)
        self.behaviourOld_opacity.apply(current_cover)
        
        self.timeline.start()
        
    #This moves the visible row of covers left and right
    def rollViewer(self, direction, timeline):
        if direction == self.DIRECTION_LEFT:
            new_y = self.images_group.get_y() - self.image_size
            self.max_visible_column += 1
            self.min_visible_column += 1
            
            #Define the row of image that now needs to disapear / appear
            outgoing = self.min_visible_column - 1
            incoming = self.max_visible_column - 1
            
            #Quick check to make sure that max_incoming isn't greater than the max number of images (This occurs when the final row is incomplete)
            if incoming > self.num_covers:
                return None
            
        elif direction == self.DIRECTION_RIGHT:
            new_y = self.images_group.get_y() + self.image_size
            self.max_visible_column -= 1
            self.min_visible_column -= 1

            #Define the row of covers that now needs to disapear / appear
            outgoing = self.min_visible_column + 1
            incoming = self.max_visible_column + 1 
            
            #Quick check to make sure that max_outgoing isn't greater than the max number of images (This occurs when the final row is incomplete)
            if outgoing > self.num_images:
                return None         
        
        #Need to add the new image to the group
        self.images_group.add(self.textureLibrary[incoming])
        #And set the outgoing row to remove after the timeline finishes
        self.timeline.connect('completed', self.removeItem, outgoing)
        
        
        knots = (\
                (self.images_group.get_x(), self.images_group.get_y()),\
                (self.images_group.get_x(), new_y) \
                )
        
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.behaviour_path = clutter.BehaviourPath(alpha, knots)
        self.behaviour_incoming = clutter.BehaviourOpacity(opacity_start=0, opacity_end=self.inactiveOpacity, alpha=alpha)
        self.behaviour_outgoing = clutter.BehaviourOpacity(opacity_start=self.inactiveOpacity, opacity_end=0, alpha=alpha)
        
        self.behaviour_path.apply(self.images_group)
        self.behaviour_outgoing.apply(self.textureLibrary[incoming])
        self.behaviour_incoming.apply(self.textureLibrary[outgoing])
        
    def remove_item(self, itemNo):
        self.images_group.remove(self.textureLibrary[itemNo])
    

    def get_current_texture(self):
        return self.textureLibrary[self.currentSelection]
    
    def get_current_item(self):
        return self.itemLibrary[(self.currentSelection-len(self.folderLibrary))]
    
    #Was get_item_x()
    def get_texture_x(self, itemNo):
        return self.textureLibrary[itemNo]
    
    def get_item_library(self):
        return self.textureLibrary
    
    def set_details_update(self, on_off, details):
        self.update_details = on_off
        self.details_group = details
        
    def on_key_press_event(self, event):
        self.input_queue.input(event)
        return self.timeline
        
            
    #These are the basic movement functions
    def move_left(self):
        #Make sure we're not already on the first cover
        if not self.currentSelection == 0:
            newItem = self.currentSelection - 1 
            self.move_common(newItem)
    def move_right(self):
        #This check makes sure that we're not on the last cover already
        if not self.currentSelection == (self.num_covers-1):
            newItem = self.currentSelection + 1
            self.move_common(newItem)
    def move_common(self, newItem):
        #Final sanity check
        if (newItem < 0) and (not newItem == None):
            newItem = self.currentSelection

        #If there is movement, make the scale happen
        if not newItem == None:
            self.select_item(newItem, self.currentSelection)