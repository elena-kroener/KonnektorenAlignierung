import os
import json
from corpus_reader import *
from nltk.tokenize import word_tokenize

def read_connector_list(txt_filepath):
    """Returns a dict of connectors read from a json file."""
    with open(txt_filepath, 'r', encoding='utf-8') as f_in:
        result = json.load(f_in)
    return result

def extract_connectors(triple, connector_list):
    """Extracts connectors as dict with their index and their relation(s)"""
    connectors_in_triple = {key: list() for key in ['de', 'en', 'it']}
    for lang, sent in triple._asdict().items():
        for i, token in enumerate(word_tokenize(sent)):
            if token.lower() in connector_list.keys():
                connectors_in_triple[lang].append((token, i, connector_list.get(token)))
    print(connectors_in_triple)
    return connectors_in_triple

def allign_connectors(extracted_connectors):
    """
    Allign connectors into a dict of the form {color: {de: {index: word, index: word} en: {index: word, index: word}}, it: {index: word, index: word}}
    """
    colors = ['red', 'blue', 'yellow', 'green', 'pink']
    # if only one connector
    if len(extracted_connectors['de']) == 1 \
        and len(extracted_connectors['en']) == 1 \
        and len(extracted_connectors['it']) == 1:
        return {colors.pop(0): extracted_connectors}
    else:
        print(extracted_connectors)
        for index, connector in extracted_connectors['de'].items():
            col = colors.pop(0)
            allign = {col: {'de': {index: connector}}}
            if index in extracted_connectors['en'].keys():
                allign.update({col: {'en': extracted_connectors['en'][index]}})
        return allign

def sent_to_html_str(sent, color, language, alligned_connectors):
    """Converts a sentence to a html-string."""
    html_elements = ['<p>']
    for i, token in enumerate(word_tokenize(sent)):
        if i in alligned_connectors[color][language].keys():
            html_elements.append(f'<font color="red">{token} </font>')
        else:
            html_elements.append(f'{token} ')
    html_elements.append('</p>')
    html_elements.append('\n')
    return ''.join(html_elements)

def write_as_html(path_out, sent_triples, connector_list):
    """Converts all sentence triples to html-strings and write to the given path."""
    with open(path_out, mode='w', encoding='utf-8') as f_out:
        for triple_id, triple in enumerate(sent_triples):
            extracted_connectors = extract_connectors(triple, connector_list)
            #print(extracted_connectors)
            alligned_connectors = allign_connectors(extracted_connectors)
            #print(alligned_connectors)
            f_out.write(f'<p>{triple_id}</p>\n')
            langs = {0: 'de', 1: 'en', 2: 'it'}
            for i, sent in enumerate(triple):
                for color in alligned_connectors.keys():
                    f_out.write(sent_to_html_str(sent, color, langs[i], alligned_connectors))
                f_out.write('\n')


if __name__ == '__main__':
    # connector lists
    CONNECTORS_DE = read_connector_list('data/connector_lists/connectors_de.json')
    CONNECTORS_EN = read_connector_list('data/connector_lists/connectors_en.json')
    CONNECTORS_IT = read_connector_list('data/connector_lists/connectors_it.json')
    connector_list = dict()
    {connector_list.update(lang) for lang in [CONNECTORS_DE, CONNECTORS_EN,
                                              CONNECTORS_IT]}
    # get all sentence triples
    corpus_root = os.path.join('data', 'corpus')
    all_sent_triples = all_xmls_to_sent_triples(
        corpus_root,
        list_xml_files(os.path.join(corpus_root, 'de'))
        )
    # write to html
    write_as_html(os.path.join('data', 'output.html'), all_sent_triples, connector_list)
