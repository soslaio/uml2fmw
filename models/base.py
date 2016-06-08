# -*- coding: utf-8 -*-


class Base(object):
    """ Objeto base para as classes de dados. """

    def __init__(self, xml_attributes):
        self.xml_attributes = xml_attributes

    @property
    def name(self):
        """Nome do objeto."""
        return self.xml_attributes['Name'] if 'Name' in self.xml_attributes.keys() else ''

    @property
    def lower_name(self):
        """Nome do objeto em caixa baixa."""
        return self.name.lower()

    @property
    def id(self):
        """ID do objeto."""
        return self.xml_attributes['Id']
