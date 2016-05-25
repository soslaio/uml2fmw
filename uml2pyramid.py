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

import generator as gen
from docopt import docopt

__author__ = u'Rogério Pereira'
__email__ = 'rogeriorp@gmail.com'
__version__ = '1.0'


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
    file_code_result = gen.generate_files(xml_file)

    # Caso informado que o código seja impresso na tela.
    if print_code:
        for f, code in file_code_result.items():
            print(u'\n---- IMPRIMINDO ARQUIVO %s ----\n' % f)
            print(code)

    # Imprime os objetos das classes, caso informado.
    if print_object:
        print(u'\n---- IMPRIMINDO CLASSES ----\n')
        print(gen.__classes)

    # Caso solicitado, compila o código gerado.
    if compile_param:
        for f, code in file_code_result.items():
            print(u'\n---- COMPILANDO %s ----\n' % f)
            execfile(f)
