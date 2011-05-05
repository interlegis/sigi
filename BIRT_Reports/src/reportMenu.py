'''
Created on 27/04/2011

@author: sesostris
'''

import os
import xml.dom.minidom as minidom

path="../"  # insert the path to the directory of interest here
dirList=os.listdir(path)
for fname in dirList:
    if fname.find(".rptdesign") != -1:
        nome = fname
        titulo = "- Sem titulo -"
        
        doc = minidom.parse(path+fname)
        root = doc.childNodes.item(0)
        
        for element in root.childNodes:
            if (element.localName == "text-property" and element.hasAttribute("name")):
                name  = element.getAttribute("name")
                value = element.childNodes[0].data
                if name == "title":
                    titulo = value
                elif name == "displayName":
                    nome = value
        
        print nome + ": " + titulo
