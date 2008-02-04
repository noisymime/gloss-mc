import os
import clutter
import pygtk
import gtk
from xml.dom import minidom

class ThemeMgr:
	defaultTheme = "default"
	currentTheme = "default"
	#currentTheme = "Pear"
	#currentTheme = "Mich"
	
	def __init__(self, glossMgr):
		self.stage = glossMgr.stage
		self.glossMgr = glossMgr
		self.docs = []
		self.default_docs = []
		
		theme_dir = "ui/" + self.currentTheme
		self.importDocs(theme_dir, self.docs)
		#If the current theme is the default theme, we just use the one list, else create a second one
		if self.currentTheme == self.defaultTheme:
			self.default_docs = self.docs
		else:
			theme_dir = "ui/" + self.defaultTheme
			self.importDocs(theme_dir, self.default_docs)

	def importDocs(self, dir, docs):
		file_list = os.listdir(dir)
		file_list = filter(self.filterXMLFile, file_list)
		
		for file in file_list:
			conf_file = dir + "/" + file
			#print conf_file
			docs.append(minidom.parse(conf_file))
	
	#Filter function for fiding XML files	
	def filterXMLFile(self, filename):
		xml_file_types = ["xml", "XML"]
		extension = filename[-3:]
		
		if extension in xml_file_types:
			return True
		else:
			return False
	
	#Loops through firstly the current theme files, then the default ones looking for an element of 'element_type' with an ID of 'element_id'
	def search_docs(self, element_type, element_id):
		texture_element = None
		
		#First loop through the current theme docs
		for doc in self.docs:
			temp_element = self.find_element(doc.getElementsByTagName(element_type), "id", element_id)
			if not temp_element is None:
				texture_element = temp_element
		
		#If texture_element is still equal to None, we check the default theme
		if (texture_element is None) and (not self.docs == self.default_docs):
			for doc in self.default_docs:
				temp_element = self.find_element(doc.getElementsByTagName(element_type), "id", element_id)
				if not temp_element is None:
					texture_element = temp_element
		
		return texture_element
	
	#Simple utity function that is used by 'search_docs' to find a matching element in an array of elements
	def find_element(self, elements, attribute, value):
		for element in elements:
			val = element.getAttribute(attribute)
			if val == value:
				#print val
				return element
			
		return None
	
	#Search through an element to find a value
	#Specifying the element name in the format 'level1. value' will result in the function looping
	def find_child_value(self, nodeList, value):
		#print "No Nodes: " + str(len(nodeList))
		#Check whether the value is in the form "xxx.y"
		values = value.find(".")
		if not values == -1:
			desiredTagName = value[:values]
			#print "test " + value[(values+1):]
			#print "blah" + tagName
			for subnode in nodeList:
				if subnode.nodeType == subnode.ELEMENT_NODE:
					#print "Tag Name: " + subnode.tagName
					if subnode.tagName == desiredTagName:
						# call function again to get children
						return self.find_child_value(subnode.childNodes, value[(values+1):])
		else:
			for subnode in nodeList:
				if (subnode.nodeType == subnode.TEXT_NODE) and (not subnode.nextSibling is None):
					subnode = subnode.nextSibling
					if subnode.localName == value:
						valueNode = subnode.childNodes[0]
						return valueNode.data
					
		#If we get to here, we hath failed
		return None
	
	#Search through an element to find an attribute
	#This is basically the same as find_child_value except it gets an attribute
	def find_attribute_value(self, nodeList, tagName, attributeID):
		#print "No Nodes: " + str(len(nodeList))
		#Check whether the value is in the form "xxx.y"
		values = tagName.find(".")
		if not values == -1:
			desiredTagName = tagName[:values]
			#print "test " + value[(values+1):]
			#print "blah" + tagName
			for subnode in nodeList:
				if subnode.nodeType == subnode.ELEMENT_NODE:
					#print "Tag Name: " + subnode.tagName
					if subnode.tagName == desiredTagName:
						# call function again to get children
						return self.find_attribute_value(subnode.childNodes, tagName[(values+1):])
		else:
			for subnode in nodeList:
				if subnode.localName == tagName:
					#print "keys: " + str(len(subnode.attributes.values()))
					if len(subnode.attributes.values()) > 0:
						return subnode.attributes[attributeID].value
						
		#If we get to here, we hath failed
		return None
	
	#Given an element, returns a subset of it based on the tag name of the subset
	def get_subnode(self, element, tag_name):
		for node in element:
			if node.nodeType == node.ELEMENT_NODE:
				if node.tagName == tag_name:
					return node.childNodes
		#Fail!
		return None
	
	
	#*********************************************************************
	# The methods below all relate to fulfilling requests for actors

	#This is the generic function for setting up an actor. 
	#It sets up all the 'common' properties:
	#Currently: size, position, opacity
	def get_value(self, type, name, property):
		element = self.search_docs(type, name).childNodes
		#Quick check to make sure we found something
		if element is None:
			return None
		
		return self.find_child_value(element, property)
	
	def setup_actor(self, actor, element, parent):
		#Set the size
		#First setup the parent
		relativeTo = str(self.find_attribute_value(element, "dimensions", "type"))
		if relativeTo == "relativeToStage":
			parent = self.stage
		elif relativeTo == "relativeToParent":
			parent = actor.get_parent()
		elif relativeTo == "relativeToSelf":
			parent = actor
		
		(width, height) = self.get_dimensions(element, parent)
		if (not width is None) and (not width == "default"): actor.set_width(width)
		if (not height is None) and (not height == "default"): 
			if height == "relative":
				xy_ratio = float(actor.get_height()) / float(actor.get_width())
				height = int(width * xy_ratio)
			actor.set_height(height)
		
		#Set the position of the actor
		(x,y) = (0,0)
		#Get the parent
		relativeTo = str(self.find_attribute_value(element, "position", "type"))
		if relativeTo == "relativeToStage":
			parent = self.stage
		elif not (relativeTo == "relativeToParent"):
			parent = None
			
		
		(x, y) = self.get_position(element, parent)
		actor.set_position(int(x), int(y))
		
		#now set the opacity
		opacity = self.find_child_value(element, "opacity")
		if not opacity is None:
			opacity = int(opacity)
			actor.set_opacity(opacity)
			
	def get_dimensions(self, element, parent):
		width = self.find_child_value(element, "dimensions.width")
		if (not width == "default") and (not width is None):
			if width[-1] == "%":
				#Quick check on parent
				if parent is None:
					print "Theme error: type must be specified when using percentage values"
					return None
				
				width = (float(width[:-1]) / 100.0) * parent.get_width()
				#print "width: " + str(width)
			width = int(width)
		else:
			width = None
		height = self.find_child_value(element, "dimensions.height")
		if (not height == "default") and (not height is None) and (not height == "relative"):
			if height[-1] == "%":
				height = (float(height[:-1]) / 100.0) * parent.get_height()
			height = int(height)
		elif height == "relative":
			pass
		else:
			height = None
		
		return (width, height)
			
	#Given an element, returns (x, y) coords for it
	def get_position(self, element, parent):
		#set the x coord
		x = self.find_child_value(element, "position.x")
		if (not x == "default") and (not x is None):
			if x[-1] == "%":
				#Quick check on parent
				if parent is None:
					print "Theme error: type must be specified when using percentage values"
					return None
				
				x = (float(x[:-1]) / 100.0) * parent.get_width()
				#print "width: " + str(width)
			elif x == "center":
				#Quick check on parent
				if parent is None:
					print "Theme error: type must be specified when using 'center' values"
					return None
				x = (parent.get_width() - actor.get_width)/2
		else:
			x = 0
				
		#set the y coord
		y = self.find_child_value(element, "position.y")
		if (not y == "default") and (not y is None):
			if y[-1] == "%":
				#Quick check on parent
				if parent is None:
					print "Theme error: type must be specified when using percentage values"
					return None
				
				y = (float(y[:-1]) / 100.0) * parent.get_height()
				#print "width: " + str(width)
			elif y == "center":
				#Quick check on parent
				if parent is None:
					print "Theme error: type must be specified when using 'center' values"
					return None
				y = (parent.get_height() - actor.get_height)/2
		else:
			y = 0
			
		return (int(x), int(y))
	
	def get_texture(self, name, parent, texture):
		texture_src = None
		if texture is None:
			texture = clutter.Texture()

		element = self.search_docs("texture", name).childNodes
		#Quick check to make sure we found something
		if element is None:
			return None
		
		#Setup the pixbuf
		src = self.find_child_value(element, "image")
		#Special case to handle no image
		if src == "None":
			return texture
		
		src = "ui/" + self.currentTheme + "/" + src
		pixbuf = gtk.gdk.pixbuf_new_from_file(src)
		texture.set_pixbuf(pixbuf)
		
		#Setup general actor properties
		self.setup_actor(texture, element, None)
		
		return texture
	
	def get_font(self, name, element):
		if element is None:
			element = self.search_docs("font", name).childNodes
		#Quick check to make sure we found something
		if element is None:
			return None
		

		face = self.find_child_value(element, "face")
		res = str(self.stage.get_width()) + "x" + str(self.stage.get_height())
		
		size = None
		defSize = None
		#Loop through all the different sizes until we find the right one (or else use the default)
		for node in element:
			if node.nodeType == node.ELEMENT_NODE:
				if node.tagName == "size":
					if node.attributes["id"].value == res:
						size = node.childNodes[0].data
					elif node.attributes["id"].value == "default":
						defSize = node.childNodes[0].data
		if size is None:
			size = defSize
		
		fontString = str(face) + " " + str(size)
		return fontString