"""Corpus reader of the argumentative microtext corpus (in german, english and italian)."""
import os
from collections import namedtuple
from xml.dom import minidom
# from lib.extract_connectors import CONNECTOR_DE, CONNECTOR_EN, CONNECTOR_IT
from data.corpus import *

# define named tuple object for sentence triple
SentTriple = namedtuple('SentTriple', 'de en it')

def list_xml_files(corpus_root):
    """Returns xml filenames (without prefix) in the given corpus root directory."""
    return [
        filename
        for _ , _, filenames in os.walk(corpus_root) 
        for filename in filenames if filename.endswith('.xml')
        ]

def xml_to_sent_triples(corpus_root, xml_filename):
    """Returns a list of parallel sentence triples from a xml file."""
    with open(os.path.join(corpus_root, 'de', xml_filename), 'r') as f_de, \
            open(os.path.join(corpus_root, 'en', xml_filename), 'r') as f_en, \
            open(os.path.join(corpus_root, 'it', xml_filename), 'r') as f_it:
        
        result = []
        sents_de = minidom.parse(f_de).getElementsByTagName('edu')
        sents_en = minidom.parse(f_en).getElementsByTagName('edu')
        sents_it = minidom.parse(f_it).getElementsByTagName('edu')

        for i in range(len(sents_de)):
            result.append(SentTriple(
                    sents_de[i].firstChild.nodeValue,
                    sents_en[i].firstChild.nodeValue,
                    sents_it[i].firstChild.nodeValue
                ))
        
        return result

if __name__ == "__main__":
    # get all xml filenames (they are the same for the three corpora)
    corpus_root = os.path.join('data', 'corpus')
    corpus_filepaths = list_xml_files(os.path.join(corpus_root, 'de'))

    # get all sentence triples
    all_sent_triples = []
    for xml_filename in corpus_filepaths:
        all_sent_triples.extend(
            xml_to_sent_triples(corpus_root, xml_filename)
            )
    
    # example usage of named tuple
    print(all_sent_triples[0].de)
    print(all_sent_triples[3].en)
    print(all_sent_triples[7].it)

