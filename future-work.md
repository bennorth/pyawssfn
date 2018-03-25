% Future work

# Small self-contained ideas

* Implement remainder of choice-rule predicates.  Currently only
  string predicates are handled, because we access the `s` attribute
  of the second argument.

* Implement remaining predicate combinator, `Not`.

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

* Allow `Parallel` state to have `Retry` and `Catch` clauses.  In
  Python, the latter is 'allow `PSF.parallel()` inside
  `try`/`except`'.

* Proper nested scopes for local variables of `Parallel` sub-tasks.

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

* Tools to automatically deploy Step Function and Lambda.

* Detection of tests like in `if x == 'JPEG'`, and conversion into
  equivalent use of `StringEquals`.

* Avoid having to ferry entire state back/forth to the Lambda
  machinery when only the function args and its return value actually
  need to be communicated.

* Implement `Wait` state.  Could be as simple as noticing a magic
  function `PSF.Wait(...)`.  Or could translate Python `time.sleep()`
  into `Wait`.

* Special entry state to extract fields from input corresponding to
  function parameter names, and create an initial `$.locals`.

* Allow use of functions called only for side-effect.  (I.e., just
  `foo()` not `x = bar(y)`.)

* Proper `setup.py`, `requirements.txt` etc. for these tools.


# Higher-level research avenues

## Automatic parallelisation

Automatic deduction, based on data-flow, of which operations are
independent and could be gathered into a `Parallel` state.  Some care
needed because there might be hidden dependencies: One function
invocation might have some side-effect that the next computation
relies on, without this being explicit in the data-flow through
variables.  E.g., in the snippet

```python
c = foo(a)
b = bar(a)
```

it seems that `foo(a)` and `bar(a)` can proceed independently, in
parallel, but perhaps `bar(a)` relies on some global state which
`foo(a)` establishes, like a change to a shared database.

## Directly interpret Python

The state-machine runtime could effectively perform the compilation
work itself, directly understanding Python.


# Wider-scope questions

The following questions are not strictly within the scope of a tool
which translates Python code to a Step Function, but arose while doing
the work:

## Rethink `Parallel` state

Reconsider the current design whereby the branches of a `Parallel` are
self-contained state machines.  It seems like it would be possible to
have each branch consist just of an entry-point state-name, within the
same top-level collection of states.  This could simplify the task of
translating programming languages to state machines, and (as a small
side-benefit) allow re-use of states between top-level execution and
parallel-branch execution.

## Automatically learn appropriate retry specifications

Could the programmer be freed from having to specify appropriate retry
specifications?  If all Lambda invocations were pure (or, more weakly,
'idempotent' might be enough), then the runtime could gather
statistics on each Lambda's reliability, how failures tend to be
clustered temporally, etc., and deduce suitable retry specs.
