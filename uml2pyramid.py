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

import glob
from os import walk, remove
from docopt import docopt
from lxml import objectify
from chameleon import PageTemplate
from os.path import abspath, dirname, join
from distutils.dir_util import copy_tree
from datamodels import *

__author__ = u'Rogério Pereira'
__email__ = 'rogeriorp@gmail.com'
__version__ = '1.0'

__here = abspath(dirname(__file__))
__classes = None


def get_classes(xml_file):
    """Retorna as classes presentes no arquivo XML."""
    # Lê o arquivo XML.
    with open(xml_file) as xf:
        xml = xf.read()

    # Objetifica o xml e lê as classes.
    xmlobj = objectify.fromstring(xml)

    # Carrega as classes numa variável global.
    global __classes
    __classes = Classes(xmlobj)

    # Lê as generalizações e utiliza como base pra relacionar as classes.
    generalizacoes = Generalizacoes(xmlobj)
    __classes.connect(generalizacoes)

    return __classes


def generate(xml_file, template_file, classes=None):
    """Gera a aplicação a partir do arquivo XML exportado de um modelo UML."""
    # Recebe a lista de classes presentes no arquivo XML, caso a lista não tenha sido repassada.
    if classes is None:
        classes = get_classes(xml_file)

    with open(template_file) as tf:
        template_code = tf.read()
    template = PageTemplate(template_code)
    rendered = template(classes=classes)

    return rendered


def generate_files(xml):
    """Gera os códigos python a partir dos dados do UML."""

    from_folder = join(__here, 'template')
    to_folder = join(__here, 'generated')

    # Faz a cópia de todos os arquivos na pasta de templates para a pasta de destino.
    copy_tree(from_folder, to_folder)

    # Busca os templates em todas as pastas copiadas.
    template_pyfile = dict()
    for root, dirs, files in walk(join(to_folder, 'u2p')):
        for template in glob.glob(join(root, '*.py.pt')):
            template_pyfile[template] = template.replace('.py.pt', '.py')

    # Gera os códigos finais a partir de cada template localizado.
    file_code = dict()
    for template in template_pyfile.keys():
        # Gera o código a partir do template utilizando o XMI com os dados.
        gen_code = generate(xml, template_file=template)
        pyfile = template_pyfile[template]
        file_code[pyfile] = gen_code

        # Escreve o código num arquivo.
        with open(pyfile, 'w') as tf:
            tf.write(gen_code.encode('utf-8'))
            tf.close()

        # Exlui o arquivo do template.
        remove(template)

    return file_code


if __name__ == '__main__':
    # Faz toda a macumba com os parâmetros da linha de comando <3.
    parametros_script = docopt(__doc__)

    # Parâmetros do script.
    xml_file = parametros_script['ARQUIVO']
    print_code = parametros_script['--print-code']
    print_object = parametros_script['--print-objects']
    compile_param = parametros_script['--compile']
    filename = parametros_script['--filename']

    # Renderiza a aplicação.
    file_code_result = generate_files(xml_file)

    # Caso informado que o código seja impresso na tela.
    if print_code:
        for f, code in file_code_result.items():
            print(u'\n---- IMPRIMINDO ARQUIVO %s ----\n' % f)
            print(code)

    # Imprime os objetos das classes, caso informado.
    if print_object:
        print(u'\n---- IMPRIMINDO CLASSES ----\n')
        print(__classes)

    # Caso solicitado, compila o código gerado.
    if compile_param:
        for f, code in file_code_result.items():
            print(u'\n---- COMPILANDO %s ----\n' % f)
            execfile(f)
