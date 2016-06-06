# -*- coding: utf-8 -*-
"""
    Módulo com classes de dados que representam o documento XML.

    Os principais atributos XML e tagged values são expostos para
    através de propsiedades para facilitar o uso.
"""

import logging
from collections import OrderedDict
from lxml import objectify, etree


class Base(object):
    """ Objeto base para as classes de dados. """

    def __init__(self, xml_attributes):
        self.xml_attributes = xml_attributes

    @property
    def name(self):
        """Nome do objeto."""
        return self.xml_attributes['Name'] if 'Name' in self.xml_attributes.keys() else ''

    @property
    def lower_name(self):
        """Nome do objeto em caixa baixa."""
        return self.name.lower()

    @property
    def id(self):
        """ID do objeto."""
        return self.xml_attributes['Id']


class TaggedValue(Base):
    """Objeto que representa um tagged value."""

    def __init__(self, xml_attributes, xmlobj=None):
        self.xml_attributes = xml_attributes
        self.datatype = dict()
        if 'Value' not in self.xml_attributes.keys():
            xmldatatypes = xmlobj.iterdescendants(tag="DataType")
            for dt in xmldatatypes:
                self.datatype = dt.attrib
        super(TaggedValue, self).__init__(self.xml_attributes)

    @property
    def widget_related_name(self):
        """Nome de um tagged value relacionado ao widget."""
        return self.name.split(':')[1]

    @property
    def value(self):
        """Valor do tagged value."""
        if 'Value' in self.xml_attributes.keys():
            return self.xml_attributes['Value']
        elif bool(self.datatype):
            return self.datatype['Name']
        else:
            return ''

    @property
    def tipo(self):
        """Tipo de dados do tagged value."""
        return self.xml_attributes['Type'] if 'Type' in self.xml_attributes.keys() else ''


class Relationship(Base):
    """Representa uma relação genérica entre classes."""


class Association(Relationship):
    """Representa uma associação entre classes."""


class Associations:
    """Lista de associações do modelo UML."""
    def __init__(self, xmlobj=None, data=None):
        if xmlobj is not None:
            self.__associations = dict()
            xmlcontainer = xmlobj.Models.ModelRelationshipContainer
            xmlassociations = xmlcontainer.iterdescendants(tag="Association")

            if xmlassociations is not None:
                for xmlassociation in xmlassociations:
                    gen = Association(xmlassociation.attrib)
                    self.__associations[gen.id] = gen
            else:
                print u'Nenhuma associação localizada.'
        elif data is not None:
            self.__associations = data
        else:
            self.__associations = dict()

    def keys(self):
        """Chaves do dicionário interno de generelizações."""
        if self.__associations is not None:
            return self.__associations.keys()
        else:
            return list()

    def __len__(self):
        return len(self.__associations)

    def __getitem__(self, key):
        return self.__associations[key]

    def __iter__(self):
        return self.__associations.itervalues()


class Generalization(Relationship):
    """Representação de uma generalização."""

    @property
    def from_id(self):
        """Classe de origem da relação."""
        return self.xml_attributes['From']

    @property
    def to_id(self):
        """Classe de destino da relação."""
        return self.xml_attributes['To']


class Generalizations:
    """Lista de generalizações do diagrama."""

    def __init__(self, xmlobj=None, data=None):
        if xmlobj is not None:
            self.__generalizacoes = dict()
            xmlcontainer = xmlobj.Models.ModelRelationshipContainer
            xmlgeneralizations = xmlcontainer.iterdescendants(tag="Generalization")

            if xmlgeneralizations is not None:
                for xmlgeneralization in xmlgeneralizations:
                    gen = Generalization(xmlgeneralization.attrib)

                    # Gambiarra para evitar que sejam adicionadas generalizações em níveis abaixo do desejado.
                    if 'Id' in gen.xml_attributes.keys():
                        self.__generalizacoes[gen.id] = gen
            else:
                print u'Nenhuma generalização localizada.'
        elif data is not None:
            self.__generalizacoes = data
        else:
            self.__generalizacoes = dict()

    def keys(self):
        """Chaves do dicionário interno de generelizações."""
        if self.__generalizacoes is not None:
            return self.__generalizacoes.keys()
        else:
            return list()

    def __len__(self):
        return len(self.__generalizacoes)

    def __getitem__(self, key):
        return self.__generalizacoes[key]

    def __iter__(self):
        return self.__generalizacoes.itervalues()


# Classes containers.
class Project(Base):
    """Representação de um projeto."""

    def __init__(self, xmlobj):
        self.classes = Classes(xmlobj)
        xml_attributes = xmlobj.attrib
        super(Project, self).__init__(xml_attributes)

    @classmethod
    def from_xml(cls, xml_file):
        """Cria uma instância de classes a partir de um XML."""

        # Lê o arquivo XML.
        with open(xml_file) as xf:
            xml = xf.read()

        # Objetifica o xml e lê as classes.
        xmlobj = objectify.fromstring(xml)

        # Retorna o construtor.
        return cls(xmlobj=xmlobj)

    @property
    def author(self):
        """Author do projeto."""
        return self.xml_attributes['Author']


class Stereotype(Base):
    """Representação de um esteriótipo."""


class Stereotypes:
    """Lista de estereótipos de um objeto."""
    def __init__(self, xmlobj):
        self.__stereotypes = list()
        xmlstereotypes = xmlobj.iterdescendants(tag="Stereotype")

        if xmlstereotypes is not None:
            for xmlstereotype in xmlstereotypes:
                xml_attributes = xmlstereotype.attrib
                stereotype = Stereotype(xml_attributes)
                self.__stereotypes.append(stereotype)

    def __len__(self):
        return len(self.__stereotypes)

    def __getitem__(self, item):
        return self.__stereotypes[item]


class Classe(Base):
    """Objeto que representa uma classe."""

    def __init__(self, attributes, xml_attributes, tagged_values, stereotypes=None):
        self.attributes = attributes
        self.xml_attributes = xml_attributes
        self.tagged_values = tagged_values
        self.parents = OrderedDict()
        self.children = OrderedDict()
        self.stereotypes = stereotypes
        super(Classe, self).__init__(xml_attributes)

    @property
    def title(self):
        """Título de apresentação da classe."""
        return self.tagged_values['title'].value \
            if 'title' in self.tagged_values.keys() else self.name

    @property
    def tablename(self):
        """Valor do tagged value 'tablename' da classe."""
        return self.tagged_values['tablename'].value \
            if 'tablename' in self.tagged_values.keys() else self.name.lower()

    @property
    def colander(self):
        """Tagged values da classe relacionados aos schemas do colander."""
        colander_class = ['title', 'description']
        data = {tvk: self.tagged_values[tvk] for tvk in self.tagged_values.keys() if tvk in colander_class}
        return TaggedValues(data=data) if data is not None else None

    @property
    def polymorphic_identity(self):
        """Valor do tagged value 'polymorphic_identity' da classe."""
        if bool(self.parents):
            return self.tagged_values['polymorphic_identity'].value \
                if 'polymorphic_identity' in self.tagged_values.keys() else self.name.lower()
        else:
            return None

    @property
    def polymorphic_on(self):
        """Valor do tagged value 'polymorphic_on' da classe."""
        if bool(self.children):
            return self.tagged_values['polymorphic_on'].value \
                if 'polymorphic_on' in self.tagged_values.keys() else 'tipo'
        else:
            return None

    def __str__(self):
        return u"Classe '%s'" % self.name


class Classes:
    """Classes presentes no arquivo XML."""

    def __init__(self, xmlobj=None, data=None):
        logger = logging.getLogger('Classes.__init__')
        if xmlobj is not None:
            self.__classes = OrderedDict()
            xmlclasses = xmlobj.Models.Class

            if xmlclasses is not None:
                for xmlclasse in xmlclasses:
                    # Define os atributos da classe.
                    attributes = Atributos(xmlclasse)
                    xml_attributes = xmlclasse.attrib
                    tagged_values = TaggedValues(xmlclasse, from_class=True)
                    stereotypes = Stereotypes(xmlclasse)

                    # Cria o objeto Classe e adiciona na lista de classes.
                    classe = Classe(attributes, xml_attributes, tagged_values, stereotypes=stereotypes)
                    self.__classes[classe.id] = classe

                    # logger.debug(u'Tagged values da classe %s: %s' % (classe.name, xmlclasse))

                # Conecta as classes através da lista de generalizações.
                generalizacoes = Generalizations(xmlobj)
                self.connect(generalizacoes)
            else:
                print u'Nenhuma classe localizada.'
        elif data is not None:
            self.__classes = data
        else:
            self.__classes = OrderedDict()

    @property
    def view_classes(self):
        """Lista de classes principais."""
        view_classes = OrderedDict()
        for classe in self.__classes.itervalues():
            for stereotype in classe.stereotypes:
                if stereotype.name == 'view_class':
                    view_classes[classe.id] = classe
        return Classes(data=view_classes)

    def connect(self, generalizacoes):
        """Analisa a lista de generalizações recebida e faz as relações entre as classes."""

        # Define os filhos e pais das classes.
        for classe in self.__classes.itervalues():
            parents = OrderedDict()
            children = OrderedDict()

            for gen in generalizacoes:
                # Localiza os filhos da classe.
                if classe.id == gen.from_id:
                    children[gen.to_id] = self.__classes[gen.to_id]

                # Localiza os pais da classe.
                if classe.id == gen.to_id:
                    parents[gen.from_id] = self.__classes[gen.from_id]

            if parents is not None:
                classe.parents = Classes(data=parents)

            if children is not None:
                classe.children = Classes(data=children)

    def keys(self):
        """Chaves do dicionário interno de classes."""
        if self.__classes is not None:
            return self.__classes.keys()
        else:
            return list()

    def __len__(self):
        return len(self.__classes)

    def __getitem__(self, key):
        return self.__classes[key]

    def __iter__(self):
        return self.__classes.itervalues()

    def __str__(self):
        strclass = ''
        for k in self.__classes.keys():
            classe = self.__classes[k]
            strclass += '%s, ID: %s\n' % (classe, classe.id)
            for atributo in classe.attributes:
                strclass += '\t%s\n' % atributo

            if bool(classe.children):
                strclass += '\tFilhos:\n'
                for children in classe.children:
                    strclass += '\t   %s\n' % children

            if bool(classe.parents):
                strclass += '\tPais:\n'
                for parents in classe.parents:
                    strclass += '\t   %s\n' % parents
        return strclass


class TaggedValues:
    """Tagged values associados ao objeto XML."""

    def __init__(self, xmlobj=None, data=None, from_class=False):
        if xmlobj is not None:
            self.__tagged_values = OrderedDict()

            # Se for oriundo de uma classe, tenta limitar o contexto.
            if from_class:
                try:
                    xmlobj = xmlobj.TaggedValues
                    self.__search(xmlobj)
                except:
                    pass
            else:
                self.__search(xmlobj)
        elif data is not None:
            self.__tagged_values = data
        else:
            self.__tagged_values = OrderedDict()

    def __search(self, xmlobj):
        """Faz a busca dos tagged values."""
        xmltaggedvalues = xmlobj.iterdescendants(tag="TaggedValue")
        if xmltaggedvalues is not None:
            for taggedv in xmltaggedvalues:
                tv = TaggedValue(taggedv.attrib, taggedv)
                self.__tagged_values[tv.name] = tv

    @property
    def widget_related(self):
        """Tagged values relacionados ao widget."""
        data = OrderedDict({k: self.__tagged_values[k] for k in self.__tagged_values.keys() if k.find(':') != -1})
        return TaggedValues(data=data)

    @property
    def not_widget_related(self):
        """Tagged values não relacionados ao widget."""
        data = OrderedDict({k: self.__tagged_values[k]
                            for k in self.__tagged_values.keys() if k not in self.widget_related.keys()})
        return TaggedValues(data=data)

    def keys(self):
        """Chaves do dicionário interno de tagged values."""
        if self.__tagged_values is not None:
            return self.__tagged_values.keys()
        else:
            return list()

    def __len__(self):
        return len(self.__tagged_values)

    def __getitem__(self, key):
        return self.__tagged_values[key]

    def __iter__(self):
        return self.__tagged_values.itervalues()


class Atributo(Base):
    """Atributo de uma classe."""

    def __init__(self, xml_attributes, tagged_values, stereotypes=None):
        self.xml_attributes = xml_attributes
        self.tagged_values = tagged_values
        self.stereotypes = stereotypes
        super(Atributo, self).__init__(self.xml_attributes)

    @property
    def colander(self):
        """Tagged values do atributo relacionados aos schemas do colander."""
        colander_attr = ['title', 'description', 'missing_msg', 'widget', 'validator', 'exclude', 'default']
        data = {tv.name: tv for tv in self.tagged_values if tv.name in colander_attr}
        return TaggedValues(data=data) if data is not None else None

    @property
    def tipo(self):
        """Tipo de dados do atributo."""
        return self.xml_attributes['Type'] if 'Type' in self.xml_attributes.keys() else None

    @property
    def is_association_attribute(self):
        """Indica se o atributo é um atributo de associação."""
        for stereotype in self.stereotypes:
            if stereotype.name == 'association_attribute':
                return True
        return False

    def __str__(self):
        return "Atributo '%s'" % self.name


class AssociationAttribute(Atributo):
    """Atributo de associação."""


class Atributos:
    """Atributos da classe."""

    def __init__(self, xmlclasse=None, data=None):
        if xmlclasse is not None:
            self.__atributos = OrderedDict()
            xmlatributos = xmlclasse.iterdescendants(tag="Attribute")

            if xmlatributos is not None:
                for xmlatributo in xmlatributos:
                    # Atribuição dos parâmetros de construção do objeto classe.
                    xml_attributes = xmlatributo.attrib
                    tagged_values = TaggedValues(xmlatributo)
                    stereotypes = Stereotypes(xmlatributo)

                    # Contrução do atributo e inclusão na lista de atributos de classe.
                    atributo = Atributo(xml_attributes, tagged_values, stereotypes=stereotypes)
                    self.__atributos[atributo.name] = atributo
            else:
                print u'Nenhum atributo localizado.'
        elif data is not None:
            self.__atributos = data
        else:
            self.__atributos = OrderedDict()

    @property
    def association_attributes(self):
        """Lista de classes principais."""
        association_attributes = OrderedDict()
        for attribute in self.__atributos.itervalues():
            if attribute.is_association_attribute:
                association_attributes[attribute.id] = attribute
        return Atributos(data=association_attributes)

    def keys(self):
        """Chaves do dicionário interno de atributos."""
        if self.__atributos is not None:
            return self.__atributos.keys()
        else:
            return list()

    def __len__(self):
        return len(self.__atributos)

    def __getitem__(self, key):
        return self.__atributos[key]

    def __iter__(self):
        return self.__atributos.itervalues()
