# -*- coding: utf-8 -*-

import glob
from distutils.dir_util import copy_tree
from chameleon import PageTemplate
from os import walk, remove
from os.path import abspath, dirname, join
from datamodels import *


class Generator(object):
    """Classe geradora de código."""

    def __init__(self, xml_file):
        self.classes = Classes.from_xml(xml_file)

    def generate(self):
        """Gera o código da aplicação Pyramid a partir do XML."""

        # Definição de diretótios de origem e destino.
        here = abspath(dirname(__file__))
        from_folder = join(here, 'template')
        to_folder = join(here, 'generated')

        # Faz a cópia de todos os arquivos na pasta de templates para a pasta de destino.
        copy_tree(from_folder, to_folder)

        # Busca os templates em todas as pastas copiadas.
        templates_pyfiles = dict()
        for root, dirs, files in walk(join(to_folder, 'u2p')):
            for template_file in glob.glob(join(root, '*.py.pt')):
                templates_pyfiles[template_file] = template_file.replace('.py.pt', '.py')

        # Gera os códigos finais a partir de cada template localizado.
        files_and_codes = dict()
        for template_file in templates_pyfiles.keys():
            # Carrega o template e o nome do arquivo de código python de destino.
            template = Template(template_file)
            python_file = templates_pyfiles[template_file]

            # Gera o código e adiciona à lista de arquivos e códigos.
            code = template.render(self.classes)
            files_and_codes[python_file] = code

            # Escreve o código num arquivo.
            with open(python_file, 'w') as tf:
                tf.write(code.encode('utf-8'))
                tf.close()

            # Exlui o arquivo do template na pasta de destino.
            remove(template_file)

        return files_and_codes


class Template(object):
    """Classe que representa um template."""
    def __init__(self, template):
        self.__template = template

    def render(self, classes):
        """Gera a aplicação a partir do arquivo XML exportado de um modelo UML."""
        with open(self.__template) as tf:
            template_code = tf.read()
        template = PageTemplate(template_code)
        rendered = template(classes=classes)
        return rendered
