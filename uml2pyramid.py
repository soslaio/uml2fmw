# -*- coding: utf-8 -*-

"""
Script que transforma um modelo UML numa aplicação Pyramid.

Usage:
    uml2pyramid.py [--print-code | -c]
    [--print-objects | -o]
    [--compilar]
    ARQUIVO

Arguments:
    ARQUIVO                 Arquivo XML do modelo.

Options:
    -c, --print-code        Número do processo a ser analisado.
    -o, --print-objects     Filtrar pelo status dos processos.
    --compilar              Indica se o código gerado deve ser compilado.
"""

from docopt import docopt
from u2p import generate


if __name__ == '__main__':
    # Faz toda a macumba com os parâmetros da linha de comando <3.
    _parametros_script = docopt(__doc__)

    # Parâmetros do script.
    xml_file = _parametros_script['ARQUIVO']
    print_code = _parametros_script['--print-code']
    print_object = _parametros_script['--print-objects']
    compilar = _parametros_script['--compilar']

    # Renderiza a aplicação.
    code = generate(xml_file)

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
        compiled = compile(code, '', 'exec')
        exec compiled
