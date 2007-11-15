import pygtk
import gtk
import pygst
import gst
import gobject
import pango
import clutter
from clutter import cluttergst
from VideoController import VideoController

class VideoPlayer():

    def __init__(self, stage, dbMgr):
        self.stage = stage
        self.cover_viewer = coverViewer(self.stage, 800, 600)
        self.videoController = VideoController(stage)
        self.is_playing = False
        
        #This block can be moved to begin() but causes a performance hit when loading the module *shrug*
        results = dbMgr.get_videos()
        if results == None:
            print "VideoPlayer: No connection to DB or no videos found in DB"
            return None
        #Load the videos into the cover viewer
        for record in results:
            tempVideo = videoItem()
            tempVideo.importFromMythObject(record)
            self.cover_viewer.add_video(tempVideo)
            
        
            
    def on_key_press_event (self, stage, event):
        if self.is_playing:
            if event.keyval == clutter.keysyms.Escape:
                self.videoController.stop_video()
                self.is_playing = False
            else:
                self.videoController.on_key_press_event(event)
            
            return False
    
        if event.keyval == clutter.keysyms.p:
            if self.paused:
                self.unpause()
            else:
                self.pause()
        if event.keyval == clutter.keysyms.q:
            clutter.main_quit()
            
        up = clutter.keysyms.Up
        down = clutter.keysyms.Down
        left = clutter.keysyms.Left
        right= clutter.keysyms.Right
        if (event.keyval == up) or (event.keyval == down) or (event.keyval == left) or (event.keyval == right):
            self.cover_viewer.on_key_press_event(event)
        
        if event.keyval == clutter.keysyms.Return:
            self.play_video()
            
        if event.keyval == clutter.keysyms.Escape:
            return True
        
            
        
        
    def begin(self, MenuMgr):
       
        #Create a backdrop for the player. In this case we just use the same background as the menus
        self.backdrop = clutter.CloneTexture(MenuMgr.get_skinMgr().get_Background())
        self.backdrop.set_size(self.stage.get_width(), self.stage.get_height())
        self.backdrop.set_opacity(0)
        self.backdrop.show()
        self.stage.add(self.backdrop)
        #Fade the backdrop in
        timeline_begin = clutter.Timeline(10,40)
        alpha = clutter.Alpha(timeline_begin, clutter.ramp_inc_func)
        self.begin_behaviour = clutter.BehaviourOpacity(alpha, 0, 255)
        self.begin_behaviour.apply(self.backdrop)

        self.cover_viewer.set_opacity(0)    
        self.cover_viewer.show_all()
        self.cover_viewer.show()
        self.stage.add(self.cover_viewer)
        cover_x = self.stage.get_width() - self.cover_viewer.get_width()
        #self.cover_viewer.set_position(cover_x, 40)
        self.cover_viewer.set_position(50, 40)
        self.cover_viewer.toggle_details() #Turns the details group on
        self.cover_viewer.select_first()
        self.begin_behaviour.apply(self.cover_viewer)
        
        timeline_begin.start()
        
    def stop(self):
           
        #Fade everything out
        timeline_stop = clutter.Timeline(10,30)
        alpha = clutter.Alpha(timeline_stop, clutter.ramp_inc_func)
        self.stop_behaviour = clutter.BehaviourOpacity(alpha, 255, 0)
        self.stop_behaviour.apply(self.cover_viewer)
        self.stop_behaviour.apply(self.backdrop)
        timeline_stop.connect('completed', self.destroyPlugin)
        timeline_stop.start()
    
    def destroyPlugin(self, data):
        self.stage.remove(self.cover_viewer)
        self.backdrop.hide()
        #self.stage.remove(self.overlay)
    
    def play_video(self):
        vid = self.cover_viewer.get_current_video()
        uri = "file://" + str(vid.filename)
        self.videoController.play_video(uri, self)
        self.is_playing = True
        
        self.stage.remove(self.cover_viewer)
        
    def stop_video(self):
        if not self.is_playing:
            return
        
        self.is_playing = False
        
    def pause(self):
        pass
        
    def unpause(self):
        pass
        
class videoItem():
    def __init(self):
        self.mythID = None
        
    def importFromMythObject(self, mythObject):
        self.mythID = mythObject[0]
        self.title = mythObject[1]
        self.director = mythObject[2]
        self.plot = mythObject[3]
        self.rating = mythObject[4]
        self.inetRef = mythObject[5]
        self.year = mythObject[6]
        self.userRating = mythObject[7]
        self.length = mythObject[8]
        self.showLevel = mythObject[9]
        self.filename = mythObject[10]
        self.coverfile = mythObject[11]
        self.childID = mythObject[12]
        self.browse = mythObject[13]
        self.playCommand = mythObject[14]
        self.category = mythObject[15]
        
    def getTitle(self):
        return self.title
    def getCoverfile(self):
        return self.coverfile        
        
class coverViewer(clutter.Group):
    scaleFactor = 1.4
    inactiveOpacity = 150

    def __init__(self, stage, width, height):
        clutter.Group.__init__(self)
        self.stage = stage
        self.videoLibrary = []
        self.textureLibrary = []
        self.current_video_details = video_details_group(width)
        self.covers_group = clutter.Group()
        self.num_covers = 0
        
        self.cover_gap = 1
        
        self.num_visible_rows = 3
        self.num_columns = 4
        self.cover_size = int(width / self.num_columns) #200 #A cover will be cover_size * cover_size (X * Y)
        
        #Setup the current min and max viewable rows
        self.min_visible_rows = 0
        self.max_visible_rows = self.num_visible_rows
        
        self.currentSelection = 0
        
        self.add(self.covers_group)
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
        self.videoLibrary.append(video)
        imagePath = video.getCoverfile()
        tempTexture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(imagePath)
        tempTexture.set_pixbuf(pixbuf)
        xy_ratio = float(tempTexture.get_width()) / tempTexture.get_height()
        
        width = int(self.cover_size * xy_ratio)
        tempTexture.set_width(width)
        tempTexture.set_height(self.cover_size)
        tempTexture.set_opacity(self.inactiveOpacity)
        
        tempTexture.set_position( (self.num_covers * self.cover_size), 0)
        tempTexture.set_depth(1)
        
        self.textureLibrary.append(tempTexture)

        #x = (self.cover_gap + self.cover_size) * (self.num_covers/self.num_rows)
        #y = (self.num_covers % self.num_rows) * self.cover_size + ( (self.num_covers % self.num_rows) * self.cover_gap)
        x = (self.num_covers % self.num_columns) * self.cover_size + ( (self.num_covers % self.num_columns) * self.cover_gap)
        y = (self.cover_gap + self.cover_size) * (self.num_covers/self.num_columns)
        
        #Center the cover
        if width < self.cover_size:
            x = x + (self.cover_size - width)/2
        
        tempTexture.set_position(x, y)
        
        #If we're past the maximum rows, make the pics invistible
        if self.num_covers > (self.num_columns * self.num_visible_rows)-1:
            tempTexture.set_opacity(0)
        else:
            self.covers_group.add(tempTexture)
        
        tempTexture.show()
        self.num_covers = self.num_covers +1
        
    def select_item(self, incomingItem, outgoingItem):
        self.timeline = clutter.Timeline(10,35)
        self.current_video_details.set_video(self.videoLibrary[incomingItem], self.timeline)
        
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
            
    def removeOutgoingRow(self, timeline, min, max):
        for i in range(min, max):
            self.covers_group.remove(self.textureLibrary[i])
            
    def addIncomingRow(self, min, max):
        for i in range(min, max):
            self.covers_group.add(self.textureLibrary[i])
            
            xy_ratio = float(self.textureLibrary[i].get_width()) / self.textureLibrary[i].get_height()
            width = int(self.cover_size * xy_ratio)
            
            x = (i % self.num_columns) * self.cover_size + ( (i % self.num_columns) * self.cover_gap)
            y = (self.cover_gap + self.cover_size) * (i/self.num_columns)
        
            #Center the cover
            if width < self.cover_size:
                x = x + (self.cover_size - width)/2
        
            self.textureLibrary[i].set_position(x, y)
            self.textureLibrary[i].show()
    
    def get_current_video(self):
        return self.videoLibrary[self.currentSelection]
        
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

    def __init__(self, desired_width):
        clutter.Group.__init__(self)
        self.width = desired_width
        
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
