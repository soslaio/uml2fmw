# -*- coding: utf-8 -*-


def print_classes(classes):
    """ Método útil para visualização de classes. """

    for classe in classes:
        print classe, classe.id
        for atributo in classe.attributes:
            print '\t%s' % atributo

        if classe.children is not None:
            for children in classe.children:
                print '\t\tFilhos: %s' % children

        if classe.parents is not None:
            for parents in classe.parents:
                print '\t\tPais: %s' % parents
