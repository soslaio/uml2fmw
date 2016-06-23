# -*- coding: utf-8 -*-
"""Classe que representa os estereótipos do modelo UML."""

import logging
from base import Base, ListBase
logger = logging.getLogger('stereotypes')


class Stereotype(Base):
    """Representação de um esteriótipo."""


class Stereotypes(ListBase):
    """Lista de estereótipos de um objeto."""
    def __init__(self, xmlobj):
        self.__stereotypes = list()
        xmlstereotypes = xmlobj.iterdescendants(tag="Stereotype")

        if xmlstereotypes is not None:
            for xmlstereotype in xmlstereotypes:
                xml_attributes = xmlstereotype.attrib
                stereotype = Stereotype(xml_attributes)
                self.__stereotypes.append(stereotype)

        # Instancia a classe superior.
        super(Stereotypes, self).__init__(self.__stereotypes, Stereotypes)
