============
Collectors
============

Collectors represent the stage that converts the information on the connection mechanism into frames that can be
translated into unit tests. For typical implementations, this may include a serial line which is hooked up to the
standard human readable testing output.

For specialised applications, the unit test output may be in binary format. It is up to the collector to define its own
encoding and data type. To support the generic nature of this, the collector is a wrapper around the python built-in
:external:py:class:`io.IOBase`.


.. autoclass:: pyetta.collectors::Collector
    :members:
    :undoc-members:

Implementations
===================

The pyetta library comes with some default collectors to capture output from devices.

.. automodule:: pyetta.collectors
    :members:
    :show-inheritance:
    :special-members: __init__
    :exclude-members: Collector
