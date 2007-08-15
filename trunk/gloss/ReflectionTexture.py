import clutter

class Texture_Reflection (clutter.Texture):

    def __init__(self, origTexture):
        clutter.Texture.__init__(self)
        self.set_pixbuf(origTexture.get_pixbuf())
        
        self.set_width(origTexture.get_width())
        self.set_height(origTexture.get_height())
        
        #Rotate the reflection based on any rotations to the master
        ang_y = origTexture.get_ryang()
        self.rotate_y(ang_y,0,0)
        ang_x = origTexture.get_rxang()
        self.rotate_x(ang_x,0,0)
        ang_z = origTexture.get_rzang()
        self.rotate_z(ang_z,0,0)

        #Get the location for it               
        (x, y) = origTexture.get_abs_position()
        
        #self.set_clip(0,self.get_height()/2,self.get_width(), (self.get_height()/2))
        
        #Flip it upside down
        self.rotate_x(180,origTexture.get_height(),0)
        self.set_opacity(50)

        self.set_position(x, y)