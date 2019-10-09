# Export to NVIL 
# (%user%\AppData\Roaming\DigitalFossils\NVil\Media\Clipboard\ClipboardObj.obj)

import os
import pymel.core.nodetypes as nt

def getTransforms(shapeList, fullPath=False):
	transforms = []
	for node in shapeList:
		if 'transform' != pm.nodeType(node):
			parent = pm.listRelatives(node, fullPath=fullPath, parent=True)
			transforms.append(parent[0])
	return transforms

def exportObj(objName, exportDir, zeroSRT=True, ignoreMat=True):
	sels = pm.selected()
	
	# filter out construction history
	sels = [i for i in sels if (i.nodeType() == 'transform' or i.nodeType() == 'mesh')]
	pm.select(sels)
	
	if len(sels) < 1:
		cmds.confirmDialog(title="Oops", message="Nothing selected!")
		return False
	
	if not objName or objName == '':
		cmds.confirmDialog(title="Oops", message="Please give it a name!")
		return False
	
	objsSRT = None
	if zeroSRT:
		objsSRT = {}
		# Store SRT for selected objects
		for obj in sels:
			s = obj.scale.get()
			r = obj.rotate.get()
			t = obj.translate.get()
			objsSRT[obj] = (s,r,t)
			# Then zero them out (For Scale it is set to 1)
			obj.scale.set((1,1,1))
			obj.rotate.set((0,0,0))
			obj.translate.set((0,0,0))
	
	obj_filepath = os.path.join(exportDir, objName+'.obj')
	
	ignoreMat = 0 if ignoreMat else 1
	pm.exportSelected(obj_filepath, pr=True, typ='OBJexport', es=1, force=True, \
		op="groups=1;ptgroups=1;materials={0};smoothing=1;normals=1".format(ignoreMat))
	
	# Display to user
	import maya.OpenMaya as OpenMaya
	OpenMaya.MGlobal.displayInfo("Exported to '{0}'.".format(obj_filepath))
	
	if objsSRT:
		# Restore SRT for selected objects
		for obj in sels:
			obj.scale.set(objsSRT[obj][0])
			obj.rotate.set(objsSRT[obj][1])
			obj.translate.set(objsSRT[obj][2])

orig_selections = pm.selected()

# Get a list of all the meshes (including the childrens that are not directly selected)
meshes = []
for i in pm.selected():
	meshshapes = pm.listRelatives(i, allDescendents=True, type='mesh')
	l = getTransforms(meshshapes, fullPath=True)
	for i in l:
		if i not in meshes:
			meshes.append(i)

pm.select(cl=True)

objs_to_export = []
dups = []

def objectContainsTransforms(obj):
	for child in obj.getChildren():
		if isinstance(child, nt.Transform):
			return True
	return False

for o in meshes:
	# If the object has a parent, we duplicate it, then parent to the world
	#  then rename it based on its hierarchy, replacing '|' with '___'
	# We parent it to the world to make sure the name is as what we gave to it inside the obj file
	#  Multiple level of parenting results in unpredictable name inside the obj file
	if o.getParent(): 
		l = (o.longName()[1:].split('|'))
		grouped_name = '___'.join(l) # bake group hierarchy into name
		dup = pm.duplicate(o)
		pm.rename(dup, grouped_name)
		pm.parent(dup, world=True)
		objs_to_export.append(dup)
		dups.append(dup)
	# If it contains any children, duplicate it without the children
	elif objectContainsTransforms(o):
		dup = pm.duplicate(o)[0]
		for child in dup.getChildren():
			if isinstance(child, nt.Transform):
				pm.delete(child)
		pm.rename(dup, o.nodeName() + '___')
		objs_to_export.append(dup)
		dups.append(dup)
	# Else if it's not parented to anything, and has no children, just export as it is
	else:
		objs_to_export.append(o)
		continue

pm.select(objs_to_export)

# user_dir = os.path.expanduser('~user')
user_dir = os.getenv('USERPROFILE')
nvil_clipboard_dir = os.path.join(user_dir, 'AppData/Roaming/DigitalFossils/NVil/Media/Clipboard')
nvil_clipboard_dir = os.path.normpath(nvil_clipboard_dir)
# <The Main Obj Export>
exportObj('ClipboardObj', nvil_clipboard_dir, False, True)

# Clean up duplicates
pm.delete(dups)

# Restore selections
pm.select(orig_selections)
