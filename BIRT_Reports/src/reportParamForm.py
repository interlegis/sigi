'''
Created on 02/05/2011

@author: sesostris
'''

import os
import sys
import xml.dom.minidom as minidom

fileName = "../listaCasas.rptdesign"

doc = minidom.parse(fileName)
parameterTags = doc.getElementsByTagName("parameters")

for parameterTag in parameterTags:
    formFields = {}
    for parameter in parameterTag.childNodes:
        if parameter.nodeName != '#text':
            formField = {}
            
            for property in parameter.childNodes:
                if property.nodeName != '#text':
                    formField[property.getAttribute('name').encode('ascii')] = property.childNodes[0].nodeValue
                    
            formFields[parameter.getAttribute('name').encode('ascii')] = formField

print formFields

for fieldName in formFields:
    print fieldName, ':', formFields[fieldName]['valueType'] 