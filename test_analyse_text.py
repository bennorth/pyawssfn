import pytest
import analyse_text as A

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
