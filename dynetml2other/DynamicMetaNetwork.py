#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: dynetml2other
:synopsis: Imports DyNetML into NetworkX, igraph, or Python dictionaries.

.. moduleauthor:: Peter M. Landwehr <plandweh@cs.cmu.edu>

"""
__author__ = 'Peter M. Landwehr <plandweh@cs.cmu.edu>'

import codecs
from datetime import datetime
import dynetmlparsingutils as dmlpu
from lxml import etree
import os


class DynamicMetaNetwork:
    """
    The DynamicMetaNetwork class is a container for dynamic meta-networks extracted from DyNetML. It bundles together a
    set of Meta-Networks collected at different times.

    :ivar __network_format: the format in which the networks should be stored:"dict", "igraph" or "networkx". \
    It cannot be changed after initialization.
    :ivar attributes: A dictionary of attributes associated with the dynamic network
    :ivar metanetworks: The list of the Meta-Networks associated with the dynamic meta-network.
    """
    def __init__(self, network_format="dict"):
        """
        Initializes a DynamicMetaNetwork

        :param str|unicode network_format: Format in which graphs should be stored: "dict", "igraph" or "networkx"
        """
        if not isinstance(network_format, (str, unicode)):
            raise TypeError('network_format must be a str or unicode')
        self.__network_format = network_format.lower()
        if self.__network_format not in ['dict', 'igraph', 'networkx', '']:
            raise ValueError('network_format must be blank, "dict", "igraph" or "networkx"; got {0}'.
                             format(network_format))

        self.attributes = {}
        self.metanetworks = []

    def get_network_format(self):
        """Returns the network format"""
        return self.__network_format

    def load_from_dynetml(self, dmn_text, properties_to_include=None, properties_to_ignore=None,
                          nodeclasses_to_include=None, nodeclasses_to_ignore=None, networks_to_include=None,
                          networks_to_ignore=None, start_date=None, end_date=None):
        """
        Parses and loads the contents of an XML containing a dynamic meta-network

        :param str|unicode dmn_text: XML containing a dynamic meta-network
        :param list properties_to_include: a list of nodeclass properties that should be included
        :param list properties_to_ignore: a list of nodeclass properties that should be ignored
        :param list nodeclasses_to_include: a list of nodeclasses that should be included
        :param list nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param list networks_to_include: a list of networks that should be included
        :param list networks_to_ignore: a list of networks that should be ignored
        :param datetime.datetime start_date: Meta-Networks from before this datetime should not be imported
        :param datetime.datetime end_date: MetaNetworks from after this datetime should not be imported
        """
        if not isinstance(dmn_text, (unicode, str)):
            raise TypeError('load_from_dynetml needs text containing XML; got {0}'.format(type(dmn_text)))

        dmn_tag = etree.XML(dmn_text)

        if dmn_tag.tag != 'DynamicMetaNetwork':
            return

        self.load_from_tag(dmn_tag, properties_to_include, properties_to_ignore, nodeclasses_to_include,
                           nodeclasses_to_ignore, networks_to_include, networks_to_ignore, start_date, end_date)

    def load_from_tag(self, dmn_tag, properties_to_include=None, properties_to_ignore=None, nodeclasses_to_include=None,
                      nodeclasses_to_ignore=None, networks_to_include=None, networks_to_ignore=None, start_date=None,
                      end_date=None):
        """
        Parses and loads the contents of an :class:`lxml._Element` containing a dynamic meta-network

        :param lxml._Element dmn_tag: A tag containing a dynamic meta-network
        :param list properties_to_include: a list of nodeclass properties that should be included
        :param list properties_to_ignore: a list of nodeclass properties that should be ignored
        :param list nodeclasses_to_include: a list of nodeclasses that should be included
        :param list nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param list networks_to_include: a list of networks that should be included
        :param list networks_to_ignore: a list of networks that should be ignored
        :param datetime.datetime start_date: MetaNetworks from before this datetime should not be imported
        :param datetime.datetime end_date: MetaNetworks from after this datetime should not be imported
        """
        #if not isinstance(dmn_tag, (unicode, str)):
        #    raise TypeError('load_from_dynetml needs text containing XML; got {0}'.format(type(dnn_text)))
        for attrib_key in dmn_tag.attrib:
            self.attributes[attrib_key] = dmlpu.format_prop(dmn_tag.attrib[attrib_key])

        if self.__network_format == 'networkx':
            from MetaNetworkNetworkX import MetaNetworkNX as MetaNetwork
        elif self.__network_format == 'igraph':
            from MetaNetworkIGraph import MetaNetworkIG as MetaNetwork
        else:
            from MetaNetwork import MetaNetwork

        for mn_tag in dmn_tag.iterfind('MetaNetwork'):

            if start_date is not None:
                if start_date > datetime.strptime(mn_tag.attrib['id'], '%Y%m%dT%H:%M:%S'):
                    continue

            if end_date is not None:
                if end_date < datetime.strptime(mn_tag.attrib['id'], '%Y%m%dT%H:%M:%S'):
                    continue

            self.metanetworks.append(MetaNetwork())
            self.metanetworks[-1].load_from_tag(mn_tag, properties_to_include, properties_to_ignore,
                                                nodeclasses_to_include, nodeclasses_to_ignore, networks_to_include,
                                                networks_to_ignore)

    def drop_metanetworks_before(self, start_date):
        """:param datetime.datetime start_date: Drop meta-networks that occur before this datetime."""
        while len(self.metanetworks) > 0 and \
                datetime.strptime(self.metanetworks[0].attributes['id'], '%Y%m%dT%H:%M:%S') < start_date:
            self.metanetworks.remove(0)

    def drop_metanetworks_after(self, end_date):
        """:param datetime.datetime end_date: Drop meta-networks that occur after this datetime."""
        while len(self.metanetworks) > 0 and \
                datetime.strptime(self.metanetworks[-1].attributes['id'], '%Y%m%dT%H:%M:%S') > end_date:
            self.metanetworks.remove(-1)

    def drop_metanetworks_for_ranges(self, range_tuples, keep_in_range=True):
        """
        :param list range_tuples: A list of tuples containing of a  start date and end date pair
        :param list keep_in_range: If true, dates outside of any tuple are dropped. If false, dates within any tuple \
        are dropped.
        """
        dmlpu.check_contained_types(range_tuples, 'range_tuples', datetime)

        for mn in self.metanetworks:
            date_val = datetime.strptime(self.metanetworks[-1].attributes['id'], '%Y%m%dT%H:%M:%S')
            for r_t in range_tuples:
                if (keep_in_range and r_t[0] > date_val or r_t[1] < date_val) or \
                        (keep_in_range is False and r_t[0] <= date_val <= r_t[1]):
                    self.metanetworks.remove(mn)

    def write_dynetml(self, out_file_path):
        """:param str|unicode out_file_path: Write the dynamic meta-network to this path."""
        if type(out_file_path) not in [str, unicode]:
            raise TypeError('out_file_path must be str or unicode')

        if os.path.exists(out_file_path) and os.path.isdir(out_file_path):
            raise IOError('out_file_path cannot be a directory')

        # bs = self.convert_to_dynetml(True)
        #
        # with codecs.open(out_file_path, 'w', 'utf8') as outfile:
        #     outfile.write(bs.prettify())
        xml_root = self.convert_to_dynetml()

        with codecs.open(out_file_path, 'w', 'utf8') as outfile:
            outfile.write('<?xml version="1.0" standalone="yes"?>\n\n')
            outfile.write(etree.tostring(xml_root, pretty_print=True))

    def convert_to_dynetml(self):
        """Return the dynamic meta-network as an :class:`lxml._Element`"""
        # bs = BeautifulSoup(features='xml')
        # bs.append(bs.new_tag('DynamicMetaNetwork'))
        # for attr in self.attributes:
        #     bs.DynamicMetaNetwork[attr] = dmlpu.unformat_prop(self.attributes[attr])
        #
        # for mn in self.metanetworks:
        #     bs.DynamicMetaNetwork.append(mn.convert_to_dynetml())
        #
        # if not is_entire_file:
        #     bs = bs.DynamicMetaNetwork
        #
        # return bs
        dmn = etree.Element('DynamicMetaNetwork')
        for attr in self.attributes:
            dmn.attrib[attr] = dmlpu.unformat_prop(self.attributes[attr])

        for mn in self.metanetworks:
            etree.SubElement(dmn, mn.convert_to_dynetml())

        return dmn

    def pretty_print(self):
        """Pretty-print the dynamic meta-network"""
        print '= Dynamic Meta-Network ='
        print '= Properties ='
        for attr in self.attributes:
            print u' {0}: {1}'.format(attr, self.attributes[attr]).encode('utf8')

        for mm in self.metanetworks:
            mm.pretty_print()