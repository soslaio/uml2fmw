# -*- coding: utf-8 -*-
"""Classe que representa os estereótipos do modelo UML."""

import logging
from base import Base
from gentle.base import ListBase
logger = logging.getLogger('stereotypes')


class Stereotype(Base):
    """Representação de um esteriótipo."""


class Stereotypes(ListBase):
    """Lista de estereótipos de um objeto."""
    def __init__(self, xmlobj=None, data=None):
        if xmlobj is not None:
            self.__stereotypes = list()
            xmlstereotypes = xmlobj.iterdescendants(tag="Stereotype")

            if xmlstereotypes is not None:
                for xmlstereotype in xmlstereotypes:
                    xml_attributes = xmlstereotype.attrib
                    stereotype = Stereotype(xml_attributes)
                    self.__stereotypes.append(stereotype)
        else:
            self.__stereotypes = data

        # Instancia a classe superior.
        super(Stereotypes, self).__init__(self.__stereotypes, Stereotypes)
