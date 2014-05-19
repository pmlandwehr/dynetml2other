from dynetml2other import *
import os
import unittest


def working_path(*args):
    return os.path.normpath(os.path.join(*args))


class UnitTests(unittest.TestCase):

    def setUp(self):
        self.test_dir_name = 'a_test_dir'
        self.test_xml_name = 'bad_xml_test.xml'

        counter = 2
        while os.path.exists(self.test_dir_name):
            self.test_dir_name = 'a_test_dir_{0}'.format(counter)
            counter += 1

        counter = 2
        while os.path.exists(self.test_xml_name):
            self.test_xml_name = 'bad_xml_test_{0}.xml'.format(counter)
            counter += 1

        os.mkdir(self.test_dir_name)
        with open(self.test_xml_name, 'w') as outfile:
            outfile.write('<?xml version="1.0" standalone="yes"?>\n\n<blah><blah_child value="1.0" /></blah>')

    def eval_node_tree(self, node_tree, expected_nodeclasses):
        self.assertEqual(len(node_tree), len(expected_nodeclasses))
        for e_n in expected_nodeclasses:
            self.assertTrue(e_n[0] in node_tree)
            self.assertEqual(len(node_tree[e_n[0]]), 1)
            self.assertTrue(e_n[1] in node_tree[e_n[0]])
            self.assertEqual(len(node_tree[e_n[0]][e_n[1]][1]), e_n[2],
                             'len(mn.node_tree[{0}][{1}][1]) = {2}, not {3}'.format(
                                 e_n[0], e_n[1], len(node_tree[e_n[0]][e_n[1]][1]), e_n[2]))

    def eval_networks(self, networks, expected_networks, network_format):
        self.assertEqual(len(networks), len(expected_networks))
        if network_format == 'networkx':
            edges_and_nodes = lambda x: (x.number_of_edges(), x.number_of_nodes())
        else:
            edges_and_nodes = lambda x: (len(x[1].es), len(x[1].vs))

        for e_n in expected_networks:
            self.assertTrue(e_n[0] in networks)
            edges, nodes = edges_and_nodes(networks[e_n[0]])
            self.assertEqual(edges, e_n[1], 'networks[{0}].number_of_edges() = {1}, not {2}'.format(
                e_n[0], edges, e_n[1]))
            self.assertEqual(nodes, e_n[2], 'networks[{0}].number_of_nodes() = {1}, not {2}'.format(
                e_n[0], nodes, e_n[2]))

    def eval_format(self, network_format):
        self.assertTrue(network_format in ('networkx', 'igraph'))
        if network_format == 'networkx':
            from MetaNetworkNetworkX import MetaNetworkNX as MetaNetwork
        else:
            from MetaNetworkIGraph import MetaNetworkIG as MetaNetwork

        dmn = dynetml2other(working_path('test_dynetml', 'files_2014022423.xml'), network_format)
        self.assertTrue(isinstance(dmn, DynamicMetaNetwork))
        self.assertEqual(len(dmn.metanetworks), 23)

        for mn in dmn.metanetworks[:5]:
            self.assertTrue(isinstance(mn, MetaNetwork))
            self.eval_node_tree(mn.node_tree, [('Agent', 'Agent', 1), ('Event', 'Tweet', 1)])
            self.eval_networks(mn.networks, [('Agent x Tweet - Sender', 1, 2)], network_format)

        mn = dmn.metanetworks[-1]
        self.assertTrue(isinstance(mn, MetaNetwork))

        self.assertEqual(mn.attributes['id'], '2014-02-24 11 PM')
        self.eval_node_tree(mn.node_tree, [('Agent', 'Agent', 923),
                                           ('Knowledge', 'Concept', 103),
                                           ('Location', 'Location', 201),
                                           ('Event', 'Tweet', 870)])
        self.eval_networks(mn.networks, [('Agent x Tweet - Sender', 870, 1566),
                                         ('Tweet x Agent - Mentions', 590, 806),
                                         ('Tweet x Concept', 211, 245),
                                         ('Tweet x Location', 250, 451),
                                         ('Tweet x Tweet - Retweeted-By', 131, 201)], network_format)

        with self.assertRaises(TypeError):
            dmn.convert_to_dynetml('blah')
            dmn.write_dynetml(1)

        with self.assertRaises(IOError):
            dmn.write_dynetml(self.test_dir_name)

        with self.assertRaises(TypeError):
            mn.convert_to_dynetml('blah')
            mn.write_dynetml(1)

        with self.assertRaises(IOError):
            mn.write_dynetml(self.test_dir_name)


    def test_dynamicmetanetwork(self):
        with self.assertRaises(TypeError):
            DynamicMetaNetwork(1)

        with self.assertRaises(ValueError):
            DynamicMetaNetwork('blah')

        self.assertTrue(isinstance(DynamicMetaNetwork('networkx'), DynamicMetaNetwork))
        self.assertTrue(isinstance(DynamicMetaNetwork('igraph'), DynamicMetaNetwork))

    def test_metanetwork(self):
        from MetaNetwork import MetaNetwork

        mn = MetaNetwork()
        with self.assertRaises(TypeError):
            mn.convert_to_dynetml('blah')

    def test_networks(self):
        self.assertTrue(os.path.exists('test_dynetml/files_2014022423.xml'))

        with self.assertRaises(TypeError):
            dynetml2other(1, 'yes')
            dynetml2other('yes', 1)

        with self.assertRaises(ValueError):
            dynetml2other('test_string', 'test_string_two')
            dynetml2other(working_path('test_dynetml', 'files_2014022423.xml'), 'test_string_two')

        with self.assertRaises(IOError):
            dynetml2other('bad_path', 'networkx')

        for network_format in ('networkx', 'igraph'):
            self.eval_format(network_format)


    def tearDown(self):
        os.rmdir(self.test_dir_name)
        os.remove(self.test_xml_name)


if __name__ == "__main__":
    unittest.main()