import clutter
import pango
import gtk
import pygtk

class MenuItem (clutter.Label):
    zoomLevel = 0.5
    opacityStep = 120

    def __init__ (self, menu, itemLabel, y):
        clutter.Label.__init__ (self)
        glossMgr = menu.glossMgr
        self.menu = menu
        self.stage = glossMgr.get_stage()
        
        #ItemTexturesGroup is what shows any images / reflections associated with the item
        self.itemTexturesGroup = clutter.Group()
        self.itemTexturesGroup.set_position(menu.menu_image_x, menu.menu_image_y)
        
        
        #setup the label
        font = menu.font
        self.set_font_name(font)
        self.set_text(itemLabel)
        self.color = clutter.Color(0xff, 0xff, 0xff, 0xdd)
        self.set_color(self.color)
        self.currentOpacity = 255
        self.data = itemLabel #By default the items data is simply its label
        
        if not glossMgr.get_selector_bar().get_pixbuf() is None:
            #The width is the length of the selector bar minus its offset
            width = glossMgr.get_selector_bar().get_width() + glossMgr.get_selector_bar().get_x_offset()
            self.set_width(width)

        self.set_ellipsize(pango.ELLIPSIZE_END)
        #Text is actually scaled down in 'regular' position so that it doesn't get jaggies when zoomed in
        self.set_scale(self.zoomLevel, self.zoomLevel)
        self.currentZoom = 0        
        
        #(label_width, label_height) = self.label.get_size()
        label_x = 0 #x #self.stage.get_width() - label_width - 50
        label_y = y #self.stage.get_height() - label_height
        self.set_position(0, y)
        
        #Add textures group and mark whether or not the textures are currently on the stage
        self.itemTexturesGroup.show_all()
        self.onStage = False

        
    def add_image_from_path(self, path, x, y):
        tempTexture = clutter.Texture()
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        tempTexture.set_pixbuf(pixbuf)
        
        self.add_image_from_texture(tempTexture)
        
    def add_image_from_texture(self, texture):
        if texture is None:
            print "NO TEXTURE!"

        """
        Removing as this is currently already handled in individual module files
        #Set the image to the size in the theme
        if not self.menu.menu_image_height is None:
            texture.set_height(self.menu.menu_image_height)
        if not self.menu.menu_image_width is None:            
            texture.set_width(self.menu.menu_image_width)
        """
        
        #Rotate appropriately
        rotation = self.menu.menu_image_rotation
        x_rotation = (texture.get_width())
        texture.set_rotation(clutter.Y_AXIS, rotation, x_rotation, 0, 0)
        self.itemTexturesGroup.add(texture)        
        
        #If reflection is turned on in the theme, add a reflection texture
        if self.menu.useReflection:
            self.reflectionTexture = Texture_Reflection(texture)
            self.itemTexturesGroup.add(self.reflectionTexture)
        
        self.itemTexturesGroup.show_all()
        
    def set_data(self, data):
        self.data = data
        
    def get_data(self):
        return self.data
    
    def setAction(self, newAction):
        self.action = newAction
        
    def getAction(self):
        return self.action
    
    def get_menu(self):
        return self.menu
