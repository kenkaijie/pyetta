============
Loaders
============

Loaders represent the interface for loading the test firmware onto the target platform. All loaders conform to the
interface and can be extended to include customer loaders if needed to integrate into the cli tool.

Pyetta provides a set of built-in loaders for common scenarios.

.. autoclass:: pyetta.loaders::Loader
    :members:
    :undoc-members:

Implementations
=================

The ``pyetta`` library comes with some default loaders for use to upload test runners to devices.

.. automodule:: pyetta.loaders
    :members:
    :show-inheritance:
    :special-members: __init__
    :exclude-members: Loader, load_to_device, reset_device, start_program

