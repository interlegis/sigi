'''
Created on 11/05/2011

@author: sesostris
'''
import os
import xml.dom.minidom as minidom

class BirtReport():
    '''
    Handles a birtReport report
    '''
    
    rptFile = ''

    def __init__(self, rptFile):
        '''
        rptFile param is the FQN of birt report file 
        '''
        self.rptFile = rptFile
        
    def rptExists(self):
        return os.path.isfile(self.rptFile)
    
    def getReportParams(self):
        if not self.rptExists():
            return {}
        
        formFields    = {}
        doc           = minidom.parse(self.rptFile)
        parameterTags = doc.getElementsByTagName("parameters")

        for parameterTag in parameterTags:
            for parameter in parameterTag.childNodes:
                if parameter.nodeType != minidom.Element.TEXT_NODE:
                    formField = {}
                    for property in parameter.childNodes:
                        if property.nodeType != minidom.Element.TEXT_NODE and property.hasChildNodes():
                            fieldName  = property.getAttribute('name').encode('ascii')
                            fieldValue = property.childNodes[0].nodeValue
                    
                            if fieldName == 'selectionList':
                                fieldValue = ()
                                for structure in property.getElementsByTagName('structure'):
                                    s = {}
                                
                                    for structProp in structure.getElementsByTagName('property'):
                                        s[structProp.getAttribute('name').encode('ascii')] = structProp.childNodes[0].nodeValue
                                    
                                    fieldValue = fieldValue + (s,)
                                    
                            if fieldName == 'defaultValue':
                                fieldValue = ()
                                for value in property.getElementsByTagName('value'):
                                    if value.getAttribute('type') == 'constant':
                                        fieldValue = fieldValue + (value.childNodes[0].nodeValue, )
                    
                            formField[fieldName] = fieldValue 
            
                    if formField['valueType'] == 'dynamic':
                        for dataSets in doc.getElementsByTagName("data-sets"):
                            for dataSet in dataSets.getElementsByTagName("oda-data-set"):
                                if dataSet.getAttribute('name') == formField['dataSetName']:
                                    for xmlProp in dataSet.getElementsByTagName('xml-property'):
                                        if xmlProp.getAttribute('name') == 'queryText':
                                            formField['queryText'] = xmlProp.childNodes[0].data
                        
                        try:
                            from django.db import connection
                            cursor = connection.cursor()
                            cursor.execute(formField['queryText'])
                            resultSet = cursor.fetchall()
                            formField['selectionList'] = ()
                            for record in resultSet:
                                formField['selectionList'] = formField['selectionList'] + ({'value': record[0],'label': record[1]},)
                                
#                            formField['selectionList'] = resultSet
                        except:
                            formField['selectionList'] = {}
                    
                    formFields[parameter.getAttribute('name').encode('ascii')] = formField

        return formFields
    
    def getName(self):
        doc  = minidom.parse(self.rptFile)
        root = doc.documentElement

        for element in root.childNodes:
            if (element.localName == "text-property" and element.hasAttribute("name") and element.getAttribute("name") == 'displayName'):
                return element.childNodes[0].data
    
    def getTitle(self):
        doc  = minidom.parse(self.rptFile)
        root = doc.documentElement

        for element in root.childNodes:
            if (element.localName == "text-property" and element.hasAttribute("name") and element.getAttribute("name") == 'title'):
                return element.childNodes[0].data
        
        

#r = birtReport('/home/sesostris/workspace/sigi/BIRT_Reports/teste_parametros.rptdesign')
#p = r.getReportParams()
#print p['prm_estado']

#for q in p:
#    print q