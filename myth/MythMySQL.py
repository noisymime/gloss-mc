import MySQLdb

class mythVideoDB():

    def __init__(self):
        self.server = "127.0.0.1" #"192.168.0.1"
        self.db = "mythconverg"
        self.uid = "root"
        self.passwd = ""
        self.connected = True
        
        try:
            self.db = MySQLdb.connect(self.server, self.uid, self.passwd,self.db)
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            self.connected = False
        
        self.cursor = self.db.cursor()
        #cursor.execute("SELECT * FROM videometadatagenre")
        # get the resultset as a tuple
        #result = cursor.fetchall()
        # iterate through resultset
        #for record in result:
            #print record[0] , "-->", record[1]
            
    def get_videos(self):
        if not self.connected:
            print "Unable to start video, could not establish connection to SQL server"
            return None
    
        sql = "SELECT * FROM videometadata WHERE coverfile <> 'No Cover'"
        
        self.cursor.execute(sql)
        # get the resultset as a tuple
        result = self.cursor.fetchall()
        
        return result
    
    def close_db(self):
        if self.connected:
            self.cursor.close()
            self.db.close()
