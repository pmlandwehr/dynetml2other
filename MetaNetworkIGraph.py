__author__ = 'plandweh'

from bs4 import BeautifulSoup
from collections import OrderedDict
import dynetmlparsingutils as dmlpu
import igraph
from MetaNetwork import MetaNetwork


class MetaNetworkIGraph (MetaNetwork):

    def parse_and_add_graph_tag(self, nk_tag):
        g = igraph.Graph(directed=nk_tag.attrib['isDirected'] == 'true')
        g['sourceType'] = nk_tag.attrib['sourceType']
        g['source'] = nk_tag.attrib['source']
        g['targetType'] = nk_tag.attrib['targetType']
        g['target'] = nk_tag.attrib['target']
        g['id'] = nk_tag.attrib['id']
        g['isDirected'] = nk_tag.attrib['isDirected'] == 'true'
        g['allowSelfLoops'] = nk_tag.attrib['allowSelfLoops'] == 'true'
        g['isBinary'] = nk_tag.attrib['isBinary'] == 'true'
        #for attrib_key in nk_tag.attrib:
        #   g[nk_tag.attrib['id']][attrib_key] = format_prop(nk_tag.attrib[attrib_key])

        edge_list = list()
        id_vertex_dict = OrderedDict()
        weight_list = list()
        for link_tag in nk_tag.iterfind('link'):
            if link_tag.attrib['source'] not in id_vertex_dict:
                id_vertex_dict[link_tag.attrib['source']] = len(id_vertex_dict)
            if link_tag.attrib['target'] not in id_vertex_dict:
                id_vertex_dict[link_tag.attrib['target']] = len(id_vertex_dict)

            edge_list.append((id_vertex_dict[link_tag.attrib['source']], id_vertex_dict[link_tag.attrib['target']]))

            try:
                weight_list.append(float(link_tag.attrib['weight']))
            except KeyError:
                weight_list.append(1.0)

        g.add_vertices(len(id_vertex_dict))
        g.add_edges(edge_list)
        if not g['isBinary']:
            g.es['weight'] = weight_list

        self.networks[nk_tag.attrib['id']] = id_vertex_dict, g

    def get_networks_tag(self):
        bs = BeautifulSoup()
        networks_tag = bs.new_tag('networks')
        for key in self.networks:
            network_tag = bs.new_tag('network')
            network_tag['sourceType'] = self.networks[key][1]['sourceType']
            network_tag['source'] = self.networks[key][1]['source']
            network_tag['targetType'] = self.networks[key][1]['targetType']
            network_tag['target'] = self.networks[key][1]['target']
            network_tag['id'] = key
            network_tag['isDirected'] = dmlpu.unformat_prop(self.networks[key]['isDirected'])
            network_tag['allowSelfLoops'] = dmlpu.unformat_prop(self.networks[key]['allowSelfLoops'])
            network_tag['isBinary'] = dmlpu.unformat_prop(self.networks[key]['isBinary'])

            e_l = self.networks[key].edge_list()
            if self.networks[key]['isBinary']:
                for i in range(len(e_l)):
                    network_tag.append(bs.new_tag('link', source=e_l[i][0], target=e_l[i][1],
                                                  value=self.networks[key].es[i]['weight']))
            else:
                for i in range(len(e_l)):
                    network_tag.append(bs.new_tag('link', source=e_l[i][0], target=e_l[i][1]))

            networks_tag.append(network_tag)

        return networks_tag

    def pretty_print_networks(self):
        print ' == Networks =='
        network_count = 0
        for nk_key in self.networks:
            nk = self.networks[nk_key][1]
            print u'  Network {0}: {1}'.format(network_count, nk_key).encode('utf8')
            for prop in nk:
                print u'   {0}: {1}'.format(prop, nk[prop]).encode('utf8')
            print '   {0} nodes'.format(len(nk.vs))
            print '   {0} edges'.format(len(nk.es))
            network_count += 1