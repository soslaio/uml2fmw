# -*- coding: utf-8 -*-

from lxml import objectify
from chameleon import PageTemplate
from .datamodels import *
from os import path

__here = path.abspath(path.dirname(__file__))


def get_classes(xml_file):
    """Retorna as classes presentes no arquivo XML."""

    # Lê o arquivo XML.
    with open(xml_file) as xf:
        xml = xf.read()

    # Objetifica o xml e lê as classes.
    xmlobj = objectify.fromstring(xml)
    classes = Classes(xmlobj)

    # Lê as generalizações e utiliza como base pra relacionar as classes.
    generalizacoes = Generalizacoes(xmlobj)
    classes.connect(generalizacoes)

    return classes


def generate(xml_file, classes=None):
    """Gera a aplicação a partir do arquivo XML exportado de um modelo UML."""

    # Recebe a lista de classes presentes no arquivo XML, caso a lista não tenha sido repassada.
    if classes is None:
        classes = get_classes(xml_file)

    # Carregamento do template com os dados.
    template_file = path.join(__here, 'template', 'models.py.pt')
    with open(template_file) as tf:
        template_code = tf.read()
    template = PageTemplate(template_code)
    rendered = template(classes=classes)

    return rendered
