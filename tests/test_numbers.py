# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

import unittest
import pytest

from datetime import date

from babel import Locale, localedata, numbers
from babel.numbers import (
    list_currencies, validate_currency, UnknownCurrencyError, is_currency, normalize_currency,
    get_currency_precision, get_decimal_precision)
from babel.localedata import locale_identifiers
from babel._compat import decimal


class FormatDecimalTestCase(unittest.TestCase):

    def test_patterns(self):
        self.assertEqual(numbers.format_decimal(12345, '##0',
                                                locale='en_US'), '12345')
        self.assertEqual(numbers.format_decimal(6.5, '0.00', locale='sv'),
                         '6,50')
        self.assertEqual(numbers.format_decimal(10.0**20,
                                                '#.00', locale='en_US'),
                         '100000000000000000000.00')
        # regression test for #183, fraction digits were not correctly cutted
        # if the input was a float value and the value had more than 7
        # significant digits
        self.assertEqual(u'12,345,678.05',
                         numbers.format_decimal(12345678.051, '#,##0.00',
                                                locale='en_US'))

    def test_subpatterns(self):
        self.assertEqual(numbers.format_decimal(-12345, '#,##0.##;-#',
                                                locale='en_US'), '-12,345')
        self.assertEqual(numbers.format_decimal(-12345, '#,##0.##;(#)',
                                                locale='en_US'), '(12,345)')

    def test_default_rounding(self):
        """
        Testing Round-Half-Even (Banker's rounding)

        A '5' is rounded to the closest 'even' number
        """
        self.assertEqual(numbers.format_decimal(5.5, '0', locale='sv'), '6')
        self.assertEqual(numbers.format_decimal(6.5, '0', locale='sv'), '6')
        self.assertEqual(numbers.format_decimal(6.5, '0', locale='sv'), '6')
        self.assertEqual(numbers.format_decimal(1.2325, locale='sv'), '1,232')
        self.assertEqual(numbers.format_decimal(1.2335, locale='sv'), '1,234')

    def test_significant_digits(self):
        """Test significant digits patterns"""
        self.assertEqual(numbers.format_decimal(123004, '@@', locale='en_US'),
                         '120000')
        self.assertEqual(numbers.format_decimal(1.12, '@', locale='sv'), '1')
        self.assertEqual(numbers.format_decimal(1.1, '@@', locale='sv'), '1,1')
        self.assertEqual(numbers.format_decimal(1.1, '@@@@@##', locale='sv'),
                         '1,1000')
        self.assertEqual(numbers.format_decimal(0.0001, '@@@', locale='sv'),
                         '0,000100')
        self.assertEqual(numbers.format_decimal(0.0001234, '@@@', locale='sv'),
                         '0,000123')
        self.assertEqual(numbers.format_decimal(0.0001234, '@@@#', locale='sv'),
                         '0,0001234')
        self.assertEqual(numbers.format_decimal(0.0001234, '@@@#', locale='sv'),
                         '0,0001234')
        self.assertEqual(numbers.format_decimal(0.12345, '@@@', locale='sv'),
                         '0,123')
        self.assertEqual(numbers.format_decimal(3.14159, '@@##', locale='sv'),
                         '3,142')
        self.assertEqual(numbers.format_decimal(1.23004, '@@##', locale='sv'),
                         '1,23')
        self.assertEqual(numbers.format_decimal(1230.04, '@@,@@', locale='en_US'),
                         '12,30')
        self.assertEqual(numbers.format_decimal(123.41, '@@##', locale='en_US'),
                         '123.4')
        self.assertEqual(numbers.format_decimal(1, '@@', locale='en_US'),
                         '1.0')
        self.assertEqual(numbers.format_decimal(0, '@', locale='en_US'),
                         '0')
        self.assertEqual(numbers.format_decimal(0.1, '@', locale='en_US'),
                         '0.1')
        self.assertEqual(numbers.format_decimal(0.1, '@#', locale='en_US'),
                         '0.1')
        self.assertEqual(numbers.format_decimal(0.1, '@@', locale='en_US'),
                         '0.10')

    def test_decimals(self):
        """Test significant digits patterns"""
        self.assertEqual(numbers.format_decimal(decimal.Decimal('1.2345'),
                                                '#.00', locale='en_US'),
                         '1.23')
        self.assertEqual(numbers.format_decimal(decimal.Decimal('1.2345000'),
                                                '#.00', locale='en_US'),
                         '1.23')
        self.assertEqual(numbers.format_decimal(decimal.Decimal('1.2345000'),
                                                '@@', locale='en_US'),
                         '1.2')
        self.assertEqual(numbers.format_decimal(decimal.Decimal('12345678901234567890.12345'),
                                                '#.00', locale='en_US'),
                         '12345678901234567890.12')

    def test_scientific_notation(self):
        fmt = numbers.format_scientific(0.1, '#E0', locale='en_US')
        self.assertEqual(fmt, '1E-1')
        fmt = numbers.format_scientific(0.01, '#E0', locale='en_US')
        self.assertEqual(fmt, '1E-2')
        fmt = numbers.format_scientific(10, '#E0', locale='en_US')
        self.assertEqual(fmt, '1E1')
        fmt = numbers.format_scientific(1234, '0.###E0', locale='en_US')
        self.assertEqual(fmt, '1.234E3')
        fmt = numbers.format_scientific(1234, '0.#E0', locale='en_US')
        self.assertEqual(fmt, '1.2E3')
        # Exponent grouping
        fmt = numbers.format_scientific(12345, '##0.####E0', locale='en_US')
        self.assertEqual(fmt, '1.2345E4')
        # Minimum number of int digits
        fmt = numbers.format_scientific(12345, '00.###E0', locale='en_US')
        self.assertEqual(fmt, '12.345E3')
        fmt = numbers.format_scientific(-12345.6, '00.###E0', locale='en_US')
        self.assertEqual(fmt, '-12.346E3')
        fmt = numbers.format_scientific(-0.01234, '00.###E0', locale='en_US')
        self.assertEqual(fmt, '-12.34E-3')
        # Custom pattern suffic
        fmt = numbers.format_scientific(123.45, '#.##E0 m/s', locale='en_US')
        self.assertEqual(fmt, '1.23E2 m/s')
        # Exponent patterns
        fmt = numbers.format_scientific(123.45, '#.##E00 m/s', locale='en_US')
        self.assertEqual(fmt, '1.23E02 m/s')
        fmt = numbers.format_scientific(0.012345, '#.##E00 m/s', locale='en_US')
        self.assertEqual(fmt, '1.23E-02 m/s')
        fmt = numbers.format_scientific(decimal.Decimal('12345'), '#.##E+00 m/s',
                                        locale='en_US')
        self.assertEqual(fmt, '1.23E+04 m/s')
        # 0 (see ticket #99)
        fmt = numbers.format_scientific(0, '#E0', locale='en_US')
        self.assertEqual(fmt, '0E0')

    def test_formatting_of_very_small_decimals(self):
        # previously formatting very small decimals could lead to a type error
        # because the Decimal->string conversion was too simple (see #214)
        number = decimal.Decimal("7E-7")
        fmt = numbers.format_decimal(number, format="@@@", locale='en_US')
        self.assertEqual('0.000000700', fmt)


class NumberParsingTestCase(unittest.TestCase):

    def test_can_parse_decimals(self):
        self.assertEqual(decimal.Decimal('1099.98'),
                         numbers.parse_decimal('1,099.98', locale='en_US'))
        self.assertEqual(decimal.Decimal('1099.98'),
                         numbers.parse_decimal('1.099,98', locale='de'))
        self.assertRaises(numbers.NumberFormatError,
                          lambda: numbers.parse_decimal('2,109,998', locale='de'))


def test_list_currencies():
    assert isinstance(list_currencies(), set)
    assert list_currencies().issuperset(['BAD', 'BAM', 'KRO'])

    assert isinstance(list_currencies(locale='fr'), set)
    assert list_currencies('fr').issuperset(['BAD', 'BAM', 'KRO'])

    with pytest.raises(ValueError) as excinfo:
        list_currencies('yo!')
    assert excinfo.value.args[0] == "expected only letters, got 'yo!'"

    assert list_currencies(locale='pa_Arab') == {'PKR', 'INR', 'EUR'}
    assert list_currencies(locale='kok') == set([])

    assert len(list_currencies()) == 296


def test_validate_currency():
    validate_currency('EUR')

    with pytest.raises(UnknownCurrencyError) as excinfo:
        validate_currency('FUU')
    assert excinfo.value.args[0] == "Unknown currency 'FUU'."


def test_is_currency():
    assert is_currency('EUR') == True
    assert is_currency('eUr') == False
    assert is_currency('FUU') == False
    assert is_currency('') == False
    assert is_currency(None) == False
    assert is_currency('   EUR    ') == False
    assert is_currency('   ') == False
    assert is_currency([]) == False
    assert is_currency(set()) == False


def test_normalize_currency():
    assert normalize_currency('EUR') == 'EUR'
    assert normalize_currency('eUr') == 'EUR'
    assert normalize_currency('FUU') is None
    assert normalize_currency('') is None
    assert normalize_currency(None) is None
    assert normalize_currency('   EUR    ') is None
    assert normalize_currency('   ') is None
    assert normalize_currency([]) is None
    assert normalize_currency(set()) is None


def test_get_currency_name():
    assert numbers.get_currency_name('USD', locale='en_US') == u'US Dollar'
    assert numbers.get_currency_name('USD', count=2, locale='en_US') == u'US dollars'


def test_get_currency_symbol():
    assert numbers.get_currency_symbol('USD', 'en_US') == u'$'


def test_get_currency_precision():
    assert get_currency_precision('EUR') == 2
    assert get_currency_precision('JPY') == 0


def test_get_territory_currencies():
    assert numbers.get_territory_currencies('AT', date(1995, 1, 1)) == ['ATS']
    assert numbers.get_territory_currencies('AT', date(2011, 1, 1)) == ['EUR']

    assert numbers.get_territory_currencies('US', date(2013, 1, 1)) == ['USD']
    assert sorted(numbers.get_territory_currencies('US', date(2013, 1, 1),
                                                   non_tender=True)) == ['USD', 'USN', 'USS']

    assert numbers.get_territory_currencies('US', date(2013, 1, 1),
                                            include_details=True) == [{
                                                'currency': 'USD',
                                                'from': date(1792, 1, 1),
                                                'to': None,
                                                'tender': True
                                            }]

    assert numbers.get_territory_currencies('LS', date(2013, 1, 1)) == ['ZAR', 'LSL']

    assert numbers.get_territory_currencies('QO', date(2013, 1, 1)) == []


def test_get_decimal_symbol():
    assert numbers.get_decimal_symbol('en_US') == u'.'


def test_get_plus_sign_symbol():
    assert numbers.get_plus_sign_symbol('en_US') == u'+'


def test_get_minus_sign_symbol():
    assert numbers.get_minus_sign_symbol('en_US') == u'-'
    assert numbers.get_minus_sign_symbol('nl_NL') == u'-'


def test_get_exponential_symbol():
    assert numbers.get_exponential_symbol('en_US') == u'E'


def test_get_group_symbol():
    assert numbers.get_group_symbol('en_US') == u','


def test_decimal_precision():
    assert get_decimal_precision(decimal.Decimal('0.110')) == 2
    assert get_decimal_precision(decimal.Decimal('1.0')) == 0
    assert get_decimal_precision(decimal.Decimal('10000')) == 0


def test_format_number():
    assert numbers.format_number(1099, locale='en_US') == u'1,099'
    assert numbers.format_number(1099, locale='de_DE') == u'1.099'


def test_format_decimal():
    assert numbers.format_decimal(1.2345, locale='en_US') == u'1.234'
    assert numbers.format_decimal(1.2346, locale='en_US') == u'1.235'
    assert numbers.format_decimal(-1.2346, locale='en_US') == u'-1.235'
    assert numbers.format_decimal(1.2345, locale='sv_SE') == u'1,234'
    assert numbers.format_decimal(1.2345, locale='de') == u'1,234'
    assert numbers.format_decimal(12345.5, locale='en_US') == u'12,345.5'
    assert numbers.format_decimal(0001.2345000, locale='en_US') == u'1.234'
    assert numbers.format_decimal(-0001.2346000, locale='en_US') == u'-1.235'
    assert numbers.format_decimal(0000000.5, locale='en_US') == u'0.5'
    assert numbers.format_decimal(000, locale='en_US') == u'0'


@pytest.mark.parametrize('input_value, expected_value', [
    ('10000', '10,000'),
    ('1', '1'),
    ('1.0', '1'),
    ('1.1', '1.1'),
    ('1.11', '1.11'),
    ('1.110', '1.11'),
    ('1.001', '1.001'),
    ('1.00100', '1.001'),
    ('01.00100', '1.001'),
    ('101.00100', '101.001'),
    ('00000', '0'),
    ('0', '0'),
    ('0.0', '0'),
    ('0.1', '0.1'),
    ('0.11', '0.11'),
    ('0.110', '0.11'),
    ('0.001', '0.001'),
    ('0.00100', '0.001'),
    ('00.00100', '0.001'),
    ('000.00100', '0.001'),
])
def test_format_decimal_precision(input_value, expected_value):
    # Test precision conservation.
    assert numbers.format_decimal(
        decimal.Decimal(input_value), locale='en_US', decimal_quantization=False) == expected_value


def test_format_decimal_quantization():
    # Test all locales.
    for locale_code in localedata.locale_identifiers():
        assert numbers.format_decimal(
            '0.9999999999', locale=locale_code, decimal_quantization=False).endswith('9999999999') is True


def test_format_currency():
    assert (numbers.format_currency(1099.98, 'USD', locale='en_US')
            == u'$1,099.98')
    assert (numbers.format_currency(0, 'USD', locale='en_US')
            == u'$0.00')
    assert (numbers.format_currency(1099.98, 'USD', locale='es_CO')
            == u'US$\xa01.099,98')
    assert (numbers.format_currency(1099.98, 'EUR', locale='de_DE')
            == u'1.099,98\xa0\u20ac')
    assert (numbers.format_currency(1099.98, 'EUR', u'\xa4\xa4 #,##0.00',
                                    locale='en_US')
            == u'EUR 1,099.98')
    assert (numbers.format_currency(1099.98, 'EUR', locale='nl_NL')
            != numbers.format_currency(-1099.98, 'EUR', locale='nl_NL'))
    assert (numbers.format_currency(1099.98, 'USD', format=None,
                                    locale='en_US')
            == u'$1,099.98')


def test_format_currency_format_type():
    assert (numbers.format_currency(1099.98, 'USD', locale='en_US',
                                    format_type="standard")
            == u'$1,099.98')
    assert (numbers.format_currency(0, 'USD', locale='en_US',
                                    format_type="standard")
            == u'$0.00')

    assert (numbers.format_currency(1099.98, 'USD', locale='en_US',
                                    format_type="accounting")
            == u'$1,099.98')
    assert (numbers.format_currency(0, 'USD', locale='en_US',
                                    format_type="accounting")
            == u'$0.00')

    with pytest.raises(numbers.UnknownCurrencyFormatError) as excinfo:
        numbers.format_currency(1099.98, 'USD', locale='en_US',
                                format_type='unknown')
    assert excinfo.value.args[0] == "'unknown' is not a known currency format type"

    assert (numbers.format_currency(1099.98, 'JPY', locale='en_US')
            == u'\xa51,100')
    assert (numbers.format_currency(1099.98, 'COP', u'#,##0.00', locale='es_ES')
            == u'1.100')
    assert (numbers.format_currency(1099.98, 'JPY', locale='en_US',
                                    currency_digits=False)
            == u'\xa51,099.98')
    assert (numbers.format_currency(1099.98, 'COP', u'#,##0.00', locale='es_ES',
                                    currency_digits=False)
            == u'1.099,98')


@pytest.mark.parametrize('input_value, expected_value', [
    ('10000', '$10,000.00'),
    ('1', '$1.00'),
    ('1.0', '$1.00'),
    ('1.1', '$1.10'),
    ('1.11', '$1.11'),
    ('1.110', '$1.11'),
    ('1.001', '$1.001'),
    ('1.00100', '$1.001'),
    ('01.00100', '$1.001'),
    ('101.00100', '$101.001'),
    ('00000', '$0.00'),
    ('0', '$0.00'),
    ('0.0', '$0.00'),
    ('0.1', '$0.10'),
    ('0.11', '$0.11'),
    ('0.110', '$0.11'),
    ('0.001', '$0.001'),
    ('0.00100', '$0.001'),
    ('00.00100', '$0.001'),
    ('000.00100', '$0.001'),
])
def test_format_currency_precision(input_value, expected_value):
    # Test precision conservation.
    assert numbers.format_currency(
        decimal.Decimal(input_value), 'USD', locale='en_US', decimal_quantization=False) == expected_value


def test_format_currency_quantization():
    # Test all locales.
    for locale_code in localedata.locale_identifiers():
        assert numbers.format_currency(
            '0.9999999999', 'USD', locale=locale_code, decimal_quantization=False).find('9999999999') > -1


def test_format_percent():
    assert numbers.format_percent(0.34, locale='en_US') == u'34%'
    assert numbers.format_percent(0, locale='en_US') == u'0%'
    assert numbers.format_percent(0.34, u'##0%', locale='en_US') == u'34%'
    assert numbers.format_percent(34, u'##0', locale='en_US') == u'34'
    assert numbers.format_percent(25.1234, locale='en_US') == u'2,512%'
    assert (numbers.format_percent(25.1234, locale='sv_SE')
            == u'2\xa0512\xa0%')
    assert (numbers.format_percent(25.1234, u'#,##0\u2030', locale='en_US')
            == u'25,123\u2030')


@pytest.mark.parametrize('input_value, expected_value', [
    ('100', '10,000%'),
    ('0.01', '1%'),
    ('0.010', '1%'),
    ('0.011', '1.1%'),
    ('0.0111', '1.11%'),
    ('0.01110', '1.11%'),
    ('0.01001', '1.001%'),
    ('0.0100100', '1.001%'),
    ('0.010100100', '1.01001%'),
    ('0.000000', '0%'),
    ('0', '0%'),
    ('0.00', '0%'),
    ('0.01', '1%'),
    ('0.011', '1.1%'),
    ('0.0110', '1.1%'),
    ('0.0001', '0.01%'),
    ('0.000100', '0.01%'),
    ('0.0000100', '0.001%'),
    ('0.00000100', '0.0001%'),
])
def test_format_percent_precision(input_value, expected_value):
    # Test precision conservation.
    assert numbers.format_percent(
        decimal.Decimal(input_value), locale='en_US', decimal_quantization=False) == expected_value


def test_format_percent_quantization():
    # Test all locales.
    for locale_code in localedata.locale_identifiers():
        assert numbers.format_percent(
            '0.9999999999', locale=locale_code, decimal_quantization=False).find('99999999') > -1


def test_format_scientific():
    assert numbers.format_scientific(10000, locale='en_US') == u'1E4'
    assert numbers.format_scientific(4234567, u'#.#E0', locale='en_US') == u'4.2E6'
    assert numbers.format_scientific(4234567, u'0E0000', locale='en_US') == u'4.234567E0006'
    assert numbers.format_scientific(4234567, u'##0E00', locale='en_US') == u'4.234567E06'
    assert numbers.format_scientific(4234567, u'##00E00', locale='en_US') == u'42.34567E05'
    assert numbers.format_scientific(4234567, u'0,000E00', locale='en_US') == u'4,234.567E03'
    assert numbers.format_scientific(4234567, u'##0.#####E00', locale='en_US') == u'4.23457E06'
    assert numbers.format_scientific(4234567, u'##0.##E00', locale='en_US') == u'4.23E06'
    assert numbers.format_scientific(42, u'00000.000000E0000', locale='en_US') == u'42000.000000E-0003'


def test_default_scientific_format():
    """ Check the scientific format method auto-correct the rendering pattern
    in case of a missing fractional part.
    """
    assert numbers.format_scientific(12345, locale='en_US') == u'1.2345E4'
    assert numbers.format_scientific(12345.678, locale='en_US') == u'1.2345678E4'
    assert numbers.format_scientific(12345, u'#E0', locale='en_US') == u'1.2345E4'
    assert numbers.format_scientific(12345.678, u'#E0', locale='en_US') == u'1.2345678E4'


@pytest.mark.parametrize('input_value, expected_value', [
    ('10000', '1E4'),
    ('1', '1E0'),
    ('1.0', '1E0'),
    ('1.1', '1.1E0'),
    ('1.11', '1.11E0'),
    ('1.110', '1.11E0'),
    ('1.001', '1.001E0'),
    ('1.00100', '1.001E0'),
    ('01.00100', '1.001E0'),
    ('101.00100', '1.01001E2'),
    ('00000', '0E0'),
    ('0', '0E0'),
    ('0.0', '0E0'),
    ('0.1', '1E-1'),
    ('0.11', '1.1E-1'),
    ('0.110', '1.1E-1'),
    ('0.001', '1E-3'),
    ('0.00100', '1E-3'),
    ('00.00100', '1E-3'),
    ('000.00100', '1E-3'),
])
def test_format_scientific_precision(input_value, expected_value):
    # Test precision conservation.
    assert numbers.format_scientific(
        decimal.Decimal(input_value), locale='en_US', decimal_quantization=False) == expected_value


def test_format_scientific_quantization():
    # Test all locales.
    for locale_code in localedata.locale_identifiers():
        assert numbers.format_scientific(
            '0.9999999999', locale=locale_code, decimal_quantization=False).find('999999999') > -1


def test_parse_number():
    assert numbers.parse_number('1,099', locale='en_US') == 1099
    assert numbers.parse_number('1.099', locale='de_DE') == 1099

    with pytest.raises(numbers.NumberFormatError) as excinfo:
        numbers.parse_number('1.099,98', locale='de')
    assert excinfo.value.args[0] == "'1.099,98' is not a valid number"


def test_parse_decimal():
    assert (numbers.parse_decimal('1,099.98', locale='en_US')
            == decimal.Decimal('1099.98'))
    assert numbers.parse_decimal('1.099,98', locale='de') == decimal.Decimal('1099.98')

    with pytest.raises(numbers.NumberFormatError) as excinfo:
        numbers.parse_decimal('2,109,998', locale='de')
    assert excinfo.value.args[0] == "'2,109,998' is not a valid decimal number"


def test_parse_grouping():
    assert numbers.parse_grouping('##') == (1000, 1000)
    assert numbers.parse_grouping('#,###') == (3, 3)
    assert numbers.parse_grouping('#,####,###') == (3, 4)


def test_parse_pattern():

    # Original pattern is preserved
    np = numbers.parse_pattern(u'¤#,##0.00')
    assert np.pattern == u'¤#,##0.00'

    np = numbers.parse_pattern(u'¤#,##0.00;(¤#,##0.00)')
    assert np.pattern == u'¤#,##0.00;(¤#,##0.00)'

    # Given a NumberPattern object, we don't return a new instance.
    # However, we don't cache NumberPattern objects, so calling
    # parse_pattern with the same format string will create new
    # instances
    np1 = numbers.parse_pattern(u'¤ #,##0.00')
    np2 = numbers.parse_pattern(u'¤ #,##0.00')
    assert np1 is not np2
    assert np1 is numbers.parse_pattern(np1)


def test_parse_pattern_negative():

    # No negative format specified
    np = numbers.parse_pattern(u'¤#,##0.00')
    assert np.prefix == (u'¤', u'-¤')
    assert np.suffix == (u'', u'')

    # Negative format is specified
    np = numbers.parse_pattern(u'¤#,##0.00;(¤#,##0.00)')
    assert np.prefix == (u'¤', u'(¤')
    assert np.suffix == (u'', u')')

    # Negative sign is a suffix
    np = numbers.parse_pattern(u'¤ #,##0.00;¤ #,##0.00-')
    assert np.prefix == (u'¤ ', u'¤ ')
    assert np.suffix == (u'', u'-')


def test_numberpattern_repr():
    """repr() outputs the pattern string"""

    # This implementation looks a bit funny, but that's cause strings are
    # repr'd differently in Python 2 vs 3 and this test runs under both.
    format = u'¤#,##0.00;(¤#,##0.00)'
    np = numbers.parse_pattern(format)
    assert repr(format) in repr(np)
