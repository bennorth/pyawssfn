% Implementation notes


# Intermediate Representation

Various concepts within the State Machine have Python representations
at a level suitable for working with in Python.  I.e., they have
Python attributes corresonding to their parts.  These are:

## `ChoiceCondition`

In fact, an instance of one of the two derived classes

* `TestComparison`
* `TestCombinator`

Represents what will be one entry in a `Choice` state's `Choices`
slot.  It may or may not have a `Next` slot, depending on whether it
is part of a larger condition.


# Local variables as Step Function state

The local variables which exist within the 'main' function will be
stored in the Step Function's state object under a `locals`
sub-object.  E.g., the local variable `foo` will be serialised into
the JSON sub-object `locals.foo`.

For these purposes, the parameters of the function are treated as
local variables.  E.g., a function with a parameter `height` will give
rise to a sub-object `locals.height`.

Python objects which are dictionaries have access to their (chained)
keys converted into JSON sub-object access.  E.g., the Python chained
key lookup `foo['bar']['baz']` will be converted to the JSON
expression `foo.bar.baz`.
