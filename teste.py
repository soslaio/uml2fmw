from models.project import Project as proj

p = proj.Project.from_xml('/home/soslaio/teste.xml/project.xml')

for c in p.classes:
  for a in c.attributes:
    print c.name, a.name, a.stereotypes.find('association_attribute')
    # print c.name, a.name, a.tipo, a.is_association_attribute
    # for tv in a.tagged_values.widget_related:
    #  print tv.name, tv.value
