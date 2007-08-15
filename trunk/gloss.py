import sys
import clutter
#import gobject
import pygtk
import gtk
from Menu import Menu
from MenuMgr import MenuMgr
from Slideshow import Slideshow
from VideoPlayer import VideoPlayer
from MusicPlayer import MusicPlayer
from TVPlayer import TVPlayer
from DvdPlayer import DvdPlayer


class MainApp:
    def __init__ (self):
        gtk.gdk.threads_init()
    
        self.stage = clutter.stage_get_default()
        self.stage.set_color(clutter.color_parse('Black'))
        #self.stage.set_size(800, 600)
        self.stage.set_property("fullscreen", True)
        self.stage.connect('button-press-event', self.on_button_press_event)
        self.stage.show_all()
                

        #color = clutter.Color(0xff, 0xcc, 0xcc, 0xdd)
        color = clutter.Color(0, 0, 0, 0)

        self.menuMgr = MenuMgr(self.stage)
        self.stage.connect('key-press-event', self.menuMgr.on_key_press_event)
        
        menu1 = Menu(self.menuMgr)
        menu1.addItem("TV", "ui/dvd.png")
        menu1.addItem("Slideshow", "ui/gallery.png")        
        menu1.addItem("Videos", "ui/videos.png")
        menu1.addItem("Link", "ui/link.png")
        menu1.addItem("DVD", "ui/dvd.png")
        menu1.addItem("nothing", "ui/dvd.png")
        menu1.addItem("nothing", "ui/dvd.png")
        menu1.addItem("nothing", "ui/dvd.png")
        
        #menu1.setListFont('Tahoma 42')
        menu1.setMenuPositionByName("center")
        self.menu1 = menu1
        self.menu1.selectFirst(True)
        
        
        self.menu1.getItemGroup().show_all()
        
        self.menu2 = Menu(self.menuMgr)
        self.menu2.addItem("Nothing", "ui/dvd.png")
        self.menu2.addItem("Link", "ui/gallery.png")
        self.menu2.addItem("blah3", "ui/game.png")
        self.menu2.addItem("blah4", "ui/music.png")
        self.menu2.addItem("blah", "ui/dvd.png")
        self.menu2.addItem("blah2", "ui/dvd.png")
        self.menu2.addItem("blah3", "ui/dvd.png")
        self.menu2.addItem("blah4", "ui/dvd.png")
        #self.menu2.setListFont('Tahoma 42')
        self.menu2.setMenuPositionByName("center")
        
        self.mySlideshow = Slideshow(self.menuMgr, "images/")
        #self.mySlideshow.loadDir("images/", True)
       
        self.vidPlayer = VideoPlayer(self.stage)
        self.tvPlayer = TVPlayer(self.stage)
        self.dvdPlayer = DvdPlayer(self.stage)
        self.musicPlayer = MusicPlayer(self.stage)
        
        menu1.getItem(0).setAction(self.tvPlayer)
        #menu1.getItem(1).setAction(self.mySlideshow)
        menu1.getItem(1).setAction(self.mySlideshow.generateMenu())
        menu1.getItem(2).setAction(self.vidPlayer)
        menu1.getItem(3).setAction(self.menu2)
        menu1.getItem(4).setAction(self.dvdPlayer)
        
        self.menu2.getItem(1).setAction(self.menu1)
        


    def on_button_press_event (self, stage, event):
        print "mouse button %d pressed at (%d, %d)" % \
              (event.button, event.x, event.y)
        if event.button == 1:
            pass
        
    
    def run (self):
        self.stage.show()
        #self.timeline.start()
        clutter.main()

def main (args):
    app = MainApp()
    app.run()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
