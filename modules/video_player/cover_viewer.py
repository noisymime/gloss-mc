import pygtk
import gtk
import pygst
import gst
import gobject
import pango
import clutter
import os
from modules.video_player.CoverItem import cover_item

class coverViewer(clutter.Group):
    scaleFactor = 1.4
    inactiveOpacity = 150
    backgroundImg = "ui/cover_bg_long.png"
    covers_size_percent = 0.90 #This is the percentage of the total group size that the covers will take
    detailBox_height = 160 #Needs a percent
    
    

    def __init__(self, stage, width, height, rows, columns):
        clutter.Group.__init__(self)
        self.stage = stage
        self.videoLibrary = []
        self.textureLibrary = []
        self.folderLibrary = []
        self.covers_group = clutter.Group()
        self.covers_width = int(width * self.covers_size_percent)
        self.covers_height = int(height * self.covers_size_percent)
        self.current_video_details = video_details_group(self.covers_width)
        self.num_covers = 0
        self.cover_gap = 1
        
        self.num_visible_rows = rows
        self.num_columns = columns
        self.cover_size = int(self.covers_width / self.num_columns) #A cover will be cover_size * cover_size (X * Y)
        
        #Add the background
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.backgroundImg)
        self.bgImg = clutter.Texture()
        self.bgImg.set_pixbuf(pixbuf)
        bgImg_height = height - ((height - (self.cover_size * rows)) / 2) + self.detailBox_height
        self.bgImg.set_size(width, bgImg_height)
        self.bgImg.show()
        self.add(self.bgImg)
        
        
        #Setup the current min and max viewable rows
        self.min_visible_rows = 0
        self.max_visible_rows = self.num_visible_rows
        
        self.currentSelection = 0
        
        self.add(self.covers_group)
        covers_x = int(width * (1-self.covers_size_percent)/2)
        covers_y = int(height * (1-self.covers_size_percent)/2)
        self.covers_group.set_position(covers_x, covers_y)
        self.covers_group.show()
        
        #self.stage.add(self.current_video_description)
        self.current_video_details.show()
        self.current_video_details.show_all()
        
            
    #Turns the description group off and on
    def toggle_details(self):
        if self.current_video_details.get_parent() == None:
            self.add(self.current_video_details)
            #Set the position of the details group
            (pos_x, pos_y) = self.get_abs_position()
            #The next two lines are horribly ugly, but all they do is position the details viewer in the middle of the gap between the bottom of the visible cover viewer and the bottom of the stage
            viewer_lower_y = int(pos_y + (self.max_visible_rows * self.cover_size))
            pos_y = viewer_lower_y# + int( (self.stage.get_height() - viewer_lower_y) / 2 - int(self.current_video_details.get_height()/2))
            self.current_video_details.set_position(20, pos_y)
        else:
            self.stage.remove(self.current_video_details)
        
    def add_video(self, video):
        #Quick snaity check to make sure the cover file exists.
        # In the future this will change so that the video is still included with a blank image
        if not os.path.exists(video.getCoverfile()):
            return
        
        self.videoLibrary.append(video)
        tempTexture = cover_item(video, None, self.cover_size)
        self.add_texture_group(tempTexture)
    
    def add_folder(self, folder_name):
        tempTexture = cover_item(None, folder_name, self.cover_size)
        self.folderLibrary.append(folder_name)
        self.add_texture_group(tempTexture)
        
    def add_texture_group(self, tempGroup):
        tempGroup.set_opacity(self.inactiveOpacity)
        
        tempGroup.set_position( (self.num_covers * self.cover_size), 0)
        tempGroup.set_depth(1)
        
        self.textureLibrary.append(tempGroup)

        x = (self.num_covers % self.num_columns) * self.cover_size + ( (self.num_covers % self.num_columns) * self.cover_gap)
        y = (self.cover_gap + self.cover_size) * (self.num_covers/self.num_columns)
        
        tempGroup.set_position(x, y)
        
        #If we're past the maximum rows, make the pics invistible
        if self.num_covers > (self.num_columns * self.num_visible_rows)-1:
            tempGroup.set_opacity(0)
        else:
            self.covers_group.add(tempGroup)
        
        tempGroup.show()
        self.num_covers = self.num_covers +1
            
        
    def select_item(self, incomingItem, outgoingItem):
        self.timeline = clutter.Timeline(10,35)
        numFolders = len(self.folderLibrary)
        if incomingItem >= numFolders:
            incomingItemVideo = incomingItem - numFolders
            self.current_video_details.set_video(self.videoLibrary[incomingItemVideo], self.timeline)
        
        #Check if the cover is currently not visible
        rolling = False
        if incomingItem > (self.num_columns * self.max_visible_rows-1):
            self.rollViewer(True, self.timeline)
            rolling = True
        if incomingItem < (self.num_columns * self.min_visible_rows):
            self.rollViewer(False, self.timeline)
            rolling = True
    
        outgoingTexture = self.textureLibrary[outgoingItem]
        incomingTexture = self.textureLibrary[incomingItem]
        
        alpha = clutter.Alpha(self.timeline, clutter.smoothstep_inc_func)# clutter.ramp_inc_func)
        self.behaviourNew_scale = clutter.BehaviourScale(alpha, 1, self.scaleFactor, clutter.GRAVITY_CENTER)
        self.behaviourNew_z = clutter.BehaviourDepth(alpha, 1, 2)
        #If we're performing a roll (See above) then the incoming opacity should start at 0 rather than the normal inactive opacity
        if rolling:
            self.behaviourNew_opacity = clutter.BehaviourOpacity(alpha, 0, 255)
        else:
            self.behaviourNew_opacity = clutter.BehaviourOpacity(alpha, self.inactiveOpacity, 255)
        
        self.behaviourOld_scale = clutter.BehaviourScale(alpha, self.scaleFactor, 1, clutter.GRAVITY_CENTER)
        self.behaviourOld_z = clutter.BehaviourDepth(alpha, 2, 1)
        self.behaviourOld_opacity = clutter.BehaviourOpacity(alpha, 255, self.inactiveOpacity)
        
        self.behaviourNew_scale.apply(incomingTexture)
        self.behaviourNew_z.apply(incomingTexture)
        self.behaviourNew_opacity.apply(incomingTexture)
        self.behaviourOld_scale.apply(outgoingTexture)
        self.behaviourOld_z.apply(outgoingTexture)
        self.behaviourOld_opacity.apply(outgoingTexture)
        
        self.currentSelection = incomingItem
        
        self.timeline.start()
        
    def select_first(self):      
        self.timeline = clutter.Timeline(20,80)
        if not len(self.folderLibrary) == 0:
            pass
        else:
            self.current_video_details.set_video(self.videoLibrary[0], self.timeline)

    
        incomingItem = 0
        incomingTexture = self.textureLibrary[incomingItem]
        
        alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.behaviourNew_scale = clutter.BehaviourScale(alpha, 1, self.scaleFactor, clutter.GRAVITY_CENTER)
        self.behaviourNew_z = clutter.BehaviourDepth(alpha, 1, 2)
        self.behaviourNew_opacity = clutter.BehaviourOpacity(alpha, self.inactiveOpacity, 255)
        
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
                
        self.behaviourOld_scale = clutter.BehaviourScale(alpha, self.scaleFactor, 1, clutter.GRAVITY_CENTER)
        self.behaviourOld_z = clutter.BehaviourDepth(alpha, 2, 1)
        self.behaviourOld_opacity = clutter.BehaviourOpacity(alpha, 255, self.inactiveOpacity)
        self.behaviourOldDetails_opacity = clutter.BehaviourOpacity(alpha, 255, 0)
        
        current_cover = self.textureLibrary[self.currentSelection]
        self.behaviourOld_scale.apply(current_cover)
        self.behaviourOld_z.apply(current_cover)
        self.behaviourOld_opacity.apply(current_cover)
        self.behaviourOldDetails_opacity.apply(self.current_video_details)
        
        self.timeline.start()
        
    #This moves the visible row of covers up and down
    # moveUp: True if the covers are to come up, false if they're to go down
    def rollViewer(self, moveUp, timeline):
        if moveUp:
            new_y = self.covers_group.get_y() - self.cover_size
            self.max_visible_rows = self.max_visible_rows + 1
            self.min_visible_rows = self.min_visible_rows + 1
            
            #Define the row of covers that now needs to disapear / appear
            min_outgoing = (self.min_visible_rows-1) * self.num_columns
            max_outgoing = min_outgoing + self.num_columns
            min_incoming = (self.max_visible_rows-1) * self.num_columns
            max_incoming = min_incoming + self.num_columns
            
            #Quick check to make sure that max_incoming isn't greater than the max number of images (This occurs when the final row is incomplete)
            if max_incoming > self.num_covers:
                max_incoming = min_incoming + (self.num_covers % self.num_columns)
        else:
            new_y = self.covers_group.get_y() + self.cover_size
            self.max_visible_rows = self.max_visible_rows - 1
            self.min_visible_rows = self.min_visible_rows - 1

            #Define the row of covers that now needs to disapear / appear
            min_incoming = (self.min_visible_rows) * self.num_columns
            max_incoming = min_incoming + self.num_columns
            min_outgoing = (self.max_visible_rows) * self.num_columns
            max_outgoing = min_outgoing + self.num_columns   
            
            #Quick check to make sure that max_outgoing isn't greater than the max number of images (This occurs when the final row is incomplete)
            if max_outgoing > self.num_covers:
                max_outgoing = min_outgoing + (self.num_covers % self.num_columns)         
        
        #Need to add the new row to the group
        self.addIncomingRow(min_incoming, max_incoming)
        #And set the outgoing row to remove after the timeline finishes
        self.timeline.connect('completed', self.removeOutgoingRow, min_outgoing, max_outgoing)
        
        
        knots = (\
                (self.covers_group.get_x(), self.covers_group.get_y()),\
                (self.covers_group.get_x(), new_y) \
                )
        
        alpha = clutter.Alpha(timeline, clutter.ramp_inc_func)
        self.behaviour_path = clutter.BehaviourPath(alpha, knots)
        self.behaviour_incoming = clutter.BehaviourOpacity(alpha, 0, self.inactiveOpacity)
        self.behaviour_outgoing = clutter.BehaviourOpacity(alpha, self.inactiveOpacity, 0)
        
        self.behaviour_path.apply(self.covers_group)
        #Also need to change a few opacities - This is really messy, but works
        for i in range(min_outgoing, max_outgoing):
            self.behaviour_outgoing.apply(self.textureLibrary[i])
        for i in range(min_incoming, max_incoming):
            self.behaviour_incoming.apply(self.textureLibrary[i])
    
    #These next two functions add and remove visible rows when the viewer rolls        
    def removeOutgoingRow(self, timeline, min, max):
        for i in range(min, max):
            self.covers_group.remove(self.textureLibrary[i])
            
    def addIncomingRow(self, min, max):
        for i in range(min, max):
            self.covers_group.add(self.textureLibrary[i])
            self.textureLibrary[i].show()
    
    def get_current_item(self):
        return self.textureLibrary[self.currentSelection]
        #If the current item # is greater than the number of folders, we have a video
        """
        if self.currentSelection >= len(self.folderLibrary):
            selection = self.currentSelection - len(self.folderLibrary)
            return self.videoLibrary[selection]
        else:
            return self.folderLibrary[self.currentSelection]
        """
        
    def get_item_x(self, itemNo):
        return self.textureLibrary[itemNo]
    
    def get_item_library(self):
        return self.textureLibrary
        
    def on_key_press_event(self, event):
        newItem = None
        if event.keyval == clutter.keysyms.Left:
            #Make sure we're not already on the first cover
            if not self.currentSelection == 0:
                newItem = self.currentSelection - 1      
        elif event.keyval == clutter.keysyms.Right:
            #This check makes sure that we're not on the last cover already
            if not self.currentSelection == (self.num_covers-1):
                newItem = self.currentSelection + 1
        elif event.keyval == clutter.keysyms.Down:
            #Check if we're already on the bottom row
            if not (self.currentSelection > (len(self.textureLibrary)-1 - self.num_columns)):
                newItem = self.currentSelection + self.num_columns
        elif event.keyval == clutter.keysyms.Up:
            #Check if we're already on the top row
            if not (self.currentSelection < self.num_columns):
                newItem = self.currentSelection - self.num_columns
        
        #Final sanity check
        if (newItem < 0) and (not newItem == None):
            newItem = self.currentSelection

        #If there is movement, make the scale happen
        if not newItem == None:
            self.select_item(newItem, self.currentSelection)
        
class video_details_group(clutter.Group):
    font = "Lucida Grande "
    title_font_size = 30
    main_font_size = 22
    plot_font_size = 18
    backgroundImg = "ui/vid_details_bg.png"

    def __init__(self, desired_width):
        clutter.Group.__init__(self)
        self.width = desired_width
        
        """
        self.bgImg = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.backgroundImg)
        self.bgImg.set_pixbuf(pixbuf)
        yx_ratio = float(self.bgImg.get_height()) / float(self.bgImg.get_width())
        bg_height = int(desired_width * yx_ratio)
        self.bgImg.set_size(desired_width, bg_height)
        #self.bgImg.set_opacity(200)
        self.bgImg.show()
        self.add(self.bgImg)
        """
        
        #Add the various labels
        self.title = clutter.Label()
        self.title.set_font_name(self.font + str(self.title_font_size))
        self.title.set_color(clutter.color_parse('White'))
        self.title.set_text("")
        self.title.set_ellipsize(pango.ELLIPSIZE_END)
        self.add(self.title)
        
        #Not sure how to get the row height before the text is set :(
        self.row_gap = self.title.get_height()
        
        self.year = clutter.Label()
        self.year.set_font_name(self.font + str(self.main_font_size))
        self.year.set_color(clutter.color_parse('White'))
        self.year.set_text("")
        self.year.set_opacity(220)
        self.year.set_ellipsize(pango.ELLIPSIZE_END)
        self.year.set_position(0, self.row_gap)
        self.add(self.year)
        
        self.director = clutter.Label()
        self.director.set_font_name(self.font + str(self.main_font_size))
        self.director.set_color(clutter.color_parse('White'))
        self.director.set_text("")
        self.director.set_opacity(220)
        self.director.set_ellipsize(pango.ELLIPSIZE_END)
        self.director.set_position(int(self.year.get_width()), self.row_gap)
        self.add(self.director)
        
        self.plot = clutter.Label()
        self.plot.set_font_name(self.font + str(self.plot_font_size))
        self.plot.set_color(clutter.color_parse('White'))
        self.plot.set_text("")
        self.plot.set_opacity(220)
        #self.plot.set_ellipsize(pango.ELLIPSIZE_END)
        self.plot.set_position(0, int(self.row_gap*2))
        self.add(self.plot)
        
        self.show_all()

    def set_video_bare(self,video):
        self.timeline = clutter.Timeline(10,45)
        self.set_video(video, self.timeline)

    def set_video(self, video, timeline):
        self.video = video
        
        self.title.set_text(video.title)
        self.title.set_width(self.width)
        
        self.year.set_text("Year: " + str(video.year))
        
        self.director.set_text("  Director: " + str(video.director))
        self.director.set_position(int(self.year.get_width()), self.row_gap)
        self.director.set_width(int(self.width - self.year.get_width()))
        
        self.plot.set_text(video.plot)
        self.plot.set_width(self.width)