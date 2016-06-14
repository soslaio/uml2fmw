# -*- coding: utf-8 -*-

import logging
from base import Base, OrderedDictBase
from collections import OrderedDict
from tagged_values import TaggedValues
from attributes import Atributos
from relationships import Generalizations
from stereotypes import Stereotypes
logger = logging.getLogger('classes')


class Classe(Base):
    """Objeto que representa uma classe."""

    def __init__(self, attributes, xml_attributes, tagged_values, stereotypes=None):
        self.nreferences = 0
        self.attributes = attributes
        self.xml_attributes = xml_attributes
        self.tagged_values = tagged_values
        self.parents = OrderedDict()
        self.children = OrderedDict()
        self.stereotypes = stereotypes
        super(Classe, self).__init__(xml_attributes)

    @property
    def association_attributes(self):
        """Atributos de associação da classe."""
        return self.attributes.association_attributes

    @property
    def referenced_classes(self):
        """Retorna uma lista com os IDs das classes referenciadas."""
        referenced_classes = list()

        # Generalizações são adicionadas primeiro.
        if bool(self.parents):
            for parent in self.parents:
                referenced_classes.append(parent.id)

        # Associações são adicionadas em seguida.
        for attribute in self.association_attributes:
            referenced_classes.append(attribute.to_id)

        return referenced_classes

    @property
    def is_view_class(self):
        """Indica se a clase é uma view class."""
        return self.stereotypes.find('name', 'view_class') is not None

    @property
    def title(self):
        """Título de apresentação da classe."""
        return self.tagged_values['title'].value \
            if 'title' in self.tagged_values.keys() else self.name

    @property
    def tablename(self):
        """Valor do tagged value 'tablename' da classe."""
        return self.tagged_values['tablename'].value \
            if 'tablename' in self.tagged_values.keys() else self.name.lower()

    @property
    def colander(self):
        """Tagged values da classe relacionados aos schemas do colander."""
        colander_class = ['title', 'description']
        data = {tv.id: tv for tv in self.tagged_values if tv.name in colander_class}
        return TaggedValues(data=data) if data is not None else None

    @property
    def polymorphic_identity(self):
        """Valor do tagged value 'polymorphic_identity' da classe."""
        if bool(self.parents):
            return self.tagged_values['polymorphic_identity'].value \
                if 'polymorphic_identity' in self.tagged_values.keys() else self.name.lower()
        else:
            return None

    @property
    def polymorphic_on(self):
        """Valor do tagged value 'polymorphic_on' da classe."""
        if bool(self.children):
            return self.tagged_values['polymorphic_on'].value \
                if 'polymorphic_on' in self.tagged_values.keys() else 'tipo'
        else:
            return None

    def __str__(self):
        return u"Classe '%s'" % self.name


class Classes(OrderedDictBase):
    """Classes presentes no arquivo XML."""

    def __init__(self, xmlobj=None, data=None, associations=None):
        if xmlobj is not None:
            self.__classes = OrderedDict()
            xmlclasses = xmlobj.Models.Class

            if xmlclasses is not None:
                view_classes = OrderedDict()
                for xmlclasse in xmlclasses:
                    # Atributos XML da classe.
                    xml_attributes = xmlclasse.attrib
                    class_id = xml_attributes['Id']

                    # Outros atributos da classe.
                    class_associations = associations.filter('from_id', class_id)
                    attributes = Atributos(xmlclasse, class_associations=class_associations)
                    tagged_values = TaggedValues(xmlclasse, from_class=True)
                    stereotypes = Stereotypes(xmlclasse)

                    # Cria o objeto Classe e adiciona na lista de classes.
                    classe = Classe(attributes, xml_attributes, tagged_values, stereotypes=stereotypes)
                    classe.nreferences = len(class_associations)

                    # Adiciona as classes, evitando adicionar as view classes.
                    # As view classes tem que ser as últimas, por depender de
                    # classes anteriores.
                    if classe.is_view_class:
                        view_classes[classe.id] = classe
                    else:
                        self.__classes[classe.id] = classe

                # Se as view classes não estiverem vazias, adiciona.
                if bool(view_classes):
                    for vclasse in view_classes.itervalues():
                        self.__classes[vclasse.id] = vclasse

                # Conecta as classes através da lista de generalizações.
                self.connect(xmlobj)

                # Ordena as classes numa segundo uma lógica de referências.
                self.order()
            else:
                logger.debug(u'Nenhuma classe localizada.')
        elif data is not None:
            self.__classes = data
        else:
            self.__classes = OrderedDict()

        # Instancia a classe superior.
        super(Classes, self).__init__(self.__classes, Classes)

    @property
    def view_classes(self):
        """Lista de classes principais."""
        view_classes = OrderedDict()
        for classe in self.__classes.itervalues():
            if classe.is_view_class:
                view_classes[classe.id] = classe
        return Classes(data=view_classes)

    def order(self):
        """Sequencia as classes baseado nas referências que as classes fazem entre elas.

        Começa adicionando classes que não fazem referências a outras, seja por genralização ou associação.
        A partir disso, busca classes que façam referências às classes anteriores, e segue repetindo esse procedimento
        até que nenhuma nova alteração seja feita na lista.
        """
        lap = 1
        have_changes = True
        ordered_classes = OrderedDict()
        while have_changes:
            have_changes = False
            for classe in self.__classes.itervalues():
                # Na primeira volta, carrega as classes que não fazem referências a nenhuma outras.
                if lap == 1:
                    if classe.nreferences == 0:
                        ordered_classes[classe.id] = classe
                        have_changes = True
                else:
                    related = OrderedDict()
                    for oclass in ordered_classes.itervalues():
                        if classe.id not in ordered_classes.keys():
                            if oclass.id in classe.referenced_classes:
                                related[classe.id] = classe
                                have_changes = True
                    if bool(related):
                        ordered_classes.update(related.copy())
            lap += 1

        # Retorna a lista de classes ordenada inversamente.
        self.__classes = ordered_classes
        return ordered_classes

    def connect(self, xmlobj):
        """Analisa a lista de generalizações recebida e faz as relações entre as classes."""

        generalizacoes = Generalizations(xmlobj)

        for classe in self.__classes.itervalues():
            # Busca generalizações relacionadas à classe.
            parents = OrderedDict()
            children = OrderedDict()

            for gen in generalizacoes:
                # Localiza os filhos da classe.
                if classe.id == gen.from_id:
                    children[gen.to_id] = self.__classes[gen.to_id]

                # Localiza os pais da classe.
                if classe.id == gen.to_id:
                    classe.nreferences += 1  # adiciona à genrelalização ao contador de referências.
                    parents[gen.from_id] = self.__classes[gen.from_id]

            if parents is not None:
                classe.parents = Classes(data=parents)

            if children is not None:
                classe.children = Classes(data=children)

    def __str__(self):
        strclass = ''
        for k in self.__classes.keys():
            classe = self.__classes[k]
            strclass += '%s, ID: %s\n' % (classe, classe.id)
            for atributo in classe.attributes:
                strclass += '\t%s\n' % atributo

            if bool(classe.children):
                strclass += '\tFilhos:\n'
                for children in classe.children:
                    strclass += '\t   %s\n' % children

            if bool(classe.parents):
                strclass += '\tPais:\n'
                for parents in classe.parents:
                    strclass += '\t   %s\n' % parents
        return strclass
