# XML Extractor
# 13.08.2022
# Based on tutorial:
# https://towardsdatascience.com/processing-xml-in-python-elementtree-c8992941efd2
# See also:
# https://docs.python.org/3/library/xml.etree.elementtree.html

import xml.etree.ElementTree as ET
import re
import pandas as pd


def find_connectors_en(xml_root):
    """returns a dataframe with coloumns: connector | relation | is_pair | counterpart for EN connectors."""
    df = pd.DataFrame(columns=['connector', 'relation', 'is_pair', 'counterpart'])
    for entry in xml_root.iter('entry'):
        # find connector/ connector pairs
        connector_parts = _find_connector_parts_for_an_entry(entry, lang='en')
        # find all relations
        relations = _find_all_relations_for_an_entry(entry, lang='en')
        # append df row
        new_rows = _generate_connector_df_rows(connector_parts, relations)
                
        for new_row in new_rows:
            df = pd.concat([df, new_row])
 
    return df

def find_connectors_de(xml_root):
    """returns a dataframe with coloumns: connector | relation | is_pair | counterpart for DE connectors."""
    df = pd.DataFrame(
        columns=['connector', 'relation', 'is_pair', 'counterpart'])
    for entry in xml_root.iter('entry'):
        connector_parts = _find_connector_parts_for_an_entry(entry, lang='de')
        
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
            # relations = _find_all_relations_for_an_entry(entry, lang='de')
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
        new_rows = _generate_connector_df_rows(connector_parts, relations)
        for new_row in new_rows:
            df = pd.concat([df, new_row])
    return df


def find_connectors_it(xml_root):
    """returns a dataframe with coloumns: connector | relation | is_pair | counterpart. for IT connectors."""
    df = pd.DataFrame(
        columns=['connector', 'relation', 'is_pair', 'counterpart'])
    for entry in xml_root.iter('entry'):
        # find connector/ connector pairs
        connector_parts = _find_connector_parts_for_an_entry(entry, lang='it')
        
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
        new_rows = _generate_connector_df_rows(connector_parts, relations)
        for new_row in new_rows:
            df = pd.concat([df, new_row])

    return df

def _find_connector_parts_for_an_entry(entry, lang):
    """find connector/ connector pairs for an entry in the connector xml-file."""
    connector_parts = set()
    if lang.lower() == 'en':
        for orths in entry.iter('orths'):
            for orth in orths.iter('orth'):
                new_orth = [part.text.lower() for part in orth.iter('part')]
                if len(new_orth) == 2: # double connector as tuple
                    connector_parts.add((new_orth[0], new_orth[1]))
                elif len(new_orth) == 1: # single connector
                    connector_parts.add(new_orth[0])
    
    elif lang.lower() in ['de', 'it']:
        for orth in entry.iter('orth'):
            new_orth = [part.text.lower() for part in orth.iter('part')]
            if len(new_orth) == 2: # double connector as tuple
                connector_parts.add((new_orth[0], new_orth[1]))
            elif len(new_orth) == 1: # single connector
                connector_parts.add(new_orth[0])
            
    return connector_parts

def _find_all_relations_for_an_entry(entry, lang):
    """find relation for an entry in the connector xml-file."""
    relations = []
    if lang == 'en':
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
    return list(set(relations))

def _generate_connector_df_rows(connector_parts, all_relations):
    """creates DataFrame (row) for a connector entry."""
    new_rows = []
    
    for connector in connector_parts:
        if type(connector) is tuple: # double connector
            fst_part, snd_part = connector[0], connector[1]
            
            new_rows.append(pd.DataFrame([[fst_part, all_relations, True, snd_part]],
                                    columns=['connector', 'relation', 'is_pair', 'counterpart'])
                            )
            new_rows.append(pd.DataFrame([[snd_part, all_relations, True, fst_part]],
                                    columns=['connector', 'relation', 'is_pair', 'counterpart'])
                            )
        else: # single connector
            new_rows.append(pd.DataFrame([[connector, all_relations, False, None]],
                                columns=['connector', 'relation', 'is_pair', 'counterpart'])
                        )
    
    return new_rows

if __name__ == '__main__':
    root_de = ET.parse('data/connectors_xml/ConAnoConnectorLexicon.xml').getroot()
    root_en = ET.parse('data/connectors_xml/en_dimlex.xml').getroot()
    root_it = ET.parse('data/connectors_xml/LICO-v.1.0.xml').getroot()

    connectors_de = find_connectors_de(root_de)
    connectors_en = find_connectors_en(root_en)
    connectors_it = find_connectors_it(root_it)

    connectors_de.to_csv('data/connectors_df/df_de.csv')
    connectors_en.to_csv('data/connectors_df/df_en.csv')
    connectors_it.to_csv('data/connectors_df/df_it.csv')