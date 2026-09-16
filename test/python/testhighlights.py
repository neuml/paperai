"""
Highlights module tests
"""

import unittest

from paperai.highlights import Highlights


class TestHighlights(unittest.TestCase):
    """
    Highlights tests
    """

    # Two sections share vocabulary, the others do not. Input order is deliberately
    # different from the order textrank produces.
    SECTIONS = [
        ("s1", "Completely separate subject about maritime shipping logistics routes"),
        ("s2", "Vaccine efficacy was measured across three independent clinical trials"),
        ("s3", "An unrelated note regarding library catalogue indexing procedures"),
        ("s4", "Clinical trials measured vaccine efficacy in three separate cohorts"),
    ]

    def uids(self, texts):
        """
        Maps highlight text back to section uids.

        Args:
            texts: highlight text

        Returns:
            list of uids
        """

        reverse = {text: uid for uid, text in self.SECTIONS}
        return [reverse[text] for text in texts]

    def testImportanceOrder(self):
        """
        Test that build returns sections ordered by importance, not input order.
        """

        ranked = [uid for uid, _ in Highlights.textrank(self.SECTIONS)]
        highlights = self.uids(Highlights.build(self.SECTIONS, 2))

        # Sanity check: the fixture must exercise a reordering, otherwise this test
        # would pass even if build returned sections in input order
        inputs = [uid for uid, _ in self.SECTIONS]
        self.assertNotEqual(ranked[0], inputs[0])

        # Highlights must appear in the same relative order textrank assigned
        self.assertEqual(highlights, sorted(highlights, key=ranked.index))

        # The top ranked section must come first
        self.assertEqual(highlights[0], ranked[0])

    def testRespectsTopn(self):
        """
        Test that build returns no more than topn sections.
        """

        self.assertEqual(len(Highlights.build(self.SECTIONS, 1)), 1)
        self.assertEqual(len(Highlights.build(self.SECTIONS, 2)), 2)

    def testSingleUseIterable(self):
        """
        Test that build works with an iterator, which can only be consumed once.
        """

        highlights = Highlights.build(iter(self.SECTIONS), 2)

        self.assertEqual(len(highlights), 2)
        self.assertEqual(self.uids(highlights)[0], Highlights.textrank(self.SECTIONS)[0][0])
