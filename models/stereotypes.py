# -*- coding: utf-8 -*-

import logging
from base import Base

logger = logging.getLogger('stereotypes')


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

    def find(self, name):
        """Busca um estereótipo pelo nome na lista de estereótipos."""
        for stereotype in self.__stereotypes:
            if stereotype.name == name:
                return stereotype
        return None

    def __len__(self):
        return len(self.__stereotypes)

    def __getitem__(self, item):
        return self.__stereotypes[item]

    def __iter__(self):
        return iter(self.__stereotypes)
