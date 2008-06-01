import gobject
from multimedia.AudioController import AudioController

class Playlist(gobject.GObject):
    #Setup signals
    __gsignals__ =  { 
        "song-change": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        "stopped": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
        }
    
    
    songs = []
    position = 0
    is_playing = False
    
    

    def __init__(self, musicPlayer):
        gobject.GObject.__init__(self)
        
        self.musicPlayer = musicPlayer
        self.backend = musicPlayer.backend
        self.glossMgr = musicPlayer.glossMgr
        self.audio_controller = AudioController(self.glossMgr)
        self.audio_controller.connect("completed", self.next_song)
        
    def clear_songs(self):
        self.songs = None
        self.songs = []
        
    def play(self):
        if len(self.songs) == 0: return
        if self.position > len(self.songs): return
        
        current_song = self.songs[self.position]
        current_song_filename = self.musicPlayer.base_dir + "/" + current_song.directory + "/" + current_song.filename
        current_song_uri = "file://" + current_song_filename
        if self.glossMgr.debug: print "Music_Player: Attempting to play file '%s'" % current_song_filename
        self.audio_controller.play_audio(current_song_uri)
        
        self.emit("song-change", current_song)
        
    #Called when the playback of one song finishes and the next is required
    def next_song(self, data = None):
        self.position += 1
        self.play()
        
    def stop(self):
        if self.is_playing:
            self.audio_controller.stop_audio()
            
        self.emit("stopped")
        
    def append_song(self, song):
        self.songs.append(song)
        
    def append_songs(self, songs):
        for song in songs:
            self.songs.append(song)
            
    def insert_song(self, position, song):
        self.songs.insert(position, song)
        
    def insert_songs(self, position, songs):
        x= position
        for song in songs:
            self.songs.insert(x, song)
            x += 1
            
    def num_songs(self):
        return len(self.songs)