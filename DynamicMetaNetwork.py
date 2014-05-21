#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'plandweh'

from bs4 import BeautifulSoup
import codecs
import dynetmlparsingutils as dmlpu
from lxml import etree
import os


class DynamicMetaNetwork:
    """
    The DynamicMetaNetwork class is a container for Dynamic Meta-Networks extracted from DyNetML.
    It bundles together a set of Meta-Networks collected at different times.
    self.__network_format is the format in which the networks should be stored. Can be 'igraph' or 'networkx'.
    It cannot be changed after initialization.
    self.attributes is a dictionary of attributes associated with the dynamic network
    self.metanetworks is the list of the Meta-Networks associated with the Dynamic Meta-Network.
    """
    def __init__(self, network_format):
        """
        Initializes a DynamicMetaNetwork
        :param network_format: format in which graphs should be stored. "igraph" or "networkx"
        :type network_format: str or unicode
        :raise TypeError: If network format is not str or unicode
        :raise ValueError: If network_format is not "igraph" or "networkx"
        """
        if not isinstance(network_format, (str, unicode)):
            raise TypeError('network_format must be a str or unicode')

        self.__network_format = network_format.lower()

        if self.__network_format not in ['igraph', 'networkx']:
            raise ValueError('network_format must be "igraph" or "networkx"; got {0}'.format(network_format))

        self.attributes = {}
        self.metanetworks = []

    def get_network_format(self):
        """Returns the network format"""
        return self.__network_format

    def load_from_dynetml(self, dmn_text, properties_to_include=list(), properties_to_ignore=list(),
                          nodeclasses_to_include=list(), nodeclasses_to_ignore=list(),
                          networks_to_include=list(), networks_to_ignore=list()):
        """
        Parses XML containing a Dynamic Meta-Network and loads the contents
        :param dmn_text: XML containing a Dynamic Meta-Network
        :param properties_to_include: a list of nodeclass properties that should be included
        :param properties_to_ignore: a list of nodeclass properties that should be ignored
        :param nodeclasses_to_include: a list of nodeclasses that should be included
        :param nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param networks_to_include: a list of networks that should be included
        :param networks_to_ignore: a list of networks that should be ignored
        :param dmn_text: str or unicode
        :param properties_to_include: list of strs or unicodes
        :param properties_to_ignore: list of strs or unicodes
        :param nodeclasses_to_include: list of strs or unicodes
        :param nodeclasses_to_ignore: list of strs or unicodes
        :param networks_to_include: list of strs or unicodes
        :param networks_to_ignore: list of strs or unicodes
        :raise TypeError: if dmn_text isn't a str or unicode
        """
        if not isinstance(dmn_text, (unicode, str)):
            raise TypeError('load_from_dynetml needs text containing XML; got {0}'.format(type(dmn_text)))

        dmn_tag = etree.XML(dmn_text)

        if dmn_tag.tag != 'DynamicMetaNetwork':
            return

        self.load_from_tag(dmn_tag, properties_to_ignore, properties_to_include,
                           nodeclasses_to_include, nodeclasses_to_ignore, networks_to_include, networks_to_ignore)

    def load_from_tag(self, dmn_tag, properties_to_include=list(), properties_to_ignore=list(),
                      nodeclasses_to_include=list(), nodeclasses_to_ignore=list(),
                      networks_to_include=list(), networks_to_ignore=list()):
        """
        Parses the content of an lxml _Element containing a Dynamic Meta-Network and loads the contents
        :param dmn_tag: An lxml _Element containing a Dynamic Meta-Network
        :param properties_to_include: a list of nodeclass properties that should be included
        :param properties_to_ignore: a list of nodeclass properties that should be ignored
        :param nodeclasses_to_include: a list of nodeclasses that should be included
        :param nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param networks_to_include: a list of networks that should be included
        :param networks_to_ignore: a list of networks that should be ignored
        :type dmn_tag: An lxml _Element containing a DynamicMetaNetwork
        :type properties_to_include: list of strs or unicode
        :type properties_to_ignore: list of strs or unicode
        :type nodeclasses_to_include: list of strs or unicode
        :type nodeclasses_to_ignore: list of strs or unicode
        :type networks_to_include: list of strs or unicode
        :type networks_to_ignore: list of strs or unicode
        :raise TypeError: if dnn isn't a BeautifulSoup Tag
        """
        #if not isinstance(dmn_tag, (unicode, str)):
        #    raise TypeError('load_from_dynetml needs text containing XML; got {0}'.format(type(dnn_text)))
        for attrib_key in dmn_tag.attrib:
            self.attributes[attrib_key] = dmlpu.format_prop(dmn_tag.attrib[attrib_key])

        if self.__network_format == 'igraph':
            from MetaNetworkIGraph import MetaNetworkIG as MetaNetwork
        else:
            from MetaNetworkNetworkX import MetaNetworkNX as MetaNetwork

        for mn_tag in dmn_tag.iterfind('MetaNetwork'):
            self.metanetworks.append(MetaNetwork())
            self.metanetworks[-1].load_from_tag(mn_tag, properties_to_ignore, properties_to_include,
                                                nodeclasses_to_include, nodeclasses_to_ignore,
                                                networks_to_include, networks_to_ignore)

    def write_dynetml(self, out_file_path):
        """
        Writes dynamic meta network to a file
        :param out_file_path: The path to the output file
        :type out_file_path: str or unicode
        :raise TypeError: if out_file_path isn't a str or unicode
        :raise IOError: if out_file_path points to a directory
        """
        if type(out_file_path) not in [str, unicode]:
            raise TypeError('out_file_path must be str or unicode')

        if os.path.exists(out_file_path) and os.path.isdir(out_file_path):
            raise IOError('out_file_path cannot be a directory')

        bs = self.convert_to_dynetml(True)

        with codecs.open(out_file_path, 'w', 'utf8') as outfile:
            outfile.write(bs.prettify())

    def convert_to_dynetml(self, is_entire_file=False):
        """
        Converts the dynamic meta network to a BeautifulSoup Tag and returns it
        :param is_entire_file: If True, Tag will include XML wrapper code
        :type is_entire_file: bool
        :return: a BeautifulSoup Tag
        :raise TypeError: if is_entire_file is not a bool
        """
        if not isinstance(is_entire_file, bool):
            raise TypeError('is_entire_file must be True or False')

        bs = BeautifulSoup(features='xml')
        bs.append(bs.new_tag('DynamicMetaNetwork'))
        for attr in self.attributes:
            bs.DynamicMetaNetwork[attr] = dmlpu.unformat_prop(self.attributes[attr])

        for mn in self.metanetworks:
            bs.DynamicMetaNetwork.append(mn.convert_to_dynetml())

        if not is_entire_file:
            bs = bs.DynamicMetaNetwork

        return bs

    def pretty_print(self):
        """Print the dynamic meta network"""
        print '= Dynamic Meta-Network ='
        print '= Properties ='
        for attr in self.attributes:
            print u' {0}: {1}'.format(attr, self.attributes[attr]).encode('utf8')

        for mm in self.metanetworks:
            mm.pretty_print()