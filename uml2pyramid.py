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
__print_code = False
__compile = False
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
    """Copia os arquivos do scaffold, interpretando os templates."""
    from_folder = join(__here, 'template')
    to_folder = join(__here, 'generated')

    # Faz a cópia de todos os arquivos na pasta de templates para a pasta de destino.
    copy_tree(from_folder, to_folder)

    # Busca os templates em todas as pastas copiadas.
    templates = dict()
    for root, dirs, files in walk(join(to_folder, 'u2p')):
        templates[root] = glob.glob(join(root, '*.py.pt'))

    # Gera os códigos finais a partir de cada template localizado.
    for k in templates.keys():
        for template in templates[k]:
            # Gera o código a partir do template utilizando o XMI com os dados.
            gen_code = generate(xml, template_file=template)

            # Escreve o código num arquivo.
            gen_filename = template.replace('.py.pt', '.py')
            with open(gen_filename, 'w') as tf:
                tf.write(gen_code.encode('utf-8'))
                tf.close()

            # Exlui o arquivo do template.
            remove(template)

            # Caso informado que o código seja impresso na tela.
            if __print_code:
                print(gen_code)

    if __compile:
        # Compila todos os arquivos localizados.
        for folder in templates.keys():
            for template in templates[folder]:
                pyfile = template.replace('.py.pt', '.py')
                print(u'\n\n#######\nCompilando %s\n#######\n' % pyfile)

                # Lê e compila o arquivo de código python.
                with open(pyfile) as pf:
                    pycode = pf.read()
                    compiled = compile(pycode, '', 'exec')
                    exec compiled

    return templates


if __name__ == '__main__':
    # Faz toda a macumba com os parâmetros da linha de comando <3.
    parametros_script = docopt(__doc__)

    # Parâmetros do script.
    xml_file = parametros_script['ARQUIVO']
    __print_code = parametros_script['--print-code']
    print_object = parametros_script['--print-objects']
    __compile = parametros_script['--compile']
    filename = parametros_script['--filename']

    # Renderiza a aplicação.
    code = generate_files(xml_file)

    # Imprime os objetos das classes, caso informado.
    if print_object:
        print(__classes)
