% Future work

* Implement remainder of choice-rule predicates.  Currently only
  string predicates are handled, because we access the `s` attribute
  of the second argument.

* Allow list indexing in main function.  Currently only dictionary
  lookup works, but should be easy enough to also allow things like
  `PSF.StringEquals(things[7], 'hello')`.

* Could handle bare `return` by converting to `return None` and
  thence to a `Succeed` with `InputPath=null`.

* More-helpful exceptions if `RetrySpecIR` given a node of the wrong
  form; test for these situations.

* More-helpful exceptions if `Catcher` given a node of the wrong
  form; test for these situations.

* When building `TryIR`, check body is single assignment.  If not,
  could maybe convert to `Parallel` with just one strand, then extract
  single result?

* Notice and collapse `if`/`elif`/`elif`/`else` chains into one
  `Choice` state.

* Check that local definitions used for `Parallel` states have no
  args.

* Check for unused or undefined branches of a `Parallel` state.

* Allow keyword arguments in a `FunctionCallIR`.

* Allow `if` without `else`.  Will be mildly fiddly because our
  concept of connecting up the 'next state' can't currently reach
  inside the `Choice` state to set its `Default` field.  Could
  possibly replace `exit_states` with a collection of closures which
  know how to set the correct field of the correct object?
  Alternatively, always create an `else` branch at the State Machine
  level, consisting of a single no-op `Pass` state.

* Validate final state machine; e.g., there should be no unexpected
  states with un-filled 'next state' slots.

* Better and more thorough error-handling throughout, including
  more-helpful error messages when requirements are not met.


# Higher-level research avenues

## `Parallel` state

Reconsider the design whereby the branches of a `Parallel` are
self-contained state machines.  It seems like it would be possible to
have each branch consist just of an entry-point state within the same
top-level collection of states.  This would simplify the task of
translating programming languages to state machines, and (as a small
side-benefit) allow re-use of states between top-level execution and
parallel-branch execution.

## Automatic parallelisation

Automatic deduction, based on data-flow, of which operations are
independent and could be gathered into a `Parallel` state.  Some care
needed because there might be hidden dependencies: One function
invocation might have some side-effect that the next computation
relies on, but this is not explicit in the data-flow through
variables.  E.g., in `c = foo(a); b = bar(a)` it seems that `foo(a)`
and `bar(a)` can proceed independently, but perhaps `bar(a)` relies on
some global state which `foo(a)` establishes, like a change to a
database.
