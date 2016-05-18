from sqlalchemy import Enum, Column, Index, Integer, Text, String, Numeric, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from zope.sqlalchemy import ZopeTransactionExtension
from deform.widget import TextInputWidget, SelectWidget, RadioChoiceWidget, SequenceWidget, AutocompleteInputWidget

import colander

import yaml
from os.path import dirname, abspath, join

from sqlalchemy import event
from colanderalchemy import setup_schema

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
path = dirname(abspath(__file__))


class Parceiro(Base):
    
    __tablename__ = "parceiro"
    __mapper_args__ = { "polymorphic_on": "tipo" }
    
    CodParceiro = Column(Integer,
        primary_key=True,
        )
    NomeRazaoSocial = Column(String,
        )
    CPFCNPJ = Column(String,
        )
    tipo = Column(String(50),
        nullable=False,
        info={ "colanderalchemy" : { 'exclude': True } })

event.listen(Parceiro, "mapper_configured", setup_schema)


class Pessoa(Parceiro):
    
    __mapper_args__ = { "polymorphic_identity": "pessoa" }
    
    Nascimento = Column(Date,
        )
    Escolaridade = Column(String(25),
        )

event.listen(Pessoa, "mapper_configured", setup_schema)


class Empresa(Parceiro):
    
    __mapper_args__ = { "polymorphic_identity": "empresa" }
    
    NomeFantasia = Column(String(50),
        )
    Abertura = Column(Date,
        )

event.listen(Empresa, "mapper_configured", setup_schema)


class Contato(Base):
    
    __tablename__ = "contato"
    __mapper_args__ = { "polymorphic_on": "tipo" }
    
    id = Column(Integer,
        primary_key=True,
        info={ "colanderalchemy" : {
               "exclude": True,}}
            
        )
    receber = Column(Boolean,
        nullable=False,
        info={ "colanderalchemy" : {
               "default": True,
               "description": "Permitir que o Sebrae entre em contato através deste meio.",
               "title": "Receber contato",}}
            
        )
    tipo = Column(String(50),
        nullable=False,
        info={ "colanderalchemy" : { 'exclude': True } })

event.listen(Contato, "mapper_configured", setup_schema)


class Email(Contato):
    
    __mapper_args__ = { "polymorphic_identity": "email" }
    
    email = Column(String(100),
        nullable=False,
        )

event.listen(Email, "mapper_configured", setup_schema)


class Telefone(Contato):
    
    __mapper_args__ = { "polymorphic_identity": "telefone" }
    
    telefone_tipo = Column(String(25),
        nullable=True,
        )
    telefone = Column(String(25),
        nullable=False,
        info={ "colanderalchemy" : {
               "widget": "TelefoneWidgetInfo()",}}
            
        )

event.listen(Telefone, "mapper_configured", setup_schema)

