from multimedia.AudioController import AudioController

class Playlist:
    
    songs = []
    position = 0
    is_playing = False
    
    

    def __init__(self, musicPlayer):
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
        
    #Called when the playback of one song finishes and the next is required
    def next_song(self, data = None):
        self.position += 1
        self.play()
        
    def add_song(self, song):
        self.songs.append(song)
        
    def add_songs(self, songs):
        for song in songs:
            self.songs.append(song)