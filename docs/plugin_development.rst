=======================
Plugin Development
=======================

This section has guidelines on creating extension plugins for the pyetta
system. This covers the scripted version via the ``--extras`` flag, but can
also apply to the packaged version.

Click Subcommands
=====================

The click commands used by pyetta subclass a special implementation of both click groups and
commands. This allows for special properties to be injected in via the provided decorators.

.. autoclass:: pyetta.cli.utils.PyettaCommand
    :members:
    :special-members: __init__
    :show-inheritance:

To use this specialisation within the plugin, the standard click decorators may be used. See the :ref:`Plugin Example`
for usage.

.. _Magic Method:

Magic Method (``load_plugin``)
====================================

The ``load_plugin`` is a magic method that the cli tool will attempt to find
after loading your python module from the relevant places. If this method is
not found or an exception is thrown during the loading of a plugin, a
``ImportError`` will be thrown instead and the cli tool will terminate.

.. warning::

    Because of this behaviour, misbehaved plugins can break the cli tool.
    Consider uninstalling the plugin if this occurs, or use the option flag
    ``--ignore-plugins`` with the name of the plugins. This flag has to be used
    before the extras flag as they are evaluated in the order of occurrence.

.. _Plugin Example:

``foo_plugin.py`` Example
===========================

.. tip::

    See the ``examples`` folder for examples of plugins. This guide only covers the basics via the ``foo_plugin.py``
    file which is also located within that folder.

Adding Sub Commands
----------------------

Subcommands can be added to the CLI by creating them using click, then injecting
the commands into the system via the :ref:`Magic Method`.

The snippet from ``examples/foo_plugin.py`` shows a new command being added into the system. Executing the ``--help``
option on pyetta will result in this new loader being present.

.. literalinclude:: ../examples/foo_plugin.py
    :linenos:
    :pyobject: lfoo

All defined objects and classes will not have any effect until they are loaded. This can be done by calling the helper
method ``add_command_to_cli``.

.. literalinclude:: ../examples/foo_plugin.py
    :linenos:
    :pyobject: load_plugin

Debugging and Validating Plugins
---------------------------------

Plugins can be debugged by either running the cli tool in debug mode, or by creating a script that acts as a wrapper
around the entry point.

An example of such a script is the entry point python script used to call pyetta itself. This can be called by importing
and calling the :func:`pyetta.cli_entry.main` function.

.. literalinclude:: ../pyetta/cli_entry.py
    :language: python
    :linenos:

Validation at a high level can be performed by testing the correct loading of the plugin. Plugins are all loaded before
the ``--help`` dialog, so any loaded plugins will be visible in the top level help. For the plugin example, we will see
the ``lfoo`` loader present in the system.

The ``[plugin: foo_plugin]`` hint is provided by the plugin loader to inform the user which commands are provided by
which plugins.

.. code-block::

    Usage: cli_entry.py [OPTIONS] STAGE1 [ARGS]... [STAGE2 [ARGS]...]...

      Python Embedded Test Toolbox and Automation

    ...

    Loaders:
      ...
      lfoo    Loader for the foo. [plugin: foo_plugin]
      ...

    ...
