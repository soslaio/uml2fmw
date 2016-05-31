# -*- coding: utf-8 -*-
"""
Script que transforma um modelo UML numa aplicação Pyramid.

Usage:
    uml2pyramid.py [--print-code | -c]
    [--print-objects | -o]
    [--compile]
    ARQUIVO

Arguments:
    ARQUIVO                     Arquivo XML do modelo.

Options:
    -c, --print-code            Número do processo a ser analisado.
    -o, --print-objects         Filtrar pelo status dos processos.
    --compile                   Indica se o código gerado deve ser compilado.
"""

from docopt import docopt
from generator import Generator

__author__ = u'Rogério Pereira'
__email__ = 'rogeriorp@gmail.com'
__version__ = '1.0'


if __name__ == '__main__':
    # Faz toda a macumba com os parâmetros da linha de comando <3.
    parametros_script = docopt(__doc__)

    # Renderiza a aplicação.
    xml_file = parametros_script['ARQUIVO']
    generator = Generator(xml_file)
    genfiles_and_codes = generator.generate()

    # Caso informado que o código seja impresso na tela.
    print_code = parametros_script['--print-code']
    if print_code:
        for f, code in genfiles_and_codes.items():
            print(u'\n---- IMPRIMINDO ARQUIVO %s ----\n' % f)
            print(code)

    # Imprime os objetos das classes, caso informado.
    print_object = parametros_script['--print-objects']
    if print_object:
        print(u'\n---- IMPRIMINDO CLASSES ----\n')
        print(generator.project.classes)

    # Caso solicitado, compila o código gerado.
    compile_param = parametros_script['--compile']
    if compile_param:
        for f in genfiles_and_codes.keys():
            print(u'\n---- COMPILANDO %s ----\n' % f)
            execfile(f)
