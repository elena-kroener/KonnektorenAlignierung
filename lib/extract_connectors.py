# XML Extractor
# 13.08.2022
# Based on tutorial:
# https://towardsdatascience.com/processing-xml-in-python-elementtree-c8992941efd2
# See also:
# https://docs.python.org/3/library/xml.etree.elementtree.html

import json
import xml.etree.ElementTree as ET

tree_de = ET.parse('../data/ConAnoConnectorLexicon.xml')
root_de = tree_de.getroot()

tree_en = ET.parse('../data/en_dimlex.xml')
root_en = tree_en.getroot()

tree_it = ET.parse('../data/LICO-v.1.0.xml')
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

connectors_de = []
# for part in root_de.iter('part'):
#     connector_low = part.text.lower()
#     if connector_low not in connectors_de:
#         connectors_de.append(connector_low)
[connectors_de.append(part.text.lower()) for part in root_de.iter('part') if
 part.text.lower() not in connectors_de]

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
                    rel = relation.attrib['sense']
                    relations.append(rel[:rel.find('.')])
        # save each part of the connector pair with '/' like 'not only/but', when/then separately
        if connector.find('/') > -1:
            for sub_connector in connector.split('/'):
                result[sub_connector] = list(set(relations))
        else:
            result[connector] = list(set(relations))

    return result

connectors_en = find_connectors_en(root_en)

connectors_it = []
[connectors_it.append(part.text.lower()) for part in root_it.iter(
    'part') if part.text.lower() not in connectors_it]


def write_dict_to_json(connector_rel_dict, path_out):
    with open(path_out, mode='w', encoding='utf-8') as f_out:
        json.dump(connector_rel_dict, f_out)

# write_list_to_json(connectors_de, '../data/connector_lists/connectors_de.txt')
write_dict_to_json(connectors_en, '../data/connector_lists/connectors_en.json')
# write_list_to_json(connectors_it, '../data/connector_lists/connectors_it.txt')