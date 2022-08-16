========
pyetta
========

.. image:: https://readthedocs.org/projects/pyetta/badge/?version=latest
    :target: https://pyetta.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/1005420113194930309?color=C5F0A4   
    :target: https://discord.gg/ZY2rRgb236
    :alt: Discord

``pyetta`` is a multi-tool made to simplify device on target testing workflows by providing some
helpers which modularise the process of on target testing. It provides both a CLI for simple use
cases, and a library of components that can simplify creation of test scripts.

Roadmap
==========

The current roadmap for features (in no specific order):

- Plugin support for registering loaders, runner, and parser
- Tidy up CLI to run tests
- Add documentation and README for usage (install libusb/openocd)
- Add switches to force file formats (etc --fmt hex)
- Adjust cli naming

CLI Usage
==========

The cli tool assists in performing tests that should be run on the embedded platform. It achieves
this by providing ``loaders``, ``collectors``, ``parsers``, ``reporters``.

- Loaders (``l*``) are responsible for loading firmware files into the connected device
- Collectors (``c*``) are responsible for opening a communications line to the target board in
  order to collect test output.
- Parsers (``p*``) are responsible for parsing captured device output to a set of tests.
- Reporters (``r*``) are responsible for turning parsed test data into various reporting types.

The naming convention for the stages are used to simplify discovery when plugins add their own
implementations.

The example below shows the cli structure, involving the use of multiple stages.

.. code-block::

    $ pyetta lLoader ... cCollector ... pParser ... rReport1 ... rReport2 ...

The image below shows above command from the perspective of the relationships in the execution
pipeline. Note that multiple parsers and reporters can be attached to a single processing chain.

.. mermaid::
    :align: center
    :caption: Execution Pipeline Relationship

    graph LR
        A[Loader] --> B[Collector]
        B --> C[Parser]
        C --> D[Report1]
        C --> E[Report2]

.. note::

    For complex setups with multiple boards or complex scenarios not provided by the CLI's
    processing structure, ``pyetta`` can be used as a library of the sample components in a
    python script that can run.


Plugins
===========

The ``pyetta`` cli can be extended to support stage implementations. There are 2 primary mechanism
implemented to support this.

#. Naming your python module as ``pyetta_*`` and providing the ``load_plugin`` magic method.
#. Passing in a file via the ``--extras`` flag on the cli and providing the ``load_plugin`` magic
   method.

See :ref:`Plugin Development` for more information about developing plugins and how they operate.
