#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'plandweh'

import codecs
from datetime import datetime
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
        :raise ValueError: If network_format is not "dict", "igraph" or "networkx"
        """
        if not isinstance(network_format, (str, unicode)):
            raise TypeError('network_format must be a str or unicode')
        self.__network_format = network_format.lower()
        if self.__network_format not in ['dict', 'igraph', 'networkx']:
            raise ValueError('network_format must be "dict", "igraph" or "networkx"; got {0}'.format(network_format))

        self.attributes = {}
        self.metanetworks = []

    def get_network_format(self):
        """Returns the network format"""
        return self.__network_format

    def load_from_dynetml(self, dmn_text, properties_to_include=None, properties_to_ignore=None,
                          nodeclasses_to_include=None, nodeclasses_to_ignore=None, networks_to_include=None,
                          networks_to_ignore=None, start_date=None, end_date=None):
        """
        Parses XML containing a Dynamic Meta-Network and loads the contents
        :param dmn_text: XML containing a Dynamic Meta-Network
        :param properties_to_include: a list of nodeclass properties that should be included
        :param properties_to_ignore: a list of nodeclass properties that should be ignored
        :param nodeclasses_to_include: a list of nodeclasses that should be included
        :param nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param networks_to_include: a list of networks that should be included
        :param networks_to_ignore: a list of networks that should be ignored
        :param start_date: MetaNetworks from before this datetime should not be imported
        :param end_date: MetaNetworks from after this datetime should not be imported
        :param dmn_text: str or unicode
        :type properties_to_include: list
        :type properties_to_ignore: list
        :type nodeclasses_to_include: list
        :type nodeclasses_to_ignore: list
        :type networks_to_include: list
        :type networks_to_ignore: list
        :type start_date: datetime.datetime
        :type end_date: datetime.datetime
        :raise TypeError: if dmn_text isn't a str or unicode
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
        Parses the content of an lxml _Element containing a Dynamic Meta-Network and loads the contents
        :param dmn_tag: An lxml _Element containing a Dynamic Meta-Network
        :param properties_to_include: a list of nodeclass properties that should be included
        :param properties_to_ignore: a list of nodeclass properties that should be ignored
        :param nodeclasses_to_include: a list of nodeclasses that should be included
        :param nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param networks_to_include: a list of networks that should be included
        :param networks_to_ignore: a list of networks that should be ignored
        :param start_date: MetaNetworks from before this datetime should not be imported
        :param end_date: MetaNetworks from after this datetime should not be imported
        :type dmn_tag: lxml._Element
        :type properties_to_include: list
        :type properties_to_ignore: list
        :type nodeclasses_to_include: list
        :type nodeclasses_to_ignore: list
        :type networks_to_include: list
        :type networks_to_ignore: list
        :type start_date: datetime
        :type end_date: datetime
        :raise TypeError: if dnn isn't an lxml._Element
        """
        #if not isinstance(dmn_tag, (unicode, str)):
        #    raise TypeError('load_from_dynetml needs text containing XML; got {0}'.format(type(dnn_text)))
        for attrib_key in dmn_tag.attrib:
            self.attributes[attrib_key] = dmlpu.format_prop(dmn_tag.attrib[attrib_key])

        if self.__network_format == 'dict':
            from MetaNetworkDict import MetaNetworkDict as MetaNetwork
        elif self.__network_format == 'igraph':
            from MetaNetworkIGraph import MetaNetworkIG as MetaNetwork
        else:
            from MetaNetworkNetworkX import MetaNetworkNX as MetaNetwork

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
        """
        Drop metanetworks that occur before a given date
        :param start_date: Metanetworks from times before start_date should be dropped
        :type start_date: datetime
        """
        while len(self.metanetworks) > 0 and \
                datetime.strptime(self.metanetworks[0].attributes['id'], '%Y%m%dT%H:%M:%S') < start_date:
            self.metanetworks.remove(0)

    def drop_metanetworks_after(self, end_date):
        """
        Drop metanetworks that occur after a given date
        :param end_date: Metanetworks from times after end_date should be dropped
        :type end_date: datetime
        """
        while len(self.metanetworks) > 0 and \
                datetime.strptime(self.metanetworks[-1].attributes['id'], '%Y%m%dT%H:%M:%S') > end_date:
            self.metanetworks.remove(-1)

    def drop_metanetworks_for_ranges(self, range_tuples, keep_in_range=True):
        """
        Drop metanetworks relative to a number of range_tuples
        :param range_tuples: a list of tuples consisting of a start date and end date.
        :param keep_in_range: if True, dates within the range are retained. If false, dates within the range are
        discarded
        :type range_tuples: list
        :type keep_in_range: bool
        """
        dmlpu.check_contained_types(range_tuples, 'range_tuples', datetime)

        for mn in self.metanetworks:
            date_val = datetime.strptime(self.metanetworks[-1].attributes['id'], '%Y%m%dT%H:%M:%S')
            for r_t in range_tuples:
                if (keep_in_range and r_t[0] > date_val or r_t[1] < date_val) or \
                (keep_in_range is False and r_t[0] <= date_val and r_t[1] >= date_val):
                    self.metanetworks.remove(mn)

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

        # bs = self.convert_to_dynetml(True)
        #
        # with codecs.open(out_file_path, 'w', 'utf8') as outfile:
        #     outfile.write(bs.prettify())
        xml_root = self.convert_to_dynetml()

        with codecs.open(out_file_path, 'w', 'utf8') as outfile:
            outfile.write('<?xml version="1.0" standalone="yes"?>\n\n')
            outfile.write(etree.tostring(xml_root, pretty_print=True))

    def convert_to_dynetml(self):
        """
        Converts the dynamic meta network to a BeautifulSoup Tag and returns it
        :return: a BeautifulSoup Tag
        :raise TypeError: if is_entire_file is not a bool
        """
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
        """Pretty print the dynamic meta network"""
        print '= Dynamic Meta-Network ='
        print '= Properties ='
        for attr in self.attributes:
            print u' {0}: {1}'.format(attr, self.attributes[attr]).encode('utf8')

        for mm in self.metanetworks:
            mm.pretty_print()