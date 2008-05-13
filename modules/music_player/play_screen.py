import clutter
from modules.music_player.playlist import Playlist
from ui_elements.image_frame import ImageFrame
from ui_elements.image_clone import ImageClone
from ui_elements.label_list import LabelList

class PlayScreen(clutter.Group):
    
    img_size = 300

    def __init__(self, musicPlayer):
        clutter.Group.__init__(self)
        
        self.musicPlayer = musicPlayer
        self.glossMgr = musicPlayer.glossMgr
        self.stage = self.glossMgr.get_stage()
        
        self.main_img = None
        self.song_list = LabelList(8)
        self.playlist = Playlist(musicPlayer)
        
        self.setup()
        
    def setup(self):
        self.song_list.setup_from_theme_id(self.glossMgr.themeMgr, "music_play_screen_songs")
        self.main_img_theme = self.glossMgr.themeMgr.get_imageFrame("music_playing_image")
        self.img_size = self.main_img_theme.img_size
        
    def on_key_press_event(self, stage, event):
        if (event.keyval == clutter.keysyms.Up):
            self.song_list.input_queue.input(event)
        elif (event.keyval == clutter.keysyms.Down):
            self.song_list.input_queue.input(event)
        
    def append_playlist(self, playlist):
        self.playlist.add_songs(playlist.songs)
        
    def display(self, image):
        self.timeline = clutter.Timeline(80,160)
        self.alpha = clutter.Alpha(self.timeline, clutter.ramp_inc_func)
        self.opacity_behaviour = clutter.BehaviourOpacity(opacity_start=0, opacity_end=255, alpha=self.alpha)
        
        #Create a backdrop for the player. In this case we just use the same background as the menus
        #self.backdrop = glossMgr.get_themeMgr().get_texture("music_play_screen_background", None, None)
        self.backdrop = clutter.Rectangle(clutter.color_parse('Black'))
        self.backdrop.set_size(self.stage.get_width(), self.stage.get_height())
        self.backdrop.set_opacity(0)
        self.backdrop.show()
        self.add(self.backdrop)
        self.opacity_behaviour.apply(self.backdrop)
        
        self.main_img = ImageClone(img_frame = image)
        self.main_img.show()
        self.add(self.main_img)
        
        x = int( self.main_img_theme.get_x() )
        y = int( self.main_img_theme.get_y() )
        knots = (\
                 (int(self.main_img.get_x()), int(self.main_img.get_y()) ),\
                 (x, y)\
                 )
        self.path_behaviour = clutter.BehaviourPath(knots = knots, alpha = self.alpha)
        self.path_behaviour.apply(self.main_img)
        
        
        #Calculate the required scale factor
        (x_scale_start, y_scale_start) = self.main_img.get_scale()
        x_scale_end = float(self.img_size) / float(self.main_img.get_width())
        y_scale_end = float(self.img_size) / float(self.main_img.get_height())
        self.scale_behaviour = clutter.BehaviourScale(x_scale_start = x_scale_start, x_scale_end = x_scale_end, y_scale_start = y_scale_start, y_scale_end = y_scale_end, alpha = self.alpha)
        self.scale_behaviour.apply(self.main_img)
        
        for song in self.playlist.songs:
            self.song_list.add_item(song.name)
        self.opacity_behaviour.apply(self.song_list)
        self.song_list.set_opacity(0)
        self.song_list.select_first()
        self.song_list.show()
        self.add(self.song_list)
        
        self.show()
        self.stage.add(self)
        
        self.timeline.start()
        
    def undisplay(self):
        self.playlist.stop()
        self.hide()