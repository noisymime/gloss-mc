import MySQLdb

class mythVideoDB():

    def __init__(self):
        self.server = "127.0.0.1" #"192.168.0.1"
        self.db = "mythconverg"
        self.uid = "root"
        self.passwd = ""
        
        db = MySQLdb.connect(self.server, self.uid, self.passwd,self.db)
        
        self.cursor = db.cursor()
        #cursor.execute("SELECT * FROM videometadatagenre")
        # get the resultset as a tuple
        #result = cursor.fetchall()
        # iterate through resultset
        #for record in result:
            #print record[0] , "-->", record[1]
            
    def get_videos(self):
        sql = "SELECT * FROM videometadata WHERE coverfile <> 'No Cover'"
        
        self.cursor.execute(sql)
        # get the resultset as a tuple
        result = self.cursor.fetchall()
        
        return result