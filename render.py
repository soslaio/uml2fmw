# -*- coding: utf-8 -*-

import os
from lxml import objectify
from chameleon import PageTemplate
from u2p.datamodels import *

# path = os.path.dirname(__file__)

# Lista de tagged values relacionados ao colanderalchemy.
# alchemy_class = ['polymorphic_on', 'polymorphic_identity']
# colander_class = ['title', 'description']


def imprimirClasse(classes):
    ''' Método útil para visualização de classes.'''

    for classe in classes:
        print classe, classe.id
        for atributo in classe.attributes:
            print '\t%s' % atributo

        if classe.children is not None:
            for children in classe.children:
                print '\t\tFilhos: %s' % children

        if classe.parents is not None:
            for parents in classe.parents:
                print '\t\tPais: %s' % parents


if __name__ == '__main__':

    # Carregamento dos dados a partir do XML.
    xml_file = '/home/soslaio/teste.xml/project.xml'
    with open(xml_file) as xf:
        xml = xf.read()
    xmlobj = objectify.fromstring(xml)
    classes = Classes(xmlobj)
    generalizacoes = Generalizacoes(xmlobj)
    classes.carregarRelacoes(generalizacoes)

    # Carregamento do template com os dados.
    template_file = '/home/soslaio/Hubic/tools/UML2Pyramid/template/models.py.pt'
    with open(template_file) as tf:
        template_code = tf.read()
    template = PageTemplate(template_code)
    rendered = template(classes=classes)

    print rendered
    # imprimirClasse(classes)

    # Compila o código gerado para localizar erros.
    compiled = compile(rendered, '', 'exec')
    exec(compiled)
