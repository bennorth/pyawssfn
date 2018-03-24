import ast
import attr


########################################################################

def psf_attr(nd, raise_if_not=True):
    """
    Extract the attribute name from an AST node of the form

        PSF.something

    If the given AST node is not of that form, either raise a
    ValueError (if raise_if_not is True), or return None (if
    raise_if_not is False).
    """
    attr_val = None
    if isinstance(nd, ast.Attribute):
        val = nd.value
        if isinstance(val, ast.Name) and val.id == 'PSF':
            attr_val = nd.attr
    if attr_val is None and raise_if_not:
        raise ValueError('expected PSF.something')
    return attr_val


def chained_key(nd):
    """
    Given an AST node representing a value like

        foo['bar']['baz']

    return a list of the components involved; here,

        ['foo', 'bar', 'baz']

    If the given node is not of that form, raise a ValueError.
    """
    if isinstance(nd, ast.Name):
        return [nd.id]
    if isinstance(nd, ast.Subscript):
        if isinstance(nd.slice, ast.Index):
            if isinstance(nd.slice.value, ast.Str):
                suffix = nd.slice.value.s
                if isinstance(nd.value, ast.Name):
                    prefix = [nd.value.id]
                else:
                    prefix = chained_key(nd.value)
                return prefix + [suffix]
    raise ValueError('expected chained lookup via strings on name')


def chained_key_smr(k):
    """
    Convert a sequence of chained lookups into the jsonPath which will
    refer to its location in the 'locals' object.
    """
    return '.'.join(['$', 'locals'] + k)


def lmap(f, xs):
    return list(map(f, xs))


def maybe_with_next(base_fields, next_state_name):
    """
    Return a copy of base_fields (a dict), with an additional item

        'Next': next_state_name

    iff next_state_name is non-None.
    """
    obj = dict(base_fields)
    if next_state_name is not None:
        obj['Next'] = next_state_name
    return obj


########################################################################

class ChoiceCondition:
    @staticmethod
    def from_ast_node(nd):
        if isinstance(nd, ast.Call):
            return TestComparison.from_ast_node(nd)
        elif isinstance(nd, ast.BoolOp):
            return TestCombinator.from_ast_node(nd)
        raise ValueError('expected Call')


@attr.s
class TestComparison(ChoiceCondition):
    predicate_name = attr.ib()
    predicate_variable = attr.ib()
    predicate_literal = attr.ib()

    @classmethod
    def from_ast_node(cls, nd):
        if isinstance(nd, ast.Call) and len(nd.args) == 2:
            return cls(psf_attr(nd.func),
                       chained_key(nd.args[0]),
                       nd.args[1].s)
        raise ValueError('expected function-call PSF.something(...)')

    def as_choice_rule_smr(self, next_state_name):
        return maybe_with_next(
            {'Variable': chained_key_smr(self.predicate_variable),
             self.predicate_name: self.predicate_literal},
            next_state_name)


@attr.s
class TestCombinator(ChoiceCondition):
    opname = attr.ib()
    values = attr.ib()

    @classmethod
    def from_ast_node(cls, nd):
        if isinstance(nd, ast.BoolOp):
            if isinstance(nd.op, ast.Or):
                opname = 'Or'
            elif isinstance(nd.op, ast.And):
                opname = 'And'
            else:
                raise ValueError('expected Or or And')
            return cls(opname, lmap(ChoiceCondition.from_ast_node, nd.values))
        raise ValueError('expected BoolOp')

    def as_choice_rule_smr(self, next_state_name):
        terms = [v.as_choice_rule_smr(None) for v in self.values]
        return maybe_with_next(
            {self.opname: terms},
            next_state_name)


########################################################################

@attr.s
class RetrySpecIR:
    error_equals = attr.ib()
    interval_seconds = attr.ib()
    max_attempts = attr.ib()
    backoff_rate = attr.ib()

    @classmethod
    def from_ast_node(cls, nd):
        return cls([error_name.s for error_name in nd.elts[0].elts],
                   nd.elts[1].n,
                   nd.elts[2].n,
                   nd.elts[3].n)


@attr.s
class CatcherIR:
    error_equals = attr.ib()
    body = attr.ib()

    @classmethod
    def from_ast_node(cls, nd):
        return cls([nd.type.id], SuiteIR.from_ast_nodes(nd.body))


########################################################################

@attr.s
class ReturnIR:
    varname = attr.ib()

    @classmethod
    def from_ast_node(cls, nd):
        if isinstance(nd.value, ast.Name):
            return cls(nd.value.id)
        raise ValueError('expected return of variable')


@attr.s
class RaiseIR:
    error = attr.ib()
    cause = attr.ib()

    @classmethod
    def from_ast_node(cls, nd):
        if (isinstance(nd.exc, ast.Call)
                and psf_attr(nd.exc.func) == 'Fail'
                and len(nd.exc.args) == 2
                and isinstance(nd.exc.args[0], ast.Str)
                and isinstance(nd.exc.args[1], ast.Str)):
            return cls(nd.exc.args[0].s, nd.exc.args[1].s)
        raise ValueError('expected raise PSF.Fail("foo", "bar")')


class AssignmentSourceIR:
    @classmethod
    def from_ast_node(cls, nd):
        if isinstance(nd, ast.Call):
            if (isinstance(nd.func, ast.Name)
                    or (isinstance(nd.func, ast.Attribute)
                        and psf_attr(nd.func) == 'with_retry_spec')):
                return FunctionCallIR.from_ast_node(nd)
        raise ValueError('expected fn(x, y)'
                         ' or PSF.with_retry_spec(fn, (x, y), s1, s2)')


@attr.s
class FunctionCallIR(AssignmentSourceIR):
    fun_name = attr.ib()
    arg_names = attr.ib()
    retry_spec = attr.ib()

    @classmethod
    def from_ast_node(cls, nd):
        if isinstance(nd, ast.Call):
            if not isinstance(nd.func, ast.Attribute):
                # Bare call
                return cls(nd.func.id, [a.id for a in nd.args], None)
            elif psf_attr(nd.func) == 'with_retry_spec':
                return cls(nd.args[0].id,
                           [a.id for a in nd.args[1].elts],
                           lmap(RetrySpecIR.from_ast_node, nd.args[2:]))
        raise ValueError('expected some_function(some, args)'
                         ' or PSF.with_retry_spec(fun, (some, args),'
                         ' retry_spec_1, retry_spec_2)')

class StatementIR:
    @classmethod
    def from_ast_node(self, nd):
        if isinstance(nd, ast.Assign):
            return AssignmentIR.from_ast_node(nd)
        raise ValueError('unexpected node type for statement')


@attr.s
class AssignmentIR(StatementIR):
    target_varname = attr.ib()
    source = attr.ib()

    @classmethod
    def from_ast_node(cls, nd):
        if isinstance(nd, ast.Assign) and len(nd.targets) == 1:
            return cls(nd.targets[0].id,
                       AssignmentSourceIR.from_ast_node(nd.value))
        raise ValueError('expected single-target assignment')


@attr.s
class TryIR(StatementIR):
    body = attr.ib()
    catchers = attr.ib()

    @classmethod
    def from_ast_node(cls, nd):
        body = SuiteIR.from_ast_nodes(nd.body)
        return cls(body, [CatcherIR.from_ast_node(h) for h in nd.handlers])


@attr.s
class SuiteIR:
    body = attr.ib()

    @classmethod
    def from_ast_nodes(cls, nds):
        body = []
        for nd in nds:
            body.append(StatementIR.from_ast_node(nd))
        return cls(body)
