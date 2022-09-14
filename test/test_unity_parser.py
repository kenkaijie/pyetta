import pytest
from pyetta.parser_data import TestCase, TestResult

from pyetta.parsers import UnityParser


def assert_test_case_equivalent(a: TestCase, b: TestCase) -> None:
    """Helper to evaluate equality for 2 test cases. Used with pytest, so wil directly assert.
    :param a: Test case to check.
    :param b: Other test case to check.
    """

    attr_a = [attr for attr in dir(a)]
    attr_b = [attr for attr in dir(b)]

    assert attr_a == attr_b
    for attr in attr_a:
        if not attr.startswith("__"):
            val_a = getattr(a, attr)
            val_b = getattr(b, attr)
            if not callable(val_a) and not callable(val_b):
                assert val_a == val_b
            elif callable(val_a) and callable(val_b):
                continue
            else:
                # raise assertion here due to mismatch, thus they are not equal
                assert False


def test_assert_test_case_should_not_throw_when_equal():

    a = TestCase(name="test_led_on_command_turns_on_led",
                 filepath="/mypath/foo.c",
                 line_num=19,
                 result=TestResult.Pass,
                 stdout="/mypath/foo.c:19:test_led_on_command_turns_on_led:PASS")

    b = TestCase(name="test_led_on_command_turns_on_led",
                 filepath="/mypath/foo.c",
                 line_num=19,
                 result=TestResult.Pass,
                 stdout="/mypath/foo.c:19:test_led_on_command_turns_on_led:PASS")

    assert_test_case_equivalent(a, b)


def test_assert_test_case_should_throw_when_not_equal():
    a = TestCase(name="test_led_on_command_turns_on_led",
                 filepath="/mypath/foo.c_",
                 line_num=19,
                 result=TestResult.Pass,
                 stdout="/mypath/foo.c:19:test_led_on_command_turns_on_led:PASS")

    b = TestCase(name="test_led_on_command_turns_on_led",
                 filepath="/mypath/foo.c",
                 line_num=19,
                 result=TestResult.Pass,
                 stdout="/mypath/foo.c:19:test_led_on_command_turns_on_led:PASS")

    with pytest.raises(AssertionError):
        assert_test_case_equivalent(a, b)


def test_parse_test_pass_information():
    test_line = b'/mypath/foo.c:19:test_led_on_command_turns_on_led:PASS'

    expected_test_case = TestCase(name="test_led_on_command_turns_on_led",
                                  filepath="/mypath/foo.c",
                                  line_num=19,
                                  result=TestResult.Pass,
                                  stdout="/mypath/foo.c:19:test_led_on_command_turns_on_led:PASS")

    parser = UnityParser()

    parser.feed_data(test_line)

    parser.stop()

    assert len(parser.test_cases) == 1

    test_case: TestCase = parser.test_cases[0]

    assert_test_case_equivalent(expected_test_case, test_case)


def test_parse_test_output():
    test_output = [
        b"/mypath/foo.c:19:test_led_on_command_turns_on_led:PASS",
        b"/mypath/foo.c:20:test_led_off_command_turns_off_led:FAIL:Test Message!",
        b"/mypath/foo.c:23:test_adder_adds_correctly:IGNORE",
        b"",
        b"-----------------------",
        b"3 Tests 1 Failures 1 Ignored ",
        b"FAIL"
    ]

    expected_test_cases = [
        TestCase(name="test_led_on_command_turns_on_led",
                 filepath="/mypath/foo.c",
                 line_num=19,
                 result=TestResult.Pass,
                 stdout=test_output[0].decode('ascii')),
        TestCase(name="test_led_off_command_turns_off_led",
                 filepath="/mypath/foo.c",
                 line_num=20,
                 result=TestResult.Fail,
                 stdout=test_output[1].decode('ascii'),
                 result_message="Test Message!"),
        TestCase(name="test_adder_adds_correctly",
                 filepath="/mypath/foo.c",
                 line_num=23,
                 result=TestResult.Skip,
                 stdout=test_output[2].decode('ascii')),
    ]

    parser = UnityParser(name="tests")

    for line in test_output:
        parser.feed_data(line)

    assert parser.done

    assert len(parser.test_cases) == 3

    for idx, test_case in enumerate(parser.test_cases):
        assert expected_test_cases[idx] == test_case
