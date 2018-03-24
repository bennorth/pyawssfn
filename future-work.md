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
