class album:
    
    def __init__(self):
        pass
    
    def import_from_mythObject(self, mythObject):
        try:
            self.artistID = mythObject[0]
            self.name = mythObject[1]
                
        except IndexError, e:
            print "Music_Player: Found difference in DB structure for artists. Attempting to continue."
        