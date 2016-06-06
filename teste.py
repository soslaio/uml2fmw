import datamodels as dm

p = dm.Project.from_xml('/home/soslaio/teste.xml/project.xml')

for c in p.classes:
  for a in c.attributes:
    if a.tipo == 'humpf':
      print c.name, a.name, a.tipo, a.is_association_attribute
    # for tv in a.tagged_values.widget_related:
    #  print tv.name, tv.value
