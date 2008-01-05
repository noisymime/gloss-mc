import clutter

class Texture_Reflection (clutter.Texture):

    def __init__(self, origTexture):
        clutter.Texture.__init__(self)
        self.set_pixbuf(origTexture.get_pixbuf())
        
        (w, h) = origTexture.get_abs_size()
        self.set_width(w)
        self.set_height(h)
        
        #Rotate the reflection based on any rotations to the master
        ang_y = origTexture.get_rotation(clutter.Y_AXIS) #ryang()
        self.set_rotation(clutter.Y_AXIS, ang_y[0], (origTexture.get_width()), 0, 0)
        ang_x = origTexture.get_rotation(clutter.X_AXIS)
        self.set_rotation(clutter.X_AXIS, ang_x[0], 0, (origTexture.get_height()), 0)
        #ang_z = origTexture.get_rotation(clutter.Z_AXIS)
        #self.set_rotation(clutter.Z_AXIS, ang_z[0], 0, 0, 0)

        #Get the location for it               
        (x, y) = origTexture.get_abs_position()
        print (x, y)
        #self.set_clip(0,self.get_height()/2,self.get_width(), (self.get_height()/2))
        
        #Flip it upside down
        #self.set_rotation(clutter.X_AXIS, 180, 0, origTexture.get_height(), 0)
        #self.rotate_x(180,origTexture.get_height(),0)
        self.set_opacity(50)

        self.set_position(x, y)