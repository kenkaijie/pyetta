
from junit_xml import TestCase

from pyetta.parsers.unity_parser import UnityParser


def test_parse_test_pass_information():

    parser = UnityParser()

    parser.scan_line("/var/jenkins/workspace/cmake-sample-ken/test/test_embedded/test_embedded.c:19:test_led_on_command_turns_on_led:PASS")

    assert len(parser.test_suites) == 1
    assert len(parser.test_suites[0].test_cases) == 1
    test_case: TestCase = parser.test_suites[0].test_cases[0]
    assert test_case.is_error() is False
    assert test_case.is_failure() is False
    assert test_case.is_skipped() is False
    assert test_case.name == "test_led_on_command_turns_on_led"
    assert test_case.line == 19
    assert test_case.file == "/var/jenkins/workspace/cmake-sample-ken/test/test_embedded/test_embedded.c"


def test_parse_test_output():
    test_output = [
        "/var/jenkins/workspace/cmake-sample-ken/test/test_embedded/test_embedded.c:19:test_led_on_command_turns_on_led:PASS",
        "/var/jenkins/workspace/cmake-sample-ken/test/test_embedded/test_embedded.c:20:test_led_off_command_turns_off_led:FAIL:Test Message!",
        "/var/jenkins/workspace/cmake-sample-ken/test/test_embedded/test_embedded.c:23:test_adder_adds_correctly:IGNORE",
        "",
        "-----------------------",
        "3 Tests 1 Failures 1 Ignored ",
        "FAIL"
    ]

    parser = UnityParser()

    for line in test_output:
        parser.scan_line(line)

    assert parser.done

    test_count = 0
    fail_count = 0
    skip_count = 0
    error_count = 0

    for test_suite in parser.test_suites:
        for test in test_suite.test_cases:  # type: TestCase
            test_count += 1
            fail_count += 1 if test.is_failure() else 0
            skip_count += 1 if test.is_skipped() else 0
            error_count += 1 if test.is_error() else 0

    assert test_count == 3
    assert fail_count == 1
    assert skip_count == 1
    assert error_count == 0