import cairo
import clutter
import gtk
from clutter.cluttercairo import CairoTexture

"""
This element is a Clutter Group that displays as a rectangle of arbitary size
with rounded corners. It is rendered using Cairo but maybe treated as per any other
Clutter element
"""

class RoundedRectangle(clutter.Group):
    
    ARC_TO_BEZIER = 0.55228475
    RADIUS = 5
    MARGIN = 1
    
    def __init__(self, width, height, colour = clutter.color_parse('Black')):
        clutter.Group.__init__(self)
  
        self.width = width
        self.height = height
        self.colour = colour
        margin = self.MARGIN
        radius = self.RADIUS
        
        #CairoTexture.__init__(self, width, height)
        #context = self.cairo_create()
        self.texture = CairoTexture(self.width, self.height)

        self.setup_rounded_context()
        self.refresh()
        
        self.add(self.texture)
        self.texture.show()
        
    def setup_rounded_context(self):        
        # Round corners
        x = 0 + self.MARGIN
        y = 0 + self.MARGIN
        w = self.width - (self.MARGIN * 2)
        h = self.height - (self.MARGIN * 2)
        radius_x = self.RADIUS
        radius_y = self.RADIUS
        
        context = self.texture.cairo_create()
        
        #Clear the texture
        #if not self.context is None:
        context.set_operator(cairo.OPERATOR_CLEAR)
        context.paint()
        context.set_operator(cairo.OPERATOR_OVER)
            
        """
        Clip cairo texture with rounded rectangle.
        """
        if radius_x > w - radius_x:
            radius_x = w / 2
        if radius_y > h - radius_y:
            radius_y = h / 2

        #approximate (quite close) the arc using a bezier curve
        c1 = self.ARC_TO_BEZIER * radius_x
        c2 = self.ARC_TO_BEZIER * radius_y

        context.new_path();
        context.move_to ( x + radius_x, y)
        context.rel_line_to ( w - 2 * radius_x, 0.0)
        context.rel_curve_to ( c1, 0.0, radius_x, c2, radius_x, radius_y)
        context.rel_line_to ( 0, h - 2 * radius_y)
        context.rel_curve_to ( 0.0, c2, c1 - radius_x, radius_y, -radius_x, radius_y)
        context.rel_line_to ( -w + 2 * radius_x, 0)
        context.rel_curve_to ( -c1, 0, -radius_x, -c2, -radius_x, -radius_y)
        context.rel_line_to (0, -h + 2 * radius_y)
        context.rel_curve_to (0.0, -c2, radius_x - c1, -radius_y, radius_x, -radius_y)
        context.close_path()
        context.clip()
        
        #context = self.get_rounded_context(x ,y, w1, h1, radius, radius)
        self.ct = gtk.gdk.CairoContext(context)
        
        # Scale context area
        #wr = width / float(pixbuf.get_width())
        #hr = height / float(pixbuf.get_height())
        #context.scale(wr,hr)
        
        #ct.set_source_pixbuf(pixbuf,0,0)
        self.ct.rectangle(
                     (0, 0, self.width, self.height)
                     )
        self.context = context
        
        #Set the colour
        self.context.set_source_rgb(self.colour.red, self.colour.green, self.colour.blue)
    
    def refresh(self):
        self.context.paint()
        del self.context # Update texture
        del self.ct
    
    def set_width(self, new_width):
        #self.texture.set_width(new_width)
        #self.texture.set_clip(0, 0, new_width, self.height)
        self.width = new_width
        self.setup_rounded_context()
        self.refresh()
        
        clutter.Group.set_width(self, new_width)
        
    def set_height(self, new_height):
        self.texture.set_height(new_height)
        clutter.Group.set_height(self,new_height)
        
    def set_size(self, new_width, new_height):
        self.set_width(new_width)
        self.set_height(new_height)
        
    def set_color(self, new_colour):
        self.setup_rounded_context()
        self.colour = new_colour
        self.refresh()
        #self.texture.set_color(new_colour)