#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'Peter M. Landwehr <plandweh@cs.cmu.edu>'

from collections import defaultdict
import dynetmlparsingutils as dmlpu
from lxml import etree
from MetaNetwork import MetaNetwork


class MetaNetworkDict (MetaNetwork):
    """
    A subclass of the MetaNetwork class that handles networks by storing them as a tuple of a dictionary of
    attributes and a defaultdict(dict) of edges.
    """

    def _rename_network_nodes(self, nodeclass_name, nodeset_name, node_name, new_node_name):
        for nk in self.networks:
            if nk[0]['sourceType'] == nodeclass_name and nk[0]['source'] == nodeset_name or \
             nk[0]['targetType'] == nodeclass_name and nk[0]['target'] == nodeset_name:
                nk[new_node_name] = nk[node_name]
                del nk[node_name]
                for src in nk:
                    if node_name in nk[src]:
                        nk[src][new_node_name] = nk[src][node_name]
                        del nk[src][node_name]

    def _parse_and_add_graph_tag(self, nk_tag):

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

    def _get_networks_tag(self):
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

    def _pretty_print_networks(self):
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