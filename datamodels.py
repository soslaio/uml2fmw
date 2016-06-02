# -*- coding: utf-8 -*-
"""
    Módulo com classes de dados que representam o documento XML.

    Os principais atributos XML e tagged values são expostos para
    através de propsiedades para facilitar o uso.
"""

from UserDict import UserDict
from collections import OrderedDict
from lxml import objectify


class Base(object):
    """ Objeto base para as classes de dados. """

    def __init__(self, xml_attributes):
        self.xml_attributes = xml_attributes

    @property
    def name(self):
        """Nome do objeto."""
        return self.xml_attributes['Name'] if 'Name' in self.xml_attributes.keys() else None

    @property
    def lower_name(self):
        """Nome do objeto em caixa baixa."""
        return self.name.lower()

    @property
    def id(self):
        """ID do objeto."""
        return self.xml_attributes['Id']


class Atributo(Base):
    """Atributo de uma classe."""

    def __init__(self, xml_attributes, tagged_values):
        self.xml_attributes = xml_attributes
        self.tagged_values = tagged_values
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
        return self.xml_attributes['Type']

    def __str__(self):
        return "Atributo '%s' do tipo '%s'" % (self.name, self.tipo)


class TaggedValue(Base):
    """Objeto que representa um tagged value."""

    @property
    def value(self):
        """Valor do tagged value."""
        return self.xml_attributes['Value']

    @property
    def tipo(self):
        """Tipo de dados do tagged value."""
        return self.xml_attributes['Type']


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


class Generalizacao(Base):
    """Representação de uma generalização."""

    @property
    def from_id(self):
        """Classe de origem da relação."""
        return self.xml_attributes['From']

    @property
    def to_id(self):
        """Classe de destino da relação."""
        return self.xml_attributes['To']


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


class Classes:
    """Classes presentes no arquivo XML."""

    def __init__(self, xmlobj=None, data=None):
        if xmlobj is not None:
            self.__classes = OrderedDict()
            xmlclasses = xmlobj.Models.Class

            if xmlclasses is not None:
                for xmlclasse in xmlclasses:
                    # Define os atributos da classe.
                    attributes = Atributos(xmlclasse)
                    xml_attributes = xmlclasse.attrib
                    tagged_values = TaggedValues(xmlclasse)
                    stereotypes = Stereotypes(xmlclasse)

                    # Cria o objeto Classe e adiciona na lista de classes.
                    classe = Classe(attributes, xml_attributes, tagged_values, stereotypes=stereotypes)
                    self.__classes[classe.id] = classe

                # Conecta as classes através da lista de generalizações.
                generalizacoes = Generalizacoes(xmlobj)
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
        view_classes = list()
        for classe in self.__classes.itervalues():
            for stereotype in classe.stereotypes:
                if stereotype.name == 'view_class':
                    view_classes.append(classe)
        return view_classes

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

    def __init__(self, xmlobj=None, data=None):
        if xmlobj is not None:
            self.__tagged_values = OrderedDict()
            xmltaggedvalues = xmlobj.iterdescendants(tag="TaggedValue")

            if xmltaggedvalues is not None:
                for taggedv in xmltaggedvalues:
                    tv = TaggedValue(taggedv.attrib)
                    self.__tagged_values[tv.name] = tv
            else:
                print u'Nenhum tagged value localizado.'
        elif data is not None:
            self.__tagged_values = data
        else:
            self.__tagged_values = OrderedDict()

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


class Generalizacoes:
    """Lista de generalizações do diagrama."""

    def __init__(self, xmlobj=None, data=None):
        if xmlobj is not None:
            self.__generalizacoes = dict()
            xmlcontainer = xmlobj.Models.ModelRelationshipContainer
            xmlgeneralizations = xmlcontainer.iterdescendants(tag="Generalization")

            if xmlgeneralizations is not None:
                for xmlgeneralization in xmlgeneralizations:
                    gen = Generalizacao(xmlgeneralization.attrib)

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


class Atributos:
    """Atributos da classe."""

    def __init__(self, xmlclasse):
        self.__atributos = OrderedDict()
        xmlatributos = xmlclasse.iterdescendants(tag="Attribute")

        if xmlatributos is not None:
            for xmlatributo in xmlatributos:
                # Atribuição dos parâmetros de construção do objeto classe.
                xml_attributes = xmlatributo.attrib
                tagged_values = TaggedValues(xmlatributo)

                # Contrução do atributo e inclusão na lista de atributos de classe.
                atributo = Atributo(xml_attributes, tagged_values)
                self.__atributos[atributo.name] = atributo
        else:
            print u'Nenhum atributo localizado.'

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
