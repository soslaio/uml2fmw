# -*- coding: utf-8 -*-
"""
    Módulo com classes de dados que representam o documento XML.

    Os principais atributos XML e tagged values são expostos para
    através de propsiedades para facilitar o uso.
"""


class ClassDiagram:
    """Diagrama de classe."""

    def __init__(self, name):
        self.name = name
