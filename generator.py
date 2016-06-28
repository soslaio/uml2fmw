# -*- coding: utf-8 -*-
"""
    Módulo do gerador de códigos.

    Possui as classes e métodos que geram o código da aplicação Pyramid a partir de um scaffold localizado na pasta
    'scaffolds' e dos dados objectificados do arquivo XML exportado do modelo UML.
"""

import os
import glob
import logging
from distutils.dir_util import copy_tree
from chameleon import PageTemplate
from shutil import rmtree
from os import walk, remove, rename
from os.path import join, exists
from gentle.util import read_yaml, short_dir
from models.project import Project

here = os.getcwd()
configfile = os.path.join(here, 'config.yml')
basepath = read_yaml(configfile, 'basepath')


class Generator(object):
    """Classe geradora de código."""
    def __init__(self, xml_file):
        self.project = Project.from_xml(xml_file)

    def generate(self):
        """Gera o código da aplicação Pyramid a partir do XML."""
        # Instancia o logger.
        logger = logging.getLogger('generator')

        # Lê o scaffold a ser utilizado e mapeia as pastas de origem e destino da cópia.
        scaffold = read_yaml(configfile, 'scaffold')
        from_folder = join(here, 'scaffolds', scaffold)
        to_folder = join(here, 'generated', self.project.name)

        # Caso o diretório destino já exista, exclui.
        if exists(to_folder):
            logger.info(u'Excluindo pasta "%s"' % short_dir(to_folder, basepath))
            rmtree(to_folder)

        # Faz a cópia de todos os arquivos na pasta de templates para a pasta de destino.
        logger.info(u'Copiando arquivos de "%s" para "%s"' % (short_dir(from_folder, basepath),
                                                              short_dir(to_folder, basepath)))
        copy_tree(from_folder, to_folder)

        # Renomeia a pasta do módulo.
        template_module = join(to_folder, scaffold)
        generated_module = join(to_folder, self.project.name)
        logger.info(u'Renomeando "%s" para "%s"' % (short_dir(template_module, basepath),
                                                    short_dir(generated_module, basepath)))
        rename(template_module, generated_module)

        # Mapeia os templates nas pastas copiadas, usando-os como chave para os arquivos de código python.
        template_extension = read_yaml(configfile, 'template_extension')
        templates_and_genfiles = {tf: tf.replace('.%s' % template_extension, '') for root, _, __ in walk(join(to_folder))
                                  for tf in glob.glob(join(root, '*.%s' % template_extension))}

        # Dicionário de arquivos python e seus respectivos códigos.
        genfiles_and_codes = dict()

        # Faz a renderização dos templates.
        logger.info(u'Iniciando renderiação dos templates.')
        for template_file, python_file in templates_and_genfiles.items():
            # Gera o código a partir do template e adiciona ao dicionário de arquivos python e códigos.
            code = Template(template_file).render(self.project)
            genfiles_and_codes[python_file] = code

            # Escreve o código num arquivo.
            with open(python_file, 'w') as pf:
                pf.write(code.encode('utf-8'))

            # Exlui o arquivo do template na pasta de destino.
            remove(template_file)
        logger.info(u'Templates renderizados com sucesso.')

        return genfiles_and_codes


class Template(object):
    """Classe que representa um template."""
    def __init__(self, template):
        self.__template = template

    def render(self, project):
        """Gera a aplicação a partir do arquivo XML exportado de um modelo UML."""
        # Instancia o logger.
        logger = logging.getLogger('render')
        logger.info(u'Renderizando "%s"' % short_dir(self.__template, basepath))

        with open(self.__template) as tf:
            template_code = tf.read()
        template = PageTemplate(template_code)
        rendered = template(project=project)
        return rendered
