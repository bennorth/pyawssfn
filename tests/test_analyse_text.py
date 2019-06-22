import pytest
from examples import analyse_text as A
from pysfn import definition as PSF


class TestAnalysis:
    def test_get_summary(self):
        assert A.get_summary('hello world') == {'head': 'h'}

    def test_get_summary_too_short(self):
        with pytest.raises(A.TextTooShortError):
            A.get_summary('')

    def test_augment_summary(self):
        summary = {'head': 'h'}
        aug_summary = A.augment_summary('hello world', summary)
        assert aug_summary['head'] == 'h'  # Original data should remain
        assert aug_summary['n_characters'] == 11

    def test_get_n_vowels(self):
        assert A.get_n_vowels('hello world') == 3
        assert A.get_n_vowels('rhythms') == 0

    def test_get_n_spaces(self):
        assert A.get_n_spaces('hello world') == 1
        assert A.get_n_spaces('goodbye') == 0
        assert A.get_n_spaces('once upon a time') == 3

    def test_format_result(self):
        summary = {'head': 'h', 'n_characters': 10}
        infos = [42, 99]
        assert (A.format_result(summary, infos)
                == ('text starts with h,'
                    ' has 10 chars,'
                    ' 42 vowels, and 99 spaces'))

    def test_summary(self):
        got = A.summarise('a short example')
        assert got == ('text starts with a, has 15 chars,'
                       ' 5 vowels, and 2 spaces')

    def test_c_summary(self):
        got = A.summarise('choose wisely')
        assert got == 'text starts with "c"; look: "c"'

    def test_summary_too_short(self):
        with pytest.raises(PSF.Fail, match='text too short'):
            A.summarise('')

    def test_summary_wrong_start(self):
        with pytest.raises(PSF.Fail, match='wrong starting letter'):
            A.summarise('do not handle starting with "d"')
