#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper class for converting DyNetML files into NetworkX graphs.
Meta-Networks will be stored as instances of the MetaNetwork class, which contains a list of nx.Graphs and nx.DiGraphs.
Dynamic Meta-Networks are stored as instances of the DynamicMetaNetwork class, which contains a list of MetaNetworks.
"""

from bs4 import BeautifulSoup
import codecs
from collections import defaultdict
import dynetmlparsingutils as dmlpu
from lxml import etree
import networkx as nx
import os
import sys

# TODO merge into coommon repo with dynetml2igraph and a dict-based graph under a common superclass
# TODO create unit test for converting to dynetml
# TODO add function for unioning DynamicMetaNetworks
# TODO add function for unioning MetaNetworks
# TODO add function for unioning networks
# TODO make it possible to reasonably build a DynamicMetaNetwork from scratch
# TODO make it possible to reasonably build a MetaNetwork from scratch


class DynamicMetaNetwork:
    """
    The DynamicMetaNetwork class is a container for Dynamic Meta-Networks
    It bundles together a set of Meta-Networks collected at different times.
    self.attributes is a dictionary of attributes associated with the dynamic network
    self.metanetworks is the list of the Meta-Networks associated with the Dynamic Meta-Network.
    """

    def __init__(self):
        self.attributes = {}
        self.metanetworks = []

    def load_from_dynetml(self, dmn_text, properties_to_include=list(), properties_to_ignore=list(),
                          nodeclasses_to_include=list(), nodeclasses_to_ignore=list(),
                          networks_to_include=list(), networks_to_ignore=list()):
        """
        Parses XML containing a dynamic meta network and loads the contents
        :param dmn_text: XML containing a DynamicMetaNetwork
        :param properties_to_include: a list of nodeclass properties that should be included
        :param properties_to_ignore: a list of nodeclass properties that should be ignored
        :param nodeclasses_to_include: a list of nodeclasses that should be included
        :param nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param networks_to_include: a list of networks that should be included
        :param networks_to_ignore: a list of networks that should be ignored
        :raise TypeError: if dmn_text isn't a string or unicode
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
        Parses the content of an lxml _Element containing a dynamic meta network and loads the contents
        :param dmn_tag: An lxml _Element containing a DynamicMetaNetwork
        :param properties_to_include: a list of nodeclass properties that should be included
        :param properties_to_ignore: a list of nodeclass properties that should be ignored
        :param nodeclasses_to_include: a list of nodeclasses that should be included
        :param nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param networks_to_include: a list of networks that should be included
        :param networks_to_ignore: a list of networks that should be ignored
        :raise TypeError: if dnn isn't a BeautifulSoup Tag
        """
        #if not isinstance(dmn_tag, (unicode, str)):
        #    raise TypeError('load_from_dynetml needs text containing XML; got {0}'.format(type(dnn_text)))
        for attrib_key in dmn_tag.attrib:
            self.attributes[attrib_key] = dmlpu.format_prop(dmn_tag.attrib[attrib_key])

        for mn_tag in dmn_tag.iterfind('MetaNetwork'):
            self.metanetworks.append(MetaNetwork())
            self.metanetworks[-1].load_from_tag(mn_tag, properties_to_ignore, properties_to_include,
                                                nodeclasses_to_include, nodeclasses_to_ignore,
                                                networks_to_include, networks_to_ignore)

    def write_dynetml(self, out_file_path):
        """
        Writes dynamic meta network to a file
        :param out_file_path: The path to the output file
        :raise TypeError: if out_file_path isn't a string or unicode
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


class MetaNetwork:
    """
    The MetaNetwork class is a container for a Meta-Network extracted from DyNetML.
    self.properties is a dictionary of the different properties associated with the Meta-Network.
    self.propertyIdentities is a dictionary of the two defining traits of each property associated with the network
    self.node_tree is a three-layer dictionary laying out node sets grouped into classes, nodes with node sets, and
    properties associated with each node: self.nodesets[node class][node set][node][node property] = <property>
    NOTE that node attributes are also stored in the dictionary. If an attribute and a property have a colliding value,
    the property will be retained.
    self.networks is a dictionary of the different networks included in the Meta-Network, stored as nx.Graphs and
    nx.DiGraphs. The type of graph depends on whether the Meta-Network property classifies the graph as directed or
    undirected.
    While ORA can constrain network properties on other dimensions, _no_other_properties_ will be automatically
    preserved if you start manipulating the networks.
    """
    def __init__(self):
        self.attributes = {}
        self.properties = {}
        self.propertyIdentities = {}
        self.node_tree = defaultdict(dmlpu.nodeclass_dict)
        self.networks = {}

    def load_from_dynetml(self, mn_text, properties_to_include=list(), properties_to_ignore=list(),
                          nodeclasses_to_include=list(), nodeclasses_to_ignore=list(),
                          networks_to_include=list(), networks_to_ignore=list()):
        """
        Reads XML defining a meta network and imports its contents
        :param mn_text: XML containing a meta network
        :param properties_to_include: a list of nodeclass properties that should be included
        :param properties_to_ignore: a list of nodeclass properties that should be ignored
        :param nodeclasses_to_include: a list of nodeclasses that should be included
        :param nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param networks_to_include: a list of networks that should be included
        :param networks_to_ignore: a list of networks that should be ignored
        """
        if not isinstance(mn_text, (unicode, str)):
            raise TypeError('load_from_dynetml needs text containing XML; got {0}'.format(type(mn_text)))

        mn_tag = etree.XML(mn_text)

        if mn_tag.tag != 'MetaNetwork':
            return

        for attrib_key in mn_tag.attrib:
            self.attributes[attrib_key] = dmlpu.format_prop(mn_tag.attrib[attrib_key])

        self.load_from_tag(mn_tag, properties_to_include, properties_to_ignore,
                           nodeclasses_to_include, nodeclasses_to_ignore,
                           networks_to_include, networks_to_ignore)

    def load_from_tag(self, mn_tag, properties_to_include=list(), properties_to_ignore=list(),
                      nodeclasses_to_include=list(), nodeclasses_to_ignore=list(),
                      networks_to_include=list(), networks_to_ignore=list()):
        """
        Reads an lxml _Elememt defining a meta network and imports its contents
        :param mn_tag: An lxml _Element containing a meta network
        :param properties_to_include: a list of nodeclass properties that should be included
        :param properties_to_ignore: a list of nodeclass properties that should be ignored
        :param nodeclasses_to_include: a list of nodeclasses that should be included
        :param nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param networks_to_include: a list of networks that should be included
        :param networks_to_ignore: a list of networks that should be ignored
        """
        prop_inclusion_test = dmlpu.validate_and_get_inclusion_test(
            (properties_to_include, 'properties_to_include'),
            (properties_to_ignore, 'properties_to_ignore'))
        nodeclass_inclusion_test = dmlpu.validate_and_get_inclusion_test(
            (nodeclasses_to_include, 'nodeclasses_to_include'),
            (nodeclasses_to_ignore, 'nodeclasses_to_ignore'))
        network_inclusion_test = dmlpu.validate_and_get_inclusion_test(
            (networks_to_include, 'networks_to_include'),
            (networks_to_ignore, 'networks_to_ignore'))

        for attrib_key in mn_tag.attrib:
            self.attributes[attrib_key] = dmlpu.format_prop(mn_tag.attrib[attrib_key])

        for prop in mn_tag.find('properties').iterfind('property'):
            self.properties[prop.attrib['id']] = dmlpu.format_prop(prop.attrib['value'])

        self.propertyIdentities = \
            dmlpu.get_property_identities_dict(mn_tag.find('propertyIdentities'), prop_inclusion_test)

        self.node_tree = dmlpu.get_nodeclass_dict(mn_tag.find('nodes'), prop_inclusion_test, nodeclass_inclusion_test)

        for nk_tag in mn_tag.find('networks').iterfind('network'):
            if not network_inclusion_test(nk_tag.attrib['id']):
                continue

            if nk_tag.attrib['isDirected'] == 'true':
                g = nx.DiGraph()
            else:
                g = nx.Graph()

            g.graph['sourceType'] = nk_tag.attrib['sourceType']
            g.graph['source'] = nk_tag.attrib['source']
            g.graph['targetType'] = nk_tag.attrib['targetType']
            g.graph['target'] = nk_tag.attrib['target']
            g.graph['id'] = nk_tag.attrib['id']
            g.graph['isDirected'] = nk_tag.attrib['isDirected'] == 'true'
            g.graph['allowSelfLoops'] = nk_tag.attrib['allowSelfLoops'] == 'true'
            g.graph['isBinary'] = nk_tag.attrib['isBinary'] == 'true'
            #for attrib_key in nk_tag.attrib:
            #   g.graph[attrib_key] = format_prop(nk_tag.attrib[attrib_key])

            link_list = list()
            if g.graph['isBinary']:
                for link in nk_tag.iterfind('link'):
                    link_list.append((link.attrib['source'], link.attrib['target']))
                g.add_edges_from(link_list)
            else:
                for link in nk_tag.iterfind('link'):
                    weight = float(link.attrib['value']) if 'value' in link.attrib else 1.0
                    link_list.append((link.attrib['source'], link.attrib['target'], weight))
                g.add_weighted_edges_from(link_list)

            self.networks[nk_tag.attrib['id']] = g

    def write_dynetml(self, out_file_path):
        """
        Takes a path and writes out generated dynetml
        :param out_file_path: path where dynetml should be written
        :raise TypeError: if out_file_path isn't a sting
        :raise IOError: if out_file_path is a directory
        """
        if type(out_file_path) not in [str, unicode]:
            raise TypeError

        if os.path.exists(out_file_path) and os.path.isdir(out_file_path):
            raise IOError

        bs = self.convert_to_dynetml(True)

        with codecs.open(out_file_path, 'w', 'utf8') as outfile:
            outfile.write(bs.prettify())

    def convert_to_dynetml(self, is_entire_file=False):
        """
        Converts the graph to dynetml and returns a BeautifulSoup tag
        :param is_entire_file: if True, wraps value as a soup. If False, returns the top tag
        :return: a BeautifulSoup tag
        :raise TypeError: if is_entire_file isn't a bool
        """
        if not isinstance(is_entire_file, bool):
            raise TypeError

        bs = BeautifulSoup(features='xml')
        bs.append(bs.new_tag('MetaNetwork'))

        for attr in self.attributes:
            bs.MetaNetwork[attr] = dmlpu.unformat_prop(self.attributes[attr])

        bs.MetaNetwork.append(dmlpu.get_property_identities_tag(self.propertyIdentities))

        bs.MetaNetwork.append(bs.new_tag('properties'))
        for key in self.properties:
            prop_tag = bs.new_tag('property')
            prop_tag['id'] = key
            prop_tag['value'] = dmlpu.unformat_prop(self.properties[key])
            bs.MetaNetwork.properties.append(prop_tag)

        bs.MetaNetwork.append(bs.new_tag('nodes'))
        for class_type in self.node_tree:
            for class_id in self.node_tree[class_type]:
                nodeclass_tag = bs.new_tag('nodeclass', type=class_type, id=class_id)
                nodeclass_tag.append(dmlpu.get_property_identities_tag(self.node_tree[class_type][class_id][0]))

                for key in self.node_tree[class_type][class_id][1]:
                    node_tag = bs.new_tag('node', id=key)
                    for attr in self.node_tree[class_type][class_id][1][key][0]:
                        node_tag[attr] = dmlpu.unformat_prop(self.node_tree[class_type][class_id][1][key][0][attr])
                    node_tag.append(dmlpu.get_properties_tag(self.node_tree[class_type][class_id][1][key][1]))
                    nodeclass_tag.append(node_tag)

                bs.MetaNetwork.nodes.append(nodeclass_tag)

        bs.MetaNetwork.append(bs.new_tag('networks'))
        for key in self.networks:
            network_tag = bs.new_tag('network')
            network_tag['sourceType'] = self.networks[key].graph['sourceType']
            network_tag['source'] = self.networks[key].graph['source']
            network_tag['targetType'] = self.networks[key].graph['targetType']
            network_tag['target'] = self.networks[key].graph['target']
            network_tag['id'] = key
            network_tag['isDirected'] = dmlpu.unformat_prop(self.networks[key].graph['isDirected'])
            network_tag['allowSelfLoops'] = dmlpu.unformat_prop(self.networks[key].graph['allowSelfLoops'])
            network_tag['isBinary'] = dmlpu.unformat_prop(self.networks[key].graph['isBinary'])

            if self.networks[key].graph['isBinary']:
                for edge in self.networks[key].edges_iter(data=True):
                    network_tag.append(bs.new_tag('link', source=edge[0], target=edge[1], value=edge[2]['weight']))
            else:
                for edge in self.networks[key].edges_iter():
                    network_tag.append(bs.new_tag('link', source=edge[0], target=edge[1]))

            bs.MetaNetwork.networks.append(network_tag)

        if not is_entire_file:
            bs = bs.MetaNetwork

        return bs

    def pretty_print(self):
        """Prints the meta network"""
        print ' == Meta-Network =='
        print ' == Properties =='
        for prop in self.properties:
            print u'  {0}: {1}'.format(prop, self.properties[prop]).encode('utf8')

        print ' == Nodeclasses & Nodesets =='
        for n_c in self.node_tree:
            print u'  Nodeclass {0}:'.format(n_c).encode('utf8')
            for n_s in self.node_tree[n_c]:
                print u'   Nodeset {0}:'.format(n_s).encode('utf8')
                print u'   |-'
                for prop_ident in self.node_tree[n_c][n_s][0]:
                    print u'   | {0}: {1}'.format(prop_ident, self.node_tree[n_c][n_s][0][prop_ident])
                print u'   |-\n'

                for node in self.node_tree[n_c][n_s][1]:
                    print u'    Node {0}'.format(node).encode('utf8')
                    for attr in self.node_tree[n_c][n_s][1][node][0]:
                        print u'     {0}: {1}'.format(attr,
                                                      self.node_tree[n_c][n_s][1][node][0][attr]).encode('utf8')
                    for prop in self.node_tree[n_c][n_s][1][node][1]:
                        print u'     {0}: {1}'.format(prop,
                                                      self.node_tree[n_c][n_s][1][node][1][prop]).encode('utf8')
        print ' == Networks =='
        network_count = 0
        for nk_key in self.networks:
            nk = self.networks[nk_key]
            print u'  Network {0}: {1}'.format(network_count, nk_key).encode('utf8')
            for prop in nk.graph:
                print u'   {0}: {1}'.format(prop, nk.graph[prop]).encode('utf8')
            print '   {0} nodes'.format(len(nk.nodes()))
            print '   {0} edges'.format(len(nk.edges()))
            network_count += 1


def dynetml2networkx(dynetml_path):
    """
    This method reads in a DyNetML file and returns the contained DynamicMetaNetwork or MetaNetwork objects.
    :return an instance of DynamicMetaNetwork, an instance of MetaNetwork, or None
    :raise TypeError: if dynetml_path isn't a string or unicode
    :raise IOError: if dynetml_path isn't a file or doesn't exist
    """
    if not type(dynetml_path) in [str, unicode]:
        raise TypeError('Path to dynetml file must be str or unicode')

    if not os.path.isfile(dynetml_path):
        raise IOError('{0} isn\'t a file'.format(dynetml_path))

    try:
        root = etree.parse(dynetml_path)
    except (etree.XMLSyntaxError, etree.XMLSchemaError, etree.XMLSchemaParseError, OSError):
        return None

    outnetwork = None
    if root.getroot().tag == 'DynamicMetaNetwork':
        outnetwork = DynamicMetaNetwork()
        outnetwork.load_from_dynetml(root.getroot())
    elif root.getroot().tag == 'MetaNetwork':
        outnetwork = MetaNetwork()
        outnetwork.load_from_dynetml(root.getroot())

    return outnetwork


def main(args):
    for arg in args:
        if not os.path.exists(arg):
            continue

        dynetml2networkx(arg)


if __name__ == "__main__":
    main(sys.argv[1:])