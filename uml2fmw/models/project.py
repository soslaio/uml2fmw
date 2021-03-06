# -*- coding: utf-8 -*-
"""Módulo com definições do projeto."""

import logging
from lxml import objectify
from base import Base
from classes import Classes
from relationships import Associations
logger = logging.getLogger('project')


class Project(Base):
    """Representação de um projeto."""

    def __init__(self, xmlobj):
        self.associations = Associations(xmlobj)
        self.classes = Classes(xmlobj, associations=self.associations)
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
