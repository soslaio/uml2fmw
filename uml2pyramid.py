# -*- coding: utf-8 -*-
"""
Script que transforma um modelo UML numa aplicação Pyramid.

Usage:
    uml2pyramid.py
    [--log-classes | -c]
    [--compile]
    ARQUIVO

Arguments:
    ARQUIVO                     Arquivo XML do modelo.

Options:
    -c, --log-classes         Loga as classes, ao invés do código gerado.
    --compile                   Indica se o código gerado deve ser compilado.
"""

import logging
from docopt import docopt
from generator import Generator
from logging.config import fileConfig

__author__ = u'Rogério Pereira'
__email__ = 'rogeriorp@gmail.com'
__version__ = '1.0'

if __name__ == '__main__':
    # Carrega a configuração do log.
    fileConfig('logging_config.ini')
    logger = logging.getLogger(__name__)

    # Faz toda a macumba com os parâmetros da linha de comando <3.
    parametros_script = docopt(__doc__)

    # Renderiza a aplicação.
    xml_file = parametros_script['ARQUIVO']
    generator = Generator(xml_file)
    logger.info(u'Iniciando geração da aplicação.')
    genfiles_and_codes = generator.generate()
    logger.info(u'Aplicação gerada com sucesso.')

    # Caso informado que o código seja impresso na tela.
    log_classes = parametros_script['--log-classes']
    if log_classes:
        logger.info(u'Classes no arquivo XML:\n%s' % generator.project.classes)
    else:
        for genfile, code in genfiles_and_codes.items():
            logger.info(u'Código do arquivo "%s":\n%s' % (genfile, code))

    # Caso solicitado, compila o código gerado.
    compile_param = parametros_script['--compile']
    if compile_param:
        pyfiles = [f for f in genfiles_and_codes.keys() if f.find('.py') != -1]
        for genfile in pyfiles:
            logger.info(u'Compilando arquivo "%s".' % genfile)
            execfile(genfile)
            logger.info(u'Compilado com sucesso "%s".' % genfile)
