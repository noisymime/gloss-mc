import clutter
import pygtk
import gtk

class SkinMgr:

    def __init__ (self, mainStage):
        self.stage = mainStage
        
    def get_Background(self):
        pixbuf = gtk.gdk.pixbuf_new_from_file("ui/background.png")
        self.background = clutter.Texture()
        self.background.set_pixbuf(pixbuf)
        self.background.set_size(self.stage.get_width(), self.stage.get_height())
        self.background.show()
        return self.background
        
    def get_menu_font(self):
        return 'Tahoma 40'