from corpus_reader import *
from nltk.tokenize import word_tokenize

def read_connector_list(txt_filepath):
    result = []
    with open(txt_filepath, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            result.append(line.strip())
    return result

def sent_to_html_str(sent, connector_list):
    html_elements = ['<p>']
    for token in word_tokenize(sent):
        if token.lower() in connector_list:
            html_elements.append(f'<font color="red">{token} </font>')
        else: 
            html_elements.append(f'{token} ')
    html_elements.append('</p>')
    html_elements.append('\n')
    return ''.join(html_elements)

def write_as_html(path_out, sent_triples):
    id = 1 # wird immer erhöht
    with open(path_out, mode='w', encoding='utf-8') as f_out:
        for triple in sent_triples:
            f_out.write(f'<p>{id}</p>\n')
            f_out.write(sent_to_html_str(triple.de, CONNECTORS_DE))
            f_out.write(sent_to_html_str(triple.en, CONNECTORS_EN))
            f_out.write(sent_to_html_str(triple.it, CONNECTORS_IT))
            f_out.write('\n')
            id += 1

if __name__ == '__main__':
    # connector lists
    CONNECTORS_DE = read_connector_list('data/connector_lists/connectors_de.txt')
    CONNECTORS_EN = read_connector_list('data/connector_lists/connectors_en.txt')
    CONNECTORS_IT = read_connector_list('data/connector_lists/connectors_it.txt')

    # get all sentence triples
    corpus_root = os.path.join('data', 'corpus')
    all_sent_triples = all_xmls_to_sent_triples(
        corpus_root,
        list_xml_files(os.path.join(corpus_root, 'de'))
        )
    
    write_as_html('data/output.html', all_sent_triples)