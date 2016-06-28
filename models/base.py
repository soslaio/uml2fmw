# -*- coding: utf-8 -*-
"""Classes-base herdadas por outras classes da aplicação."""


class Base(object):
    """Classe base para as classes de dados."""

    def __init__(self, xml_attributes):
        self.xml_attributes = xml_attributes

    @property
    def id(self):
        """ID do objeto."""
        return self.xml_attributes['Id']

    @property
    def lower_name(self):
        """Nome do objeto em caixa baixa."""
        return self.name.lower()

    @property
    def name(self):
        """Nome do objeto."""
        return self.xml_attributes['Name'] if 'Name' in self.xml_attributes.keys() else ''
