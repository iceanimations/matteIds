'''
Created on Sep 8, 2015

@author: qurban.ali
'''
import pymel.core as pc

def getMeshes():
    chars = pc.ls('characters')
    if chars:
        return [x for x in chars[0].getChildren() if type(x) == pc.nt.Transform and x.getShapes(ni=True)]
    else: return []

def getMtls(mtls):
    pc.ls(type=mtls)
    
def getSelectedMeshes():
    sl = pc.ls(sl=True, type='mesh', dag=True)
    return [obj.firstParent().name() for obj in sl]