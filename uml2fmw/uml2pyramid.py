# -*- coding: utf-8 -*-
"""
Script que transforma um modelo UML numa aplicação Pyramid.

Usage:
    uml2pyramid.py
    [--show-code | -c]
    [--show-object | -o]
    [--compile]
    ARQUIVO

Arguments:
    ARQUIVO                   Arquivo XML do modelo.

Options:
    -c, --show-code           Mostra o código gerado no log.
    -o, --show-object         Mostra os objetos das classes geradas.
    --compile                 Indica se o código python gerado deve ser compilado.
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
    logger.info(u'Iniciando geração da aplicação.')
    generator = Generator(parametros_script['ARQUIVO'])
    genfiles_and_codes = generator.generate()
    logger.info(u'Aplicação gerada com sucesso.')

    # Caso informado, loga o código.
    if parametros_script['--show-code']:
        for genfile, code in genfiles_and_codes.items():
            logger.info(u'Código do arquivo "%s":\n%s' % (genfile, code))

    # Caso informado, loga o objeto das classes.
    if parametros_script['--show-object']:
        logger.info(u'Classes no arquivo XML:\n%s' % generator.project.classes)

    # Caso solicitado, compila o código gerado.
    compile_param = parametros_script['--compile']
    if compile_param:
        pyfiles = [f for f in genfiles_and_codes.keys() if f.find('.py') != -1]
        for genfile in pyfiles:
            logger.info(u'Compilando arquivo "%s".' % genfile)
            execfile(genfile)
            logger.info(u'Compilado com sucesso "%s".' % genfile)
