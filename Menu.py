import clutter
import pygtk
import gtk
import time
from ReflectionTexture import Texture_Reflection

class Menu:
    item_gap = 10 #Distance between items
    
    def __init__ (self, menuMgr):
        self.menuMgr = menuMgr
        self.stage = self.menuMgr.get_stage()
        self.menuItems = []
        self.selected = 0
        self.displayPosition = (0, 0)
        self.itemGroup = clutter.Group()
        self.menuGroup = clutter.Group()
        self.stage.add(self.itemGroup)
        self.stage.add(self.menuGroup)
        #self.hasTimeline = False
        self.timeline = clutter.Timeline(15, 75) #This timeline is used on any movements that occur when changing items
        self.timeline_completed=True
        self.menuMgr.addMenu(self)
        #self.itemGroup.hide_all()
    
    def addItem(self, itemLabel, imagePath):
        if len(self.menuItems) == 0:
            label_height = 0
            label_width = 0
        else:
            (label_width, label_height) = self.menuItems[0].get_size()
            
        label_y = label_height * len(self.menuItems)+self.item_gap
        
        newItem = ListItem(self, itemLabel, label_y, imagePath)
        self.menuItems.append(newItem)
        self.itemGroup.add(newItem)
        
        group_x = self.itemGroup.get_x()
        group_y = self.itemGroup.get_y() - (label_height)
        self.itemGroup.set_position(group_x, group_y) 
        
        return newItem
        
    def getItem(self, index):
        return self.menuItems[index]
    def getStage(self):
        return self.stage
    def getMenuMgr(self):
        return self.menuMgr
        
    def setMenuPositionByName(self, location):
        if location == "center":
            menu_y = (self.stage.get_height()-self.itemGroup.get_height())/2
            menu_x = (self.stage.get_width()-self.itemGroup.get_width())/2
            self.itemGroup.set_position(menu_x, menu_y)
            self.displayPosition = (menu_x, menu_y)
            print "Original Group size: " + str(self.itemGroup.get_width())
            print "Starting at : " + str(menu_x) + ":" + str(menu_y)
    
    #The display position is the x, y coords of where the menu is when it is active
    def get_display_position(self):
        return self.displayPosition
        
    def setMenuPosition(self, x, y):
        self.itemGroup.set_position(x,y)
        
    def getItemGroup(self):
        return self.itemGroup
        
    def getMenuGroup(self):
        return self.menuGroup
        
    def setListFont(self, newFont):
        currentY= 0 #self.itemGroup.get_y()
        self.font = newFont
        for li in self.menuItems:
            x = li.get_x()
            #y = li.getPositionY()
            li.set_font_name(newFont)
            li.set_position(x,currentY)
            currentY = currentY + li.get_height()
    
    #Returns the newly selected item
    def selectNext(self):
        
        #Initially check whether the last animation is still going           
        if self.timeline.is_playing():
            self.timeline.set_speed(1000) # Nasty hack to make sure the timeline finishes
            
    
        self.timeline = clutter.Timeline (15,85)
        #Check if we're at the last item in the list
        if (self.selected) != (len(self.menuItems)-1):
            self.selected = self.selected+1
 
            self.menuItems[self.selected].scaleLabel(0, self.timeline)
            self.menuItems[self.selected-1].scaleLabel(1, self.timeline)
            if (self.selected >= 2):
                self.menuItems[self.selected-2].scaleLabel(2, self.timeline)
            #Finally move the selection bar
            self.menuMgr.get_selector_bar().selectItem(self.menuItems[self.selected], self.timeline)
            
        if self.selected != (len(self.menuItems)-1):
            self.menuItems[self.selected+1].scaleLabel(1, self.timeline)
        
        self.timeline.start()
        
    #Returns the newly selected item
    def selectPrevious(self):
        
        #Initially check whether the last animation is still going
        if self.timeline.is_playing():
            self.timeline.set_speed(1000) # Nasty hack to make sure the timeline finishes
            
        self.timeline = clutter.Timeline (15,85)
        self.timeline_completed=False
        
        #Check if we're at the first item in the list
        if (self.selected) != 0:
            self.selected = self.selected-1
            #Move the selection bar
            self.menuMgr.get_selector_bar().selectItem(self.menuItems[self.selected], self.timeline)
            
            self.menuItems[self.selected].scaleLabel(0, self.timeline)
            self.menuItems[self.selected+1].scaleLabel(1, self.timeline)
            if self.selected <= (len(self.menuItems)-3):
                self.menuItems[self.selected+2].scaleLabel(2, self.timeline)
            
        if self.selected != 0:
            self.menuItems[self.selected-1].scaleLabel(1, self.timeline)
        
        self.timeline.start()
            
    def selectFirst(self, moveBar):
        self.timeline = clutter.Timeline(15, 75)
        self.selected = 0
        for i in range(0,len(self.menuItems)):
            if i == 0:
                self.menuItems[i].scaleLabel(0, self.timeline)
            elif i == 1:
                self.menuItems[i].scaleLabel(1, self.timeline)
            else:
                self.menuItems[i].scaleLabel(2, self.timeline)
        
        if moveBar:    
            self.menuMgr.get_selector_bar().selectItem(self.menuItems[self.selected], self.timeline)
        
        self.timeline.start()
        
    def get_item_gap(self):
        return self.item_gap
        
    def get_current_item(self):
        return self.menuItems[self.selected]
            
    
class ListItem (clutter.Label):
    zoomLevel = 0.5
    opacityStep = 120

    def __init__ (self, menu, itemLabel, y, imagePath):
        clutter.Label.__init__ (self)
        self.itemTexturesGroup = clutter.Group()
        font = menu.getMenuMgr().get_skinMgr().get_menu_font()
        self.stage = menu.getMenuMgr().get_stage()
        self.set_font_name(font)
        self.set_text(itemLabel)
        self.color = clutter.Color(0xff, 0xff, 0xff, 0xdd)
        self.set_color(self.color)
        self.currentOpacity = 255
        self.menu = menu
        
        #Text is actually scaled down in 'regular' position so that it doesn't get jaggies when zoomed in
        self.set_scale(self.zoomLevel, self.zoomLevel)
        self.currentZoom = self.zoomLevel
        
        
        #(label_width, label_height) = self.label.get_size()
        label_x = 0 #x #self.stage.get_width() - label_width - 50
        label_y = y #self.stage.get_height() - label_height
        self.set_position(0, y)
        self.addImage(imagePath, True)
        
        #Add textures group and hide it
        self.menu.getMenuGroup().add(self.itemTexturesGroup)
        self.itemTexturesGroup.hide_all()
        
    def scaleLabel(self, level, timeline):
        self.timeline = timeline
        self.timeline.set_loop(False)
        
        #Determine the zooming level
        zoomTo=0
        opacityTo = 255
        if level==0:
            zoomTo = 1 #self.zoomLevel * 1.5
            opacityTo = 255
            self.itemTexturesGroup.show_all()
        if level==1:
            zoomTo = self.zoomLevel * 1.2
            opacityTo = 255 - self.opacityStep
            self.itemTexturesGroup.hide_all()
        if level==2:
            zoomTo = self.zoomLevel
            opacityTo = 255 - 2*self.opacityStep
            self.itemTexturesGroup.hide_all()
        
        alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.behaviour1 = clutter.BehaviourScale(alpha, self.currentZoom, zoomTo, clutter.GRAVITY_WEST)
        self.behaviour2 = clutter.BehaviourOpacity(alpha, self.currentOpacity, opacityTo)
        self.behaviour1.apply(self)
        self.behaviour2.apply(self)

        
        self.currentZoom = zoomTo
        self.currentOpacity = opacityTo
        return self.timeline
        
    def get_zoom_level(self):
        return self.zoomLevel

        
    def addImage(self, path, useReflection):
        self.tempTexture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)

        self.tempTexture.set_pixbuf(pixbuf)
        (abs_x, abs_y) = self.get_abs_position()

        x = abs_x# - self.tempTexture.get_width()
        y = (self.menu.getStage().get_height()/2) - (self.tempTexture.get_height()/2)
        self.tempTexture.set_position(x, y)
        
        self.tempTexture.rotate_y(45,0,0)    
        self.itemTexturesGroup.add(self.tempTexture)
        self.tempTexture.hide_all()
        
        #Scale the image down by half
        xy_ratio = self.tempTexture.get_width() / self.tempTexture.get_height()
        self.tempTexture.set_width(int(self.stage.get_width() * 0.30)) #30% of the stages width
        self.tempTexture.set_height(self.tempTexture.get_width() * xy_ratio ) #Just makes sure the sizes stay the same
        
        if useReflection:
            self.reflectionTexture = Texture_Reflection(self.tempTexture)
            #self.reflectionTexture.set_position(0, 0)#self.tempTexture.get_height())
            self.itemTexturesGroup.add(self.reflectionTexture)
        self.itemTexturesGroup.hide_all()
    
    def setAction(self, newAction):
        self.action = newAction
        
    def getAction(self):
        return self.action
    
    def get_menu(self):
        return self.menu
