import socket
import time
import threading

class MythBackendConnection(threading.Thread):

    def __init__(self, videoPlayer):    
        self.protocolVersion = 31
        self.localhost_name = "myhost" # Change this later
        self.server = "192.168.0.8"
        self.server_port = 6543
        self.videoPlayer = videoPlayer
        
        #2 Sockets, 1 for cmds, 1 for data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #self.sock.connect( ("192.168.0.8", 6543) )
        self.connected = False
        self.recorder = None # Mythtv recorder
        self.connect(self.server, self.server_port)
        
        threading.Thread.__init__(self)
        
    #def start(self):
    #    threading.Thread.start(self)
         
        
    def run(self):
        print "Starting thread"
        self.setup_recorder()
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
         
    def connect(self, host, port):
        self.sock.connect((host, port))
        
        #Do the protocol version check
        protString = "MYTH_PROTO_VERSION "+ str(self.protocolVersion)
        self.send_cmd(self.sock, protString)
        protRecvString = "ACCEPT[]:[]" + str(self.protocolVersion)
        result = self.receive_reply(self.sock)
        print result
        if not result == protRecvString:
            #Protocol Version check failed
            raise RuntimeError, "Myth Protocol version failure. Aborting."
        
        #Perform the mandatory ANN
        ANNstring = "ANN Playback " + self.localhost_name + " 0"
        self.send_cmd(self.sock, ANNstring)
        ANN_recv_string = "OK" #What a successful return should be
        result = self.receive_reply(self.sock)
        if not result == ANN_recv_string:
            raise RuntimeError, "Myth: ANN connection failed"
        
        #All looks good
        self.connected = True
        
    def disconnect(self):
        self.sock.close()
        
    def setup_recorder(self):
        if not self.connected:
            print "Cannot get recorder, no server connection exists"
            return None
            
        recorder_request_string = "GET_NEXT_FREE_RECORDER[]:[]-1"
        self.send_cmd(self.sock, recorder_request_string)
        result = self.receive_reply(self.sock)
        result_list = result.rsplit("[]:[]")
        if not result_list[0] == -1:
            #Then everything worked fine
            self.recorder = result_list[0]
        else:
            print "Myth: No recorders available"
            
    def spawn_live(self):
        if self.recorder == None:
            print "Myth: Cannot spawn live tv, no recorder available"
        
        chainID = "live-" + self.localhost_name + "-2007-08-03T21:54:21"#+str(time.clock())
        spawn_string = "QUERY_RECORDER "+str(self.recorder)+"[]:[]SPAWN_LIVETV[]:[]"+chainID +"[]:[]0"
        self.send_cmd(self.sock, spawn_string)
        spawn_receive_string = "ok"
        result = self.receive_reply(self.sock)
        if not result == spawn_receive_string:
            print "Myth: failed to spawn live tv. Result: "+str(result)
        
        #Check the recording
        check_string = "QUERY_RECORDER "+str(self.recorder)+"[]:[]IS_RECORDING"
        self.send_cmd(self.sock, check_string)
        is_recording = self.receive_reply(self.sock)
        if not is_recording == str(1):
            #Just send the check again
            self.send_cmd(self.sock, check_string)
        
        #Create a new data socket
        self.data_sock.connect( (self.server, self.server_port) )
        protString = "MYTH_PROTO_VERSION "+ str(self.protocolVersion)
        self.send_cmd(self.data_sock, protString)
        protRecvString = "ACCEPT[]:[]" + str(self.protocolVersion)
        result = self.receive_reply(self.data_sock)
        
        #This is just a hack to make sure the channel has locked, I'll fix it later
        time.sleep(5)
        
        #Get the recording filename
        filename_string = "QUERY_RECORDER "+str(self.recorder)+"[]:[]GET_CURRENT_RECORDING"
        self.send_cmd(self.sock, filename_string)
        filedetails = self.receive_reply(self.sock)
        detail_list = filedetails.rsplit("[]:[]")
        filename_list = detail_list[8].rsplit("/")
        filename_list.reverse()
        filename = "/" + filename_list[0]
        print filename
             
        #Announce our intent to read a file
        announce_cmd = "ANN FileTransfer " + self.localhost_name + "[]:[]" + filename
        self.send_cmd(self.data_sock, announce_cmd)
        result = self.receive_reply(self.data_sock)
        result_list = result.rsplit("[]:[]")
        data_socket_id = result_list[1]
        print "Socket ID: " + str(data_socket_id)
        
        #Do some housekeeping
        frontend_ready_cmd = "QUERY_RECORDER "+str(self.recorder) +"[]:[]FRONTEND_READY"
        self.send_cmd(self.sock, frontend_ready_cmd)
        result = self.receive_reply(self.sock)
        input_cmd = "QUERY_RECORDER "+ str(self.recorder) +"[]:[]GET_INPUT"
        self.send_cmd(self.sock, input_cmd)
        result = self.receive_reply(self.sock)
        rec_list_cmd = "MESSAGE[]:[]RECORDING_LIST_CHANGE"
        self.send_cmd(self.sock, rec_list_cmd)
        result = self.receive_reply(self.sock)  
        
        #Start a recording thread
        self.buffer_live(self.sock, self.data_sock, data_socket_id)
    
    def buffer_live(self, cmd_sock, data_sock, socket_id):
        #Create a buffer file
        self.buffer_file = open("test.mpg","w")

        print "grunt0"
        #read some data
        x=0
        request_size = 32768
        
        #Need to create a bit of a buffer so playback will begin
        while x<80:
            transfer_cmd = "QUERY_FILETRANSFER "+ str(socket_id) + "[]:[]REQUEST_BLOCK[]:[]"+str(request_size)
            self.send_cmd(cmd_sock, transfer_cmd)
            num_bytes = int(self.receive_reply(cmd_sock))
            data = data_sock.recv(num_bytes)
            self.buffer_file.write(data)
            self.buffer_file.flush()
            x=x+1
        
        #data_sock.flush()
        tempfile = data_sock.makefile("r", request_size)
        tempfile.flush()
        self.videoPlayer.begin_playback(tempfile.fileno())
        print "BEGINNING PLAYBACK!"
        while x<1000:
            transfer_cmd = "QUERY_FILETRANSFER "+ str(socket_id) + "[]:[]REQUEST_BLOCK[]:[]"+str(request_size)
            self.send_cmd(cmd_sock, transfer_cmd)
            num_bytes = int(self.receive_reply(cmd_sock))
            data_sock.recv(num_bytes)
            #self.buffer_file.write(data)
            #self.buffer_file.flush()
            x=x+1
        
        print "Ending playback"
        self.buffer_file.close()

    def end_stream(self):
        self.stream = False
        