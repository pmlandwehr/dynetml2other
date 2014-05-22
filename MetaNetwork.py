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
    self.__node_tree is a three-layer dictionary laying out node sets grouped into classes, nodes with node sets, and
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
        """Initializes a MetaNetwork"""
        self.attributes = {}
        self.properties = {}
        self.propertyIdentities = {}
        self.__node_tree = defaultdict(dmlpu.nodeclass_dict)
        self.networks = {}

    def __validate_tree_branch(self, nodeclass_name, nodeset_name=None, node_name=None):
        """
        Verify that a particular nodeclass, nodeset, or node exists in the node tree
        :param nodeclass_name: The name of a nodeclass
        :param nodeset_name: The name of a nodeset
        :param node_name: The name of a node
        :type nodeclass_name: unicode or str
        :type nodeset_name: unicode, str, or None
        :type node_name: unicode, str, or None
        :raise TypeError: if nodeclass_name, nodeset_name, or node_name is not a str, unicode or None
        :raise KeyError: if nodeclass_name, nodeset_name, or node_name cannot be found in self.__node_tree
        """
        dmlpu.check_type(nodeclass_name, 'nodeclass_name', (str, unicode))
        dmlpu.check_type(nodeset_name, 'nodeset_name', (str, unicode, None))
        dmlpu.check_type(node_name, 'node_name', (str, unicode, None))

        dmlpu.check_key(nodeclass_name, 'nodeclass_name', self.__node_tree, 'self.__node_tree')
        if nodeset_name is not None:
            dmlpu.check_key(nodeset_name, 'nodeset_name', self.__node_tree[nodeclass_name], nodeclass_name)
        if node_name is not None:
            dmlpu.check_key(node_name, 'node_name', self.__node_tree[nodeclass_name][nodeset_name][1], 'nodeset_name')

    def load_from_dynetml(self, mn_text, properties_to_include=list(), properties_to_ignore=list(),
                          nodeclasses_to_include=list(), nodeclasses_to_ignore=list(),
                          networks_to_include=list(), networks_to_ignore=list()):
        """
        Parses XML containing a Meta-Network and loads the contents
        :param mn_text: XML containing a Meta-Network
        :param properties_to_include: a list of nodeclass properties that should be included
        :param properties_to_ignore: a list of nodeclass properties that should be ignored
        :param nodeclasses_to_include: a list of nodeclasses that should be included
        :param nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param networks_to_include: a list of networks that should be included
        :param networks_to_ignore: a list of networks that should be ignored
        :param mn_text: str or unicode
        :param properties_to_include: list of strs or unicodes
        :param properties_to_ignore: list of strs or unicodes
        :param nodeclasses_to_include: list of strs or unicodes
        :param nodeclasses_to_ignore: list of strs or unicodes
        :param networks_to_include: list of strs or unicodes
        :param networks_to_ignore: list of strs or unicodes
        :raise TypeError: if mn_text isn't a str or unicode
        """
        dmlpu.check_type(mn_text, 'mn_text', (unicode, str))
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
        Parses the content of an lxml _Element containing a Meta-Network and loads the contents
        :param mn_tag: An lxml _Element containing a Dynamic Meta-Network
        :param properties_to_include: a list of nodeclass properties that should be included
        :param properties_to_ignore: a list of nodeclass properties that should be ignored
        :param nodeclasses_to_include: a list of nodeclasses that should be included
        :param nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param networks_to_include: a list of networks that should be included
        :param networks_to_ignore: a list of networks that should be ignored
        :type mn_tag: An lxml _Element containing a DynamicMetaNetwork
        :type properties_to_include: list of strs or unicode
        :type properties_to_ignore: list of strs or unicode
        :type nodeclasses_to_include: list of strs or unicode
        :type nodeclasses_to_ignore: list of strs or unicode
        :type networks_to_include: list of strs or unicode
        :type networks_to_ignore: list of strs or unicode
        :raise TypeError: if dnn isn't a BeautifulSoup Tag
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

        self.__node_tree = dmlpu.get_nodeclass_dict(mn_tag.find('nodes'), prop_inclusion_test, nodeclass_inclusion_test)

        for nk_tag in mn_tag.find('networks').iterfind('network'):
            if not network_inclusion_test(nk_tag.attrib['id']):
                continue

            self._parse_and_add_graph_tag(nk_tag)

    def get_node_tree(self):
        """
        Return self.__node_tree
        :return: self.__node_tree
        :rtype: defaultdict(dmlpu.nodeclass_dict)
        """
        return self.__node_tree

    def get_nodeclass(self, nodeclass_name):
        """
        Return a given nodeclass
        :param nodeclass_name: name of the nodeclass to be returned
        :type nodeclass_name: str or unicode
        :return: self.__node_tree[nodeclass_name]
        :rtype: dmlpu.nodeclass_dict
        """
        self.__validate_tree_branch(nodeclass_name)
        return self.__node_tree[nodeclass_name]

    def get_nodeset(self, nodeclass_name, nodeset_name):
        """
        Return a given nodeset
        :param nodeclass_name: name of the parent of nodeset_name
        :param nodeset_name: name of the nodeset to be returned
        :type nodeclass_name: str or unicode
        :type nodeset_name: str or unicode
        :return: self.__node_tree[nodeclass_name][nodeset_name]
        :rtype: dmlpu.nodeset_tuple
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name)
        return self.__node_tree[nodeclass_name][nodeset_name]

    def get_node(self, nodeclass_name, nodeset_name, node_name):
        """
        Return a given node
        :param nodeclass_name: name of the parent of nodeset_name
        :param nodeset_name: name of the parent of node_name
        :param node_name: name of the node to be returned
        :type nodeclass_name: str or unicode
        :type nodeset_name: str or unicode
        :type node_name: str or unicode
        :return: self.__node_tree[nodeclass_name][nodeset_name][node]
        :rtype: dmlpu.node_tuple
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name, node_name)
        return self.__node_tree[nodeclass_name][nodeset_name][node_name]

    def set_node_property(self, nodeclass_name, nodeset_name, node_name, property_name, value):
        """
        Set the value of a node property
        :param nodeclass_name: the name of the parent of nodeset_name
        :param nodeset_name: the name of the parent of node_name
        :param node_name: the name of the node whose property is being set
        :param property_name: the name of the property to be set
        :param value: the value of the parameter
        :type nodeclass_name: str or unicode
        :type nodeset_name: str or unicode
        :type node_name: str or unicode
        :type property_name: str or unicode
        :type value: str, unicode, or the appropriate type specified in dmlpu.format_prop
        :raise TypeError: if property_name isn't a str or unicode
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name, node_name)
        dmlpu.check_type(property_name, 'property_name', (str, unicode))
        dmlpu.check_key(property_name, 'property_name', self.__node_tree[nodeclass_name][nodeset_name][0], nodeset_name)

        self.__node_tree[nodeclass_name][nodeset_name][1][node_name][property_name] = \
            dmlpu.format_prop(value, self.__node_tree[nodeclass_name][nodeset_name][0][property_name][0])

    def create_nodeset_property(self, nodeclass_name, nodeset_name, property_name, type_str, singlevalued_bool):
        """
        Create a new nodeset property
        :param nodeclass_name: the name of the parent of nodeset_name
        :param nodeset_name: the name of the nodeset that should get the new property
        :param property_name: the name of the property to be added
        :param type_str: the type of the parameter
        :param singlevalued_bool: whether or not the parameter should be single-valued
        :type nodeclass_name: str or unicode
        :type nodeset_name: str or unicode
        :type property_name: str or unicode
        :type type_str: str or unicode
        :type singlevalued_bool: bool
        :raise KeyError: If a property named property_name already exists.
        :raise TypeError: If type_str isn't a str or unicode
        :raise ValueError: If type_str isn't "number", "date", "text", "categoryText", or "URI"
        :raise TypeError: If singlevalued_bool isn't a bool
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name)
        dmlpu.check_key(property_name, self.__node_tree[nodeclass_name][nodeset_name],
                        'property {0} already exists for nodeset {1}'.format(property_name, nodeset_name), False)
        dmlpu.check_type(type_str, 'type_str', (str, unicode))
        if type_str not in ['number', 'date', 'text', 'categoryText', 'URI']:
            raise ValueError('type_str must be "number", "date" "text", "categoryText", or "URI"; got {0}'.
                             format(type_str))
        dmlpu.check_type(singlevalued_bool, 'singlevalued_bool', bool)

        self.__node_tree[nodeclass_name][nodeset_name][0][property_name] = type_str, singlevalued_bool

    def add_node(self, nodeclass_name, nodeset_name, node_name, property_dict=None):
        """
        Add a node to a give nodeset in a give nodeclass. If a set of properties are specified, add the properties.
        :param nodeclass_name: name of the parent of nodeset_name
        :param nodeset_name: name of the parent of node_name
        :param node_name: name of the node to be created
        :param property_dict: A dictionary of properties to assign the new node.
        :type nodeclass_name: str or unicode
        :type nodeset_name: str or unicode
        :type node_name: str or unicode
        :type property_dict: dict or None
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name)
        dmlpu.check_type(node_name, 'node_name', (str, unicode))
        dmlpu.check_key(node_name, 'node_name', self.__node_tree[nodeclass_name][nodeset_name][1], nodeset_name, False)
        dmlpu.check_type(property_dict, 'property_dict', (dict, None))
        for property_name in property_dict.keys():
            dmlpu.check_key(property_name, 'property_name', self.__node_tree[nodeclass_name][nodeset_name][0],
             '{0} properties'.format(nodeset_name))

        self.__node_tree[nodeclass_name][nodeset_name][1][node_name] = property_dict


    def rename_node(self, nodeclass_name, nodeset_name, node_name, new_node_name):
        """
        Rename a particular node, both in the node tree and in the networks containing it.
        :param nodeclass_name: name of the parent of nodeset_name
        :param nodeset_name: name of the parent of node_name
        :param node_name: current node name
        :param new_node_name: new name for the node
        :type nodeclass_name: str or unicode
        :type nodeset_name: str or unicode
        :type node_name: str or unicode
        :type new_node_name: str or unicode
        :raise TypeError: if new_node_name is not a str or unicode
        :raise KeyError: if new_node_name is already a node in the node class
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name, node_name)
        dmlpu.check_type(new_node_name, 'new_node_name', (str, unicode))
        dmlpu.check_key(new_node_name, self.__node_tree[nodeclass_name][nodeset_name],
                        '{0} is already a key in nodeset {1}'.format(new_node_name, nodeset_name), False)

        self.__node_tree[nodeclass_name][nodeset_name][new_node_name] = \
            self.__node_tree[nodeclass_name][nodeset_name][node_name]
        del self.__node_tree[nodeclass_name][nodeset_name][node_name]
        self._rename_network_nodes(nodeclass_name, nodeset_name, node_name, new_node_name)

    def write_dynetml(self, out_file_path):
        """
        Takes a path and writes out generated dynetml
        :param out_file_path: path where dynetml should be written
        :type out_file_path: str or unicode
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
        :type is_entire_file: bool
        :return: bs4.element.Tag
        :raise TypeError: if is_entire_file isn't a bool
        """
        dmlpu.check_type(is_entire_file, 'is_entire_file', bool)

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
        for class_type in self.__node_tree:
            for class_id in self.__node_tree[class_type]:
                nodeclass_tag = bs.new_tag('nodeclass', type=class_type, id=class_id)
                nodeclass_tag.append(dmlpu.get_property_identities_tag(self.__node_tree[class_type][class_id][0]))

                for key in self.__node_tree[class_type][class_id][1]:
                    node_tag = bs.new_tag('node', id=key)
                    for attr in self.__node_tree[class_type][class_id][1][key][0]:
                        node_tag[attr] = dmlpu.unformat_prop(self.__node_tree[class_type][class_id][1][key][0][attr])
                    node_tag.append(dmlpu.get_properties_tag(self.__node_tree[class_type][class_id][1][key][1]))
                    nodeclass_tag.append(node_tag)

                bs.MetaNetwork.nodes.append(nodeclass_tag)

        networks_tag = self._get_networks_tag()
        bs.MetaNetwork.networks.append(networks_tag)

        if not is_entire_file:
            bs = bs.MetaNetwork

        return bs

    def pretty_print(self):
        """Pretty prints the meta network"""
        print ' == Meta-Network =='
        print ' == Properties =='
        for prop in self.properties:
            print u'  {0}: {1}'.format(prop, self.properties[prop]).encode('utf8')

        print ' == Nodeclasses & Nodesets =='
        for n_c in self.__node_tree:
            print u'  Nodeclass {0}:'.format(n_c).encode('utf8')
            for n_s in self.__node_tree[n_c]:
                print u'   Nodeset {0}:'.format(n_s).encode('utf8')
                print u'   |-'
                for prop_ident in self.__node_tree[n_c][n_s][0]:
                    print u'   | {0}: {1}'.format(prop_ident, self.__node_tree[n_c][n_s][0][prop_ident])
                print u'   |-\n'

                for node in self.__node_tree[n_c][n_s][1]:
                    print u'    Node {0}'.format(node).encode('utf8')
                    for attr in self.__node_tree[n_c][n_s][1][node][0]:
                        print u'     {0}: {1}'.format(attr,
                                                      self.__node_tree[n_c][n_s][1][node][0][attr]).encode('utf8')
                    for prop in self.__node_tree[n_c][n_s][1][node][1]:
                        print u'     {0}: {1}'.format(prop,
                                                      self.__node_tree[n_c][n_s][1][node][1][prop]).encode('utf8')

        self._pretty_print_networks()

    def _rename_network_nodes(self, nodeclass_name, nodeset_name, node_name, new_node_name):
        """
        Stub class for renaming a node in the networks containing it.
        :param nodeclass_name: name of the parent of nodeset_name
        :param nodeset_name: name of the parent of node_name
        :param node_name: current node name
        :param new_node_name: new name for the node
        :type nodeclass_name: str or unicode
        :type nodeset_name: str or unicode
        :type node_name: str or unicode
        :type new_node_name: str or unicode
        """
        pass

    def _get_networks_tag(self):
        """Stub class for generating a bs4.element.Tag from the networks"""
        pass

    def _parse_and_add_graph_tag(self, nk_tag):
        """
        Stub class for parsing an lxml _Element tag containing a network and adding it to the MetaNetwork.
        :param nk_tag: The tag to be parsed.
        :type nk_tag: lxml _Element
        """
        pass

    def _pretty_print_networks(self):
        """Stub class for pretty printing the networks"""
        pass