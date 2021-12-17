"""
Column module
"""

import regex as re

from dateutil.parser import parse
from text2digits.text2digits import Text2Digits


class Column:
    """
    Column formatting functions for reports.
    """

    @staticmethod
    def integer(text):
        """
        Format text as a string. This method also converts text describing a number to a number.
        For example, twenty three is converted to 23.

        Args:
            text: input text

        Returns:
            number if parsed, otherwise None
        """

        # Format text for numeric parsing
        text = text.replace(",", "")
        text = re.sub(r"(\d+)\s+(\d+)", r"\1\2", text)

        try:
            # Convert numeric words to numbers
            text = text if text.isdigit() else Text2Digits().convert(text)
        # pylint: disable=W0702
        except:
            pass

        return text if text.isdigit() else None

    @staticmethod
    def categorical(model, text, labels):
        """
        Applies a text classification model to text using labels.

        Args:
            model: text classification model
            text: input text
            labels: labels to use

        Returns:
            categorical label, if model not None, otherwise original text returned
        """

        if model:
            index = model(text, labels)[0][0] if model else text
            return labels[index]

        return text

    @staticmethod
    def duration(text, dtype):
        """
        Attempts to standardize a date duration string to a format specified by dtype.
        If dtype is days and the duration string specifies a month range, the duration is converted
        to days. If the duration is in years and the dtype is months, the duration is converted to months.

        Examples:
            2021-01-01 to 2021-01-31. In days = 30, in months = 1, in years = 0.083
            Jan 2021 to Mar 2021. In days = 60, in months = 2, in years = 0.167

        Args:
            text: date duration string
            dtype: target duration type [supports days, weeks, months, years]

        Returns:
            duration as number
        """

        try:
            data = re.sub(r"(?i)\s*(between|over|up to)\s+", "", text)
            data = re.split(r"\s+(?:and|to|through)\s+", data)

            d1, d2 = parse(data[0]), parse(data[1])
            value = (d2 - d1).days

            # Handle case where no year specified for first date
            if value < 0:
                d1 = d1.replace(year=d2.year)
                value = (d2 - d1).days

            return Column.convert(value, "days", dtype)
        # pylint: disable=W0702
        except:
            pass

        data = re.sub(r"\(.*?\)", "", text)
        data = re.split(r"\s+|\-", data)
        data = sorted(data)

        data[0] = Text2Digits().convert(data[0])
        if len(data) > 1 and not data[1].endswith("s"):
            data[1] = data[1] + "s"

        if len(data) == 2 and (
            data[0].replace(".", "", 1).isdigit()
            and data[1] in (["days", "weeks", "months", "years"])
        ):

            value, suffix = sorted(data)
            value = float(value)

            return Column.convert(value, suffix, dtype)

        return None

    # pylint: disable=R0911,R0912
    @staticmethod
    def convert(value, itype, otype):
        """
        Attempts to convert a numeric duration from itype to otype.

        Args:
            value: numeric duration
            itype: input type [days, weeks, months, years]
            otype: output type [days, weeks, months, years]

        Returns:
            converted numeric duration
        """

        if itype == otype:
            return value

        if itype == "days":
            if otype == "weeks":
                return value / 7
            if otype == "months":
                return value / 30

            # Years
            return value / 365

        if itype == "weeks":
            if otype == "days":
                return value * 7
            if otype == "months":
                return value / 4

            # Years
            return value / 52

        if itype == "months":
            if otype == "days":
                return value * 30
            if otype == "weeks":
                return value * 4

            # Years
            return value / 12

        if itype == "years":
            if otype == "days":
                return value * 365
            if otype == "weeks":
                return value * 52

            # Months
            return value * 12

        return value
