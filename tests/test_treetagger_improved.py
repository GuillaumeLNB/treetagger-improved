#!/bin/python3
import os
import re
import sys
import unittest

from glob import glob
from parameterized import parameterized_class

sys.path.insert(0, os.path.join(".."))
from treetagger_improved import TreeTaggerImproved, TreeTaggerImprovedError
from test_data import TEXTS


@parameterized_class(
    ("language", "sentence"), [(lang, text) for lang, text in TEXTS.items()]
)
class TestTreeTagger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tt = TreeTaggerImproved(TAGLANG=cls.language)
        cls.text = cls.sentence

    def test_assert_correct_lang_text(self):
        self.tt.assert_correct_lang_text(self.text, strict=True)

    def test_tag_text_tokens(self):
        res = self.tt.tag_text_tokens(
            self.text,
        )
        self.assertTrue(res)
        self.assertIsInstance(res, list)
        self.assertIsInstance(res[0], dict)

    def test_get_text_lemmatized(self):
        res = self.tt.get_text_lemmatized(
            self.text,
        )
        self.assertTrue(res)
        self.assertIsInstance(res, str)


class TestDummyTreeTagger(unittest.TestCase):
    def test_weird_string(self):
        text = "E.G[arnett]. thinks that the intelligence and irony  of the book may appeal to H.G.[Wells] I think so too.' "
        tt = TreeTaggerImproved(TAGLANG="en")
        text_lemmas = tt.get_text_lemmatized(text)
        self.assertTrue(text_lemmas)


unittest.main()
