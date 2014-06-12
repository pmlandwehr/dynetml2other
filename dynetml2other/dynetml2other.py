#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper class for converting DyNetML files into NetworkX or igraph graphs.
Meta-Networks will be stored as instances of the MetaNetwork class, which contains graphs from the chosen library.
Dynamic Meta-Networks are stored as instances of the DynamicMetaNetwork class, which contains a list of MetaNetworks.
"""
__author__ = 'plandweh'

from DynamicMetaNetwork import DynamicMetaNetwork
from lxml import etree
import os


def dynetml2other(dynetml_path, network_format):
    """
    This method reads in a DyNetML file and returns the contained DynamicMetaNetwork or MetaNetwork objects.
    :param dynetml_path: Path to dynetml file
    :param network_format: str or unicode containing the network format; we expect "networkx" or "igraph"
    :type dynetml_path: str or unicode
    :type network_format: str or unicode
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

    if network_format.lower() not in ('dict', 'igraph', 'networkx'):
        raise ValueError('network_format must be "dict", "igraph" or "networkx"; got {0}'.format(network_format))

    if not os.path.isfile(dynetml_path):
        raise IOError('{0} isn\'t a file'.format(dynetml_path))

    try:
        root = etree.parse(dynetml_path)
    except (etree.XMLSyntaxError, etree.XMLSchemaError, etree.XMLSchemaParseError, OSError):
        return None

    outnetwork = None
    root_tag = root.getroot().tag
    if root_tag in ['DynamicMetaNetwork', 'DynamicNetwork']:
        outnetwork = DynamicMetaNetwork(network_format.lower())
        outnetwork.load_from_tag(root.getroot())
    elif root_tag == 'MetaNetwork':
        if network_format.lower() == 'dict':
            from MetaNetworkDict import MetaNetworkDict as MetaNetwork
        elif network_format.lower() == 'igraph':
            from MetaNetworkIGraph import MetaNetworkIG as MetaNetwork
        else:
            from MetaNetworkNetworkX import MetaNetworkNX as MetaNetwork

        outnetwork = MetaNetwork()
        outnetwork.load_from_tag(root.getroot())

    return outnetwork