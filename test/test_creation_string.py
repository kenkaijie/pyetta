import pytest

from pyetta.core.util import creation_string_to_dict


def test_missing_key():
    test_str = """key1=value1,key2="value two","value '3'"""

    with pytest.raises(ValueError):
        creation_string_to_dict(test_str)


def test_quoted_values():
    test_str = """key1=value1,key2="value two",key3="value '3'",key4='"value"4'"""
    expected_dictionary = {
        "key1": "value1",
        "key2": "value two",
        "key3": "value '3'",
        "key4": '\'"value"4\'',
    }

    actual_dictionary = creation_string_to_dict(test_str)

    assert expected_dictionary == actual_dictionary
