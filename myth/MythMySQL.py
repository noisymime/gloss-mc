import MySQLdb
import os, socket
import clutter

class mythDB():

    def __init__(self):

        self.localHost = socket.gethostname()
        if not self.read_config():
            self.connected = False
            return
        
        try:
            self.db = MySQLdb.connect(self.server, self.uid, self.passwd,self.db)
            self.connected = True
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            clutter.main_quit()
            self.connected = False
            return None
        
        self.cursor = self.db.cursor()
            
    #Attempts to read the local mythtv config file to get the server, username and password
    def read_config(self):
        conf_file = os.path.expanduser("~/.mythtv/mysql.txt")
        if not os.path.exists(conf_file):
            print "ERROR: No config file found at ~.mythtv/mysql.txt!"
            print "No connection to MythTV Database can be made. Quitting"
            clutter.main_quit()
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
        
        return True
    
    def run_sql(self, sql):
        if not self.connected:
            print "Unable to perform lookup, could not establish connection to SQL server"
            return None
    
        self.cursor.execute(sql)
        # get the resultset as a tuple
        result = self.cursor.fetchall()
        return result
        
    #Gets an arbitary setting from the settings table
    def get_setting(self, setting_name):
        if not self.connected:
            print "Error: Could not establish connection to SQL server. Unable to obtain setting '" + setting_name + "'"
            return None
        
        sql = "SELECT * FROM settings where value = '" + setting_name + "' AND hostname = '" + self.localHost + "'"
        
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        if data == ():
            sql = "SELECT * FROM settings where value = '" + setting_name + "'"
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            if not data == ():
                return data[1][1]
            else:
                return None
        
        # get the resultset as a tuple
        return data[0][1]
    
    def set_setting(self, setting, value):
        if not self.connected:
            print "Error: Could not establish connection to SQL server. Unable to obtain setting '" + setting_name + "'"
            return None
        
        sql = "INSERT INTO settings VALUES('%s', '%s', '%s')" % (setting, value, self.localHost)
        self.cursor.execute(sql)
    
    #Gets the backend server details, which, in theory, can be different from the SQL server details and/or default port
    def get_backend_server(self):
        if not self.connected:
            print "Unable to get backend details, could not establish connection to SQL server"
            return None
        
        sql = "SELECT * FROM settings where value = 'BackendServerIP'"
        self.cursor.execute(sql)
        # get the resultset as a tuple
        server =  self.cursor.fetchall()[0][1]
       
        sql = "SELECT * FROM settings where value = 'BackendServerPort'"
        self.cursor.execute(sql)
        # get the resultset as a tuple
        port =  self.cursor.fetchall()[0][1]
        
        return (server, int(port))
    
    def close_db(self):
        if self.connected:
            self.cursor.close()
            self.db.close()
