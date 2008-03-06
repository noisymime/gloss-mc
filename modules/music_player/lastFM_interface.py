import urllib
from xml.dom import minidom
import pygtk
import gtk

class lastFM_interface:
    lastFM_base_xml_uri = "http://ws.audioscrobbler.com/1.0/"
    lastFM_artist_xml_uri = lastFM_base_xml_uri + "artist/"
    lastFM_album_xml_uri = lastFM_base_xml_uri + "album/"
    lastFM_track_xml_uri = lastFM_base_xml_uri + "track/"
    
    def __init__(self):
        pass
    
    #Returns a pixbuf with an image of the specified artist
    #Returns None if it is unable to get an image
    def get_artist_image(self, artist):
        artist_clean = artist.replace(" ", "+")
        similar_uri = self.lastFM_artist_xml_uri + artist_clean +"/similar.xml"
        filehandle = urllib.urlopen(similar_uri)
        
        #We only need the first 2 lines of this file
        xml = ""
        for x in range(2):
            xml += filehandle.readline()
        filehandle.close()
            
        #Check to see if the artist name was found
        error_string = "No artist exists with this name: '%s'" % artist
        #print "Error String: " + error_string
        #print "XML: " + xml
        if xml == error_string:
            return None
        
        #Because we only read in 2 lines, we need to manually close the block
        xml += "</similarartists>"

        dom = minidom.parseString(xml)
        element = dom.getElementsByTagName("similarartists")[0]
        pic_url = element.getAttribute("picture")
        
        return self.get_pixbuf_from_url(pic_url)
        
        
    def get_pixbuf_from_url(self, pic_url):
        img_handle = urllib.urlopen(pic_url)
        img_data = img_handle.read()
        
        loader = gtk.gdk.PixbufLoader()
        loader.write(img_data)
        loader.close()
        return loader.get_pixbuf()
        