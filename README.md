TODO

# Empyre
Rule Engine written in Python.

## Concepts

### Context
The provided data against which `Empyre` will check `Rules`/`Matchers`.

### Matcher
A condition to be evaluated against the `Context`, defined by:
- path: a json-path used to retrieve data from the `Context`
- value: a value that will be matched against the path-retrieved value(s)
- op: the `Operator` that will be used to perform the matching between the above
- comp: a `Comparator` telling if the evaluation should produce `True` or `False`
- transform: an optional callable to modify the `Context` values before the match
- matchers: a list of `Matchers` to be used with the `and`/`or` `Operators`

### Comparator
The expectation for a matcher to match or not. Can be either `is` or `not`.

### Operator
The matching operation performed by a `Matcher`.

Available operators are of different kinds: logical, comparison, membership and regex.

#### Logical
To be used with Matcher's child Matchers
- `and_`: all the child matchers should be True
- `or_`: at least one child matcher should be True

#### Comparison
A comparison between the context-extracted value (left hand) and the Matcher value (right hand):
- `eq`: equivalent to == 
- `gt`: equivalent to >
- `lt`: equivalent to <
- `ge`: equivalent to >=
- `le`: equivalent to <=

#### Membership
Checks that the context-extracted value is present in the Matcher value
- `in_`

#### Regex
Check for a regex match of the Matcher's value against the context-extracted values
- `re`

### Outcome
The output returned is all defined Matchers match.
Can be of 4 kinds:

- `VALUE`: a fixed value
- `DATA`: a dynamic/nested container of values, either extracted from the context or fixed
- `EVENT`: a DATA outcome with a fixed identifier
- `RULE`: another Rule to be evaluated, for complex chains of evaluations

### Rule
Represents a set of Matchers to be evaluated against the context that eventually produces a set of Outcomes.
Defined by:
- matchers: a list of Matchers
- op: the `and_`/`or_` condition to extract matcher's expected results
- comp: a `Comparator` for the op's result
