# parallel corpus reader
import os
from xml.dom import minidom
from lib.extract_connectors import CONNECTOR_DE, CONNECTOR_EN, CONNECTOR_IT
from data.corpus import *

def list_xml_files(corpus_root):
    """returns xml filenames (without prefix) in the given corpus root directory."""
    return [
        filename
        for _ , _, filenames in os.walk(corpus_root) 
        for filename in filenames if filename.endswith('.xml')
        ]

if __name__ == "__main__":
    ## (1) Datei öffnen: DE-Corpus als Basis
    corpus_root = os.path.join('data', 'corpus')
    corpus_filepaths = list_xml_files(os.path.join(corpus_root, 'de'))
    # die EN und IT Dateien einlesen, die die gleiche Nr./Dateiname wie de DE Datei haben
    for filepath in corpus_filepaths:
        with open(os.path.join(corpus_root, 'de', filepath), 'r') as f_de, \
        open(os.path.join(corpus_root, 'en', filepath), 'r') as f_en, \
        open(os.path.join(corpus_root, 'it', filepath), 'r') as f_it:
            
            ## (2) XML-Inhalt extrahieren (eine separate Methode?)
            # DE Beispiel
            xml_de = minidom.parse(f_de)
            sents_de = xml_de.getElementsByTagName('edu')
            print(sents_de[0].firstChild.nodeValue)    
            break

            # methode for 3-sent-tuple (type: named tuple?) for all 3 corpora? 