import MySQLdb
import os

class mythVideoDB():

    def __init__(self):
        self.server = "127.0.0.1" #"192.168.0.1"
        self.db = "mythconverg"
        self.uid = "root"
        self.passwd = ""
        self.connected = True
        self.read_config()
        
        try:
            self.db = MySQLdb.connect(self.server, self.uid, self.passwd,self.db)
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            self.connected = False
        
        self.cursor = self.db.cursor()
        self.get_gallery_directory()

        #cursor.execute("SELECT * FROM videometadatagenre")
        # get the resultset as a tuple
        #result = cursor.fetchall()
        # iterate through resultset
        #for record in result:
            #print record[0] , "-->", record[1]
            
    #Attempts to read the local mythtv config file to get the server, username and password
    def read_config(self):
        conf_file = os.path.expanduser("~/.mythtv/mysql.txt")
        if not os.path.exists(conf_file):
            return False
  
        f=open(conf_file, 'r')
        for line in f:
            if (not line[0] == "#"):
                variables = line.rsplit("=")
                
                if variables[0] == "DBHostName":
                    self.server = variables[1].rstrip()
                if variables[0] == "DBUserName":
                    self.uid = variables[1].rstrip()
                if variables[0] == "DBPassword":
                    self.passwd = variables[1].rstrip()
                if variables[0] == "DBName":
                    self.db = variables[1].rstrip()
    
        
            
    def get_videos(self):
        if not self.connected:
            print "Unable to start video, could not establish connection to SQL server"
            return None
    
        sql = "SELECT * FROM videometadata WHERE coverfile <> 'No Cover'"
        
        self.cursor.execute(sql)
        # get the resultset as a tuple
        result = self.cursor.fetchall()
        
        return result
        
    def get_gallery_directory(self):
        if not self.connected:
            print "Unable to start video, could not establish connection to SQL server"
            return None
        
        sql = "SELECT * FROM settings where value = 'GalleryDir'"
        
        self.cursor.execute(sql)
        # get the resultset as a tuple
        return self.cursor.fetchall()[1][1]
    
    def close_db(self):
        if self.connected:
            self.cursor.close()
            self.db.close()
