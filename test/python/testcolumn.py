"""
Column module tests
"""

import unittest

from paperai.report.column import Column


class TestColumn(unittest.TestCase):
    """
    Column tests
    """

    def testInteger(self):
        """
        Tests parsing integers from strings.
        """

        self.assertEqual(Column.integer("Twenty Three"), "23")
        self.assertEqual(Column.integer("Two hundred and twelve"), "212")
        self.assertEqual(Column.integer("4,000,234"), "4000234")
        self.assertEqual(Column.integer("23"), "23")
        self.assertEqual(Column.integer("30 days"), None)

    def testCategorical(self):
        """
        Tests generating categorical strings.
        """

        def model(text, labels):
            return [(0, 0.9), (1, 0.85), (text, labels)]

        self.assertEqual(Column.categorical(model, "text", ["labels"]), "labels")
        self.assertEqual(Column.categorical(None, "text", ["labels"]), "text")

    def testDurationStartEnd(self):
        """
        Test duration ranges with start and end
        """

        self.assertEqual(Column.duration("2021-01-01 to 2021-01-31", "days"), 30)
        self.assertEqual(Column.duration("2021-01-01 to 2021-01-31", "months"), 1)
        self.assertEqual(
            round(Column.duration("2021-01-01 to 2021-01-31", "weeks"), 2), 4.29
        )
        self.assertEqual(
            round(Column.duration("2021-01-01 to 2021-01-31", "years"), 2), 0.08
        )

    def testDurationStartEndNoYear(self):
        """
        Test duration ranges with start and end but no year for first date
        """

        self.assertEqual(Column.duration("January to March 2020", "days"), 60)

    def testDurationRelative(self):
        """
        Test relative duration ranges
        """

        self.assertEqual(Column.duration("30 day", "days"), 30)

        self.assertEqual(Column.duration("1 week", "days"), 7)
        self.assertEqual(Column.duration("1 week", "months"), 0.25)
        self.assertEqual(round(Column.duration("1 week", "years"), 2), 0.02)

        self.assertEqual(Column.duration("2 months", "days"), 60)
        self.assertEqual(Column.duration("2 months", "weeks"), 8)
        self.assertEqual(round(Column.duration("2 months", "years"), 2), 0.17)

        self.assertEqual(Column.duration("1 year", "days"), 365)
        self.assertEqual(Column.duration("1 year", "weeks"), 52)
        self.assertEqual(Column.duration("1 year", "months"), 12)

        self.assertEqual(Column.duration("30 moons", "days"), None)
        self.assertEqual(Column.convert("30", "moons", "days"), "30")
