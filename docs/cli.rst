=====================
CLI Usage
=====================

.. tip::

    Detail help messages are available by adding the ``--help`` flag either at the program level, or at the individual
    pipline stage level.

The cli tool assists in performing tests that should be run on the embedded platform. It achieves this by providing
``loaders``, ``collectors``, ``parsers``, ``reporters`` in a preset pipeline.

- Loaders (``l*``) are responsible for loading firmware files into the connected device.
- Collectors (``c*``) are responsible for opening a communications line to the target board in
  order to collect test output.
- Parsers (``p*``) are responsible for parsing test output into structured test data.
- Reporters (``r*``) are responsible for turning test data into various reporting outputs.

The naming convention for the stages are used to simplify discovery when plugins add their own implementations. View the
respective sections of the documentation for information on the built-in stages.

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

.. tip::

    For complex setups with multiple boards or complex scenarios not provided by the CLI's
    processing structure, ``pyetta`` can be used as a library of the sample components in a
    python script that can run.

General Options
================

Each stage has their custom switches and parameters which can be inspected using the ``--help`` on that stage. The
``--help`` command on the cli tool itself will list all the loaded stages in their respective category.

In the command below, the help dialog will be called for the ``cstdin`` stage specifically.

.. code::

    $ pyetta cstdin --help

Plugin Options (``--extras``/``--exclude-plugins``)
`````````````````````````````````````````````````````````

The cli provides a project specific plugin extension point. This is used when a custom stage is needed, but does not
warrant injection via the standard method.

See the ``examples/plugins`` folder for examples on how to develop a script to be used with this option.

In the event a specific library or extension causes the cli to fail but cannot be removed, the ``--exclude-plugins``
option allows the cli to skip loading of modules matching the name.

Verbosity (``-v``)
```````````````````

When diagnosing issues with either the built-in stages or custom loaded stages, it may be useful to set the verbosity of
the cli tool.

The ``-v`` flag can be used to set the log level depending on the number of ``v``'s added. The default amount (0) only
reports errors. The maximum count is 4, which allows all log information to pass through.

.. tip::

    If further customisation is needed, the ``--extras`` flag from the plugin options can be used to grab a specific
    logger from the python ``logging`` library to individually configure the log output that way.
