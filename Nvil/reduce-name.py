
sels = pm.selected()

for obj in sels:
	name = obj.nodeName()
	basename = name.rsplit('___', 1)[-1]
	pm.rename(obj, basename)

pm.select(sels)
