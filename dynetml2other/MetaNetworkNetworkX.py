#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Peter M. Landwehr <plandweh@cs.cmu.edu>'

import dynetmlparsingutils as dmlpu
from lxml import etree
from MetaNetwork import MetaNetwork
from networkx import nx


class MetaNetworkNX (MetaNetwork):
    """
    A subclass of the MetaNetwork class that handles networks by storing them as instances of :class:`networkx.Graph` \
    and :class:`networkx.DiGraph`.
    """

    def _rename_network_nodes(self, nodeclass_name, nodeset_name, node_name, new_node_name):
        new_mapping = {node_name: new_node_name}
        for nk in self.networks:
            if nk.graph['sourceType'] == nodeclass_name and nk.graph['source'] == nodeset_name or \
                                    nk.graph['targetType'] == nodeclass_name and nk.graph['target'] == nodeset_name:
                nx.relabel_nodes(nk, new_mapping)

    def _parse_and_add_graph_tag(self, nk_tag):
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

    def _get_networks_tag(self):
        # bs = BeautifulSoup()
        # networks_tag = bs.new_tag('networks')
        # for key in self.networks:
        #     network_tag = bs.new_tag('network')
        #     network_tag['sourceType'] = self.networks[key].graph['sourceType']
        #     network_tag['source'] = self.networks[key].graph['source']
        #     network_tag['targetType'] = self.networks[key].graph['targetType']
        #     network_tag['target'] = self.networks[key].graph['target']
        #     network_tag['id'] = key
        #     network_tag['isDirected'] = dmlpu.unformat_prop(self.networks[key].graph['isDirected'])
        #     network_tag['allowSelfLoops'] = dmlpu.unformat_prop(self.networks[key].graph['allowSelfLoops'])
        #     network_tag['isBinary'] = dmlpu.unformat_prop(self.networks[key].graph['isBinary'])
        #
        #     if self.networks[key].graph['isBinary']:
        #         for edge in self.networks[key].edges_iter(data=True):
        #             network_tag.append(bs.new_tag('link', source=edge[0], target=edge[1], value=edge[2]['weight']))
        #     else:
        #         for edge in self.networks[key].edges_iter():
        #             network_tag.append(bs.new_tag('link', source=edge[0], target=edge[1]))
        #
        #     networks_tag.append(network_tag)
        #
        # return networks_tag
        networks_tag = etree.Element('networks')
        for key in self.networks:
            network_tag = etree.SubElement(networks_tag, 'network', attrib={
                'sourceType': self.networks[key].graph['sourceType'], 'source': self.networks[key].graph['source'],
                'targetType': self.networks[key].graph['targetType'], 'target': self.networks[key].graph['target'],
                'id': key, 'isDirected': dmlpu.unformat_prop(self.networks[key].graph['isDirected']),
                'allowSelfLoops': dmlpu.unformat_prop(self.networks[key].graph['isBinary'])
            })

            if not self.networks[key].graph['isBinary']:
                for edge in self.networks[key].edges_iter(data=True):
                    etree.SubElement(network_tag, 'link', attrib={'source': edge[0], 'target': edge[1],
                                                                  'value': edge[2]['weight']})
            else:
                for edge in self.networks[key].edges_iter():
                    etree.SubElement(network_tag, 'link', attrib={'source': edge[0], 'target': edge[1]})

        return networks_tag

    def _pretty_print_networks(self):
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
            network_count += 1