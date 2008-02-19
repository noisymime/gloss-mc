import socket
import threading
import thread
import os
from modules.myth_tv_player.recorder import recorder

class MythBackendConnection(threading.Thread):
    pipe_rfd = None
    pipe_wfd = None
    connected = False
    recorder = None # Mythtv recorder
    chanNum = None

    def __init__(self, videoPlayer, server, port):    
        threading.Thread.__init__(self)  
        
        self.protocolVersion = 31
        self.localhost_name = "myhost" # Change this later
        self.server = server #"192.168.0.8"
        self.server_port = port #6543
        self.addr = (self.server, self.server_port)
        self.videoPlayer = videoPlayer
        self.lock = False #Dictakes whether or not we have a signal lock

        
        try:
            #3 Sockets, 1 for cmds, 1 for data, 1 for monitoring messages
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_socket_id = None
            self.data_sock.connect((self.server, self.server_port))
            self.msg_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.msg_sock.connect((self.server, self.server_port))
        except socket.error, e:
            print "TV_PLAYER: Error connecting to Myth Backend socket"
            return
        
        thread.start_new_thread(self.message_socket_mgr,(self.msg_sock,))
        self.connected = self.connect_socket(self.sock)   

      
    def run(self):
        print "Starting thread"
        self.recorder = recorder(self)
        #self.setup_recorder()
        self.spawn_live()
        #self.disconnect()
        
    def receive_reply(self, sock):
        ret = ""
        tmp = sock.recv(8)
        count = int(tmp)
        #debug("REPLY LEN: %d" % count)
        ret = sock.recv(count)

        #print "read<--" + ret
        return ret

    def send_cmd(self, sock, base_cmd):
        cmd = str(len(base_cmd)).ljust(8) + base_cmd
        sock.send(cmd)
        #print "write-->" + cmd  
        
    def connect_socket(self, socket):
        try:
            socket.connect((self.server, self.server_port))
        except Exception, (error,message):
            print "TV_PLAYER: Error connecting to Myth Backend socket"
            return False
        
        #Do the protocol version check
        protString = "MYTH_PROTO_VERSION "+ str(self.protocolVersion)
        self.send_cmd(socket, protString)
        protRecvString = "ACCEPT[]:[]" + str(self.protocolVersion)
        result = self.receive_reply(socket)
        if self.videoPlayer.glossMgr.debug: print "TV_Player: Protocol version check: " + result
        
        if not result == protRecvString:
            #Protocol Version check failed
            raise RuntimeError, "Myth Protocol version failure. Aborting."
        
        #Perform the mandatory ANN
        ANNstring = "ANN Playback " + self.localhost_name + " 0"
        self.send_cmd(socket, ANNstring)
        ANN_recv_string = "OK" #What a successful return should be
        result = self.receive_reply(socket)
        if not result == ANN_recv_string:
            raise RuntimeError, "Myth: ANN connection failed"
        
        return True
        
    def disconnect(self):
        self.sock.close()
    
            
    def spawn_live(self):
        if self.recorder == None:
            print "TV_PLAYER: Cannot spawn live tv, no recorder available"
        
        result = self.recorder.spawnLive()
        if not result == "ok":
            print "TV_PLAYER: failed to spawn live tv. Result: "+str(result)
            return
        
        #Set channel if it has been set
        if not self.chanNum is None: 
            result = self.recorder.checkChannel(self.chanNum)
            print "Channel change result: " + result
            #if result == "ok":
            self.recorder.setChannel(self.chanNum)
        
        
        self.setup_recording()
        
    def setup_recording(self):
        #Check the recording
        is_recording = self.recorder.isRecording()

        #Wait for the recorder to start doing things
        frames = self.recorder.getFramesWritten()
        while frames < 35:
            frames = self.recorder.getFramesWritten()
            
        #Create a new data socket (For receiving the data stream)
        protString = "MYTH_PROTO_VERSION "+ str(self.protocolVersion)
        self.send_cmd(self.data_sock, protString)
        protRecvString = "ACCEPT[]:[]" + str(self.protocolVersion)
        result = self.receive_reply(self.data_sock)
        
        #Get the recording filename
        detail_list = self.recorder.getCurrentRecording()
        if self.videoPlayer.glossMgr.debug: print "TV_Player: Results from GET_CURRENT_RECORDING='%s'" % str(detail_list)

        #This is an attempt to get the filename (Its meant to be at position 8)
        try:
            filename_list = detail_list[8].rsplit("/")
        except IndexError, e:
            print "TV_PLAYER: Unable to retrieve recording details. No filename returned by backend."
            print "TV_PLAYER: Aborting!"
            self.stop()
            return
        
        filename_list.reverse()
        filename = "/" + filename_list[0]
        
        if self.videoPlayer.glossMgr.debug: print "TV_Player: Playback filename=" + filename
             
        #Announce our intent to read a file
        announce_cmd = "ANN FileTransfer " + self.localhost_name + "[]:[]" + filename
        self.send_cmd(self.data_sock, announce_cmd)
        result = self.receive_reply(self.data_sock)
        result_list = result.rsplit("[]:[]")
        self.data_socket_id = result_list[1]
        
        #Do some housekeeping
        self.recorder.frontendReady()
        input = self.recorder.getInput()
        
        rec_list_cmd = "MESSAGE[]:[]RECORDING_LIST_CHANGE"
        self.send_cmd(self.sock, rec_list_cmd)
        result = self.receive_reply(self.sock)  
        
        #Start a recording thread
        self.buffer_live(self.sock, self.data_sock, self.data_socket_id)
    
    def buffer_live(self, cmd_sock, data_sock, socket_id):
        request_size = 32768
        #max_request_size = 135000
        max_request_size = 128000#270000
        request_size_step = 16384
        
        if self.pipe_rfd is None:
            #Data is sent through a pipe to GStreamer
            (self.pipe_rfd, self.pipe_wfd) = os.pipe()
            self.videoPlayer.begin_playback(self.pipe_rfd)
        
        print "BEGINNING PLAYBACK!"
        self.Playing = True
        while self.Playing:
            #print "Begin loop"
            transfer_cmd = "QUERY_FILETRANSFER "+ str(socket_id) + "[]:[]REQUEST_BLOCK[]:[]"+str(request_size)
            #print "Requesting: " + str(request_size)
            self.send_cmd(cmd_sock, transfer_cmd)
            num_bytes = int(self.receive_reply(cmd_sock))
            #print "Should receive: " + str(num_bytes)
            data = data_sock.recv(num_bytes)
            #print "Received: " + str(num_bytes)
            try:
                os.write(self.pipe_wfd, data)
            except TypeError, e:
                pass
            
            #print "Being Optimisatoin"
            #This tries to optimise the request size
            if (num_bytes == request_size) and (request_size < max_request_size):
                request_size += request_size_step
                if request_size > max_request_size:
                    request_size = max_request_size
            elif (request_size > request_size_step) and (num_bytes != request_size):
                request_size -= request_size_step
                if num_bytes < request_size:
                    print "TV_PLAYER: Failed to receive full allocation"
            #print "End optimisation"
        
        print "Ending playback"
        self.stop()
        
    def message_socket_mgr(self, msg_socket):
        #Do the protocol version check
        print "Starting the msg thread"
        protString = "MYTH_PROTO_VERSION "+ str(self.protocolVersion)
        self.send_cmd(self.msg_sock, protString)
        protRecvString = "ACCEPT[]:[]" + str(self.protocolVersion)
        result = self.receive_reply(self.msg_sock)
        if not result == protRecvString:
            #Protocol Version check failed
            raise RuntimeError, "Myth Protocol version failure. Aborting."
        
        #Perform the mandatory ANN (The 1 at the end says that we want to receive all messages from the server)
        ANNstring = "ANN Monitor " + self.localhost_name + " 1"
        self.send_cmd(self.msg_sock, ANNstring)
        ANN_recv_string = "OK" #What a successful return should be
        result = self.receive_reply(self.msg_sock)
        if not result == ANN_recv_string:
            raise RuntimeError, "Myth: ANN connection failed"
       
        while not self.lock:
            #ANN_recv_string = "OK" #What a successful return should be
            result = self.receive_reply(self.msg_sock)
            result_list = result.rsplit("[]:[]")
            if self.videoPlayer.glossMgr.debug: print "TV_Player: Backend Message: " + result
            
            if result_list[1] == "RECORDING_LIST_CHANGE":
                self.lock = True
        
    def change_channel(self, chanName):
        if self.Playing:
            self.Playing = False
            #First check its a valid channel ID
            validate_cmd = "QUERY_RECORDER "+str(self.recorder) +"[]:[]CHECK CHANNEL[]:[]"+str(chanName)
            self.send_cmd(self.sock, validate_cmd)
            result = self.receive_reply(self.sock)
            print "Recorder Result: " + result
            
            if result == "ok":
                
                change_cmd = "QUERY_RECORDER "+str(self.recorder) +"[]:[]SET CHANNEL[]:[]"+str(chanName)
                self.send_cmd(self.sock, change_cmd)
                result = self.receive_reply(self.sock)
                print "Change result: " + result
                
                #Reset the data socket
                self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.data_socket_id = None
                self.data_sock.connect((self.server, self.server_port))
                
                #Start a recording thread
                self.setup_recording()
                #self.buffer_live(self.sock, self.data_sock, self.data_socket_id)
            else:
                print "TV_PLAYER: Invalid channel selected"

    def end_stream(self):
        self.stream = False
        
    def stop(self):
        self.Playing = False
        
        if not self.recorder is None:
            result = self.recorder.stopLive()
        
        #Close the pipe
        if not self.pipe_wfd is None: 
            os.close(self.pipe_wfd)
            self.pipe_wfd = None
        if not self.pipe_rfd is None: 
            os.close(self.pipe_rfd)
            self.pipe_rfd = None
        
        if not self.data_socket_id is None:
            end_transfer_cmd = "QUERY_FILETRANSFER "+str(self.data_socket_id) +"[]:[]DONE"
            self.send_cmd(self.sock, end_transfer_cmd)
