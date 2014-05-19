#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper class for converting DyNetML files into NetworkX graphs.
Meta-Networks will be stored as instances of the MetaNetwork class, which contains a list of nx.Graphs and nx.DiGraphs.
Dynamic Meta-Networks are stored as instances of the DynamicMetaNetwork class, which contains a list of MetaNetworks.
"""

from DynamicMetaNetwork import DynamicMetaNetwork
from MetaNetwork import MetaNetwork
from lxml import etree
import os
import sys

# TODO merge into coommon repo with dynetml2igraph and a dict-based graph under a common superclass
# TODO create unit test for converting to dynetml
# TODO add function for unioning DynamicMetaNetworks
# TODO add function for unioning MetaNetworks
# TODO add function for unioning networks
# TODO make it possible to reasonably build a DynamicMetaNetwork from scratch
# TODO make it possible to reasonably build a MetaNetwork from scratch


def dynetml2other(dynetml_path, network_format=str()):
    """
    This method reads in a DyNetML file and returns the contained DynamicMetaNetwork or MetaNetwork objects.
    :return an instance of DynamicMetaNetwork, an instance of MetaNetwork, or None
    :rtype: DynamicMetaNetwork, MetaNetwork, or None
    :raise TypeError: if dynetml_path isn't a string or unicode
    :raise TypeError: if network_format isn't a string or unicode
    :raise ValueError: if network_format isn't "igraph" or "networkx"
    :raise IOError: if dynetml_path isn't a file or doesn't exist
    """
    if not isinstance(dynetml_path, (str, unicode)):
        raise TypeError('dynetml_path must be str or unicode')

    if not isinstance(network_format, (str, unicode)):
        raise TypeError('network_format must be str or unicode')

    if network_format.lower() not in ('igraph', 'networkx'):
        raise ValueError('network_format must be "igraph" or "networkx"; got {0}'.format(network_format))

    if not os.path.isfile(dynetml_path):
        raise IOError('{0} isn\'t a file'.format(dynetml_path))

    try:
        root = etree.parse(dynetml_path)
    except (etree.XMLSyntaxError, etree.XMLSchemaError, etree.XMLSchemaParseError, OSError):
        return None

    outnetwork = None
    if root.getroot().tag == 'DynamicMetaNetwork':
        outnetwork = DynamicMetaNetwork(network_format)
        outnetwork.load_from_dynetml(root.getroot())
    elif root.getroot().tag == 'MetaNetwork':
        outnetwork = MetaNetwork(network_format)
        outnetwork.load_from_dynetml(root.getroot())

    return outnetwork


def main(args):
    for arg in args:
        if not os.path.exists(arg):
            continue

        dynetml2other(arg)


if __name__ == "__main__":
    main(sys.argv[1:])