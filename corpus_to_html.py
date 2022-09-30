"""Read corpus into html file, with color-coded connectors"""
import ast
import csv
import os
from collections import Counter
from corpus_reader import *
from nltk import ngrams
from nltk.tokenize import word_tokenize


def read_connector_list(txt_filepath):
    """
    Returns a dict of connectors read from a csv file.
    Dict is structured into two dicts, one containing all single connectors,
    the other containing the connectors with a counterpart.
    """
    result = {'single': {}, 'double': {}}
    with open(txt_filepath, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            row['connector'] = tuple(row['connector'].split(' '))
            # get the right types: list and boolean
            row['relation'] = ast.literal_eval(row['relation'])
            row['is_pair'] = ast.literal_eval(row['is_pair'])
            row_values = {key: value for key, value in row.items()
                          if key in ['relation', 'is_pair', 'counterpart']}
            if row['is_pair']:
                result['double'][row['connector']] = row_values
            else:
                result['single'][row['connector']] = row_values
    return result

def extract_connectors(triple, connector_list):
    """Extracts connectors as dict with their index and their relation(s)"""
    connectors_in_triple = {key: list() for key in ['de', 'en', 'it']}
    for lang, sent in triple._asdict().items():
        already_parsed = []  # remember indices of already seen connectors
        sent = word_tokenize(sent)
        # seach input in 4-grams, then 3-grams, then bi-grams, finally uni-grams
        for n in range(4, 0, -1):
            i = 0
            for token in ngrams(sent, n):
                if not i in already_parsed:
                    token = tuple([word.lower() for word in token])

                    # check if connector has a counterpart
                    found_counterpart = False
                    if token in connector_list['double'].keys():
                        index_of_connector = [i]
                        for index in range(1, n):
                            index_of_connector += [i+index]
                        counterpart = tuple(connector_list['double'][token]
                                            ['counterpart'].split(' '))
                        len_counterpart = len(counterpart)
                        index = 0
                        # search the sentence in ngrams of the length
                        #    of the counterpart
                        for part in ngrams(sent, len_counterpart):
                            if part == counterpart:
                                for i_counter in range(len_counterpart):
                                    index_of_connector += [index+i_counter]
                                connectors_in_triple[lang].append(
                                     (list(token) + list(part),
                                     index_of_connector,
                                     connector_list['double'][token]['relation'])
                                     )
                                already_parsed += index_of_connector
                                found_counterpart = True
                                break
                            else:
                                index += len_counterpart

                    # find single connectors
                    if (token in connector_list['single'].keys()
                       and not found_counterpart):
                        index_of_connector = [i]
                        # get indices of multiple worded connectors
                        for index in range(1, n):
                            index_of_connector += [i+index]
                        connectors_in_triple[lang].append(
                             (list(token),
                             index_of_connector,
                             connector_list['single'][token]['relation'])
                             )
                        already_parsed += index_of_connector
                i += 1
    return connectors_in_triple

def align_connectors(extracted_connectors):
    """
    Align connectors sentence-triple-wise into a dict of the form
    {lang: {color: ([index_de], [index_en], [index_it])}}
    """
    colors = ['#FF2828', '#00c853', '#512da8', '#ff5722', '#4e342e', '#2962ff',
              '#e91e63', '#26c6da', '#ffd600', '#9e9d24', '#004d40', '#455a64',
              '#9C1717']
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
        lang_with_most_cons = max((len(v), k) for k, v
                                   in extracted_connectors.items())[1]
        other_langs = ['de', 'en', 'it']
        other_langs.remove(lang_with_most_cons)
        already_aligned = {lang: [] for lang in other_langs}
        # iterate through connectors of language with most connectors in sentence
        for first_lang_connector in extracted_connectors[lang_with_most_cons]:
            # connectors without a relation are ignored
            if first_lang_connector[2]:
                align_con = {lang_with_most_cons: first_lang_connector[1]}
                for lang in other_langs:
                    index = None
                    for con in extracted_connectors[lang]:
                        if not con[1] in already_aligned[lang]:
                            if con[2]:
                                # align connectors if they share a relation
                                if any(relation in con[2] for relation
                                       in first_lang_connector[2]):
                                    index = con[1]
                                    already_aligned[lang].append(con[1])
                                    break
                    align_con[lang] = index
                color = colors.pop(0)
                # save all aligned connectors for this sentence
                #    with the same color-key
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
    """
    Converts all sentence triples to html-strings, writes to the given path and
    records alignment statistics in txt-files.
    """
    with open(path_out, mode='w', encoding='utf-8') as f_out:
        de_en_stat = Counter()
        de_it_stat = Counter()
        en_it_stat = Counter()

        f_out.write('<meta charset="utf-8">\n')
        for triple_id, triple in enumerate(sent_triples):
            extracted_connectors = extract_connectors(triple, connector_list)
            aligned_connectors = align_connectors(extracted_connectors)

            # update HTML-file
            f_out.write(f'<p>{triple_id}</p>\n')
            langs = {0: 'de', 1: 'en', 2: 'it'}
            for i, sent in enumerate(triple):
                f_out.write(sent_to_html_str(sent,
                                             aligned_connectors, langs[i]))
            f_out.write('\n')

            # update stats
            _update_alignment_stats(triple, aligned_connectors, de_en_stat,
                                    de_it_stat, en_it_stat)

        _stat_as_csv(de_en_stat, 'output/de_en_stat.csv')
        _stat_as_csv(de_it_stat, 'output/de_it_stat.csv')
        _stat_as_csv(en_it_stat, 'output/en_it_stat.csv')

def _update_alignment_stats(sent_triple, aligned_connectors, de_en_stat,
                            de_it_stat, en_it_stat):
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

        de_en_stat[(de_connector, en_connector)] = de_en_stat.get((de_connector,
                                                   en_connector), 0) + 1
        de_it_stat[(de_connector, it_connector)] = de_it_stat.get((de_connector,
                                                   it_connector), 0) + 1
        en_it_stat[(en_connector, it_connector)] = en_it_stat.get((en_connector,
                                                   it_connector), 0) + 1

def _stat_as_csv(counter_obj, output_path):
    with open(output_path, mode='w', encoding='utf-8') as f_out:
        for key, value in sorted(counter_obj.items(), key=lambda pair: pair[1],
                                 reverse=True):
            f_out.write(f"{key},{value}\n")

if __name__ == '__main__':
    # connector lists
    CONNECTORS_DE = read_connector_list('data/connectors_df/df_de.csv')
    CONNECTORS_EN = read_connector_list('data/connectors_df/df_en.csv')
    CONNECTORS_IT = read_connector_list('data/connectors_df/df_it.csv')
    connector_list = {'single': {}, 'double': {}}
    {connector_list['single'].update(lang) for lang in [CONNECTORS_DE['single'],
                              CONNECTORS_EN['single'], CONNECTORS_IT['single']]}
    {connector_list['double'].update(lang) for lang in [CONNECTORS_DE['double'],
                              CONNECTORS_EN['double'], CONNECTORS_IT['double']]}
    # get all sentence triples
    corpus_root = os.path.join('data', 'corpus')
    all_sent_triples = all_xmls_to_sent_triples(
        corpus_root,
        list_xml_files(os.path.join(corpus_root, 'de'))
        )
    write_as_html(os.path.join('output', 'output.html'),
                  all_sent_triples, connector_list)
