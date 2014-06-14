#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Peter M. Landwehr <plandweh@cs.cmu.edu>'

from collections import defaultdict
from datetime import datetime
from lxml import etree


def node_tuple():
    """
    :returns: The tuple that defines a node
    :rtype: :class:`tuple_(dict, dict)`
    """
    return {}, {}  # attrs, properties


def nodeset_tuple():
    """
    :returns: The tuple that defines a nodeset
    :rtype: :class:`tuple_(dict, defaultdict(node_tuple))`
    """
    return {}, defaultdict(node_tuple)  # property identities, list of nodes


def nodeclass_dict():
    """
    :returns: The defaultdict that defines a nodeclass
    :rtype: :class:`defaultdict(nodeset_tuple)`
    """
    return defaultdict(nodeset_tuple)  # nodesets


def node_tree():
    """
    :returns: The default dict that define
    :rtype: :class:`defaultdict(nodeclass_dict)`
    """
    return defaultdict(nodeclass_dict())  # node tree


def check_key(var, var_name, used_map, map_name, check_if_in_map=True):
    """
    Helper function for checking if a key is in a map

    :param var: the variable which needs to be checked
    :param str|unicode var_name: the name of the variable
    :param used_map: the map
    :param str|unicode map_name: the name of the map
    :param bool check_if_in_map: if True, verify that var is in map. If False, check if var is not in map
    """
    if check_if_in_map and var not in used_map:
        raise KeyError('{0} not in {1}; looked for {2}'.format(var_name, map_name, var))
    elif not check_if_in_map and var in used_map:
        raise KeyError('{0} in {1}; looked for {2}'.format(var_name, map_name, var))


def check_type(var, var_name, allowable_types):
    """
    Helper function for checking a variable's type

    :param var: the variable which needs its type checked
    :param str|unicode var_name: the name of the variable
    :param allowable_types: a type or tuple of types that var can be
    """
    if not isinstance(var, allowable_types):
        raise TypeError('{0} must be of type {1}'.format(var_name, str(allowable_types)))


def check_contained_types(iterable, iterable_name, allowable_types):
    """
    Helper function for validating that an iterable object only contains allowed types.

    :param tuple|list iterable: the tuple or list to be evaluated
    :param str|unicode iterable_name: the name of the iterable
    :param allowable_types: the types the iterable can be.
    """
    if not isinstance(iterable, (tuple, list)):
        raise TypeError('{0} must be a tuple or list'.format(iterable_name))
    for entry in iterable:
        if not isinstance(entry, allowable_types):
            raise TypeError('{0} can only contain types {1}'.format(iterable_name, allowable_types))


def validate_and_get_inclusion_test(include_tuple, ignore_tuple):
    """
    A method for validating variables and then returning an inclusion test

    :param tuple include_tuple: A two element tuple, the first element is a list of strings, the second is the list's \
    name
    :param tuple ignore_tuple: A two element tuple, the first element is a list of strings, the second is the list's \
    name
    :returns: a test for whether or not an item should be included
    :rtype: lambda
    """
    if include_tuple[0] is None:
        include_tuple = [], ''
    if ignore_tuple[0] is None:
        ignore_tuple = [], ''

    for pair, name in (include_tuple, 'include_tuple'), (ignore_tuple, 'ignore_tuple'):
        check_contained_types(pair[0], name, (str, unicode))
        #check_contained_types(pair[1], name, (str, unicode))

    if len(include_tuple[0]) > 0 and len(ignore_tuple[0]) > 0:
            raise ValueError('{0} and {1} cannot both contain values'.format(include_tuple[1], ignore_tuple[1]))

    if len(include_tuple[0]) > 0:
        good_set = set(include_tuple[0])
        return lambda x: x in good_set
    elif len(ignore_tuple[0]) > 0:
        bad_set = set(ignore_tuple[0])
        return lambda x: x not in bad_set

    return lambda x: True


def format_prop(prop_str, prop_type=str()):
    """
    A method for converting properties to appropriate formats. Currently just covers dates (bools handled elsewhere)

    :param str|unicode prop_str: a property to be converted
    :param str|unicode prop_type: str or unicode specifying the type of property
    :returns: a property value that has been converted to the appropriate type.
    :rtype: bool|float|datetime|str|unicode
    """
    if not isinstance(prop_type, (unicode, str)):
        raise TypeError('prop_type must be unicode or str')

    if prop_type == 'bool':
        if prop_str.lower() == 'true':
            return True
        elif prop_str.lower() == 'false':
            return False
        raise ValueError('Bad value for bool prop_type: {0}'.format(prop_str))
    elif prop_type == 'number':
        return float(prop_str)
    elif prop_type == 'date':
        return datetime.strptime(prop_str, '%Y-%m-%d %H:%M:%S')

    return prop_str  # 'text', 'categoryText', and 'URI' caught here


def unformat_prop(prop):
    """
    A method for un-formatting properties back to strings. Currently covers dates and bools.

    :param prop: a property storied in a properties dictionary, of unknown type.
    :returns: the property value transformed to a string containing equivalent dynetml contents
    :rtype: unicode or str
    """
    if isinstance(prop, (unicode, str)):
        return prop
    elif isinstance(prop, datetime):
        return prop.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(prop, bool):
        return unicode(prop).lower()
    return unicode(prop)  # 'number', 'numberCategory', and 'URI' caught here


def get_property_identities_tag(property_identities_dict):
    """
    Reads a dictionary of Property Identities and converts it to a propertyIdentities tag

    :param dict property_identities_dict: a dictionary containing propertyIndentity values
    :returns: a propertyIdentities tag
    :rtype: :class:`lxml._Element`
    """
    # property_identities_tag = BeautifulSoup(features='xml').new_tag('propertyIdentities')
    #
    # if not isinstance(property_identities_dict, dict):
    #     return property_identities_tag
    #
    # for key in property_identities_dict:
    #
    #     if not isinstance(property_identities_dict[key], tuple) or len(property_identities_dict[key]) != 2:
    #         continue
    #
    #     prop_ident_tag = BeautifulSoup(features='xml').new_tag('propertyIdentity')
    #     prop_ident_tag['id'] = key
    #     prop_ident_tag['type'] = property_identities_dict[key][0]
    #     prop_ident_tag['singleValued'] = unformat_prop(property_identities_dict[key][1])
    #     property_identities_tag.append(prop_ident_tag)
    #
    # return property_identities_tag
    property_identities_tag = etree.Element('propertyIdentities')
    if not isinstance(property_identities_dict, dict):
        return property_identities_tag

    for key in property_identities_dict:
        if not isinstance(property_identities_dict[key], tuple) or len(property_identities_dict[key]) != 2:
            continue

        etree.SubElement(property_identities_tag, 'propertyIdentity',
                         attrib={'id': key,
                                 'type': property_identities_dict[key][0],
                                 'singleValued': unformat_prop(property_identities_dict[key][1])})

    return property_identities_tag


def get_property_identities_dict(property_identities_tag, inclusion_test=None):
    """
    Reads in a propertyIdentities tag and converts it to a dictionary of property identities

    :param lxml._Element property_identities_tag: a tag containing propertyIdentities, or None
    :param lambda inclusion_test: a test for whether or not to include a particular property. Defaults to including all.
    :returns: A dictionary of property identities, or an empty dictionary
    :rtype: dict
    """
    property_identities_dict = {}

    if inclusion_test is None:
        inclusion_test = lambda x: True

    if property_identities_tag is None:
        return property_identities_dict

    for p_i in property_identities_tag.iterfind('propertyIdentity'):
        if inclusion_test(p_i.attrib['id']):
            property_identities_dict[p_i.attrib['id']] = \
                p_i.attrib['type'], p_i.attrib['singleValued'] == 'true'

    return property_identities_dict


def get_properties_tag(properties_dict):
    """
    Reads in a dictionary of properties and converts it to a properties tag

    :param properties_dict: a dictionary of properties
    :returns: A <properties> tag
    :rtype: :class:`lxml._Element`
    """
    # properties_tag = BeautifulSoup(features='xml').new_tag('properties')
    #
    # if not isinstance(properties_dict, dict):
    #     return properties_tag
    #
    # for key in properties_dict:
    #     prop_tag = BeautifulSoup(features='xml').new_tag('property')
    #     prop_tag['id'] = key
    #     prop_tag['value'] = unformat_prop(properties_dict[key])
    #     properties_tag.append(prop_tag)
    #
    # return properties_tag
    properties_tag = etree.Element('properties')

    if not isinstance(properties_dict, dict):
        return properties_tag

    for key in properties_dict:
        etree.SubElement(properties_tag, 'property', attrib={'id': key, 'value': unformat_prop(properties_dict[key])})

    return properties_tag


def get_nodeset_tuple(nodeclass_tag, property_inclusion_test=None):
    """
    :param nodeclass_tag: An lxml._Element extracted from the <nodeclass> tag in a DyNetML file
    :param lambda property_inclusion_test: Test for whether a node property should be included
    :returns: :class:`dict`, :class:`Collections.defaultdict(node_tuple)`
    """
    if property_inclusion_test is None:
        property_inclusion_test = lambda x: True

    p_i_dict = get_property_identities_dict(nodeclass_tag.find('propertyIdentities'), property_inclusion_test)
    node_tuples = defaultdict(node_tuple)

    for node in nodeclass_tag.iterfind('node'):
        for attrib_key in node.attrib:
            node_tuples[node.attrib['id']][0][attrib_key] = format_prop(node.attrib[attrib_key])
        for prop in node.iterfind('property'):
            if property_inclusion_test(prop.attrib['id']):
                node_tuples[node.attrib['id']][1][prop.attrib['id']] = \
                    format_prop(prop.attrib['value'], p_i_dict[prop.attrib['id']][0])

    return p_i_dict, node_tuples


def get_nodeclass_dict(nodes_tag, prop_inclusion_test=None, nodeclass_inclusion_test=None):
    """
    :param lxml._Element nodes_tag: An lxml._Element extracted from the  <nodes> tag in a DynetML file
    :param lambda prop_inclusion_test: Test for whether a node property should be included
    :param lambda nodeclass_inclusion_test: Test for whether a nodeclass should be included
    :returns: A dictionary defining a nodeclass
    :rtype: :class:`Collections.defaultdict(dict)`
    """
    if nodeclass_inclusion_test is None:
        nodeclass_inclusion_test = lambda x: True

    new_nodeclass_dict = defaultdict(dict)
    for nc_tag in nodes_tag.iterfind('nodeclass'):
        if not nodeclass_inclusion_test(nc_tag.attrib['id']):
            continue
        new_nodeclass_dict[nc_tag.attrib['type']][nc_tag.attrib['id']] = get_nodeset_tuple(nc_tag, prop_inclusion_test)

    return new_nodeclass_dict
