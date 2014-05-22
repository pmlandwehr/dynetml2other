from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime


def node_tuple():
    """
    The tuple that defines a node
    :rtype: tuple_(dict, dict)
    """
    return {}, {}  # attrs, properties


def nodeset_tuple():
    """
    The tuple that defines a nodeset
    :rtype: tuple_(dict, defaultdict(node_tuple)
    """
    return {}, defaultdict(node_tuple)  # property identities, list of nodes


def nodeclass_dict():
    """
    The defaultdict that defines a nodeclass
    :rtype: defaultdict(nodeset_tuple)
    """
    return defaultdict(nodeset_tuple)  # nodesets


def check_key(var, var_name, map, map_name, check_if_in_map=True):
    """
    Helper function for validating if a key is in a map
    :param var: the variable which needs to be checked
    :param var_name: the name of the variable
    :param map: the map
    :param map_name: the name of the map
    :param check_if_in_map: if True, verify that var is in map. If False, check if var is not in map
    :raise KeyError: if var is not or is in map, depending on check_if_in_map
    """
    if check_if_in_map and var not in map:
        raise KeyError('{0} not in {1}; looked for {2}'.format(var_name, map_name, var))
    elif not check_if_in_map and var in map:
        raise KeyError('{0} in {1}; looked for {2}'.format(var_name, map_name, var))

def check_type(var, var_name, allowable_types):
    """
    Helper function for validating a variable's type
    :param var: the variable which needs its type checked
    :param var_name: the name of the variable
    :param allowable_types: a type or tuple of types that var can be
    :raise TypeError: if var is not a type included in allowable_types
    """
    if not isinstance(var, allowable_types):
        raise TypeError('{0} must be of type {1}'.format(var_name, str(allowable_types)))


def validate_and_get_inclusion_test(include_tuple, ignore_tuple):
    """
    A method for validating variables and then returning an inclusion test
    :param include_tuple: A two element tuple, the first element is a list of strings, the second is the list's name
    :param ignore_tuple: A two element tuple, the first element is a list of strings, the second is the list's name
    :returns: a test for whether or not an item should be included
    :rtype: lambda
    """
    for pair in include_tuple, ignore_tuple:
        check_type(pair[0], pair[1], list)
        if not all(isinstance(entry, (str, unicode)) for entry in pair[0]):
            raise TypeError('{0} can only contain elements of type str or unicode'.format(pair[1]))

    if len(include_tuple[0]) > 0 and len(ignore_tuple[0]) > 0:
            raise ValueError('{0} and {1} cannot both contain values'.format(include_tuple[1], ignore_tuple[1]))

    if len(include_tuple[0]) > 0:
        good_set = set(include_tuple[0])
        return lambda x: x in good_set
    elif len(ignore_tuple) > 0:
        bad_set = set(ignore_tuple[0])
        return lambda x: x not in bad_set

    return lambda x: True


def format_prop(prop_str, prop_type=str()):
    """
    A method for converting properties to appropriate formats. Currently just covers dates (bools handled elsewhere)
    :param prop_str: a property to be converted
    :param prop_type: str or unicode specifying the type of property
    :returns: a converted property value, changed to an appropriate type.
    :rtype: bool, float, datetime, unicode, or str
    :raises TypeError: if prop_type isn't unicode or str
    :raises ValueError: if prop_type is 'bool' and prop_str doesn't contain some form of 'true' or 'false'
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
    A method for un-formatting properties back to strings. Currently covers dates and bools
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
    :param property_identities_dict: a dictionary containing propertyIndentity values
    :returns: a <propertyIdentities> BeautifulSoup Tag, containing appropriate <propertyIdentity> tags
    :rtype: bs4.element.Tag
    """
    property_identities_tag = BeautifulSoup(features='xml').new_tag('propertyIdentities')

    if not isinstance(property_identities_dict, dict):
        return property_identities_tag

    for key in property_identities_dict:

        if not isinstance(property_identities_dict[key], tuple) or len(property_identities_dict[key]) != 2:
            continue

        prop_ident_tag = BeautifulSoup(features='xml').new_tag('propertyIdentity')
        prop_ident_tag['id'] = key
        prop_ident_tag['type'] = property_identities_dict[key][0]
        prop_ident_tag['singleValued'] = unformat_prop(property_identities_dict[key][1])
        property_identities_tag.append(prop_ident_tag)

    return property_identities_tag


def get_property_identities_dict(property_identities_tag, inclusion_test=lambda x: True):
    """
    Reads in a propertyIdentities tag and converts it to a dictionary of property identities
    :param property_identities_tag: a BeautifulSoup tag containing propertyIdentities, or None
    :param inclusion_test: a test for whether or not to include a particular property. Defaults to including all.
    :returns: A dictionary of property identities, or an empty dictionary
    :rtype: dictionary
    """
    property_identities_dict = {}

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
    :returns: a BeautifulSoup <properties> tag, containing appropriate <property> tags
    :rtype: bs4.element.Tag
    """
    properties_tag = BeautifulSoup(features='xml').new_tag('properties')

    if not isinstance(properties_dict, dict):
        return properties_tag

    for key in properties_dict:
        prop_tag = BeautifulSoup(features='xml').new_tag('property')
        prop_tag['id'] = key
        prop_tag['value'] = unformat_prop(properties_dict[key])
        properties_tag.append(prop_tag)

    return properties_tag


def get_nodeset_tuple(nodeclass_tag, property_inclusion_test=lambda x: True):
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


def get_nodeclass_dict(nodes_tag, prop_inclusion_test=lambda x: True, nodeclass_inclusion_test=lambda x: True):
    new_nodeclass_dict = defaultdict(dict)
    for nc_tag in nodes_tag.iterfind('nodeclass'):
        if not nodeclass_inclusion_test(nc_tag.attrib['id']):
            continue
        new_nodeclass_dict[nc_tag.attrib['type']][nc_tag.attrib['id']] = get_nodeset_tuple(nc_tag, prop_inclusion_test)

    return new_nodeclass_dict
