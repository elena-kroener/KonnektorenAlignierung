# KonnektorenAlignierung
This repository contains the code to visualize the connectors in the "argumentative microtext corpus" (in English, German and Italien respectively) in HTML-format based on the connector lexica in [connective-lex.info](connective-lex.info).
It was created in the scope of the final project of the seminar 
"Textstrukturen", taught by Prof. Dr. Manfred Stede, at the University of 
Potsdam in the summer term of 2022 by Elena Kröner, Opal Leung and Cordula 
Scholz.

## Installation Guide
It is assumed that you have installed python3 (Python 3.8.10 was used in the development) on your machine.

1. Clone this repository and go to the root of the repository:
```bash
git clone https://github.com/elena-kroener/KonnektorenAlignierung.git
cd KonnektorenAlignierung
```

2. Install the required packages by:
```bash
pip install -r requirement.txt
```

## Usage
```
python3 corpus_to_html.py
```
The HTML-file which visualizes the corresponding connectors in the parallel corpus will be saved as `output.html` in `output/`, as well as the alignment statistics as `csv` files.

## Program Structure and Flow
1. `extract_connectors.py` extracts the connectors and the relevant information (e.g. connector relations) from the [connective-lex.info](connective-lex.info) in `xml`-format (in `data/connectors_xml/`) and saves them as pandas DataFrames in `csv`-format in `data/connectgors_df/`.
2. `corpus_reader.py` generates the sentence triples (in English, German and Italien) from the "argumentative microtext corpus" in `xml`-format (in `data/corpus/`).
3. `corpus_to_html.py` creates the HTML-file which visualizes the corresponding connectors in the parallel corpus and saves it as `output.html` in `output/`, as well as the alignment statistics as `csv` files.

## Literature
Andreas Peldszus, Manfred Stede. An annotated corpus of argumentative microtexts. First European Conference on Argumentation: Argumentation and Reasoned Action, Portugal, Lisbon, June 2015.
Manfred Stede, Tatjana Scheffler, and Amália Mendes. Connective-lex: A web-based multilingual lexical resource for connectives. Discours. Revue de linguistique, psycholinguistique et informatique, 2019.