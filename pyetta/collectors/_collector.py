from pyetta.collectors import Collector
from serial import Serial

class SerialCollector(Serial, Collector):
    """Serial implementation for a collector. This is just a wrapper around the serial
    library.
    """
    pass