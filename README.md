TreeTaggerImproved
----------------------
This repo contains a python wrapper for [TreeTagger](https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/).

It is based on [Laurent Pointal's TreeTaggerWrapper](https://treetaggerwrapper.readthedocs.io/en/latest).


Demo
-------
```
>>> from treetagger_improved import TreeTaggerImproved
>>> tagger = TreeTaggerImproved(TAGLANG="fr")
>>> text = "Le silence éternel de ces espaces infinis m’effraie."
>>> tagger.tag_text_tokens(text)
[{'word': 'Le', 'pos': 'DET:ART', 'lemma': 'le', 'start': 0, 'end': 2}, {'word': 'silence', 'pos': 'NOM', 'lemma': 'silence', 'start': 3, 'end': 10}, {'word': 'éternel', 'pos': 'ADJ', 'lemma': 'éternel', 'start': 11, 'end': 18}, {'word': 'de', 'pos': 'PRP', 'lemma': 'de', 'start': 19, 'end': 21}, {'word': 'ces', 'pos': 'PRO:DEM', 'lemma': 'ce', 'start': 22, 'end': 25}, {'word': 'espaces', 'pos': 'NOM', 'lemma': 'espace', 'start': 26, 'end': 33}, {'word': 'infinis', 'pos': 'ADJ', 'lemma': 'infini', 'start': 34, 'end': 41}, {'word': 'm’effraie', 'pos': 'VER:subp', 'lemma': 'm’effraie', 'start': 42, 'end': 51}, {'word': '.', 'pos': 'SENT', 'lemma': '.', 'start': 51, 'end': 52}]
>>> tagger.get_text_lemmatized(text)
'le silence éternel de ce espace infini m’effraie .'
```
