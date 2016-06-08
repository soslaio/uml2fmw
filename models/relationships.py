# -*- coding: utf-8 -*-

import logging
from base import Base

logger = logging.getLogger('relationships')


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
