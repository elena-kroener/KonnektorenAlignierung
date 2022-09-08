# XML Extractor
# 13.08.2022
# Based on tutorial:
# https://towardsdatascience.com/processing-xml-in-python-elementtree-c8992941efd2
# See also:
# https://docs.python.org/3/library/xml.etree.elementtree.html

import re
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
    # connector_low = part.text.lower()
    # if connector_low not in connectors_de:
    #     connectors_de.append(connector_low)
[connectors_de.append(part.text.lower()) for part in root_de.iter('part') if
 part.text.lower() not in connectors_de]
# print(connectors_de)

connectors_en = []
[connectors_en.append(part.text.lower()) for part in root_en.iter(
    'part') if part.text.lower() not in connectors_en]
# print(connectors_en)

connectors_it = []
[connectors_it.append(part.text.lower()) for part in root_it.iter(
    'part') if part.text.lower() not in connectors_it]
# print(connectors_it)

# write into txt file: 
# 1) pop from list
# 2) check if it needs to be cleaned
# 3) writes the clean version into the txt

def write_list_to_txt(connector_list, path_out):
    """Saves a (cleaned) connector list to the given path as txt."""
    with open(path_out, mode='w', encoding='utf-8') as f_out:
        while len(connector_list) > 0:
            current_connector = connector_list.pop()
            
            ## clean the connector list
            # problem 1: remove space before comma in DE corpus
            current_connector = re.sub('\s,', ',', current_connector)
            
            # problem 2 (settled manually): slash in pairwise connectors in EN -> saved separately,
            # but we have to pay attention later in the html files
            # only two examples:'not only/but', when/then
            
            # write to file
            f_out.write(current_connector)
            f_out.write('\n')

write_list_to_txt(connectors_de, '../data/connector_lists/connectors_de.txt')
write_list_to_txt(connectors_en, '../data/connector_lists/connectors_en.txt')
write_list_to_txt(connectors_it, '../data/connector_lists/connectors_it.txt')