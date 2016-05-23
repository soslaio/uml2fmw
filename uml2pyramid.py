# -*- coding: utf-8 -*-
"""
Script que transforma um modelo UML numa aplicação Pyramid.

Usage:
    uml2pyramid.py [--print-code | -c]
    [--print-objects | -o]
    [--filename NAME| -n NAME]
    [--compile]
    ARQUIVO

Arguments:
    ARQUIVO                     Arquivo XML do modelo.

Options:
    -c, --print-code            Número do processo a ser analisado.
    -o, --print-objects         Filtrar pelo status dos processos.
    -n NAME, --filename NAME    Nome do arquivo a ser gerado.
    --compile                   Indica se o código gerado deve ser compilado.
"""

from docopt import docopt
from lxml import objectify
from chameleon import PageTemplate
from datamodels import *
from os import path

__author__ = u'Rogério Pereira'
__email__ = 'rogeriorp@gmail.com'
__version__ = '1.0'

__here = path.abspath(path.dirname(__file__))
__classes = None


def get_classes(xml_file):
    """Retorna as classes presentes no arquivo XML."""
    # Lê o arquivo XML.
    with open(xml_file) as xf:
        xml = xf.read()

    # Objetifica o xml e lê as classes.
    xmlobj = objectify.fromstring(xml)
    global __classes
    __classes = Classes(xmlobj)

    # Lê as generalizações e utiliza como base pra relacionar as classes.
    generalizacoes = Generalizacoes(xmlobj)
    __classes.connect(generalizacoes)

    return __classes


def generate(xml_file, classes=None):
    """Gera a aplicação a partir do arquivo XML exportado de um modelo UML."""
    # Recebe a lista de classes presentes no arquivo XML, caso a lista não tenha sido repassada.
    if classes is None:
        classes = get_classes(xml_file)

    # Carregamento do template com os dados.
    template_file = path.join(__here, 'template', 'u2p', 'u2p', 'models.py.pt')
    with open(template_file) as tf:
        template_code = tf.read()
    template = PageTemplate(template_code)
    rendered = template(classes=classes)

    return rendered


if __name__ == '__main__':
    # Faz toda a macumba com os parâmetros da linha de comando <3.
    parametros_script = docopt(__doc__)

    # Parâmetros do script.
    xmi_file = parametros_script['ARQUIVO']
    print_code = parametros_script['--print-code']
    print_object = parametros_script['--print-objects']
    compilar = parametros_script['--compile']
    filename = parametros_script['--filename']

    # Renderiza a aplicação.
    code = generate(xmi_file)

    # Escreve o código num arquivo.
    filename = filename if filename else 'generated_code.py'
    code_file = path.join(__here, 'generated', filename)
    with open(code_file, 'w') as cf:
        cf.write(code.encode('utf-8'))
        cf.close()

    # Imprime o código, caso informado.
    if print_code:
        print(code)

    # Imprime os objetos das classes, caso informado.
    if print_object:
        # classes = get_classes(xmi_file)
        print(__classes)

    # Compila o código gerado para localizar erros.
    if compilar:
        print()
        compiled = compile(code, '', 'exec')
        exec compiled
