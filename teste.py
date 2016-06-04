import datamodels as dm

p = dm.Project.from_xml('/home/soslaio/teste.xml/project.xml')

for c in p.classes:
  for a in c.attributes:
    for tv in a.tagged_values.widget_related:
      print tv.name, tv.value
