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

## `ReturnIR`

Represents a `return some_variable` statement.  Can only return a
variable.

## `RaiseIR`

Represents a `raise PSF.Fail("BadThing", "something went wrong")`
statement.  The exception raised must be of that form.

## `FunctionCallIR`

Represents a function call of one of the two forms

* `foo(bar, baz)`
* `PSF.with_retry_spec(foo, (bar, baz), spec1, spec2)`

In both of these examples, the function-name is `foo` and the argnames
list is `['bar', 'baz']`.  The second example also has a retry-spec.

## `AssignmentSourceIR`

Represents the source of an assignment; e.g., in `foo = bar(baz)`, the
assignment source is the function call `bar(baz)`.

## `AssignmentIR`

Represents an assignment to a single simple variable from a source.


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


# State Machine Representation

The concepts also have Python representations essentially equivalent
to what will be written out as the JSON description of the state
machine.  Often this will be a dictionary, although lists and literals
also occur.

## `ChoiceCondition`

Objects of (one of the two subclasses of) this class have a method
`as_choice_rule_smr(next)` which returns a dictionary suitable for use
as one element of the `Choices` list of a `Choice` state, or as a
component of such an element.  Top-level elements have a `Next` slot;
lower-level elements do not.
