# -*- coding: utf-8 -*-
"""Classes que representam relações entre as classes do diagrama."""

import logging
from base import Base, DictBase
from tagged_values import TaggedValues
logger = logging.getLogger('relationships')


class Relationship(Base):
    """Representa uma relação genérica entre classes."""

    @property
    def from_id(self):
        """Classe de origem da relação."""
        return self.xml_attributes['From']

    @property
    def to_id(self):
        """Classe de destino da relação."""
        return self.xml_attributes['To']


class Generalization(Relationship):
    """Representação de uma generalização."""


class Generalizations(DictBase):
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
                logger.debug(u'Nenhuma generalização localizada.')
        elif data is not None:
            self.__generalizacoes = data
        else:
            self.__generalizacoes = dict()

        # Instancia a classe superior.
        super(Generalizations, self).__init__(self.__generalizacoes, Generalizations)


class Association(Relationship):
    """Representa uma associação entre classes."""
    def __init__(self, xml_attributes, tagged_values):
        self.xml_attributes = xml_attributes
        self.tagged_values = tagged_values
        super(Association, self).__init__(xml_attributes)

    @property
    def from_id(self):
        """ID da classe de origem"""
        return self.xml_attributes['EndRelationshipFromMetaModelElement']

    @property
    def to_id(self):
        """ID da classe de origem"""
        return self.xml_attributes['EndRelationshipToMetaModelElement']


class Associations(DictBase):
    """Lista de associações do modelo UML."""
    def __init__(self, xmlobj=None, data=None, class_id=None):
        global logger
        logger = logging.getLogger('relationships')
        if xmlobj is not None:
            self.__associations = dict()
            xmlcontainer = xmlobj.Models.ModelRelationshipContainer
            xmlassociations = xmlcontainer.iterdescendants(tag="Association")

            if xmlassociations is not None:
                for xmlassociation in xmlassociations:
                    logger.debug(u'XML attr associação: %s' % xmlassociation.attrib)
                    xml_attributes = xmlassociation.attrib
                    tagged_values = TaggedValues(xmlobj=xmlassociation)
                    association = Association(xml_attributes, tagged_values)

                    # Gambiarra pra evitar que sejam adicionados associações em níveis abaixo do desejado.
                    if 'Id' in association.xml_attributes.keys():
                        # Verifica se é pra filtrar por classe.
                        if class_id is not None:
                            if association.from_id == class_id:
                                self.__associations[association.id] = association
                        else:
                            self.__associations[association.id] = association
            else:
                logger.info(u'Nenhuma associação localizada.')
        elif data is not None:
            self.__associations = data
        else:
            self.__associations = dict()

        # Instancia a classe superior.
        super(Associations, self).__init__(self.__associations, Associations)
