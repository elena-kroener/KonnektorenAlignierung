# KonnektorenAlignierung
This repository contains the code to visualize the connectors in the "argumentative microtext corpus" (in English, German and Italien respectively) in HTML-format based on the connector lexica in [connective-lex.info](connective-lex.info).

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