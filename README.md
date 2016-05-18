# uml2pyramid
Script que transforma sistemas modelados em UML para aplicações Pyramid em Python 2.

### Uso ###
* Modelar as classes em UML no Visual Paradigm e exportar em XML;
* Rodar o comando

    $ python render.py /path/to/xml/file

### Dependências ###
* Visual Paradigm: Modelagem das classes;
* lxml: Parse do arquivo XML;
* chameleon: Templates de arquivos;

### Roadmap ###
* Não depender do Visual Paradigm, utilizando o padrão XMI.
