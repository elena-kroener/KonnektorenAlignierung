import ast
import os
import csv
from corpus_reader import *
from nltk.tokenize import word_tokenize
from nltk import ngrams
from collections import namedtuple

def read_connector_list(txt_filepath):
    """Returns a dict of connectors read from a csv file."""
    result = {}
    with open(txt_filepath, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            row['connector'] = tuple(row['connector'].split(' '))
            row['relation'] = ast.literal_eval(row['relation']) # get type list
            row['is_pair'] = ast.literal_eval(row['is_pair'])
            result[row['connector']] = {key: value for key, value in row.items() if key in ['relation','is_pair','counterpart']}
    return result

def extract_connectors(triple, connector_list):
    """Extracts connectors as dict with their index and their relation(s)"""
    connectors_in_triple = {key: list() for key in ['de', 'en', 'it']}
    for lang, sent in triple._asdict().items():
        already_parsed = [] #remember second part of connector to avoid adding it to connector list on its own
        sent = word_tokenize(sent)
        for n in range(4, 0, -1):
            i = 0
            for token in ngrams(sent, n):
                if not i in already_parsed:
                    token = tuple([word.lower() for word in token])
                    if token in connector_list.keys():
                        index_of_connector = [i]
                        for index in range(1, n): # get indices of multiple worded connectors
                            index_of_connector += [i + index]
                        if not connector_list[token]['is_pair']:
                            connectors_in_triple[lang].append((list(token), index_of_connector, connector_list[token]['relation']))
                            already_parsed += index_of_connector
                        else:
                            len_counterpart = len(connector_list[token]['counterpart'].split(' '))
                            index = 0
                            found_counterpart = False
                            for part in ngrams(sent, len_counterpart):
                                if part == tuple(connector_list[token]['counterpart'].split(' ')):
                                    for i_counter in range(len_counterpart):
                                        index_of_connector += [index + i_counter]
                                    connectors_in_triple[lang].append((list(token) + list(part), index_of_connector, connector_list[token]['relation']))
                                    already_parsed += index_of_connector
                                    found_counterpart = True
                                    break
                                else:
                                    index += len_counterpart
                            # if no counterpart found: add to found connectors on its own
                            if not found_counterpart:
                                connectors_in_triple[lang].append((list(token), index_of_connector, connector_list[token]['relation']))
                i += 1
    return connectors_in_triple

def allign_connectors(extracted_connectors):
    """
    Allign connectors into a dict of the form {color: ([index_de], [index_en], [index_it])}
    """
    colors = ['red', 'blue', 'green', 'pink', 'purple', 'orange', 'brown', 'magenta', 'coral', 'beer', 'khaki']
    result = {'de': dict(), 'en': dict(), 'it': dict()}
    # if no connector
    if len(extracted_connectors['de']) == 0 \
        and len(extracted_connectors['en']) == 0 \
        and len(extracted_connectors['it']) == 0:
        return result
    # if only one connector
    elif len(extracted_connectors['de']) == 1 \
        and len(extracted_connectors['en']) == 1 \
        and len(extracted_connectors['it']) == 1:
        color = colors.pop(0)
        # get {lang: {index: color, index: color}}
        for lang in extracted_connectors.keys():
            for index in extracted_connectors[lang][0][1]:
                result[lang].update({index: color})
        return result
    else:
        align = []
        lang_with_most_cons = max((len(v), k) for k, v in extracted_connectors.items())[1]
        other_langs = ['de', 'en', 'it']
        other_langs.remove(lang_with_most_cons)
        already_aligned = {lang: [] for lang in other_langs}
        for first_lang_connector in extracted_connectors[lang_with_most_cons]:
            if first_lang_connector[2]:  # currently only possible if relation given
                align_con = {lang_with_most_cons: first_lang_connector[1]}
                for lang in other_langs:
                    index = None
                    for con in extracted_connectors[lang]:
                        if not con[1] in already_aligned[lang]:
                            if con[2]:
                                if any(relation in con[2] for relation in first_lang_connector[2]):
                                    index = con[1]
                                    already_aligned[lang].append(con[1])
                                    break
                    align_con[lang] = index
                color = colors.pop(0)
                for lang, index_list in align_con.items():
                    if index_list:
                        for index in index_list:
                            result[lang].update({index: color})
        return result

def sent_to_html_str(sent, aligned_connectors, lang):
    """Converts a sentence to a html-string."""
    html_elements = ['<p>']
    for i, token in enumerate(word_tokenize(sent)):
        if i in aligned_connectors[lang].keys():
            color = aligned_connectors[lang].get(i)
            html_elements.append(f'<font color={color}>{token} </font>')
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
            aligned_connectors = allign_connectors(extracted_connectors)
            f_out.write(f'<p>{triple_id}</p>\n')
            langs = {0: 'de', 1: 'en', 2: 'it'}
            for i, sent in enumerate(triple):
                f_out.write(sent_to_html_str(sent, aligned_connectors, langs[i]))
                f_out.write('\n')


if __name__ == '__main__':
    # connector lists
    CONNECTORS_DE = read_connector_list('data/connectors_df/df_de.csv')
    CONNECTORS_EN = read_connector_list('data/connectors_df/df_en.csv')
    CONNECTORS_IT = read_connector_list('data/connectors_df/df_it.csv')
    connector_list = dict()
    {connector_list.update(lang) for lang in [CONNECTORS_DE, CONNECTORS_EN,
                                              CONNECTORS_IT]}
    # get all sentence triples
    corpus_root = os.path.join('data', 'corpus')
    all_sent_triples = all_xmls_to_sent_triples(
        corpus_root,
        list_xml_files(os.path.join(corpus_root, 'de'))
        )
    # SentTriple = namedtuple('SentTriple', 'de en it')
    # all_sent_triples = [SentTriple('und zu viele Ressourcen gehen verloren , wenn zusammen verbrannt wird , was getrennt eigentlich verwertet werden könnte . ',
    #                      'and too many resources are lost when what actually should be separated and recycled is burnt . ',
    #                      'e si perdono troppe risorse se quello che in realtà dovrebbe essere separato e riciclato viene incenerito . ')]
    # all_sent_triples = [SentTriple('Solange aber nicht klar ist , wieso es dazu kommt , sollte das Geld besser für Behandlungen ausgegeben werden , bei denen man es mit Sicherheit weiss . ',
    #                      'But as long as it is unclear as to how this works , the funds should rather be spent on therapies where one knows with certainty . ',
    #                      'Ma fino a quando non si capisce perché questo accade , sarebbe meglio spendere i soldi per trattamenti che si conoscono per certo .')]
    # all_sent_triples = [SentTriple('Schließlich wollen wir unsereren Blick auf die Welt weder durch die Brille der Regierung noch durch die von reichen Medienunternehmern bekommen . ',
    #                      'After all we want to get our view of the world neither through the lens of the government nor through that of rich media entrepreneurs . ',
    #                      'Dopo tutto , non vogliamo ottenere la nostra visione del mondo attraverso le lenti del governo o attraverso quelle dei ricchi imprenditori dei media .')]
    # write to html
    write_as_html(os.path.join('data', 'output.html'), all_sent_triples, connector_list)
