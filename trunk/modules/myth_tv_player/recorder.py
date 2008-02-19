

class recorder():
    delimiter = "[]:[]"
    
    def __init__(self, recorderID, socket):
        self.recorderID = recorderID
        self.socket = socket
        
    def send_receive(self, strList):
        #Setup the cmd string
        cmd = ""
        for token in strList:
            cmd += token + self.delimiter
        
        #Send cmd
        cmd = str(len(cmd)).ljust(8) + cmd
        self.socket.send(cmd)
         
        #Receive reply
        ret = ""
        tmp = self.socket.recv(8)
        count = int(tmp)
        ret = self.socket.recv(count)

        #print "read<--" + ret
        return ret
    
    #Begin recorder commands
    #####################################################
    
    def IsRecording(self):
        strList = []
        strList.append( "QUERY_RECORDER %s" % self.recorderID )
        strList.append( "IS_RECORDING" )
        
        retval = boolean(self.send_receive(strList)
    
    def checkChannel(self, chanID):
        strList = []
        strList.append( ")