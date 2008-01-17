class videoItem():
    def __init(self):
        self.mythID = None
        
    def importFromMythObject(self, mythObject):
        self.mythID = mythObject[0]
        self.title = mythObject[1]
        self.director = mythObject[2]
        self.plot = mythObject[3]
        self.rating = mythObject[4]
        self.inetRef = mythObject[5]
        self.year = mythObject[6]
        self.userRating = mythObject[7]
        self.length = mythObject[8]
        self.showLevel = mythObject[9]
        self.filename = mythObject[10]
        self.coverfile = mythObject[11]
        self.childID = mythObject[12]
        self.browse = mythObject[13]
        self.playCommand = mythObject[14]
        self.category = mythObject[15]
        
    def getTitle(self):
        return self.title
    def getCoverfile(self):
        return self.coverfile