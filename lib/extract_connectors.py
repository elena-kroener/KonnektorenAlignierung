# XML Extractor
# 13.08.2022
# Based on tutorial:
# https://towardsdatascience.com/processing-xml-in-python-elementtree-c8992941efd2
# See also:
# https://docs.python.org/3/library/xml.etree.elementtree.html

import json
import xml.etree.ElementTree as ET
import re

tree_de = ET.parse('KonnektorenAlignierung/data/ConAnoConnectorLexicon.xml')
root_de = tree_de.getroot()

tree_en = ET.parse('KonnektorenAlignierung/data/en_dimlex.xml')
root_en = tree_en.getroot()

tree_it = ET.parse('KonnektorenAlignierung/data/LICO-v.1.0.xml')
root_it = tree_it.getroot()

# # Print root tag and look at its attributes
# print(root_de.tag)
# print(root_de.attrib)
#
# # Navigate through children with for loop
# for child in root_de:
#     print(child.tag, child.attrib)
#
# # Iterate over all sub tags
# print([elem.tag for elem in root_de.iter()])
#
# # Print attributes of specific tag
# for part in root_de.iter('part'):
#     print(part.attrib)
#
# # Print text for specific tag
# for part in root_de.iter('part'):
#     print(part.text)
#
# # Findall - does not work as supposed to, path doesn't work
# for part in root_de.findall("./entry/orth/part/[type='single']"):
#     print(part.text)

# connectors_de = []
# # for part in root_de.iter('part'):
# #     connector_low = part.text.lower()
# #     if connector_low not in connectors_de:
# #         connectors_de.append(connector_low)
# [connectors_de.append(part.text.lower()) for part in root_de.iter('part') if
#  part.text.lower() not in connectors_de]

def find_connectors_en(xml_root):
    """returns a dictionary in which each entry is in the for of {connector: [relations]}."""
    result = dict()
    for entry in xml_root.iter('entry'):
        connector = entry.attrib['word']
        relations = []
        # find all relations
        for syn in entry.iter('syn'):
            for sem in syn.iter('sem'):
                for relation in sem.iter('pdtb2_relation'):
                    rel = relation.attrib['sense'].lower()
                    if rel.find('.') == -1:
                        relations.append(rel)
                    else:
                       relations.append(rel[:rel.find('.')])
        # save each part of the connector pair with '/' like 'not only/but', when/then separately
        if connector.find('/') > -1:
            for sub_connector in connector.split('/'):
                result[sub_connector] = list(set(relations))
        else:
            result[connector] = list(set(relations))

    return result

def find_connectors_de(xml_root):
    """Extract connectors and save them with their relation"""
    connectors_relations = {}
    # Traverse tree to check each entry for connector alternatives and their
    # relations
    for entry in xml_root.iter('entry'):
        # List of connector alternatives
        connector_alternatives = []
        for orth in entry.iter('orth'):
            connector = orth.find('part').text.lower()
            connector_alternatives.append(connector)
            # Clean spaces before commas
            for connector in connector_alternatives:
                connector = re.sub('\s,', ',', connector)
            # List of relations for connector_alternatives
            relations = []
            for syn in entry.iter('syn'):
                for sem in syn.iter('sem'):
                    for relation in sem.iter('coh-relation'):
                        rel = relation.text
                        # Make sure entry is not empty
                        if rel != None:
                            rel = rel.lower()
                            # Avoid cutting off for one-part relations
                            if rel.find('.') == -1:
                                relations.append(rel)
                            else:
                                relations.append(rel[:rel.find('.')])
            connectors_relations[connector] = list(set(relations))
    return connectors_relations

def find_connectors_it(xml_root):
    """Extract connectors and save them with their relation"""
    connectors_relations = {}
    # Traverse tree to check each entry for connector alternatives and their
    # relations
    for entry in xml_root.iter('entry'):
        connector_alternatives = []
        for orth in entry.iter('orth'):
            connector = orth.find('part').text.lower()
            connector_alternatives.append(connector)
            # Clean spaces before commas
            for connector in connector_alternatives:
                connector = re.sub('\s,', ',', connector)
            # List of relations for connector_alternatives
            relations = []
            for syn in entry.iter('syn'):
                for sem in syn.iter('sem'):
                    for relation in sem.iter('coh-relation'):
                        rel = relation.text
                        # Make sure entry is not empty
                        if rel != None:
                            rel = rel.lower()
                            # Avoid cutting off for one-part relations
                            if rel.find(':') == -1:
                                relations.append(rel)
                            else:
                                relations.append(rel[:rel.find(':')])
            connectors_relations[connector] = list(set(relations))
    return connectors_relations

connectors_en = find_connectors_en(root_en)
connectors_de = find_connectors_de(root_de)
connectors_it = find_connectors_it(root_it)

# connectors_it = []
# [connectors_it.append(part.text.lower()) for part in root_it.iter(
#     'part') if part.text.lower() not in connectors_it]


def write_dict_to_json(connector_rel_dict, path_out):
    with open(path_out, mode='w', encoding='utf-8') as f_out:
        json.dump(connector_rel_dict, f_out, ensure_ascii=False)

write_dict_to_json(connectors_de,
                   'KonnektorenAlignierung/data/connector_lists'
                   '/connectors_de.json')
write_dict_to_json(connectors_en,
                   'KonnektorenAlignierung/data/connector_lists/connectors_en'
                   '.json')
write_dict_to_json(connectors_it,
                   'KonnektorenAlignierung/data/connector_lists/connectors_it'
                   '.json')