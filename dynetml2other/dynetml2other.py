#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Imports a DyNetML file into a wrapper class that uses NetworkX, igraph, or Python dictionaries to contain the networks.

.. moduleauthor:: Peter M. Landwehr <plandweh@cs.cmu.edu>
"""


__author__ = 'Peter M. Landwehr <plandweh@cs.cmu.edu>'

from DynamicMetaNetwork import DynamicMetaNetwork
from lxml import etree
import os


def main(dynetml_path, network_format="dict"):
    """
    :param str|unicode dynetml_path: Path to a dynetml file
    :param str|unicode network_format: The network format; we expect "networkx", "igraph", or nothing ("dict")
    :returns: The data wrapped in the appropriate class and stored in the specified graph library
    :rtype: DynamicMetaNetwork|MetaNetwork|None
    """
    if not isinstance(dynetml_path, (str, unicode)):
        raise TypeError('dynetml_path must be str or unicode')

    if not isinstance(network_format, (str, unicode)):
        raise TypeError('network_format must be str or unicode')

    if network_format.lower() not in ('dict', 'igraph', 'networkx', ''):
        raise ValueError('network_format must be blank, "dict", "igraph" or "networkx"; got {0}'.format(network_format))

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
        if network_format.lower() == 'networkx':
            from MetaNetworkNetworkX import MetaNetworkNX as MetaNetwork
        elif network_format.lower() == 'igraph':
            from MetaNetworkIGraph import MetaNetworkIG as MetaNetwork
        else:
            from MetaNetwork import MetaNetwork

        outnetwork = MetaNetwork()
        outnetwork.load_from_tag(root.getroot())

    return outnetwork

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])