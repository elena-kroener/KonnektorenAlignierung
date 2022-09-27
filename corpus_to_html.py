import ast
from collections import Counter
import os
import csv
from corpus_reader import *
from nltk.tokenize import word_tokenize
from nltk import ngrams

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
        already_parsed = [] # remember indices of already seen connectors for multi-worded connectors and those with a counterpart
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
                        # if connector doesn't have a counterpart (e.g. neither-nor):
                        if not connector_list[token]['is_pair']:
                            connectors_in_triple[lang].append((list(token), index_of_connector, connector_list[token]['relation']))
                            already_parsed += index_of_connector
                        else:
                            len_counterpart = len(connector_list[token]['counterpart'].split(' '))
                            index = 0
                            found_counterpart = False
                            # search the sentence in ngrams of the length of the counterpart
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
    Allign connectors into a dict of the form {lang: {color: ([index_de], [index_en], [index_it])}}
    """
    colors = ['#b71c1c', '#1a237e', '#00c853', '#512da8', '#ff5722', '#4e342e', '#e91e63', '#26c6da', '#ffd600', '#9e9d24', '#2962ff', '#455a64', '#004d40']
    result = {'de': dict(), 'en': dict(), 'it': dict()}
    # if no connector in the sentence
    if len(extracted_connectors['de']) == 0 \
        and len(extracted_connectors['en']) == 0 \
        and len(extracted_connectors['it']) == 0:
        pass
    # if only one connector in the sentence
    elif len(extracted_connectors['de']) == 1 \
        and len(extracted_connectors['en']) == 1 \
        and len(extracted_connectors['it']) == 1:
        color = colors.pop(0)
        for lang in extracted_connectors.keys():
            for index in extracted_connectors[lang][0][1]:
                result[lang].update({index: color})
    else:
        # find language with most connectors in this sentence
        lang_with_most_cons = max((len(v), k) for k, v in extracted_connectors.items())[1]
        other_langs = ['de', 'en', 'it']
        other_langs.remove(lang_with_most_cons)
        already_aligned = {lang: [] for lang in other_langs}
        # iterate through connectors of language with most connectors in this sentence
        for first_lang_connector in extracted_connectors[lang_with_most_cons]:
            # connectors without a relation are ignored
            if first_lang_connector[2]:
                align_con = {lang_with_most_cons: first_lang_connector[1]}
                for lang in other_langs:
                    index = None
                    for con in extracted_connectors[lang]:
                        if not con[1] in already_aligned[lang]:
                            if con[2]:
                                # if the connectors share a relation, they get aligned
                                if any(relation in con[2] for relation in first_lang_connector[2]):
                                    index = con[1]
                                    already_aligned[lang].append(con[1])
                                    break
                    align_con[lang] = index
                color = colors.pop(0)
                # save all aligned connectors for this sentence with the same color-key
                for lang, index_list in align_con.items():
                    if index_list:
                        for index in index_list:
                            result[lang].update({index: color})
        # color all connectors that couldn't be aligned on their own
        not_aligned = {'de': list(), 'en': list(), 'it': list()}
        for lang in extracted_connectors.keys():
            for connector in extracted_connectors[lang]:
                if connector[1][0] not in result[lang].keys():
                    color = colors.pop(0)
                    for index in connector[1]:
                        result[lang].update({index: color})
    return result

def sent_to_html_str(sent, aligned_connectors, lang):
    """Converts a sentence to an html-string."""
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
    """Converts all sentence triples to html-strings and writes to the given path and
    records alignment statistics in txt-files."""
    with open(path_out, mode='w', encoding='utf-8') as f_out:
        de_en_stat = Counter()
        de_it_stat = Counter()
        en_it_stat = Counter()

        f_out.write('<meta charset="utf-8">\n')
        for triple_id, triple in enumerate(sent_triples):
            extracted_connectors = extract_connectors(triple, connector_list)
            aligned_connectors = allign_connectors(extracted_connectors)

            # update HTML-file
            f_out.write(f'<p>{triple_id}</p>\n')
            langs = {0: 'de', 1: 'en', 2: 'it'}
            for i, sent in enumerate(triple):
                f_out.write(sent_to_html_str(sent, aligned_connectors, langs[i]))
            f_out.write('\n')

            # update stats
            _update_alignment_stats(triple, aligned_connectors, de_en_stat, de_it_stat, en_it_stat)

        _stat_as_csv(de_en_stat, 'output/de_en_stat.csv')
        _stat_as_csv(de_it_stat, 'output/de_it_stat.csv')
        _stat_as_csv(en_it_stat, 'output/en_it_stat.csv')

def _update_alignment_stats(sent_triple, aligned_connectors, de_en_stat, de_it_stat, en_it_stat):
    tokenized_sents = dict()
    tokenized_sents['de'] = word_tokenize(sent_triple.de)
    tokenized_sents['en'] = word_tokenize(sent_triple.en)
    tokenized_sents['it'] = word_tokenize(sent_triple.it)

    # figure out alignments according to color
    color_dict = dict()
    for lang, value in aligned_connectors.items():
        for i, color in value.items():
            if color not in color_dict:
                color_dict[color] = {'de':[], 'en':[], 'it':[]}

            color_dict[color][lang].append(tokenized_sents[lang][i])

    for color in color_dict:
        de_connector = ' '.join(color_dict[color]['de']).lower()
        en_connector = ' '.join(color_dict[color]['en']).lower()
        it_connector = ' '.join(color_dict[color]['it']).lower()

        de_en_stat[(de_connector, en_connector)] = de_en_stat.get((de_connector, en_connector), 0) + 1
        de_it_stat[(de_connector, it_connector)] = de_it_stat.get((de_connector, it_connector), 0) + 1
        en_it_stat[(en_connector, it_connector)] = en_it_stat.get((en_connector, it_connector), 0) + 1

def _stat_as_csv(counter_obj, output_path):
    with open(output_path, mode='w', encoding='utf-8') as f_out:
        for key, value in sorted(counter_obj.items(), key=lambda pair: pair[1], reverse=True):
            f_out.write(f"{key},{value}\n")

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
    write_as_html(os.path.join('output', 'output.html'), all_sent_triples, connector_list)
