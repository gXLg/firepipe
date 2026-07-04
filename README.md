# Firepipe
<sup><i>
<b>F</b>ramework for
<b>I</b>terative,
<b>Re</b>sumable
<b>P</b>rocessing and
<b>I</b>nterpretation of
<b>P</b>arseable
<b>E</b>ntities
</i></sup>

A generator framework for iterative, serializable parsers and processors
for arbitrary structured data.

# Usage

To use the library, clone the repo, add it in `PYTHONPATH` and
simply import `firepipe`.

> [!NOTE]
> There are plans to publish this package to PyPi in the future.

> [!IMPORTANT]
> The name **might be slightly or completely changed in the future**,
> as currently `pypi.org/project/firepipe` is occupied by another
> unrelated project.

Documentation and detailed explanation will follow in distant future.
For now, see [<kbd>examples</kbd>](/examples).

# Description
`firepipe` is a library aimed at generating lexers, parsers
and processors dynamically from a set of rules. It provides a
powerful yet simple API suitable for designing tools that work with
parseable and interpretable contents, such as DSLs, scripting
languages, expression evaluators, type inferrers or transpilers.

Common use cases:
* Programming Language
  1. A user decied to design a programming language
  2. They use this library to define and generate lexers, parsers
     and interpreters for that language
  3. They serialize the finished language toolkit and use it in
     production environments through a small python wrapper
* Configuration Files
  1. A user decides to write a reusable config library for their
     other projects
  2. During initialization, the library generates a liteweight
     parser optimized for the provided config
  3. Projects can provide their own typing and meta-parameters,
     and the generated parser will handle the user input
* Type Analysis
  1. A user decides to write a type analyzer for a language that
     currently lacks one
  2. They create a parser and make the processor reduce the
     parsed values to a type
  3. They embed the parser and the processor in their product
     and ship it

# Features
## Iterative Approach
* Both the parser and the processor are executed iteratively
* Reduces call-overhead and removes the recursion limit
* Provides explicit frame and stack implementations
* Enables serialization, stepping and easier debugging

## Typing
* The runtime environment is designed to support
  typing at interpreter-level
* Simple integration of domain-specific types and python-like
  operator overloading

## Grammar
* Parser rules (a.k.a. grammar), are defined similar to
  regular expressions, with an additional ability for
  circular references
* The library is equipped with a set of useful, predefined
  rules, such as `Ordered`, `Or`, `Repeat`, `Star`
* Operators are defined directly at the grammar level
  through `Op` and `ArgOp` and can support any number of arguments
* The grammar allows any types of associativity
* The AST produced by the parser is flattened, making the handling
  of nested abstract rules easier (note: the resulting AST is not
  flat, but all unnecessary tree levels are removed in the process
  of construction)

## Serialization
* Every component of the library is serializable
* Allows checkpointing, resumable runtime, processing pipelines
  and distributed execution

# Design Decisions
## Top-Down Parsing
The parser uses **top-down** methods to process the data.

Pros:
* Top-down parsers can process highly ambiguous grammars
* The recursion has been replaced with an iterative stack-based
  approach, which improves flexibility

Cons:
* Backtracking top-down parsers may exhibit exponential worst-case
  complexity on ambiguous grammars
* Requires the user to manually write a curated rule list
  free from left recursion or other infinitely recursive rule
  definitions
