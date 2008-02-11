import time
import datetime

class tv_db_controller:
    title = "TV"

    def __init__(self, dbMgr):
        self.dbMgr = dbMgr
        
    def get_channels(self):
        sql = "SELECT * FROM channel WHERE channum <> ''"
        results = self.dbMgr.run_sql(sql)
        
        channels = []
        
        for entry in results:
            tmpChannel = channel()
            tmpChannel.import_from_mythObject(entry)
            channels.append(tmpChannel)
            
    def get_current_show(self, chanID):
        timeString = time.strftime( "%Y-%m-%d %H:%M:%S" )
        tim = time.strptime(time.ctime())
        myDateTime = datetime.datetime(*tim[0:6])
        sql = "SELECT * FROM program WHERE chanid = %s AND starttime < '%s' AND endtime > '%s'" % (str(chanID), myDateTime, myDateTime)
        #print sql
        result = self.dbMgr.run_sql(sql)
        
        tmpShow = show()
        if len(result) > 0:
            tmpShow.import_from_mythObject(result[0])
            return tmpShow
        
class channel:
    
    def __init__(self):
        pass
    
    def import_from_mythObject(self, mythObject):
        self.chanID = mythObject[0]
        self.channum = mythObject[1]
        self.freqid = mythObject[2]
        self.sourceid = mythObject[3]
        self.callsign = mythObject[4]
        self.name = mythObject[5]
        self.icon = mythObject[6]
        self.finetune = mythObject[7]
        self.videofilters = mythObject[8]
        self.xmltvid = mythObject[9]
        self.recpriority = mythObject[10]
        self.contrast = mythObject[11]
        self.brightness = mythObject[12]
        self.colour = mythObject[13]
        self.hue = mythObject[14]
        self.tvformat = mythObject[15]
        self.commfree = mythObject[16]
        self.visible = mythObject[17]
        self.outputfilters = mythObject[18]
        self.useonairguide = mythObject[19]
        self.mplexid = mythObject[20]
        self.serviceid = mythObject[21]
        self.atscsrcid = mythObject[22]
        self.tmoffset = mythObject[23]
        self.atsc_major_chan = mythObject[24]
        self.atsc_minor_chan = mythObject[25]
        self.last_record = mythObject[26]
        
class show:
    
    def __init__(self):
        pass
    
    def import_from_mythObject(self, mythObject):
        self.chanID = mythObject[0]
        self.channum = mythObject[1]
        self.freqid = mythObject[2]
        self.sourceid = mythObject[3]
        self.callsign = mythObject[4]
        self.name = mythObject[5]
        self.icon = mythObject[6]
        self.finetune = mythObject[7]
        self.videofilters = mythObject[8]
        self.xmltvid = mythObject[9]
        self.recpriority = mythObject[10]
        self.contrast = mythObject[11]
        self.brightness = mythObject[12]
        self.colour = mythObject[13]
        self.hue = mythObject[14]
        self.tvformat = mythObject[15]
        self.commfree = mythObject[16]
        self.visible = mythObject[17]
        self.outputfilters = mythObject[18]
        self.useonairguide = mythObject[19]
        self.mplexid = mythObject[20]
        self.serviceid = mythObject[21]
        self.atscsrcid = mythObject[22]
        self.tmoffset = mythObject[23]
        self.atsc_major_chan = mythObject[24]
        self.atsc_minor_chan = mythObject[25]
        self.last_record = mythObject[26]