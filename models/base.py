# -*- coding: utf-8 -*-
"""Classes com métodos comuns à outras classes da aplicação, para herança."""

from collections import OrderedDict


class Base(object):
    """Classe base para as classes de dados."""

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


class DictBase(object):
    """Classe base para coleções baseadas em dicionários."""

    def __init__(self, dict_object, collection_class, base_class=dict):
        self.__dict_object = dict_object
        self.__collection_class = collection_class
        self.__base_class = base_class

    def filter(self, attribute_name, value=None):
        """Retorna uma lista de objetos filtrados pelo valor de um determinado atributo.

        A priori, o método verifica se foi repassado um valor de comparação para o atributo.
        Se foi repassado, retorna apenas objetos que possuam o aributo com esse valor.

        Se nenhum valor foi repassado, verifica se o atributo é de uma classe baseada em dict ou DictBase.
        Se for, retorna apenas objetos cujo atributo possua algum elemento, usando a notação padrão de dicionários
        para essa verificação: bool(objeto).

        Se não for um dicionário de nenhuma natureza, retorna objetos cujo atributo seja diferente de None.
        """
        bc_object = self.__base_class()
        for obj in self.__dict_object.itervalues():
            attr_value = getattr(obj, attribute_name)
            condition = attr_value == value if value is not None else \
                bool(attr_value) if isinstance(attr_value, (dict, DictBase)) else \
                attr_value is not None
            if condition:
                bc_object[obj.id] = obj
        return self.__collection_class(data=bc_object)

    def find(self, attribute_name, value):
        """Retorna o primeiro argumento que corresponde ao filtro."""
        for obj in self.__dict_object.itervalues():
            if getattr(obj, attribute_name) == value:
                return obj
        return None

    def keys(self):
        """Chaves do dicionário interno de classes."""
        if self.__dict_object is not None:
            return self.__dict_object.keys()
        else:
            return list()

    def __len__(self):
        return len(self.__dict_object)

    def __getitem__(self, key):
        return self.__dict_object[key]

    def __iter__(self):
        return self.__dict_object.itervalues()


class OrderedDictBase(DictBase):
    """Classe base para coleções baseadas em OrderedDict."""

    def __init__(self, dict_object, collection_class):
        super(OrderedDictBase, self).__init__(dict_object, collection_class,
                                              base_class=OrderedDict)


class ListBase(object):
    """Classe base para coleções baseadas em listas."""

    def __init__(self, list_object, collection_class):
        self.__list_object = list_object
        self.__collection_class = collection_class

    def filter(self, attribute_name, value):
        """Busca uma classe pelo nome na lista de classes."""
        list_object = list()
        for obj in self.__list_object:
            if getattr(obj, attribute_name) == value:
                list_object[obj.id] = obj
        return self.__collection_class(data=list_object)

    def find(self, attribute_name, value):
        """Retorna o primeiro argumento que corresponde ao filtro."""
        for obj in self.__list_object:
            if getattr(obj, attribute_name) == value:
                return obj
        return None

    def __len__(self):
        return len(self.__list_object)

    def __getitem__(self, item):
        return self.__list_object[item]

    def __iter__(self):
        return iter(self.__list_object)
