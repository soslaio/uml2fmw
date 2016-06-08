# -*- coding: utf-8 -*-

import logging
from base import Base
from tagged_values import TaggedValues
from stereotypes import Stereotypes
from collections import OrderedDict

logger = logging.getLogger('attributes')


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
        return self.stereotypes.find('association_attribute') is not None

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
                    if stereotypes.find('association_attribute') is not None:
                        atributo = AssociationAttribute(xml_attributes, tagged_values, stereotypes=stereotypes)
                    else:
                        atributo = Atributo(xml_attributes, tagged_values, stereotypes=stereotypes)

                    self.__atributos[atributo.name] = atributo
            else:
                logger.debug(u'Nenhum atributo encontrado.')
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