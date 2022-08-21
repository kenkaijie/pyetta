from io import IOBase

from serial import Serial


class Collector(IOBase):
    """Pyetta collector class, provides a small abstraction on top of an
    IOBase object which will allow additional functionality in the future.
    """


class SerialCollector(Serial, Collector):
    """Serial implementation for a collector. This is just a wrapper around the serial
    library.
    """
