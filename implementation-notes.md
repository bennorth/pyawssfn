% Implementation notes

Ben North
([GitHub](https://www.github.com/bennorth/)
/ [blog](http://www.redfrontdoor.org/blog/)),
March 2018


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

## `SuiteIR`

Represents a Python suite of statements, e.g., the body executed if
the test in an `if` statement evaluates to true.

## `CatcherIR`

Represents one `except` clause within a Python `try`/`except`
statement.  The Python-level exception name gets mapped by the Step
Function machinery into the Error Name.

## `TryIR`

Represents a `try`/`except` statement, with body and some handlers
(which become `CatcherIR`s).  In a Step Function, catchers apply to a
`Task`, so the body can be only a single assignment.

## `IfIR`

Represents an `if`/`else` statement, with test (`ChoiceCondition`),
body for when test true, and body for when test false.

## `ParallelIR`

Represents a `Parallel` state.  A few plausible approaches to how the
Python should look for this; settled on local function definitions,
which have access to variables in the enclosing scope.  See
`sample_parallel_invocation` test fixture and its usage.  Seems
slightly clunky to pass around the 'enclosing scope' of definitions
but not too bad.

There is precedent for the `(function, (arg1, arg2))` description of a
function in, for example, `multiprocessing.Process()`.


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

## `StateMachineStateIR`

Has a name, a collection of key/value pairs, and an optional 'next
state name'.  Names are assigned incrementally via a class attribute.
The 'value' is accessible via `value_as_json_obj()`.

## `StateMachineFragmentIR`

A fragment of a state machine, representing some well-defined piece of
the source program.  For example, an `if` statement.  Has a collection
of states, knowledge of which state is the 'entry' state, and
knowledge of which states, if any, are 'exit' states.

The whole fragment can be connected to its correct 'next' state via
the `set_next_state()` method.

Can be turned into a JSON-friendly object via `as_json_obj()`.
Components are stored as possibly nested JSON-friendly objects.

The following objects can be converted into fragments, via an
`as_fragment()` method:

### `FunctionCallIR`

As a state-machine fragment, consists of a bit of a dance to pass the
details of which function, called with which arguments, to the Lambda
function.  Uses a `Pass` state to inject a 'call descriptor' into the
state, and then a `Task` state to perform the call and inject the
results into the appropriate slot within `locals`.

### `ParallelIR`

Because each branch of a `Parallel` state is its own self-contained
state machine, we find that state-machine and then 'render' it into
its JSON-friendly form.  All such forms are gathered together into the
resulting `Parallel` state representation, which is then the sole
state of the resulting fragment.

### `RaiseIR`

State-machine fragment is just one `Fail` state.

### `ReturnIR`

State-machine fragment is just one `Succeed` state, pulling out the
appropriate variable from `$.locals` via its `InputPath`.

### `AssignmentIR`

An assignment is from either a simple function call (with optional
retry-specs), or from a `Parallel` call.  The source of the assignment
knows how to construct the fragment, so the `AssignmentIR` delegates
to its `source`.

The source can be either a `FunctionCallIR` or a `ParallelIR`.

### `SuiteIR`

A simple chain of fragments, each one having its next state set to the
'enter state' of the following fragment.

### `IfIR`

A `Choice` state with only one choice clause, corresponding to the
`True` branch of the Python-level `if`.  The `else` clause becomes the
`Default` state.

### `TryIR`

The state-machine semantics are such that only a single `Task` can
have `Catch` clauses, so at the Python level, the body of a `try` must
consist of exactly one assignment.  As a state machine fragment, we
create the assignment's fragment, then punch in a `Catch` field
linking to all the fragments arising from the Python-level `except`
clauses.


# Lambda code

For invoking functions via the Lambda machinery, we create a single
'wrapper'/'dispatcher' Lambda.  This has a very short entry-point
function, which finds the required function name and arg names from
the input dict.  It then finds the required function in the original
module, looks up the arguments from `locals`, and returns the result
of calling that function on those args.  This is all created by the
'wrapper-compiler', `pysfnwc.py`.


---

This document: Copyright 2018 Ben North; licensed under
[CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/)

See the file `COPYING` for full licensing details.
