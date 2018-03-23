import ast


def expr_value(txt):
    return ast.parse(txt).body[0].value
