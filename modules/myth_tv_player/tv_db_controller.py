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
            
        return channels
            
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
        try:
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
        except IndexError, e:
            print "TV_Player: Found difference in DB structure for channels. Attempting to continue."
        
class show:
    
    def __init__(self):
        pass
    
    def import_from_mythObject(self, mythObject):
        try:
            self.chanID = mythObject[0]
            self.starttime = mythObject[1]
            self.endtime = mythObject[2]
            self.title = mythObject[3]
            self.subtitle = mythObject[4]
            self.description = mythObject[5]
            self.category = mythObject[6]
            self.category_type = mythObject[7]
            self.airdate = mythObject[8]
            self.stars = mythObject[9]
            self.previouslyshown = mythObject[10]
            self.title_pronounce = mythObject[11]
            self.stereo = mythObject[12]
            self.subtitled = mythObject[13]
            self.hdtv = mythObject[14]
            self.closecaptioned = mythObject[15]
            self.partnumber = mythObject[16]
            self.parttotal = mythObject[17]
            self.seriesid = mythObject[18]
            self.originalairdate = mythObject[19]
            self.showtype = mythObject[20]
            self.colorcode = mythObject[21]
            self.syndicatedepisodenumber = mythObject[22]
            self.programid = mythObject[23]
            self.manualid = mythObject[24]
            self.generic = mythObject[25]
            self.listingsource = mythObject[26]
            self.first = mythObject[27]
            self.last = mythObject[28]
        except IndexError, e:
            print "TV_Player: Found difference in DB structure for show. Attempting to continue."