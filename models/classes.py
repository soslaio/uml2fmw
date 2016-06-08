# -*- coding: utf-8 -*-

import logging
from base import Base
from collections import OrderedDict
from tagged_values import TaggedValues
from attributes import Atributos
from relationships import Generalizations
from stereotypes import Stereotypes

logger = logging.getLogger('classes')


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
                logger.debug(u'Nenhuma classe localizada.')
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
