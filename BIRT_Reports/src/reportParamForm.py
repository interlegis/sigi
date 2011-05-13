'''
Created on 02/05/2011

@author: sesostris
'''

import os
import sys
import xml.dom.minidom as minidom

fileName = "../teste_parametros.rptdesign"

doc = minidom.parse(fileName)
parameterTags = doc.getElementsByTagName("parameters")

formFields = {}

for parameterTag in parameterTags:
    for parameter in parameterTag.childNodes:
        if parameter.nodeName != '#text':
#            print "Processando campo ", parameter.getAttribute('name').encode('ascii')
            formField = {}
            
            for property in parameter.childNodes:
                if property.nodeName != '#text' and property.hasChildNodes():
#                    print "    Processando propriedade ", property.getAttribute('name').encode('ascii'), "(", property.__class__, ")"
                    fieldName  = property.getAttribute('name').encode('ascii')
                    fieldValue = property.childNodes[0].nodeValue
                    
                    if fieldName == 'selectionList':
                        fieldValue = ()
                        for structure in property.getElementsByTagName('structure'):
                            s = {}
                            for structProp in structure.getElementsByTagName('property'):
                                s[structProp.getAttribute('name').encode('ascii')] = structProp.childNodes[0].nodeValue
                            fieldValue = fieldValue + (s,)
                    
                    formField[fieldName] = fieldValue 
            
            if formField['valueType'] == 'dynamic':
                for dataSets in doc.getElementsByTagName("data-sets"):
                    for dataSet in dataSets.getElementsByTagName("oda-data-set"):
                        if dataSet.getAttribute('name') == formField['dataSetName']:
                            for xmlProp in dataSet.getElementsByTagName('xml-property'):
                                if xmlProp.getAttribute('name') == 'queryText':
                                    formField['queryText'] = xmlProp.childNodes[0].data


                                         
                    
            formFields[parameter.getAttribute('name').encode('ascii')] = formField

#print formFields
#exit(0)

for field in formFields:
    print "field '" + field + "':"
    for param in formFields[field]:
        print '    ', param, ' = "', formFields[field][param], '"' 

'''form = '<form action="printReport" method="post">'
for fieldName in formFields:
    htmlField = '<input name="' + fieldName + '" ' 
    field = formFields[fieldName]
    print fieldName, ':', formFields[fieldName]['controlType'], field
    
    if field['controlType'] == 'text-box':
        htmlField += 'type = "text">'
    elif field['controlType'] == 'list-box':
        htmlField += 'type = "select">'
    form += htmlField
print form + '</form>'''