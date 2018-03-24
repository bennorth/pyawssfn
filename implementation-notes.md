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
