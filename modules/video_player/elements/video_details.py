import pango
import clutter

class video_details(clutter.Group):
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
        
    def set_folder(self, folder_name):
        self.title.set_text("Folder: " + str(folder_name))
        self.year.set_text("")
        self.director.set_text("")
        self.plot.set_text("")
    
    def clear(self):
        self.title.set_text("")
        self.year.set_text("")
        self.director.set_text("")
        self.plot.set_text("")