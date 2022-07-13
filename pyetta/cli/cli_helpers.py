from typing import IO, Optional, Sequence

import click
from junit_xml import TestSuite

from pyetta.loaders.interfaces import IDeviceLoader
from pyetta.parsers.builder import ParserBuilder


def cli_process_io_collector(capture: IO,
                             parser_name: str,
                             decode: Optional[str] = None,
                             loader: Optional[IDeviceLoader] = None) -> Sequence[TestSuite]:
    parser = ParserBuilder.from_name(parser_name)

    if loader is not None:
        loader.start_program()

    while not parser.done:
        read_bytes = capture.readline()

        if decode is not None:
            read_bytes = read_bytes.decode(decode)

        if read_bytes is not None and len(read_bytes) > 0:
            ascii_string = read_bytes.strip('\r\n')
            click.echo(ascii_string)
            parser.scan_line(ascii_string)
        else:
            parser.abort()

    return parser.test_suites


