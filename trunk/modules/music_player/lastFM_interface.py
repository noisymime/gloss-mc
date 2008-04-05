import urllib
import xml
from xml.dom import minidom
import pygtk
import gtk
import gobject
from itertools import izip, repeat, chain

class lastFM_interface:
    lastFM_base_xml_uri = "http://ws.audioscrobbler.com/1.0/"
    lastFM_artist_xml_uri = lastFM_base_xml_uri + "artist/"
    lastFM_album_xml_uri = lastFM_base_xml_uri + "album/"
    lastFM_track_xml_uri = lastFM_base_xml_uri + "track/"
    
    #Maximum size of images returned
    #If images are larger than this, they will be downloaded and resized
    max_image_width = 800
    max_image_height = 600
    
    def __init__(self):
        pass
    
    #Returns a pixbuf with an image of the specified artist
    #Returns None if it is unable to get an image
    def get_artist_image(self, artist):
        artist_clean = artist.replace(" ", "+")
        artist_clean = artist_clean.replace("/", "+")
        similar_uri = self.lastFM_artist_xml_uri + artist_clean +"/similar.xml"
        filehandle = urllib.urlopen(similar_uri)
        
        #We only need the first 2 lines of this file
        xml_string = ""
        for x in range(2):
            xml_string += filehandle.readline()
        filehandle.close()
            
        #Check to see if the artist name was found
        error_string = "No artist exists with this name"
        #print "Error String: " + error_string
        #print "XML: " + xml
        if xml_string[0:len(error_string)] == error_string:
            return None
        
        #We make a little manual change to the url, so that we get a bigger pic off last.FM rather than the 160x160 one
        #xml_string = xml_string.replace("/160/", "/_/") #Force use this to get BIG images
        xml_string = xml_string.replace("/160/", "/500/") #Attempt to use the 500 size image
        
        #Because we only read in 2 lines, we need to manually close the block
        xml_string += "</similarartists>"
        
        try:
            dom = minidom.parseString(xml_string)
            element = dom.getElementsByTagName("similarartists")[0]
            pic_url = element.getAttribute("picture")
        except xml.parsers.expat.ExpatError, e:
            print "LastFM Error: Could not parse XML '%s'" % (xml_string)
            print "LastFM Error: URI Attempted '%s'" % (similar_uri)
            return None
        
        #We do a check to see if a 500 size image exists
        #If not, fall back onto the _ size image (ie the Biggest Last.fm has)
        img_handle = urllib.urlopen(pic_url)
        img_size = int(img_handle.info().getheader("Content-Length"))
        if img_size == 0:
            pic_url = pic_url.replace("/500/", "/_/")
        img_handle.close()
        
        return self.get_pixbuf_from_url(pic_url)
        

    def get_pixbuf_from_url(self, pic_url):
        chunk_size = 32768
        
        img_handle = urllib.urlopen(pic_url)
        img_size = int(img_handle.info().getheader("Content-Length"))
        img_data = img_handle.read(img_size)
        img_handle.close()
        
        #print pic_url
        #print "Img Size: " + str(img_size)
        #print "Read size: " + str(len(img_data))
        
        loader = gtk.gdk.PixbufLoader()
        try:
            #This is a nasty hack to get over GDK Bug: http://bugzilla.gnome.org/show_bug.cgi?id=494667
            for chunk in izip(*[chain(img_data, repeat('', chunk_size-1))] * chunk_size):
                loader.write(''.join(chunk))
                
            loader.close()
        except gobject.GError, e:
            print "Last.FM: '%s'" % (e)
            #print "Last.FM: Received invalid image file: '%s' " % (pic_url)
        
        pixbuf = loader.get_pixbuf()
        
        #If the image is larger than our maximum size, shrink it down
        #This should _generally_ not be needed, but will be used whenver last.fm returns a very large image by mistake
        if pixbuf.get_width() > self.max_image_width:
            yx_ratio = float(pixbuf.get_height()) / float(pixbuf.get_width())
            height = int(self.max_image_width * yx_ratio)
            pixbuf = pixbuf.scale_simple(self.max_image_width, height, gtk.gdk.INTERP_HYPER)
        elif pixbuf.get_height() > self.max_image_height:
            xy_ratio = float(pixbuf.get_width()) / float(pixbuf.get_height())
            width = int(self.max_image_height * xy_ratio)
            pixbuf = pixbuf.scale_simple(width, self.max_image_height, gtk.gdk.INTERP_HYPER)
        
        return pixbuf
        