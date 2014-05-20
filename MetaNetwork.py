#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'plandweh'

from bs4 import BeautifulSoup
import codecs
from collections import defaultdict
import dynetmlparsingutils as dmlpu
from lxml import etree
import os


class MetaNetwork:
    """
    The MetaNetwork class is a container for a Meta-Network extracted from DyNetML.
    self.properties is a dictionary of the different properties associated with the Meta-Network.
    self.propertyIdentities is a dictionary of the two defining traits of each property associated with the network
    self._node_tree is a three-layer dictionary laying out node sets grouped into classes, nodes with node sets, and
    properties associated with each node: self.nodesets[node class][node set][node][node property] = <property>
    NOTE that node attributes are also stored in the dictionary. If an attribute and a property have a colliding value,
    the property will be retained. _node_tree is protected so that tweet modifications will be included in the
    corresponding graphs.
    self.networks is a dictionary of the different networks included in the Meta-Network. The specifications for these
    are largely left out
    While ORA can constrain network properties on other dimensions, _no_other_properties_ will be automatically
    preserved if you start manipulating the networks.
    """
    def __init__(self):
        self.attributes = {}
        self.properties = {}
        self.propertyIdentities = {}
        self._node_tree = defaultdict(dmlpu.nodeclass_dict)
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

        self._node_tree = dmlpu.get_nodeclass_dict(mn_tag.find('nodes'), prop_inclusion_test, nodeclass_inclusion_test)

        for nk_tag in mn_tag.find('networks').iterfind('network'):
            if not network_inclusion_test(nk_tag.attrib['id']):
                continue

            self._parse_and_add_graph_tag(nk_tag)

    def get_node_tree(self):
        return self._node_tree

    def validate_tree_branch(self, nodeclass_name, nodeset_name=None, node_name=None):
        for pair in (nodeclass_name, 'nodeclass_name'), (nodeset_name, 'nodeset_name'), (node_name, 'node_name'):
            if not isinstance(pair[0], (str, unicode, None)):
                raise TypeError('{0} must be str or unicode'.format(pair[1]))

        if nodeclass_name not in self._node_tree:
            raise KeyError('No nodeclass named {0}'.format(nodeclass_name))

        if nodeset_name is not None and nodeset_name not in self._node_tree[nodeclass_name]:
            raise KeyError('No nodeset named {0} in nodeclass {1}'.format(nodeset_name, nodeclass_name))

        if node_name is not None and node_name not in self._node_tree[nodeclass_name][nodeset_name][1]:
            raise KeyError('No node named {0} in nodeset {1}'.format(node_name, nodeset_name))

    def get_nodeclass(self, nodeclass_name):
        self.validate_tree_branch(nodeclass_name)
        return self._node_tree[nodeclass_name]

    def get_nodeset(self, nodeclass_name, nodeset_name):
        self.validate_tree_branch(nodeclass_name, nodeset_name)
        return self._node_tree[nodeclass_name][nodeset_name]

    def get_node(self, nodeclass_name, nodeset_name, node_name):
        self.validate_tree_branch(nodeclass_name, nodeset_name, node_name)
        return self._node_tree[nodeclass_name][nodeset_name][node_name]

    def set_node_property(self, nodeclass_name, nodeset_name, node_name, property_name, value):
        self.validate_tree_branch(nodeclass_name, nodeset_name, node_name)
        if property_name not in self._node_tree[nodeclass_name][nodeset_name][0]:
            raise KeyError('{0} is not a property for nodeset {1}'.format(property_name, nodeset_name))

        self._node_tree[nodeclass_name][nodeset_name][1][node_name][property_name] = \
            dmlpu.format_prop(value, self._node_tree[nodeclass_name][nodeset_name][0][property_name][0])

    def create_nodeset_property(self, nodeclass_name, nodeset_name, property_name, type_str, singlevalued_bool):
        self.validate_tree_branch(nodeclass_name, nodeset_name)
        if property_name in self._node_tree[nodeclass_name][nodeset_name]:
            raise KeyError('property {0} already exists for nodeset {1}'.format(property_name, nodeset_name))
        if not isinstance(type_str, (str, unicode)):
            raise TypeError('type_str must be a str or unicode')
        if type_str not in ['number', 'date', 'text', 'categoryText', 'URI']:
            raise ValueError('type_str must be "number", "date" "text", "categoryText", or "URI"; got {0}'.
                             format(type_str))
        if not isinstance(singlevalued_bool, bool):
            raise KeyError('singlevalued_bool must be a bool')

        self._node_tree[nodeclass_name][nodeset_name][0][property_name] = type_str, singlevalued_bool

    def rename_node(self, nodeclass_name, nodeset_name, node_name, new_node_name):
        """

        :param nodeclass_name:
        :param nodeset_name:
        :param node_name:
        :param new_node_name:
        """
        self.validate_tree_branch(nodeclass_name, nodeset_name, node_name)
        if not isinstance(new_node_name, (str, unicode)):
            raise TypeError('new_node_name must be a str or unicode')
        if new_node_name in self._node_tree[nodeclass_name][nodeset_name]:
            raise KeyError('{0} is already a key in nodeset {1}'.format(new_node_name, nodeset_name))

        self._node_tree[nodeclass_name][nodeset_name][new_node_name] = \
            self._node_tree[nodeclass_name][nodeset_name][node_name]
        del self._node_tree[nodeclass_name][nodeset_name][node_name]
        self._rename_network_nodes(nodeclass_name, nodeset_name, node_name, new_node_name)

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
            raise TypeError('is_entire_file must be a bool')

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
        for class_type in self._node_tree:
            for class_id in self._node_tree[class_type]:
                nodeclass_tag = bs.new_tag('nodeclass', type=class_type, id=class_id)
                nodeclass_tag.append(dmlpu.get_property_identities_tag(self._node_tree[class_type][class_id][0]))

                for key in self._node_tree[class_type][class_id][1]:
                    node_tag = bs.new_tag('node', id=key)
                    for attr in self._node_tree[class_type][class_id][1][key][0]:
                        node_tag[attr] = dmlpu.unformat_prop(self._node_tree[class_type][class_id][1][key][0][attr])
                    node_tag.append(dmlpu.get_properties_tag(self._node_tree[class_type][class_id][1][key][1]))
                    nodeclass_tag.append(node_tag)

                bs.MetaNetwork.nodes.append(nodeclass_tag)

        networks_tag = self._get_networks_tag()
        bs.MetaNetwork.networks.append(networks_tag)

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
        for n_c in self._node_tree:
            print u'  Nodeclass {0}:'.format(n_c).encode('utf8')
            for n_s in self._node_tree[n_c]:
                print u'   Nodeset {0}:'.format(n_s).encode('utf8')
                print u'   |-'
                for prop_ident in self._node_tree[n_c][n_s][0]:
                    print u'   | {0}: {1}'.format(prop_ident, self._node_tree[n_c][n_s][0][prop_ident])
                print u'   |-\n'

                for node in self._node_tree[n_c][n_s][1]:
                    print u'    Node {0}'.format(node).encode('utf8')
                    for attr in self._node_tree[n_c][n_s][1][node][0]:
                        print u'     {0}: {1}'.format(attr,
                                                      self._node_tree[n_c][n_s][1][node][0][attr]).encode('utf8')
                    for prop in self._node_tree[n_c][n_s][1][node][1]:
                        print u'     {0}: {1}'.format(prop,
                                                      self._node_tree[n_c][n_s][1][node][1][prop]).encode('utf8')

        self._pretty_print_networks()

    def _rename_network_nodes(self, nodeclass_name, nodeset_name, node_name, new_node_name):
        pass

    def _get_networks_tag(self):
        pass

    def _parse_and_add_graph_tag(self, nk_tag):
        print 'bloop...'
        pass

    def _pretty_print_networks(self):
        pass