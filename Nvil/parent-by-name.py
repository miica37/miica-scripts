import pymel.core as pm

def parent_by_name(obj):
	name = obj.nodeName()
	parents = name.split('___')
	first_parent = parents[0]

	obj_path = '|'
	if obj.getParent():
		obj_path = obj.getParent().longName()

	first_parent_path = obj_path + '|' + first_parent
	if pm.objExists(first_parent_path):
		pm.parent(obj, first_parent_path)
		pm.rename(obj, '___'.join(parents[1:]))
	else:
		pm.group(n=first_parent)
		pm.rename(obj, '___'.join(parents[1:]))
		pm.select(obj)

	if '___' in obj.nodeName():
		parent_by_name(obj)

sels = pm.selected()

for i in sels:
	pm.select(i)
	parent_by_name(i)

pm.select(sels)
