============
Parsers
============

Parsers are used to obtain data chunks from collectors in order to convert them into test suites and cases.

.. autoclass:: pyetta.parsers::Parser
    :members:
    :undoc-members:

Implementations
=================

The pyetta library comes with some default parsers for use that can interpret output from various unit testing programs.

.. automodule:: pyetta.parsers
    :members:
    :show-inheritance:
    :special-members: __init__
    :exclude-members: Parser, feed_data, stop, done, test_suites

