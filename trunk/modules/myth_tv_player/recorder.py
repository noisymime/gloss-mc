import socket
import time

class recorder():
    delimiter = "[]:[]"
    recorderID = None
    
    def __init__(self, BackendController):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        BackendController.connect_socket(self.socket)
        self.localHost = socket.gethostname()
        
        #Find a free recorder
        strList = []
        strList.append( "GET_NEXT_FREE_RECORDER" )
        strList.append( "-1" )
        result_list = self.send_receive(strList)
        if not result_list[0] == -1:
            #Then everything worked fine
            self.recorderID = result_list[0]
        else:
            print "TV_PLAYER: Backend reports no recorders available"
        
    def send_receive(self, strList):
        self.send(strList)
        ret = self.receive()
        ret = ret.rsplit(self.delimiter)

        #print "read<--" + ret
        return ret
        
    def send(self, strList):
        #Setup the cmd string
        cmd = ""
        for token in strList:
            cmd += token + self.delimiter        
        
        #Send cmd
        cmd = str(len(cmd)).ljust(8) + cmd
        self.socket.send(cmd)
         
    def receive(self):
        #Receive reply
        ret = ""
        tmp = self.socket.recv(8)
        count = int(tmp)
        ret = self.socket.recv(count)
        return ret
    
    #Begin recorder commands
    #####################################################
    
    def isRecording(self):
        strList = []
        strList.append( "QUERY_RECORDER %s" % self.recorderID )
        strList.append( "IS_RECORDING" )
    
        return self.send_receive(strList)[0]
        #retval = boolean(self.send_receive(strList))
                         
        
    def checkChannel(self, chanNum):
        strList = []
        strList.append( "QUERY_RECORDER %s" % self.recorderID )
        strList.append( "CHECK_CHANNEL")
        strList.append( str(chanNum) )
        
        return self.send_receive(strList)[0]
    
    def setChannel(self, chanNum):
        strList = []
        strList.append( "QUERY_RECORDER %s" % self.recorderID )
        strList.append( "SET_CHANNEL")
        strList.append( str(chanNum) )
        
        return self.send_receive(strList)[0]
    
    def spawnLive(self):
        chainID = "live-" + self.localHost + "-" + str(time.clock())
        
        strList = []
        strList.append( "QUERY_RECORDER %s" % self.recorderID )
        strList.append( "SPAWN_LIVETV")
        strList.append( chainID )
        strList.append( "0" ) #pip
        
        return self.send_receive(strList)[0]
    
    def stopLive(self):
        strList = []
        strList.append( "QUERY_RECORDER %s" % self.recorderID )
        strList.append( "STOP_LIVETV")
        
        #Not sure why this doesn't fit the same protocol standard but it simply returns 'ok' rather than '2       ok'
        self.send(strList)
        return self.socket.recv(2)
    
    def getFramesWritten(self):
        strList = []
        strList.append( "QUERY_RECORDER %s" % self.recorderID )
        strList.append( "GET_FRAMES_WRITTEN")
        
        return int(self.send_receive(strList)[1])
    
    def getCurrentRecording(self):
        strList = []
        strList.append( "QUERY_RECORDER %s" % self.recorderID )
        strList.append( "GET_CURRENT_RECORDING")
        
        return self.send_receive(strList)
    
    def frontendReady(self):
        strList = []
        strList.append( "QUERY_RECORDER %s" % self.recorderID )
        strList.append( "FRONTEND_READY")
        
        return self.send_receive(strList)[0]
    
    def getInput(self):
        strList = []
        strList.append( "QUERY_RECORDER %s" % self.recorderID )
        strList.append( "GET_INPUT")
        
        return self.send_receive(strList)[0]