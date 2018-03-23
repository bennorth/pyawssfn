import pysfnc as C
import ast


def expr_value(txt):
    return ast.parse(txt).body[0].value


class TestSupportFunctions:
    def test_psf_attr(self):
        val = expr_value('PSF.hello_world')
        assert C.psf_attr(val) == 'hello_world'
