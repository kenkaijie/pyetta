# flake8: noqa
# as we run unit tests, we will hide certain special classes from being run as tests
from junit_xml import TestCase as jtc
from junit_xml import TestSuite as jts
from pyetta.parser_data import TestCase as ptc
from pyetta.parser_data import TestResult as ptr

for test_classes in [jtc, jts, ptc, ptr]:
    test_classes.__test__ = False

from .fixtures import *
