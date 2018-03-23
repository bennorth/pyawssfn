import ast


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
