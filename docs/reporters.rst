============
Reporters
============

Reporters are used to convert the parsed test suites into a different forms. These represent the
output stage of the pipeline.

Pyetta supports conversion of the parsed test reporting into some built-in formats, but can be used to
implement custom reporters.

.. autoclass:: pyetta.reporters::Reporter
    :members:
    :undoc-members:

Implementations
=================

The pyetta library comes with some default reporters for use.

.. automodule:: pyetta.reporters
    :members:
    :show-inheritance:
    :special-members: __init__
    :exclude-members: Reporter, generate_report

