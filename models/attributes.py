# -*- coding: utf-8 -*-
"""Módulo com definições de atributos de classes."""

import logging
from base import Base, OrderedDictBase
from tagged_values import TaggedValues
from stereotypes import Stereotypes
from collections import OrderedDict
from relationships import Association
logger = logging.getLogger('attributes')


class Attribute(Base):
    """Atributo de uma classe."""

    def __init__(self, xml_attributes, tagged_values, stereotypes=None):
        self.xml_attributes = xml_attributes
        self.tagged_values = tagged_values
        self.stereotypes = stereotypes

        # O instanciamento da classe superior no old-style é necessário, devido haverem classes que herdam
        # dessa classe. Por algum motivo o interpretador se enrola em instanciar usando o super().
        Base.__init__(self, xml_attributes)

    def __repr__(self):
        return u'Atributo %s' % self.name

    @property
    def attr_type(self):
        """Tipo de dados do atributo.

        O nome não pode ser simplesmente 'type', pois esta é uma palavra reservada."""
        return self.xml_attributes['Type'] if 'Type' in self.xml_attributes.keys() else None

    @property
    def colander_tagged_values(self):
        """Tagged values do atributo relacionados aos schemas do colander."""
        colander_attr = ['title', 'description', 'missing_msg', 'widget', 'validator', 'exclude', 'default']
        data = {tv.name: tv for tv in self.tagged_values if tv.name in colander_attr}
        return TaggedValues(data=data) if data is not None else None

    @property
    def is_association_attribute(self):
        """Verifica se o atributo é de associação."""
        return isinstance(self, AssociationAttribute)


class AssociationAttribute(Attribute, Association):
    """Atributo de associação."""

    def __init__(self, xml_attributes, tagged_values, stereotypes=None):
        self.xml_attributes = xml_attributes
        self.tagged_values = tagged_values
        self.stereotypes = stereotypes
        super(AssociationAttribute, self).__init__(xml_attributes, tagged_values)


class Atributos(OrderedDictBase):
    """Atributos da classe."""

    def __init__(self, xmlclasse=None, data=None, class_associations=None):
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
                    if stereotypes.find('name', 'association_attribute') is not None:
                        atributo = AssociationAttribute(xml_attributes, tagged_values, stereotypes=stereotypes)
                    else:
                        atributo = Attribute(xml_attributes, tagged_values, stereotypes=stereotypes)

                    self.__atributos[atributo.name] = atributo
            else:
                logger.debug(u'Nenhum atributo encontrado.')

            # Cria os atributos associativos.
            if class_associations is not None:
                for association in class_associations:
                    attribute = AssociationAttribute(association.xml_attributes, association.tagged_values)
                    self.__atributos[attribute.name] = attribute
        elif data is not None:
            self.__atributos = data
        else:
            self.__atributos = OrderedDict()

        # Instancia a classe superior.
        super(Atributos, self).__init__(self.__atributos, Atributos)

    @property
    def association_attributes(self):
        """Lista de classes principais."""
        association_attributes = OrderedDict()
        for attribute in self.__atributos.itervalues():
            if attribute.is_association_attribute:
                association_attributes[attribute.id] = attribute
        return Atributos(data=association_attributes)
