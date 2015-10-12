'''
Created on Sep 8, 2015

@author: qurban.ali
'''
import pymel.core as pc

matteIdsObjectsSetName = 'matte_ids_objects'

def getMeshes():
    chars = pc.ls(matteIdsObjectsSetName)
    if chars:
        return [x for x in chars[0].members() if type(x) == pc.nt.Transform and x.getShapes(ni=True)]
    else: return []

def getSelectedMeshes():
    sl = pc.ls(sl=True, type='mesh', dag=True)
    return [obj.firstParent().name() for obj in sl]

def addMeshesToSet(meshes):
    objSet = pc.ls(matteIdsObjectsSetName)
    if objSet:
        pc.sets(objSet[0], e=True, fe=meshes)
    else:
        sl = pc.ls(sl=True)
        pc.select(meshes)
        pc.sets(name=matteIdsObjectsSetName)
        pc.select(sl)
    