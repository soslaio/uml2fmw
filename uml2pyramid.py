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
from u2p import generate
from os import path

__here = path.abspath(path.dirname(__file__))

if __name__ == '__main__':
    # Faz toda a macumba com os parâmetros da linha de comando <3.
    parametros_script = docopt(__doc__)

    # Parâmetros do script.
    xml_file = parametros_script['ARQUIVO']
    print_code = parametros_script['--print-code']
    print_object = parametros_script['--print-objects']
    compilar = parametros_script['--compile']
    filename = parametros_script['--filename']

    # Renderiza a aplicação.
    code = generate(xml_file)

    # Escreve o código num arquivo.
    filename = filename if filename else 'generated_code.py'
    code_file = path.join(__here, 'generated', filename)
    with open(code_file, 'w') as cf:
        cf.write(code.encode('utf-8'))
        cf.close()

    # Imprime o código, caso informado.
    if print_code:
        print code

    # Imprime os objetos das classes, caso informado.
    if print_object:
        from u2p import get_classes
        from u2p.util import print_classes

        classes = get_classes(xml_file)
        print_classes(classes)

    # Compila o código gerado para localizar erros.
    if compilar:
        print
        compiled = compile(code, '', 'exec')
        exec compiled
