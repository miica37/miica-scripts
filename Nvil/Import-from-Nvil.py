# Import from NVIL 
# (%user%\AppData\Roaming\DigitalFossils\NVil\Media\Clipboard\ClipboardObj.obj)

import os

# OPTIONS
#=============
RESTORE_HIERARCHY = True
IMPORT_INTO_GROUP = False

def importObj(filepath, ignoreMat=True):
	""" importObj(str) -> returns names of imported objs
	"""
	
	filepath_noext, ext = os.path.splitext(filepath) # 'c:\hello\test.txt' -> ('c:\\hello\test', '.txt')
	filename = os.path.basename(filepath)
	
	# Remember what's inside the scene before import
	all_transforms_before = cmds.ls(et='transform', long=True)
	
	# Import the obj file
	mel_import_command = 'file -import -type "OBJ" -ignoreVersion -ra true -mergeNamespacesOnClash false -rpr "import" -options "mo=1" -pr '
	mel_import_command = mel_import_command + '"' + filepath.replace('\\', '/') + '"'
	
	if ignoreMat:
		# Rename the .mtl file to .123 temporary, to forcefully avoid importing material
		mtl_file = filepath_noext + '.mtl'
		if os.path.exists(mtl_file):
			if os.path.exists(mtl_file+'.123'):
				os.remove(mtl_file+'.123')
			os.rename(mtl_file, mtl_file+'.123')
		
		# <The Main Obj Import>
		mel.eval(mel_import_command)
		
		# Rename back the .mtl
		if os.path.exists(mtl_file+'.123'):
			os.rename(mtl_file+'.123', mtl_file)
	else:
		# <The Main Obj Import>
		mel.eval(mel_import_command)

	# Select imported obj
	all_transforms_after = cmds.ls(et='transform', long=True)
	imported_objs = list(set(all_transforms_after) - set(all_transforms_before))
	imported_objs.sort()

	# Note: This is probably not necessary anymore but very old Maya used to import 
	#       with the two attributes checked off
	#for obj in imported_objs:
	#	# Turn on visible in reflection/refraction
	#	cmds.setAttr(obj + '.visibleInReflections', 1)
	#	cmds.setAttr(obj + '.visibleInRefractions', 1)
	
	cmds.select(imported_objs)

	return imported_objs

# user_dir = os.path.expanduser('~user')
user_dir = os.getenv('USERPROFILE')
nvil_clipboard_obj = os.path.join(user_dir, 'AppData/Roaming/DigitalFossils/NVil/Media/Clipboard/ClipboardObj.obj')
nvil_clipboard_dir = os.path.normpath(nvil_clipboard_obj)
if os.path.isfile(nvil_clipboard_obj):
	imported = importObj(nvil_clipboard_obj)
	imported = [pm.PyNode(o) for o in imported]
	
	# Update user on what's imported
	import maya.OpenMaya
	maya.OpenMaya.MGlobal.displayInfo("Imported {0} objects. ('{1}')".format(len(imported), nvil_clipboard_obj))
	
	# Put it into a temporary group
	pm.select(clear=True)
	imported_group = pm.group(imported, name='import_obj')
	
	for o in imported:
		pm.rename(o, o.nodeName().replace('import_', ''))

	if RESTORE_HIERARCHY:
		for obj in imported:
			objname = obj.nodeName()
			if '___' in objname and objname[-3:] != '___':
				l = objname.split('___')
				basename = l[-1]
				parentname = '___'.join(l[:-1]) + '___'
				for o in imported:
					if o.nodeName() == parentname:
						pm.parent(obj, o)
						pm.rename(obj, basename)

	for o in imported:
		if o.nodeName()[-3:] == '___':
			pm.rename(o, o.nodeName()[:-3])
	
	# Ungroup
	if not IMPORT_INTO_GROUP:
		for child in imported_group.getChildren():
			pm.parent(child, world=True)
		pm.delete(imported_group)

	pm.select(imported)
else:
	cmds.warning("File '{0}' does not exists.".format(nvil_clipboard_obj))

