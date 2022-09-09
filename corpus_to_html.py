import os
from corpus_reader import *
from nltk.tokenize import word_tokenize

def read_connector_list(txt_filepath):
    """Returns a set of connectors read from a txt file."""
    result = set()
    with open(txt_filepath, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            result.add(line.strip())
    return result

def extract_connectors(triple, connector_list):
    """Extracts connectors with their index for one triple of sentences"""
    connectors_in_triple = {key: list() for key in ['de', 'en', 'it']}
    for lang, sent in triple._asdict().items():
        for i, token in enumerate(word_tokenize(sent)):
            if token.lower() in connector_list:
                connectors_in_triple[lang] += [(token, i)]
    return connectors_in_triple

def allign_connectors(extracted_connectors):
    pass

def sent_to_html_str(sent, connector_list):
    """Converts a sentence to a html-string."""
    html_elements = ['<p>']
    for token in word_tokenize(sent):
        # red color for the connector
        if token.lower() in connector_list:
            html_elements.append(f'<font color="red">{token} </font>')
        else:
            html_elements.append(f'{token} ')
    html_elements.append('</p>')
    html_elements.append('\n')
    return ''.join(html_elements)

def write_as_html(path_out, sent_triples, connector_list):
    """Converts all sentence triples to html-strings and write to the given path."""
    triple_id = 1
    with open(path_out, mode='w', encoding='utf-8') as f_out:
        for triple in sent_triples:
            extracted_connectors = extract_connectors(triple, connector_list)
            allign_connectors(extracted_connectors)
            f_out.write(f'<p>{triple_id}</p>\n')
            f_out.write(sent_to_html_str(triple.de, connector_list))
            f_out.write(sent_to_html_str(triple.en, connector_list))
            f_out.write(sent_to_html_str(triple.it, connector_list))
            f_out.write('\n')
            triple_id += 1


if __name__ == '__main__':
    # connector lists
    CONNECTORS_DE = read_connector_list('data/connector_lists/connectors_de.txt')
    CONNECTORS_EN = read_connector_list('data/connector_lists/connectors_en.txt')
    CONNECTORS_IT = read_connector_list('data/connector_lists/connectors_it.txt')
    connector_list = set()
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
