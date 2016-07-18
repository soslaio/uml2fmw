# -*- coding: utf-8 -*-
"""Classe com representações dos tagged values do modelo UML."""

import logging
from base import Base
from gentle.base import OrderedDictBase
from collections import OrderedDict
logger = logging.getLogger('tagged_values')


class TaggedValue(Base):
    """Objeto que representa um tagged value."""

    def __init__(self, xml_attributes, xmlobj=None):
        self.xml_attributes = xml_attributes
        self.datatype = dict()
        if 'Value' not in self.xml_attributes.keys():
            xmldatatypes = xmlobj.iterdescendants(tag="DataType")
            for dt in xmldatatypes:
                self.datatype = dt.attrib
        super(TaggedValue, self).__init__(self.xml_attributes)

    @property
    def tagv_type(self):
        """Tipo de dados do tagged value.

        O nome não pode ser simplesmente 'type', pois esta é uma palavra reservada."""
        return self.xml_attributes['Type'] if 'Type' in self.xml_attributes.keys() else ''

    @property
    def value(self):
        """Valor do tagged value."""
        if 'Value' in self.xml_attributes.keys():
            return self.xml_attributes['Value']
        elif bool(self.datatype):
            return self.datatype['Name']
        else:
            return ''

    @property
    def widget_related_name(self):
        """Nome de um tagged value relacionado ao widget."""
        return self.name.split(':')[1]


class TaggedValues(OrderedDictBase):
    """Tagged values associados ao objeto XML."""

    def __init__(self, xmlobj=None, data=None, from_class=False):
        if xmlobj is not None:
            self.__tagged_values = OrderedDict()

            # Se for oriundo de uma classe, tenta limitar o contexto.
            if from_class:
                try:
                    xmlobj = xmlobj.TaggedValues
                    self.__search(xmlobj)
                except AttributeError:
                    pass
            else:
                self.__search(xmlobj)
        elif data is not None:
            self.__tagged_values = data
        else:
            self.__tagged_values = OrderedDict()

        # Instancia a classe superior.
        super(TaggedValues, self).__init__(self.__tagged_values, TaggedValues)

    def __search(self, xmlobj):
        """Faz a busca dos tagged values."""
        xmltaggedvalues = xmlobj.iterdescendants(tag="TaggedValue")
        if xmltaggedvalues is not None:
            for taggedv in xmltaggedvalues:
                tv = TaggedValue(taggedv.attrib, taggedv)
                self.__tagged_values[tv.name] = tv

    @property
    def not_widget_related(self):
        """Tagged values não relacionados ao widget."""
        data = OrderedDict({k: self.__tagged_values[k]
                            for k in self.__tagged_values.keys() if k not in self.widget_related.keys()})
        return TaggedValues(data=data)

    @property
    def widget_related(self):
        """Tagged values relacionados ao widget."""
        data = OrderedDict({k: self.__tagged_values[k] for k in self.__tagged_values.keys() if k.find(':') != -1})
        return TaggedValues(data=data)
