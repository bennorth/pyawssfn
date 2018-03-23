import pytest
import analyse_text as A

class TestAnalysis:
    def test_get_summary(self):
        assert A.get_summary('hello world') == {'head': 'h'}

    def test_get_summary_too_short(self):
        with pytest.raises(A.TextTooShortError):
            A.get_summary('')
