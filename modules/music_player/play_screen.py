import clutter
from modules.music_player.playlist import Playlist
from multimedia.progress_bar import ProgressBar
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
        self.song_list = LabelList()
        self.playlist = musicPlayer.playlist #Playlist(musicPlayer)
        self.song_details = SongDetails(self)
        
        #Connect to "song-change" on playlist so any details can be updated
        self.playlist.connect("song-change", self.set_song_cb)
        
        controller = self.playlist.audio_controller
        self.progress_bar = ProgressBar(controller)

        self.displayed = False
        self.setup()
        
    def setup(self):
        self.progress_bar.setup_from_theme_id(self.glossMgr.themeMgr, "music_progress_bar")
        self.song_list.setup_from_theme_id(self.glossMgr.themeMgr, "music_play_screen_songs")
        self.main_img_theme = self.glossMgr.themeMgr.get_imageFrame("music_playing_image")
        self.img_size = self.main_img_theme.img_size
        
    def on_key_press_event(self, stage, event):
        if (event.keyval == clutter.keysyms.Up) or (event.keyval == clutter.keysyms.Down):
            self.song_list.input_queue.input(event)
        elif (event.keyval == clutter.keysyms.Return):
            self.playlist.play(self.song_list.selected)
        
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
        self.opacity_behaviour.apply(self.backdrop)
        
        
        if not image is None:
            if not self.main_img is None: self.remove(self.main_img)
            self.main_img = ImageClone(img_frame = image)
            self.add(self.main_img)
            self.main_img.show()
            
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
        
        #Clear the song list and readd from playlist
        self.song_list.clear()
        for song in self.playlist.songs:
            self.song_list.add_item(song.name)
            
        self.opacity_behaviour.apply(self.song_list)
        self.song_list.set_opacity(0)
        self.song_list.select_first()
        self.song_list.show()

        
        #self.song_details.set_song(self.playlist.current_song)
        self.song_details.set_opacity(0)
        self.opacity_behaviour.apply(self.song_details)
        self.song_details.show()

        x = (self.stage.get_width() - self.progress_bar.get_width())/2
        self.progress_bar.set_position(x, 650)
        self.progress_bar.display()
        
        if not self.displayed:
            self.first_run_display()
            self.displayed = True
        
        self.show()
        self.stage.add(self)
        
        self.timeline.start()
        
    def first_run_display(self):
        self.add(self.backdrop)
        self.add(self.song_list)
        self.add(self.song_details)
        self.add(self.progress_bar)
        
    def undisplay(self):
        self.playlist.stop()
        self.hide()
        
    def set_song(self, song):
        self.song_details.set_song(song)
        #***INSERT IMAGE UPDATE HERE***
        image = song.get_image()
        if not image is None: self.main_img.set_pixbuf(image)
        
    def set_song_cb(self, data, song):
        self.set_song(song)
        
    def clear_songs(self):
        self.song_list.clear()
        
        
"""
This is a Clutter group containing labels only that 
describe the current song being played
"""
class SongDetails(clutter.Group):
    
    def __init__(self, playScreen, song=None):
        clutter.Group.__init__(self)
        
        self.themeMgr = playScreen.glossMgr.themeMgr
        self.backend = playScreen.musicPlayer.backend
        self.stage = self.themeMgr.stage
        
        self.setup()
        self.show_all()
        
    def setup(self):
        #Setup size / position properties of group
        tmpGroup = self.themeMgr.get_group("music_play_screen_song_details", group = self)
        
        #Create all the various labels
        self.artist_heading = self.themeMgr.get_label("music_play_screen_artist_heading", parent = self)
        self.album_heading = self.themeMgr.get_label("music_play_screen_album_heading", parent = self)
        self.song_heading = self.themeMgr.get_label("music_play_screen_song_heading", parent = self)
        
        self.artist = self.themeMgr.get_label("music_play_screen_artist", parent = self)
        self.album = self.themeMgr.get_label("music_play_screen_album", parent = self)
        self.song = self.themeMgr.get_label("music_play_screen_song", parent = self)
        #self.song.set_color(clutter.Color(0xff, 0xff, 0xff, 0xdd))
        
        self.artist_heading.set_text("artist: ")
        self.song_heading.set_text("song: ")
        self.album_heading.set_text("album: ")
        
        self.add(self.artist_heading)
        self.add(self.album_heading)
        self.add(self.song_heading)
        self.add(self.artist)
        self.add(self.album)
        self.add(self.song)
        
    def set_song(self, song):
        
        self.song.set_text(song.name)
        
        artist = self.backend.get_artist_by_ID(song.artistID)
        if artist is None:
            self.artist.set_text("unknown artist")
        else:
            self.artist.set_text(artist.name)
        
        album = self.backend.get_album_by_ID(song.albumID)
        if album is None:
            self.album.set_text("unknown album")
        else:
            self.album.set_text(album.name)