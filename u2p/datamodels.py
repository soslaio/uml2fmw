# -*- coding: utf-8 -*-

from collections import OrderedDict


# Classes de modelos de dados.
class BaseXml:
    """ Objeto base para as classes de dados. """

    def __init__(self, xml_attributes):
        self.xml_attributes = xml_attributes

    @property
    def name(self):
        """Nome do objeto."""
        return self.xml_attributes['Name']

    @property
    def id(self):
        """ID do objeto."""
        return self.xml_attributes['Id']


class Atributo(BaseXml):
    """Atributo de uma classe."""

    def __init__(self, xml_attributes, tagged_values):
        self.xml_attributes = xml_attributes
        self.tagged_values = tagged_values

    @property
    def colander(self):
        """"""
        colander_attr = ['title', 'description', 'missing_msg', 'widget', 'validator', 'exclude', 'default']
        data = {tv.name: tv for tv in self.tagged_values if tv.name in colander_attr}
        return TaggedValues(data=data)

    @property
    def tipo(self):
        return self.xml_attributes['Type']

    def __repr__(self):
        return "Atributo '%s' do tipo '%s'" % (self.name, self.tipo)


class TaggedValue(BaseXml):
    """Objeto que representa um tagged value."""

    @property
    def value(self):
        return self.xml_attributes['Value']

    @property
    def tipo(self):
        return self.xml_attributes['Type']


class Classe(BaseXml):
    """Objeto que representa uma classe."""

    def __init__(self, attributes, xml_attributes, tagged_values):
        self.attributes = attributes
        self.xml_attributes = xml_attributes
        self.tagged_values = tagged_values

    @property
    def tablename(self):
        if not bool(self.parents):
            return self.tagged_values['tablename'].value if 'tablename' in self.tagged_values.keys() else self.name.lower()
        else:
            return None

    @property
    def colander(self):
        data = { tvk : self.tagged_values[tvk] for tvk in self.tagged_values.keys() if tvk in colander_class }
        return TaggedValues(data=data)

    @property
    def polymorphic_identity(self):
        if bool(self.parents):
            return self.tagged_values['polymorphic_identity'].value if 'polymorphic_identity' in self.tagged_values.keys() else self.name.lower()
        else:
            return None

    @property
    def polymorphic_on(self):
        if bool(self.children):
            return self.tagged_values['polymorphic_on'].value if 'polymorphic_on' in self.tagged_values.keys() else 'tipo'
        else:
            return None

    def __repr__(self):
        return "Classe '%s'" % self.name


class Generalizacao(BaseXml):
    """Representação de uma generalização."""

    @property
    def name(self):
        raise ValueError(u'Generalizações não possuem nomes.')

    @property
    def from_id(self):
        return self.xml_attributes['From']

    @property
    def to_id(self):
        return self.xml_attributes['To']


# Classes de lista de dados.
class TaggedValues:
    """Tagged values associados ao objeto XML."""

    def __init__(self, xmlobj=None, data=None):
        if xmlobj is not None:
            self._tagged_values = OrderedDict()
            xmltaggedvalues = xmlobj.iterdescendants(tag="TaggedValue")

            if xmltaggedvalues is not None:
                for taggedv in xmltaggedvalues:
                    tv = TaggedValue(taggedv.attrib)
                    self._tagged_values[tv.name] = tv
            else:
                print 'Nenhum tagged value localizado.'
        elif data is not None:
            self._tagged_values = data
        else:
            self._tagged_values = OrderedDict()

    def __len__(self):
        return len(self._tagged_values)
    
    def __getitem__(self, key):
        return self._tagged_values[key]

    def __iter__(self):
        return self._tagged_values.itervalues()

    def keys(self):
        if self._tagged_values is not None:
            return self._tagged_values.keys()
        else:
            return list()


class Generalizacoes:
    """Lista de generalizações do diagrama."""

    def __init__(self, xmlobj=None, data=None):
        if xmlobj is not None:
            self._generalizacoes = dict()
            xmlrelationship = xmlobj.Models.ModelRelationshipContainer
            xmlgeneralizations = xmlrelationship.iterdescendants(tag="Generalization")

            if xmlgeneralizations is not None:
                for xmlgeneralization in xmlgeneralizations:
                    gen = Generalizacao(xmlgeneralization.attrib)
                    
                    # Gambiarra para evitar que sejam adicionadas generalizações em níveis abaixo do desejado.
                    if 'Id' in gen.xml_attributes.keys():
                        self._generalizacoes[gen.id] = gen
            else:
                print u'Nenhuma generalização localizada.'
        elif data is not None:
            self._generalizacoes = data
        else:
            self._generalizacoes = dict()

    def __len__(self):
        return len(self._generalizacoes)
    
    def __getitem__(self, key):
        return self._generalizacoes[key]

    def keys(self):
        if self._generalizacoes is not None:
            return self._generalizacoes.keys()
        else:
            return list()

    def __iter__(self):
        return self._generalizacoes.itervalues()


class Atributos:
    """Atributos da classe."""

    def __init__(self, xmlclasse):
        self._atributos = OrderedDict()
        xmlatributos = xmlclasse.iterdescendants(tag="Attribute")

        if xmlatributos is not None:
            for xmlatributo in xmlatributos:
                # Atribuição dos parâmetros de construção do objeto classe.
                xml_attributes = xmlatributo.attrib
                tagged_values = TaggedValues(xmlatributo)

                # Contrução do atributo e inclusão na lista de atributos de classe.
                atributo = Atributo(xml_attributes, tagged_values)
                self._atributos[atributo.name] = atributo
        else:
            print 'Nenhum atributo localizado.'

    def __len__(self):
        return len(self._atributos)
    
    def __getitem__(self, key):
        return self._atributos[key]

    def keys(self):
        if self._atributos is not None:
            return self._atributos.keys()
        else:
            return list()

    def __iter__(self):
        return self._atributos.itervalues()


class Classes:
    """Classes presentes no arquivo XML."""

    def __init__(self, xmlobj=None, data=None):
        if xmlobj is not None:
            self._classes = OrderedDict()
            xmlclasses = xmlobj.Models.Class

            if xmlclasses is not None:
                for xmlclasse in xmlclasses:
                    # Define os atributos da classe.
                    attributes = Atributos(xmlclasse)
                    xml_attributes = xmlclasse.attrib
                    tagged_values = TaggedValues(xmlclasse)

                    # Cria o objeto Classe e adiciona na lista de classes.
                    classe = Classe(attributes, xml_attributes, tagged_values)
                    self._classes[classe.id] = classe
                            
            else:
                print 'Nenhuma classe localizada.'
        elif data is not None:
            self._classes = data
        else:
            self._classes = OrderedDict()

    def connect(self, generalizacoes):
        """Analisa a lista de generalizações recebida e faz as relações entre as classes."""
        # Define os filhos e pais das classes.
        for classe in self._classes.itervalues():
            parents = OrderedDict()
            children = OrderedDict()

            for gen in generalizacoes:
                # Localiza os filhos da classe.
                if classe.id == gen.from_id:
                    children[gen.to_id] = self._classes[gen.to_id]

                # Localiza os pais da classe.
                if classe.id == gen.to_id:
                    parents[gen.from_id] = self._classes[gen.from_id]

            if parents is not None:
                classe.parents = Classes(data=parents)

            if children is not None:
                classe.children = Classes(data=children)

    def keys(self):
        if self._classes is not None:
            return self._classes.keys()
        else:
            return list()

    def __len__(self):
        return len(self._classes)
    
    def __getitem__(self, key):
        return self._classes[key]

    def __iter__(self):
        return self._classes.itervalues()
