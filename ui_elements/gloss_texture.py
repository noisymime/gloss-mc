import pygtk
import gtk
import clutter
import cluttergtk

########################################################

########################################################
class GlossTexture(cluttergtk.Texture):
    pixbuf = None
    
    def __init__(self):
        cluttergtk.Texture.__init__(self)
        print "loading"
    
    def set_from_pixbuf(self, pixbuf):
        self.pixbuf = pixbuf
        cluttergtk.Texture.set_from_pixbuf(self, pixbuf)
    
    def get_pixbuf(self):
        return self.pixbuf
    