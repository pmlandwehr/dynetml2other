#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: dynetml2other
:synopsis: Imports DyNetML into NetworkX, igraph, or Python dictionaries.

.. moduleauthor:: Peter M. Landwehr <plandweh@cs.cmu.edu>

"""

__author__ = 'Peter M. Landwehr <plandweh@cs.cmu.edu>'

import codecs
from collections import defaultdict
import dynetmlparsingutils as dmlpu
from lxml import etree
import os


class MetaNetwork:
    """
    The MetaNetwork class is a container for a meta-network extracted from DyNetML. The base class stores network data \
    in dictionaries; using a graphing library to store network data requires that you use one of the two SubClasses. \
    Manipulating networks will *not* guarantee corresponding modifications of data contained in __node_tree; you will \
    need to make any desired transformations to the nodes yourself.

    :ivar properties: A dictionary of the different properties associated with the meta-network.
    :ivar propertyIdentities: A dictionary of the two defining traits of each property associated with the network
    :ivar __node_tree: A three-layer dictionary laying out node sets grouped into classes, nodes with node sets, and \
    properties associated with each node: self.nodesets[node class][node set][node][node property] = <property>. \
    *Note* that node attributes are also stored in the dictionary. If an attribute and a property colide on some \
    value, the property value will be retained. __node_tree is private in order to regulate how properties are added \
    and to help insure that networks are valid. This may change in future updates.
    :ivar networks: A dictionary of the different networks in the meta-network.
    :ivar sources: A dictionary of source materials; it exists exclusively in networks generated by AutoMap, and is \
    not yet fully handled.
    """
    def __init__(self):
        """Initializes a MetaNetwork"""
        self.attributes = {}
        self.properties = {}
        self.propertyIdentities = {}
        self.__node_tree = dmlpu.node_tree()
        self.networks = {}
        self.sources = {}

    def __validate_tree_branch(self, nodeclass_name, nodeset_name=None, node_name=None):
        """
        Verify that a particular nodeclass, nodeset, or node exists in __node_tree

        :param unicde|str nodeclass_name: The name of a nodeclass
        :param unicode|str|None nodeset_name: The name of a nodeset
        :param unicode|str|None node_name: The name of a node
        """
        dmlpu.check_type(nodeclass_name, 'nodeclass_name', (str, unicode))
        dmlpu.check_type(nodeset_name, 'nodeset_name', (str, unicode, None))
        dmlpu.check_type(node_name, 'node_name', (str, unicode, None))

        dmlpu.check_key(nodeclass_name, 'nodeclass_name', self.__node_tree, 'self.__node_tree')
        if nodeset_name is not None:
            dmlpu.check_key(nodeset_name, 'nodeset_name', self.__node_tree[nodeclass_name], nodeclass_name)
        if node_name is not None:
            dmlpu.check_key(node_name, 'node_name', self.__node_tree[nodeclass_name][nodeset_name][1], 'nodeset_name')

    def load_from_dynetml(self, mn_text, properties_to_include=None, properties_to_ignore=None,
                          nodeclasses_to_include=None, nodeclasses_to_ignore=None, networks_to_include=None,
                          networks_to_ignore=None):
        """
        Parses XML containing a meta-network and loads the contents

        :param str|unicode mn_text: XML containing a meta-network
        :param list properties_to_include: a list of nodeclass properties that should be included
        :param list properties_to_ignore: a list of nodeclass properties that should be ignored
        :param list nodeclasses_to_include: a list of nodeclasses that should be included
        :param list nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param list networks_to_include: a list of networks that should be included
        :param list networks_to_ignore: a list of networks that should be ignored
        """
        dmlpu.check_type(mn_text, 'mn_text', (unicode, str))
        mn_tag = etree.XML(mn_text)
        if mn_tag.tag != 'MetaNetwork':
            return
        for attrib_key in mn_tag.attrib:
            self.attributes[attrib_key] = dmlpu.format_prop(mn_tag.attrib[attrib_key])

        self.load_from_tag(mn_tag, properties_to_include, properties_to_ignore, nodeclasses_to_include,
                           nodeclasses_to_ignore, networks_to_include, networks_to_ignore)

    def load_from_tag(self, mn_tag, properties_to_include=None, properties_to_ignore=None, nodeclasses_to_include=None,
                      nodeclasses_to_ignore=None, networks_to_include=None, networks_to_ignore=None):
        """
        Parses the content of an :class:`lxml._Element` containing a meta-network and loads the contents

        :param lxml._Element mn_tag: A tag containing a dynamic meta-network
        :param list properties_to_include: a list of nodeclass properties that should be included
        :param list properties_to_ignore: a list of nodeclass properties that should be ignored
        :param list nodeclasses_to_include: a list of nodeclasses that should be included
        :param list nodeclasses_to_ignore: a list of nodeclasses that should be ignored
        :param list networks_to_include: a list of networks that should be included
        :param list networks_to_ignore: a list of networks that should be ignored
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

        properties_tag = mn_tag.find('properties')
        if properties_tag is not None:
            for prop in properties_tag.iterfind('property'):
                self.properties[prop.attrib['id']] = dmlpu.format_prop(prop.attrib['value'])

        # TODO: Deal with source tag in AutoMap output.

        self.propertyIdentities = \
            dmlpu.get_property_identities_dict(mn_tag.find('propertyIdentities'), prop_inclusion_test)

        self.__node_tree = dmlpu.get_nodeclass_dict(mn_tag.find('nodes'), prop_inclusion_test, nodeclass_inclusion_test)

        for nk_tag in mn_tag.find('networks').iterfind('network'):
            if not network_inclusion_test(nk_tag.attrib['id']):
                continue

            self._parse_and_add_graph_tag(nk_tag)

    def get_node_tree(self):
        """
        :returns: __node_tree
        :rtype: :class:`dynetmlparsingutils.node_tree)`
        """
        return self.__node_tree

    def get_nodeclass(self, nodeclass_name):
        """
        :returns: __node_tree[nodeclass_name]
        :rtype: :class:`dynetmlparsingutils.nodeclass_dict`
        """
        self.__validate_tree_branch(nodeclass_name)
        return self.__node_tree[nodeclass_name]

    def get_nodeset(self, nodeclass_name, nodeset_name):
        """
        :param str|unicode nodeclass_name: name of the parent of nodeset_name
        :param str|unicode nodeset_name: name of the nodeset to be returned
        :return: self.__node_tree[nodeclass_name][nodeset_name]
        :rtype: :class:`dmlpu.nodeset_tuple`
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name)
        return self.__node_tree[nodeclass_name][nodeset_name]

    def get_node(self, nodeclass_name, nodeset_name, node_name):
        """
        :param str|unicode nodeclass_name: name of the parent of nodeset_name
        :param str|unicode nodeset_name: name of the parent of node_name
        :param str|unicode node_name: name of the node to be returned
        :return: self.__node_tree[nodeclass_name][nodeset_name][node]
        :rtype: :class:`dynetmlparsingutils.node_tuple`
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name, node_name)
        return self.__node_tree[nodeclass_name][nodeset_name][node_name]

    def set_node_property(self, nodeclass_name, nodeset_name, node_name, property_name, value):
        """
        Set the value of a node property

        :param str|unicode nodeclass_name: the name of the parent of nodeset_name
        :param str|unicode nodeset_name: the name of the parent of node_name
        :param str|unicode node_name: the name of the node whose property is being set
        :param str|unicode property_name: the name of the property to be set
        :param str|unicode|bool|float|datetime.datetime value: the value of the parameter
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name, node_name)
        dmlpu.check_type(property_name, 'property_name', (str, unicode))
        dmlpu.check_key(property_name, 'property_name', self.__node_tree[nodeclass_name][nodeset_name][0], nodeset_name)

        self.__node_tree[nodeclass_name][nodeset_name][1][node_name][property_name] = \
            dmlpu.format_prop(value, self.__node_tree[nodeclass_name][nodeset_name][0][property_name][0])

    def create_nodeset_property(self, nodeclass_name, nodeset_name, property_name, type_str, singlevalued_bool):
        """
        Create a new nodeset property

        :param str|unicode nodeclass_name: the name of the parent of nodeset_name
        :param str|unicode nodeset_name: the name of the nodeset that should get the new property
        :param str|unicode property_name: the name of the property to be added
        :param str|unicode type_str: the type of the parameter
        :param bool singlevalued_bool: whether or not the parameter should be single-valued
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name)
        dmlpu.check_key(property_name, 'property_name',
                        self.__node_tree[nodeclass_name][nodeset_name][0], nodeset_name, False)
        dmlpu.check_type(type_str, 'type_str', (str, unicode))
        if type_str not in ['number', 'date', 'text', 'categoryText', 'URI']:
            raise ValueError('type_str must be "number", "date" "text", "categoryText", or "URI"; got {0}'.
                             format(type_str))
        dmlpu.check_type(singlevalued_bool, 'singlevalued_bool', bool)

        self.__node_tree[nodeclass_name][nodeset_name][0][property_name] = type_str, singlevalued_bool

    def create_node(self, nodeclass_name, nodeset_name, node_name, property_dict=None):
        """
        Create a node in a give nodeset in a give nodeclass. If a set of properties are specified, add the properties.

        :param str|unicode nodeclass_name: name of the parent of nodeset_name
        :param str|unicode nodeset_name: name of the parent of node_name
        :param str|unicode node_name: name of the node to be created
        :param dict|None property_dict: A dictionary of properties to assign the new node.
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name)
        dmlpu.check_type(node_name, 'node_name', (str, unicode))
        dmlpu.check_key(node_name, 'node_name', self.__node_tree[nodeclass_name][nodeset_name][1], nodeset_name, False)
        dmlpu.check_type(property_dict, 'property_dict', (dict, None))
        for property_name in property_dict.keys():
            dmlpu.check_key(
                property_name, 'property_name',
                self.__node_tree[nodeclass_name][nodeset_name][0], '{0} properties'.format(nodeset_name))

        self.__node_tree[nodeclass_name][nodeset_name][1][node_name] = property_dict

    def rename_node(self, nodeclass_name, nodeset_name, node_name, new_node_name):
        """
        Rename a particular node, both in the node tree and in the networks containing it.

        :param str|unicode nodeclass_name: name of the parent of nodeset_name
        :param str|unicode nodeset_name: name of the parent of node_name
        :param str|unicode node_name: current node name
        :param str|unicode new_node_name: new name for the node
        """
        self.__validate_tree_branch(nodeclass_name, nodeset_name, node_name)
        dmlpu.check_type(new_node_name, 'new_node_name', (str, unicode))
        dmlpu.check_key(new_node_name, 'new_node_name',
                        self.__node_tree[nodeclass_name][nodeset_name][1], nodeset_name, False)

        self.__node_tree[nodeclass_name][nodeset_name][1][new_node_name] = \
            self.__node_tree[nodeclass_name][nodeset_name][1][node_name]
        del self.__node_tree[nodeclass_name][nodeset_name][1][node_name]

        # We assume 'id' exists. If it doesn't, the data has bigger problems.
        self.__node_tree[nodeclass_name][nodeset_name][new_node_name]['id'] = new_node_name

        self._rename_network_nodes(nodeclass_name, nodeset_name, node_name, new_node_name)

    def union_nodesets(self, nodeclass_name, *args):
        """
        Takes two nodesets and combines them in a new nodeset. Properties and entries from the first nodeset override \
        those from the second nodeset.

        :param str|unicode  nodeclass_name: The name of the parent nodeclass of nodeset_one_name and nodeset_two_name
        :param str|unicode nodeset_one_name: The name of the first nodeset in the union.
        :param str|unicode nodset_two_name: The name of the second ndeset in the union.
        :param other_nodesets: union_nodesets takes a \*args argument, so any number of nodesets is acceptable
        :param str|unicode new_nodeset_name: The name of the new nodeset to be created
        """
        if len(args) < 3:
            raise ValueError('Need at least 3 argumets; got {0}'.format(len(args)))

        for nodeset_name in args[:-1]:
            self.__validate_tree_branch(nodeclass_name, nodeset_name)
        dmlpu.check_type(args[-1], 'new_nodeset_name', (str, unicode))
        dmlpu.check_key(args[-1], 'union_nodeset', self.__node_tree[nodeclass_name], nodeclass_name,
                        False)

        merge_nodeset = self.__node_tree[nodeclass_name][args[-2]]
        for i in range(len(args)-3, -1, -1):
            for entry in self.__node_tree[nodeclass_name][args[i]][1]:
                merge_nodeset[1][entry] = self.__node_tree[nodeclass_name][args[i]][1][entry]
            for entry in self.__node_tree[nodeclass_name][args[i]][0]:
                merge_nodeset[0][entry] = self.__node_tree[nodeclass_name][args[i]][0][entry]

        self.__node_tree[nodeclass_name][args[-1]] = merge_nodeset

    def write_dynetml(self, out_file_path):
        """:param str|unicode out_file_path: Write the meta-network to this path."""
        dmlpu.check_type(out_file_path, 'out_file_path', (str, unicode))

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
        """Converts the graph to DyNetML and returns an :class:`lxml._Element`"""

        # bs = BeautifulSoup(features='xml')
        # bs.append(bs.new_tag('MetaNetwork'))
        #
        # for attr in self.attributes:
        #     bs.MetaNetwork[attr] = dmlpu.unformat_prop(self.attributes[attr])
        #
        # bs.MetaNetwork.append(dmlpu.get_property_identities_tag(self.propertyIdentities))
        #
        # bs.MetaNetwork.append(bs.new_tag('properties'))
        # for key in self.properties:
        #     prop_tag = bs.new_tag('property')
        #     prop_tag['id'] = key
        #     prop_tag['value'] = dmlpu.unformat_prop(self.properties[key])
        #     bs.MetaNetwork.properties.append(prop_tag)
        #
        # bs.MetaNetwork.append(bs.new_tag('nodes'))
        # for class_type in self.__node_tree:
        #     for class_id in self.__node_tree[class_type]:
        #         nodeclass_tag = bs.new_tag('nodeclass', type=class_type, id=class_id)
        #         nodeclass_tag.append(dmlpu.get_property_identities_tag(self.__node_tree[class_type][class_id][0]))
        #
        #         for key in self.__node_tree[class_type][class_id][1]:
        #             node_tag = bs.new_tag('node', id=key)
        #             for attr in self.__node_tree[class_type][class_id][1][key][0]:
        #                 node_tag[attr] = dmlpu.unformat_prop(self.__node_tree[class_type][class_id][1][key][0][attr])
        #             node_tag.append(dmlpu.get_properties_tag(self.__node_tree[class_type][class_id][1][key][1]))
        #             nodeclass_tag.append(node_tag)
        #
        #         bs.MetaNetwork.nodes.append(nodeclass_tag)
        #
        # networks_tag = self._get_networks_tag()
        # bs.MetaNetwork.networks.append(networks_tag)
        #
        # if not is_entire_file:
        #     bs = bs.MetaNetwork
        #
        # return bs
        mn = etree.Element('MetaNetwork')

        for attr in self.attributes:
            mn.attrib[attr] = dmlpu.unformat_prop(self.attributes[attr])

        etree.SubElement(mn, dmlpu.get_property_identities_tag(self.propertyIdentities))

        properties_tag = etree.SubElement(mn, 'properties')
        for key in self.properties:
            prop_tag = etree.SubElement(properties_tag, 'property')
            prop_tag.attrib['id'] = key
            prop_tag['value'] = dmlpu.unformat_prop(self.properties[key])

        nodes_tag = etree.SubElement(mn, 'nodes')
        for class_type in self.__node_tree:
            for class_id in self.__node_tree[class_type]:
                nodeclass_tag = etree.SubElement(nodes_tag, 'nodeclass', attrib={'type': class_type, 'id': class_id})
                etree.SubElement(nodeclass_tag,
                                 dmlpu.get_property_identities_tag(self.__node_tree[class_type][class_id][0]))

        etree.SubElement(mn, self._get_networks_tag())

        return mn

    def pretty_print(self):
        """Pretty print the meta-network"""
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
        Rename a node in all the networks containing it.

        :param str|unicode nodeclass_name: name of the parent of nodeset_name
        :param str|unicode nodeset_name: name of the parent of node_name
        :param str|unicode node_name: current node name
        :param str|unicode new_node_name: new name for the node
        """
        for nk in self.networks:
            if nk[0]['sourceType'] == nodeclass_name and nk[0]['source'] == nodeset_name or \
                    nk[0]['targetType'] == nodeclass_name and nk[0]['target'] == nodeset_name:
                nk[new_node_name] = nk[node_name]
                del nk[node_name]
                for src in nk:
                    if node_name in nk[src]:
                        nk[src][new_node_name] = nk[src][node_name]
                        del nk[src][node_name]

    def _get_networks_tag(self):
        """Generates an :class:`lxml._Element` from the networks"""
        # bs = BeautifulSoup()
        # networks_tag = bs.new_tag('networks')
        # for key in self.networks:
        #     network_tag = bs.new_tag('network')
        #     network_tag['sourceType'] = self.networks[key][0]['sourceType']
        #     network_tag['source'] = self.networks[key][0]['source']
        #     network_tag['targetType'] = self.networks[key][0]['targetType']
        #     network_tag['target'] = self.networks[key][0]['target']
        #     network_tag['id'] = key
        #     network_tag['isDirected'] = dmlpu.unformat_prop(self.networks[key][0]['isDirected'])
        #     network_tag['allowSelfLoops'] = dmlpu.unformat_prop(self.networks[key][0]['allowSelfLoops'])
        #     network_tag['isBinary'] = dmlpu.unformat_prop(self.networks[key][0]['isBinary'])
        #
        #     if self.networks[key][0]['isBinary']:
        #         for edge in self.networks[key].edges_iter():
        #             network_tag.append(bs.new_tag('link', source=edge[0], target=edge[1]))
        #     else:
        #         for edge in self.networks[key].edges_iter(data=True):
        #             network_tag.append(bs.new_tag('link', source=edge[0], target=edge[1], value=edge[2]['weight']))
        #
        #     networks_tag.append(network_tag)
        #
        # return networks_tag
        networks_tag = etree.Element('networks')
        for key in self.networks:
            network_tag = etree.SubElement(networks_tag, 'network', attrib={
                'sourceType': self.networks[key][0]['sourceType'], 'source': self.networks[key][0]['source'],
                'targetType': self.networks[key][0]['targetType'], 'target': self.networks[key][0]['target'],
                'id': key, 'isDirected': dmlpu.unformat_prop(self.networks[key][0]['isDirected']),
                'allowSelfLoops': dmlpu.unformat_prop(self.networks[key][0]['allowSelfLoops']),
                'isBinary': dmlpu.unformat_prop(self.networks[key][0]['isBinary'])})

            if self.networks[key][0]['isBinary']:
                for edge in self.networks[key].edges_iter():
                    etree.SubElement(network_tag, 'link', attrib={'source': edge[0], 'target': edge[1]})
            else:
                for edge in self.networks[key].edges_iter(data=True):
                    etree.SubElement(network_tag, 'link', attrib={'source': edge[0], 'target': edge[1],
                                                                  'value': edge[2]['weight']})

        return networks_tag

    def _parse_and_add_graph_tag(self, nk_tag):
        """:param lxml._Element nk_tag: The tag to be parsed and added to the MetaNetwork"""
        g = {}, defaultdict(dict)

        g[0]['sourceType'] = nk_tag.attrib['sourceType']
        g[0]['source'] = nk_tag.attrib['source']
        g[0]['targetType'] = nk_tag.attrib['targetType']
        g[0]['target'] = nk_tag.attrib['target']
        g[0]['id'] = nk_tag.attrib['id']
        g[0]['isDirected'] = nk_tag.attrib['isDirected'] == 'true'
        g[0]['allowSelfLoops'] = nk_tag.attrib['allowSelfLoops'] == 'true'
        g[0]['isBinary'] = nk_tag.attrib['isBinary'] == 'true'
        #for attrib_key in nk_tag.attrib:
        #   g[0][attrib_key] = format_prop(nk_tag.attrib[attrib_key])

        if g[0]['isDirected']:
            for link in nk_tag.iterfind('link'):
                weight = float(link.attrib['value']) if 'value' in link.attrib else 1.0
                g[1][link.attrib['source']][link.attrib['target']] = weight
        else:
            for link in nk_tag.iterfind('link'):
                weight = float(link.attrib['value']) if 'value' in link.attrib else 1.0
                g[1][link.attrib['source']][link.attrib['target']] = weight
                g[1][link.attrib['target']][link.attrib['source']] = weight

        self.networks[nk_tag.attrib['id']] = g

    def _pretty_print_networks(self):
        """Pretty-print the networks"""
        print ' == Networks =='
        network_count = 0
        for nk_key in self.networks:
            nk = self.networks[nk_key]
            print u'  Network {0}: {1}'.format(network_count, nk_key).encode('utf8')
            for prop in nk[0]:
                print u'   {0}: {1}'.format(prop, nk[0][prop]).encode('utf8')

            nodes = set()
            edges = list()
            for src in nk[1]:
                nodes.add(src)
                for target in nk[1][src]:
                    nodes.add(target)
                    edges.append([src, target])

            if nk[0]['isDirected']:
                for edge in edges:
                    edge.sort()

            print '   {0} nodes'.format(len(nodes))
            print '   {0} edges'.format(len(set(edges)))
            network_count += 1