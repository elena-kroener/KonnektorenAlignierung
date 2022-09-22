# XML Extractor
# 13.08.2022
# Based on tutorial:
# https://towardsdatascience.com/processing-xml-in-python-elementtree-c8992941efd2
# See also:
# https://docs.python.org/3/library/xml.etree.elementtree.html

import xml.etree.ElementTree as ET
import re

import pandas as pd

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

# connectors_de = []
# # for part in root_de.iter('part'):
# #     connector_low = part.text.lower()
# #     if connector_low not in connectors_de:
# #         connectors_de.append(connector_low)
# [connectors_de.append(part.text.lower()) for part in root_de.iter('part') if
#  part.text.lower() not in connectors_de]

def find_connectors_en(xml_root):
    """returns a dataframe with coloumns: connector | relation | is_pair | counterpart."""
    df = pd.DataFrame(columns=['connector', 'relation', 'is_pair', 'counterpart'])
    count = 0
    for entry in xml_root.iter('entry'):
        count += 1
        # find connector/ connector pairs
        for orths in entry.iter('orths'):
            connector_parts = set()
            for orth in orths.iter('orth'):
                connector_parts.update(
                    part.text.lower() for part in orth.iter('part')
                    )
        
        # find all relations
        relations = []
        for syn in entry.iter('syn'):
            for sem in syn.iter('sem'):
                for relation in sem.iter('pdtb2_relation'):
                    rel = relation.attrib['sense'].lower()
                    if rel.find('.') == -1: # if no subcategory is specified
                        relations.append(rel)
                    else: # one main relation + one sub-relation (e.g. comparison.contrast)
                        relations.append(
                            '.'.join(re.split('[.]+', rel)[:2])
                            )
        relations = list(set(relations))

        # append df row
        new_rows = []
        if len(connector_parts) == 1:
            new_rows.append(pd.DataFrame([[connector_parts.pop(), relations, False, None]],
                                    columns=['connector', 'relation', 'is_pair', 'counterpart'])
                            )
        
        # double connectors or 'afterward(s)'
        elif len(connector_parts) == 2:
            # the form can be 'afterward' or 'afterwards' 
            if 'afterward' in connector_parts: 
                for _ in range(2):      
                    new_rows.append(pd.concat([df, pd.DataFrame([[connector_parts.pop(), relations, False, None]],
                                            columns=['connector', 'relation', 'is_pair', 'counterpart'])])
                                    )
            # double connectors: order does not matter
            else:
                fst_part, snd_part = connector_parts.pop(), connector_parts.pop()
                new_rows.append(pd.DataFrame([[fst_part, relations, True, snd_part]],
                                        columns=['connector', 'relation', 'is_pair', 'counterpart'])
                                )
                new_rows.append(pd.DataFrame([[snd_part, relations, True, fst_part]],
                                        columns=['connector', 'relation', 'is_pair', 'counterpart'])
                                )
                
        for new_row in new_rows:
            df = pd.concat([df, new_row])
        
    # print(df)
    # print(count)
    return df

def find_connectors_de(xml_root):
    df = pd.DataFrame(
        columns=['connector', 'relation', 'is_pair', 'counterpart'])
    count = 0
    for entry in xml_root.iter('entry'):
        count += 1
        # find connector/ connector pairs
        for orth in entry.iter('orth'):
            connector_parts = set()
            for orth in orth.iter('orth'):
                connector_parts.update(
                    part.text.lower() for part in orth.iter('part')
                )

        connectors_relations = {}
    # Traverse tree to check each entry for connector alternatives and their
    # relations
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
                                relations.append(
                                    '.'.join(re.split('[.]+', rel)[:2])
                                    )
            connectors_relations[connector] = list(set(relations))

        # append df row
        new_rows = []
        if len(connector_parts) == 1:
            new_rows.append(
                pd.DataFrame([[connector_parts.pop(), relations, False, None]],
                             columns=['connector', 'relation', 'is_pair',
                                      'counterpart'])
            )

        # double connectors or 'afterward(s)'
        elif len(connector_parts) == 2:
            # the form can be 'afterward' or 'afterwards'
            if 'afterward' in connector_parts:
                for _ in range(2):
                    new_rows.append(pd.concat([df, pd.DataFrame(
                        [[connector_parts.pop(), relations, False, None]],
                        columns=['connector', 'relation', 'is_pair',
                                 'counterpart'])])
                                    )
            # double connectors: order does not matter
            else:
                fst_part, snd_part = connector_parts.pop(), connector_parts.pop()
                new_rows.append(
                    pd.DataFrame([[fst_part, relations, True, snd_part]],
                                 columns=['connector', 'relation', 'is_pair',
                                          'counterpart'])
                    )
                new_rows.append(
                    pd.DataFrame([[snd_part, relations, True, fst_part]],
                                 columns=['connector', 'relation', 'is_pair',
                                          'counterpart'])
                    )

        for new_row in new_rows:
            df = pd.concat([df, new_row])
    return df

def find_connectors_it(xml_root):
    df = pd.DataFrame(
        columns=['connector', 'relation', 'is_pair', 'counterpart'])
    count = 0
    for entry in xml_root.iter('entry'):
        count += 1
        # find connector/ connector pairs
        for orth in entry.iter('orth'):
            connector_parts = set()
            for orth in orth.iter('orth'):
                connector_parts.update(
                    part.text.lower() for part in orth.iter('part')
                )

        connectors_relations = {}
    # Traverse tree to check each entry for connector alternatives and their
    # relations
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
                            if rel.find(':') == -1:
                                relations.append(rel)
                            else:
                                relations.append(
                                    '.'.join(re.split('[:]+', rel)[:2])
                                    )
            connectors_relations[connector] = list(set(relations))

        # append df row
        new_rows = []
        if len(connector_parts) == 1:
            new_rows.append(
                pd.DataFrame([[connector_parts.pop(), relations, False, None]],
                             columns=['connector', 'relation', 'is_pair',
                                      'counterpart'])
            )

        # double connectors or 'afterward(s)'
        elif len(connector_parts) == 2:
            # the form can be 'afterward' or 'afterwards'
            if 'afterward' in connector_parts:
                for _ in range(2):
                    new_rows.append(pd.concat([df, pd.DataFrame(
                        [[connector_parts.pop(), relations, False, None]],
                        columns=['connector', 'relation', 'is_pair',
                                 'counterpart'])])
                                    )
            # double connectors: order does not matter
            else:
                fst_part, snd_part = connector_parts.pop(), connector_parts.pop()
                new_rows.append(
                    pd.DataFrame([[fst_part, relations, True, snd_part]],
                                 columns=['connector', 'relation', 'is_pair',
                                          'counterpart'])
                    )
                new_rows.append(
                    pd.DataFrame([[snd_part, relations, True, fst_part]],
                                 columns=['connector', 'relation', 'is_pair',
                                          'counterpart'])
                    )

        for new_row in new_rows:
            df = pd.concat([df, new_row])
    return df

connectors_en = find_connectors_en(root_en)
connectors_de = find_connectors_de(root_de)
connectors_it = find_connectors_it(root_it)

connectors_en.to_csv('./df_en.csv')
connectors_de.to_csv('./df_de.csv')
connectors_it.to_csv('./df_it.csv')