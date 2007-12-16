import os
import clutter
from xml.dom import minidom

class ThemeMgr:
	defaultTheme = "default"
	currentTheme = "default"
	
	def __init__(self):
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
			docs.append(minidom.parse(conf_file))
	
	#Filter function for fiding XML files	
	def filterXMLFile(self, filename):
		xml_file_types = ["xml", "XML"]
		extension = filename[-3:]
		
		if extension in xml_file_types:
			return True
		else:
			return False
			
	def get_texture(self, name):
		texture_src = None
		texture = clutter.Texture()

		element = self.search_docs("texture", name)
		#Quick check to make sure we found something
		if element is None:
			return None
		
		return element
					
	def setup_actor(self, actor, element):
		pass
	
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
		print "No Nodes: " + str(len(nodeList))
		#Check whether the value is in the form "xxx.y"
		values = value.find(".")
		if not values == -1:
			desiredTagName = value[:values]
			#print "test " + value[(values+1):]
			#print "blah" + tagName
			for subnode in nodeList:
				if subnode.nodeType == subnode.ELEMENT_NODE:
					print "Tag Name: " + subnode.tagName
					if subnode.tagName == desiredTagName:
						# call function again to get children
						return self.find_child_value(subnode.childNodes, value[(values+1):])
		else:
			for subnode in nodeList:
				if subnode.nodeType == subnode.TEXT_NODE:
					subnode = subnode.nextSibling
					if subnode.localName == value:
						valueNode = subnode.childNodes[0]
						#print subnode.localName + ": " + valueNode.data
						return valueNode.data
		