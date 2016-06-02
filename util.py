# -*- coding: utf-8 -*-
"""Métodos úteis."""

import yaml
from os.path import abspath, dirname, join, sep

here = abspath(dirname(__file__))


def read_yaml(key):
    """Lê parâmetros do arquivo de configuração YAML."""
    yaml_file = join(here, 'config.yml')
    with open(yaml_file, 'r') as f:
        d = yaml.load(f)
    return d[key]


def short_dir(path):
    """Retorna o caminho encurtado para a pasta"""
    basepath = read_yaml('basepath')
    spath = path.split(sep)
    i = spath.index(basepath) + 1
    sdir = sep.join(spath[i:])
    return '~%s%s' % (sep, sdir)