# XML Extractor
# 13.08.2022
# Based on tutorial:
# https://towardsdatascience.com/processing-xml-in-python-elementtree-c8992941efd2
# See also:
# https://docs.python.org/3/library/xml.etree.elementtree.html

import xml.etree.ElementTree as ET

# tree_de = ET.parse('../data/ConAnoConnectorLexicon.xml')
# tree_de = ET.parse('../data/ConAnoConnectorLexicon.xml')
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

connectors_de = []
# for part in root_de.iter('part'):
    # connector_low = part.text.lower()
    # if connector_low not in connectors_de:
    #     connectors_de.append(connector_low)
[connectors_de.append(part.text.lower()) for part in root_de.iter('part') if
 part.text.lower() not in connectors_de]
print(connectors_de)

connectors_en = []
[connectors_en.append(part.text.lower()) for part in root_en.iter(
    'part') if part.text.lower() not in connectors_en]
print(connectors_en)

connectors_it = []
[connectors_it.append(part.text.lower()) for part in root_it.iter(
    'part') if part.text.lower() not in connectors_it]
print(connectors_it)