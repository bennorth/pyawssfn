import pytest
import pysfnc as C
import ast


def expr_value(txt):
    return ast.parse(txt).body[0].value


class TestSupportFunctions:
    def test_psf_attr(self):
        val = expr_value('PSF.hello_world')
        assert C.psf_attr(val) == 'hello_world'

    @pytest.mark.parametrize(
        'text',
        ['99 + 42',
         'something_else.odd',
         'PSF.nested.attribute']
    )
    def test_psf_attr_bad_input(self, text):
        val = expr_value(text)
        with pytest.raises(ValueError):
            C.psf_attr(val)
        assert C.psf_attr(val, raise_if_not=False) is None

    def test_chained_key(self):
        val = expr_value('foo["bar"]["baz"]')
        assert C.chained_key(val) == ['foo', 'bar', 'baz']

    def test_simple_chained_key(self):
        val = expr_value('foo')
        assert C.chained_key(val) == ['foo']

    @pytest.mark.parametrize(
        'text',
        ['1 + 1',
         'some_dict[3]["foo"]',
         'some_obj[slice_lb:slice_ub]',
         'some_obj.attrib_access']
    )
    def test_chained_key_bad_input(self, text):
        val = expr_value(text)
        with pytest.raises(ValueError):
            C.chained_key(val)


class TestChoice:
    def test_comparison(self):
        val = expr_value('PSF.StringEquals(foo, "bar")')
        cmp = C.TestComparison.from_ast_node(val)
        assert cmp.predicate_name == 'StringEquals'
        assert cmp.predicate_variable == ['foo']
        assert cmp.predicate_literal == 'bar'

    def test_chained_comparison(self):
        val = expr_value('PSF.StringEquals(foo["bar"], "baz")')
        cmp = C.TestComparison.from_ast_node(val)
        assert cmp.predicate_name == 'StringEquals'
        assert cmp.predicate_variable == ['foo', 'bar']
        assert cmp.predicate_literal == 'baz'
