# Compiling Python into AWS Lambda / Step Function

Ben North
([GitHub](https://www.github.com/bennorth/)
/ [blog](http://www.redfrontdoor.org/blog/)),
March 2018
[(repository root)](https://github.com/bennorth/pyawssfn)


## Installation

```bash
pip install .
```


# Background

Among the components of Amazon Web Services are the following two
parts of their 'serverless' approach:

* [Lambda](https://aws.amazon.com/lambda/) &mdash; a 'Lambda function'
  is a self-contained piece of code which AWS runs on your behalf in
  response to triggers you specify;
* [Step Functions](https://aws.amazon.com/step-functions/) &mdash; a
  'Step Function' is a mechanism for controlling the interlinked
  operation of multiple steps, including invocation of Lambda
  functions.

While Lambda functions can be written in many languages, to write a
Step Function you describe the logic as a state machine in JSON.  This
seems cumbersome when compared to our normal way of describing how to
control interlinked computations, which is to write some Python (or
C#, or Java, or...).

Based on this observation, the tools presented here are a
'plausibility argument of concept' for the idea that you could write
your top-level logic as a Python program and have it compiled into a
Step Function state machine.  (I haven't developed this far enough to
call it a '*proof* of concept'.)

One of the desired properties of the system is that the source program
should be more or less 'normal Python'.  It should be possible to use
it in two ways:

* Run it as a Python program with the usual Python interpreter;
* Compile it into a Step Function and run in the AWS cloud.

The ability to run your logic as a normal Python program allows local
development and testing.


# Status

Although I think the tools here do show that the idea has promise,
there would be [plenty still to do](future-work.md) to make them
useful for production purposes.  I am very unlikely to have time in
the near future to develop this any further, but the source is all
here (under GPL) if anybody wants to build on it.


# General approach

## Compile Python code to Step Function state machine

The ['Python to Step Function compiler' tool](src/pysfn/tools/compile.py),
`pysfn.tools.compile`,
reads in a file of Python code and emits JSON corresponding to the
control flow of a specified 'entry point' function in that code.  The
resulting JSON is used for the creation of an AWS Step Function.
Various supplied Python functions allow the programmer to express
intent in terms of retry characteristics, parallel invocations, error
handling, etc.  Nonetheless the code is valid normal Python and
executes with (mostly) equivalent semantics to those the resulting
Step Function will have.

## Wrap original Python code as Lambda function

The ['Python to Step Function wrapper compiler' tool](
src/pysfn/tools/gen_lambda.py), `pysfn.tools.gen_lambda`,
constructs a zip-file containing the original Python
code together with a small wrapper.  The zip-file is suitable for
uploading as an AWS Lambda function.  This gives the top-level Step
Function access to what were callees in the original Python code.


# Example

In the below I have omitted details like creation of
[IAM users](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users.html),
creation of
[roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html),
etc.  See Amazon's documentation on these points.


## Run unit tests on original Python

The [original Python source](examples/analyse_text.py) consists of a
main
driver function, with a collection of small functions used by the main
function.  It is very simple, performing a few computations on an
input string, but serves the purpose of illustrating the compilation
process.  It has a suite of unit tests:

```bash
pip install .[dev]  # install development dependencies
pytest tests/test_analyse_text.py
```

Output:
```
# ... ======== 10 passed in 0.02 seconds ======== ...
```

## Wrap original Python ready for Lambda

```bash
python -m pysfn.tools.gen_lambda examples/analyse_text.py lambda-function.zip
unzip -l lambda-function.zip
```

Output:
```
Archive:  lambda-function.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
      302  1980-01-01 00:00   handler.py
     1981  2018-03-25 20:01   inner/analyse_text.py
      452  2018-03-23 22:32   pysfn.py
---------                     -------
     2735                     3 files
```

Now upload `lambda-function.zip` as a new Lambda function with the
`Python 3.6` runtime, specify `handler.dispatch` as its entry point,
and note its ARN for use in the next step.

## Compile original Python into Step Function JSON

```bash
python -m pysfn.tools.compile examples/analyse_text.py LAMBDA-FUN-ARN > examples/stepfun.json
cat examples/stepfun.json
```

Output (the [full output](examples/stepfun.json) is 196 lines):
```
{
  "States": {
    "n0": {
      "Type": "Pass",
      "Result": {
        "function": "get_summary",
        "arg_names": [
          "text"
        ]
      },
      "ResultPath": "$.call_descr",
      "Next": "n1"
    },

    [...]

    "n19": {
      "Type": "Succeed",
      "InputPath": "$.locals.result"
    }
  },
  "StartAt": "n0"
}
```

Now copy-and-paste this as the JSON for a new Step Function.

## Execute Step Function

You should now be able to perform an execution of this Step Function with,
for example, the input
```json
{
  "locals": {
    "text": "a short example"
  }
}
```
to get the output
```json
{
  "output": "text starts with a, has 15 chars, 5 vowels, and 2 spaces"
}
```


# More documentation

* [Implementation notes](implementation-notes.md)
* [Future work](future-work.md)


---

This document: Copyright 2018 Ben North; licensed under
[CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/)

See the file `COPYING` for full licensing details.
