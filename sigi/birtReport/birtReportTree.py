# -*- encoding: utf-8 -*-
'''
Created on 11/05/2011

@author: sesostris
'''

import os
import xml.dom.minidom as minidom

class BirtReportTree():
    '''Gerencia uma árvore de relatórios birtReports, permitindo montar telas
       de navegação (menus) para acessar os relatórios'''
    birtReportRoot = '/'

    def __init__(self, root = '/'):
        self.birtReportRoot = root
    
    def getRootItems(self):
        return self.getFolderItems('')
    
    def getFolderItems(self, folder):
        folder  = self.birtReportRoot + folder
        items   = {'folders': {}, 'reports': {}}
        dirList = os.listdir(folder)
        
        for fname in dirList:
            name  = fname
            title = "- * -"
            
            if os.path.isdir(folder + fname) and fname[0] != '.':
                # Tratar folders #
                if os.path.isfile(folder + fname + '/.birtfolder'):
                    fd = os.open(folder + fname + '/.birtfolder', os.O_RDONLY)
                    try:
                        data = eval(os.read(fd, 4096))
                        name  = data['name']
                        title = data['title']
                    finally:
                        os.close(fd)
                items['folders'][fname] = {'name': name, 'title': title}
            elif fname[-10:] == '.rptdesign' and fname[0] != '.':
                doc  = minidom.parse(folder + fname)
                root = doc.documentElement

                for element in root.childNodes:
                    if (element.localName == "text-property" and element.hasAttribute("name")):
                        name  = element.getAttribute("name")
                        value = element.childNodes[0].data
                        if name == "title":
                            title = value
                        elif name == "displayName":
                            name = value
        
                items['reports'][fname] = {'name': name, 'title': title}

        return items