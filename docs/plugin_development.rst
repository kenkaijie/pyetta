=======================
Plugin Development
=======================

This section has guidelines on creating extension plugins for the pyetta
system. This covers the scripted version via the ``--extras`` flag, but can
also apply to the packaged version.

Examples
===========

See the ``examples/plugins`` folder for examples of a contrived plugins.

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
