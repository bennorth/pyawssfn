import pytest
import pysfnc as C
import ast
import textwrap
from functools import partial


def stmt_value(txt):
    return ast.parse(textwrap.dedent(txt)).body[0]


def expr_value(txt):
    return stmt_value(txt).value


def suite_value(txt):
    return ast.parse(textwrap.dedent(txt)).body


def _test_factory_raises(nd, factory):
    with pytest.raises(ValueError):
        factory(nd)


def _assert_is_assignment(ir, target, src_funname, *src_argnames):
    assert ir.target_varname == target
    assert ir.source.fun_name == src_funname
    assert ir.source.arg_names == list(src_argnames)


def _assert_is_return(ir, exp_var_name):
    assert isinstance(ir, C.ReturnIR)
    assert ir.varname == exp_var_name


def _assert_comparison_correct(cmp, exp_name, exp_variable, exp_literal):
    assert cmp.predicate_name == exp_name
    assert cmp.predicate_variable == exp_variable
    assert cmp.predicate_literal == exp_literal


mk_statement_empty_defs = partial(C.StatementIR.from_ast_node, defs={})
mk_assign_src_empty_defs = partial(C.AssignmentSourceIR.from_ast_node, defs={})


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

    def test_chained_key_smr(self):
        assert C.chained_key_smr(['foo']) == '$.locals.foo'
        assert C.chained_key_smr(['foo', 'bar']) == '$.locals.foo.bar'

    def test_maybe_with_next(self):
        assert (C.maybe_with_next({'foo': 99}, None)
                == {'foo': 99})
        assert (C.maybe_with_next({'foo': 99}, 'done')
                == {'foo': 99, 'Next': 'done'})


class TestChoice:
    @pytest.fixture(scope='module', params=[C.TestComparison, C.ChoiceCondition])
    def cmp_class(self, request):
        return request.param

    @pytest.fixture(scope='module', params=[C.TestCombinator, C.ChoiceCondition])
    def comb_class(self, request):
        return request.param

    @staticmethod
    def _test_comparison(cmp_class, text, name, variable, literal):
        val = expr_value(text)
        cmp = cmp_class.from_ast_node(val)
        _assert_comparison_correct(cmp, name, variable, literal)

    def test_comparison(self, cmp_class):
        self._test_comparison(cmp_class,
                              'PSF.StringEquals(foo, "bar")',
                              'StringEquals', ['foo'], 'bar')

    def test_chained_comparison(self, cmp_class):
        self._test_comparison(cmp_class,
                              'PSF.StringEquals(foo["bar"], "baz")',
                              'StringEquals', ['foo', 'bar'], 'baz')

    @pytest.mark.parametrize(
        'text',
        ['1 == 1', 'random_check(a, b)']
    )
    def test_comparison_bad_input(self, cmp_class, text):
        _test_factory_raises(expr_value(text), cmp_class.from_ast_node)

    @pytest.mark.parametrize(
        'op, exp_opname',
        [('or', 'Or'), ('and', 'And')]
    )
    def test_combinator(self, comb_class, op, exp_opname):
        val = expr_value(f'PSF.StringEquals(foo, "x")'
                         f' {op} PSF.StringEquals(foo["bar"], "y")')
        choice = comb_class.from_ast_node(val)
        assert choice.opname == exp_opname
        _assert_comparison_correct(choice.values[0],
                                   'StringEquals', ['foo'], 'x')
        _assert_comparison_correct(choice.values[1],
                                   'StringEquals', ['foo', 'bar'], 'y')

    @pytest.mark.parametrize(
        'text',
        ['1 == 1', 'random_check(a, b)', 'x < 77']
    )
    def test_combinator_bad_input(self, comb_class, text):
        _test_factory_raises(expr_value(text), comb_class.from_ast_node)

    def test_comparison_conversion_to_smr(self):
        val = expr_value('PSF.StringEquals(foo, "x")')
        choice = C.ChoiceCondition.from_ast_node(val)
        smr = choice.as_choice_rule_smr('wash_dishes')
        assert smr == {'Variable': '$.locals.foo',
                       'StringEquals': 'x',
                       'Next': 'wash_dishes'}

    def test_combinator_conversion_to_smr(self):
        val = expr_value('PSF.StringEquals(foo, "x")'
                         ' or PSF.StringEquals(foo["bar"], "y")')
        choice = C.ChoiceCondition.from_ast_node(val)
        smr = choice.as_choice_rule_smr('wash_dishes')
        assert smr == {'Or': [{'Variable': '$.locals.foo',
                               'StringEquals': 'x'},
                              {'Variable': '$.locals.foo.bar',
                               'StringEquals': 'y'}],
                       'Next': 'wash_dishes'}


class TestRetrySpec:
    def test_retry_spec(self):
        expr = expr_value('(["BadThing", "WorseThing"], 2.5, 3, 2.0)')
        ir = C.RetrySpecIR.from_ast_node(expr)
        assert ir.error_equals == ['BadThing', 'WorseThing']
        assert ir.interval_seconds == 2.5
        assert ir.max_attempts == 3
        assert ir.backoff_rate == 2.0


@pytest.fixture
def sample_try_stmt(scope='module'):
    return stmt_value("""
        try:
            x = f(y)
        except BadThing:
            foo = bar(baz)
            qux = hello(world)
        except WorseThing:
            qux = bar(baz)
            foo = hello(world)
        """)


def _assert_sample_try_catchers_correct(catchers):
        assert len(catchers) == 2
        assert catchers[0].error_equals == ['BadThing']
        _assert_is_assignment(catchers[0].body.body[0], 'foo', 'bar', 'baz')
        _assert_is_assignment(catchers[0].body.body[1], 'qux', 'hello', 'world')
        assert catchers[1].error_equals == ['WorseThing']
        _assert_is_assignment(catchers[1].body.body[0], 'qux', 'bar', 'baz')
        _assert_is_assignment(catchers[1].body.body[1], 'foo', 'hello', 'world')


class TestCatcher:
    def test_catcher(self, sample_try_stmt):
        handlers = sample_try_stmt.handlers
        catchers = [C.CatcherIR.from_ast_node(h) for h in handlers]
        _assert_sample_try_catchers_correct(catchers)


class TestReturnIR:
    @pytest.fixture(scope='module', params=[C.ReturnIR, C.StatementIR])
    def return_class(self, request):
        return request.param

    @pytest.mark.xfail(reason='part-way through change')
    def test_return(self, return_class):
        stmt = stmt_value('return banana')
        ir = return_class.from_ast_node(stmt)
        _assert_is_return(ir, 'banana')

    @pytest.mark.xfail(reason='part-way through change')
    def test_return_bad_input(self, return_class):
        _test_factory_raises(stmt_value('return 42'), return_class)


class TestRaiseIR:
    @pytest.fixture(scope='module', params=[C.RaiseIR, C.StatementIR])
    def raise_class(self, request):
        return request.param

    @pytest.mark.xfail(reason='part-way through change')
    def test_raise(self, raise_class):
        stmt = stmt_value('raise PSF.Fail("OverTemp", "too hot!")')
        ir = raise_class.from_ast_node(stmt)
        assert ir.error == 'OverTemp'
        assert ir.cause == 'too hot!'

    @pytest.mark.xfail(reason='part-way through change')
    def test_raise_bad_input(self, raise_class):
        _test_factory_raises(stmt_value('raise x.y()'), raise_class)


class TestFunctionCallIR:
    @pytest.fixture(scope='module', params=[C.FunctionCallIR, C.AssignmentSourceIR])
    def funcall_class(self, request):
        return request.param

    @pytest.mark.xfail(reason='part-way through change')
    def test_bare_call(self, funcall_class):
        expr = expr_value('foo(bar, baz)')
        ir = funcall_class.from_ast_node(expr)
        assert ir.fun_name == 'foo'
        assert ir.arg_names == ['bar', 'baz']
        assert ir.retry_spec is None

    @pytest.mark.xfail(reason='part-way through change')
    def test_call_with_retry_spec(self, funcall_class):
        expr = expr_value('PSF.with_retry_spec(foo, (bar, baz),'
                          ' (["Bad"], 1.5, 3, 1.5),'
                          ' (["Worse"], 1.75, 5, 2.5))')
        ir = funcall_class.from_ast_node(expr)
        assert ir.fun_name == 'foo'
        assert ir.arg_names == ['bar', 'baz']
        assert ir.retry_spec[0].error_equals == ['Bad']
        assert ir.retry_spec[0].interval_seconds == 1.5
        assert ir.retry_spec[0].max_attempts == 3
        assert ir.retry_spec[0].backoff_rate == 1.5
        assert ir.retry_spec[1].error_equals == ['Worse']
        assert ir.retry_spec[1].interval_seconds == 1.75
        assert ir.retry_spec[1].max_attempts == 5
        assert ir.retry_spec[1].backoff_rate == 2.5


class TestAssignmentIR:
    @pytest.fixture(scope='module', params=[C.AssignmentIR, C.StatementIR])
    def assignment_class(self, request):
        return request.param

    @pytest.mark.xfail(reason='part-way through change')
    def test_bare_call(self, assignment_class):
        stmt = stmt_value('foo = bar(baz, qux)')
        ir = assignment_class.from_ast_node(stmt)
        _assert_is_assignment(ir, 'foo', 'bar', 'baz', 'qux')


class TestTryIR:
    @pytest.fixture(scope='module', params=[C.TryIR, C.StatementIR])
    def try_class(self, request):
        return request.param

    @pytest.mark.xfail(reason='part-way through change')
    def test_try(self, sample_try_stmt, try_class):
        ir = try_class.from_ast_node(sample_try_stmt)
        _assert_is_assignment(ir.body.body[0], 'x', 'f', 'y')
        _assert_sample_try_catchers_correct(ir.catchers)


@pytest.fixture(scope='module')
def sample_if_statement():
    return stmt_value("""
    if PSF.StringEquals(foo, 'hello'):
        x = f(y)
    else:
        z = g(u)
        s = h(t)
    """)


class TestIfIR:
    @pytest.fixture(scope='module', params=[C.IfIR, C.StatementIR])
    def if_class(self, request):
        return request.param

    @pytest.mark.xfail(reason='part-way through change')
    def test_if(self, sample_if_statement, if_class):
        ir = if_class.from_ast_node(sample_if_statement)
        _assert_comparison_correct(ir.test, 'StringEquals', ['foo'], 'hello')
        _assert_is_assignment(ir.true_body.body[0], 'x', 'f', 'y')
        _assert_is_assignment(ir.false_body.body[0], 'z', 'g', 'u')
        _assert_is_assignment(ir.false_body.body[1], 's', 'h', 't')


@pytest.fixture(scope='module')
def sample_parallel_invocation():
    return suite_value("""
    def f1():
        r = f(bar, baz)
        s = g(r)
        return s
    def f2():
        x = m(u)
        return x
    results = PSF.parallel(f1, f2)
    """)


class TestParallelIR:
    def test_parallel(self, sample_parallel_invocation):
        def_f1 = C.SuiteIR.from_ast_nodes(sample_parallel_invocation[0].body)
        def_f2 = C.SuiteIR.from_ast_nodes(sample_parallel_invocation[1].body)
        ir = C.ParallelIR.from_ast_node_and_defs(
            sample_parallel_invocation[2].value,
            {'f1': def_f1, 'f2': def_f2})
        assert len(ir.branches) == 2
        br0 = ir.branches[0]
        _assert_is_assignment(br0.body[0], 'r', 'f', 'bar', 'baz')
        _assert_is_assignment(br0.body[1], 's', 'g', 'r')
        _assert_is_return(br0.body[2], 's')
        br1 = ir.branches[1]
        _assert_is_assignment(br1.body[0], 'x', 'm', 'u')
        _assert_is_return(br1.body[1], 'x')


class TestSuiteIR:
    def test_assignments(self):
        body = suite_value("""
            foo = bar(baz)
            qux = hello(world)
        """)
        ir = C.SuiteIR.from_ast_nodes(body)
        _assert_is_assignment(ir.body[0], 'foo', 'bar', 'baz')
        _assert_is_assignment(ir.body[1], 'qux', 'hello', 'world')
