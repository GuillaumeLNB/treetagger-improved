#!/bin/python3.6
import logging
import os
import re

import treetaggerwrapper
from treetaggerwrapper import TreeTaggerError
from langdetect import detect

dict_iso_to_full_language_name = {
    # ISO-639-1 language code to the full language name
    # python module iso639 is not used here as the 'el' input
    # returns modern greek (1453-)
    "cs": "czech",
    "da": "danish",
    "de": "german",
    "el": "greek",
    "en": "english",
    "es": "spanish",
    "et": "estonian",
    "fi": "finnish",
    "fr": "french",
    "it": "italian",
    "nl": "dutch",
    "no": "norwegian",
    "pl": "polish",
    "pt": "portuguese",
    "ru": "russian",
    "sl": "slovene",
    "sv": "swedish",
    "tr": "turkish",
}

TREETAGGER_LOCATION = "~/treetagger"


class TreeTaggerImprovedError(Exception):
    # need a custom exception as the project is still under
    # development and I need the feedback
    # https://github.com/GuillaumeLNB/treetagger-improved/issues
    general_msg = "\nplease repport this issue at https://github.com/GuillaumeLNB/treetagger-improved/issues"

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg) + self.general_msg


class TreeTaggerImproved(treetaggerwrapper.TreeTagger):
    """same class as TreeTagger objects,
    but witht a tag_text_tokens() method that give the token positions
    >>> from treetagger_improved import TreeTaggerImproved
    >>> tagger = TreeTaggerImproved(TAGLANG="fr")
    >>> text = "Le silence éternel de ces espaces infinis m’effraie."
    >>> tagger.tag_text_tokens(text)
    [{'word': 'Le', 'pos': 'DET:ART', 'lemma': 'le', 'start': 0, 'end': 2}, {'word': 'silence', 'pos': 'NOM', 'lemma': 'silence', 'start': 3, 'end': 10}, {'word': 'éternel', 'pos': 'ADJ', 'lemma': 'éternel', 'start': 11, 'end': 18}, {'word': 'de', 'pos': 'PRP', 'lemma': 'de', 'start': 19, 'end': 21}, {'word': 'ces', 'pos': 'PRO:DEM', 'lemma': 'ce', 'start': 22, 'end': 25}, {'word': 'espaces', 'pos': 'NOM', 'lemma': 'espace', 'start': 26, 'end': 33}, {'word': 'infinis', 'pos': 'ADJ', 'lemma': 'infini', 'start': 34, 'end': 41}, {'word': 'm’effraie', 'pos': 'VER:subp', 'lemma': 'm’effraie', 'start': 42, 'end': 51}, {'word': '.', 'pos': 'SENT', 'lemma': '.', 'start': 51, 'end': 52}]
    >>> tagger.get_text_lemmatized(text)
    'le silence éternel de ce espace infini m’effraie .'
    """

    def __init__(self, **kwargs):
        logging.debug(f"init TreeTaggerImproved with '{kwargs}'")
        try:
            super().__init__(**kwargs)
        except TreeTaggerError as e:
            logging.error(f"error while initializing the tagger '{e}'")
            logging.error(f"will init from direct TAGPARFILE")
            logging.error(f"The TAGLANG parameter will be set to German")
            tagparfile = os.path.join(
                TREETAGGER_LOCATION,
                "lib",
                f"{dict_iso_to_full_language_name[kwargs['TAGLANG']]}.par",
            )
            logging.error(f"The TAGPARFILE parameter will be set to '{tagparfile}'")
            kwargs["TAGLANG"] = "de"
            kwargs["TAGPARFILE"] = tagparfile
            super().__init__(**kwargs)

    def assert_correct_lang_text(self, text, strict=False):
        """if no TAGLANG parameter is used for instanciation,
        the default self.lang is English
        This method assert the self.lang is the same language
        as the text passed in argument"""
        detected_language = detect(text)
        if detected_language != self.lang:
            msg = f"detected language of text is  '{detected_language}', but self.lang is '{self.lang}'. Did you instanciate the tagger with the correct TAGLANG parameter?"
            if strict:
                logging.exception(msg)
                raise ValueError(msg)
            logging.error(msg)

    def tag_text_tokens(self, text, check_language=True) -> list[dict]:
        """return a list of the tokens as dictionaries

        :param text: the text to be lemmatized
        :type text: str
        :param check_language: check with `self.assert_correct_lang_text`
        if the language is consistent with the tagger, defaults to True
        :type check_language: bool, optional
        :return: tokens
        :rtype: list[dict]
        """

        if check_language:
            self.assert_correct_lang_text(text)
        tags = self.tag_text(
            text,
            notagurl=True,
            notagemail=True,
            notagip=True,
            notagdns=True,
            nosgmlsplit=True,
        )
        ls_tags = treetaggerwrapper.make_tags(tags)
        ls_tokens = []
        last_pos = 0
        num_errors = 0
        for i, tag in enumerate(ls_tags):
            word = tag[0]
            if word == "...":
                # by default TT changes '…' to '...'
                # this causes misleading characters count
                # note that the token can also be '...'
                # we check that the token has not been replaced:
                if re.match(r"\s*…", text[last_pos:]):
                    # the token has been replaced from '…' to '...'
                    logging.debug("remplacing ... by …")
                    word = "…"
            # counting the number of spaces after last token
            num_spaces_after_last_token = re.match("\s*", text[last_pos:]).span()[1]
            try:
                # the new token position is the sum of the last position,
                # and the index of the text containing the word.
                # upper limit in the search method in the text
                # with num_spaces_after_last_token, otherwise,
                # the index search could go very far in the text
                token_position = last_pos + text[
                    last_pos : last_pos + num_spaces_after_last_token + len(word)
                ].index(word)
            except Exception as e:
                logging.warning(
                    f"cannot find 1st substring (word is: '{word}'). Checking another position ..."
                )
                # checking if the token is an Acronym as
                # Acronyms like U.S.A. are systematically written
                # with a final dot, even if it is missing in original file. See
                # https://treetaggerwrapper.readthedocs.io/en/latest/#other-things-done-by-this-module
                token_position = None
                try:
                    token_position = last_pos + text[last_pos:].index(word.strip("."))
                    word = word.strip(".")
                except Exception as e2:
                    logging.critical(f"cannot find {tag} even without trailing dot")
                    logging.exception(e2)
                    raise TreeTaggerImprovedError(e2)
                if token_position is None:
                    # the token position could be equal to 0
                    # so checking for the booleaness can raise Error
                    logging.critical(f"ignoring {tag}")
                    logging.critical(f"\ttoken position: {token_position}")
                    logging.critical(f"\tlast_position {last_pos}")
                    logging.critical(f"\t{e}")
                    num_errors += 1
                    # continue
                    logging.exception(e)
                    raise TreeTaggerImprovedError(e)
                logging.warning(f"-> found corresponding substring")
            if token_position - last_pos > 100:
                logging.warning(
                    f"token position is too far. Last pos is {last_pos} new pos is {token_position}"
                )
            if type(tag) == treetaggerwrapper.Tag:
                pos = tag[1]
                lemma = tag[2]
            elif type(tag) == treetaggerwrapper.NotTag:
                pos = ""
                lemma = word
            token = {
                "word": word,
                "pos": pos,
                "lemma": lemma,
                "start": token_position,
                "end": token_position + len(word),
            }
            ls_tokens.append(token)
            last_pos = token["end"]
        if num_errors:
            logging.error(f"{num_errors} on {i} tokens")
        # last assertion
        for token in ls_tokens:
            if not token["word"] == text[token["start"] : token["end"]]:
                raise TreeTaggerImprovedError(
                    "the token position doesnt match in the text"
                )
        return ls_tokens

    def get_text_lemmatized(self, text, check_language=True) -> str:
        """return a lemmatized version of the text

        :param text: [description]
        :type text: [type]
        :param check_language: [description], defaults to True
        :type check_language: bool, optional
        :return: [description]
        :rtype: [type]
        """
        if check_language:
            self.assert_correct_lang_text(text)
        tokens = self.tag_text_tokens(text, check_language=check_language)
        return " ".join([word["lemma"] for word in tokens])


if __name__ == "__main__":
    pass
